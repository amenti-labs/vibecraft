"""Client bridge for communicating with the local Fabric mod over WebSocket."""

from __future__ import annotations

import asyncio
import json
import logging
import random
import threading
import time
import uuid
from typing import Any, Dict, Optional

from websocket import create_connection
from websocket import WebSocketTimeoutException, WebSocketConnectionClosedException

from .config import VibeCraftConfig
from .exceptions import (
    ClientBridgeConnectionError,
    ClientBridgeTimeoutError,
    ClientBridgeProtocolError,
)
from .command_patterns import WORLDEDIT_VERSION_PATTERN
from .constants import WorldEditConstants
from .message_schemas import (
    validate_request,
    validate_response,
    validate_hello_result,
    validate_capabilities,
)

logger = logging.getLogger(__name__)

# Reconnect backoff constants
BACKOFF_BASE_SECONDS = 1.0
BACKOFF_MAX_SECONDS = 60.0
BACKOFF_MULTIPLIER = 2.0
BACKOFF_JITTER_FACTOR = 0.25  # +/- 25% jitter


class ClientBridge:
    """Manages a local WebSocket connection to the Fabric client mod."""

    def __init__(self, config: VibeCraftConfig):
        self.config = config
        self.host = config.client_host
        self.port = config.client_port
        self.path = config.client_path
        self.token = config.client_token
        self.timeout = config.client_timeout

        self._connection = None
        self._connection_lock = threading.Lock()
        self._request_lock = threading.Lock()
        self._command_lock = (
            threading.Lock()
        )  # Serialize command execution to prevent response mixing
        self._last_used = 0.0
        self._connection_max_idle = config.client_max_idle
        self._capabilities: Dict[str, Any] = {}
        self._inbox: list[Dict[str, Any]] = []
        self._inbox_lock = threading.Lock()
        self._pending_responses: Dict[str, Dict[str, Any]] = {}
        self._pending_condition = threading.Condition()
        self._pending_request_ids: set[str] = set()
        self._reader_thread: Optional[threading.Thread] = None
        self._reader_stop = threading.Event()
        self._reader_error: Optional[Exception] = None

        # Reconnect backoff state
        self._consecutive_failures = 0
        self._last_failure_time = 0.0
        self._backoff_until = 0.0

    def _endpoint(self) -> str:
        scheme = "wss" if self.config.client_use_ssl else "ws"
        path = self.path if self.path.startswith("/") else f"/{self.path}"
        return f"{scheme}://{self.host}:{self.port}{path}"

    def _calculate_backoff(self) -> float:
        """Calculate backoff delay with exponential increase and jitter."""
        if self._consecutive_failures == 0:
            return 0.0

        # Exponential backoff: base * (multiplier ^ (failures - 1))
        delay = BACKOFF_BASE_SECONDS * (BACKOFF_MULTIPLIER ** (self._consecutive_failures - 1))
        delay = min(delay, BACKOFF_MAX_SECONDS)

        # Add jitter: +/- BACKOFF_JITTER_FACTOR
        jitter_range = delay * BACKOFF_JITTER_FACTOR
        delay += random.uniform(-jitter_range, jitter_range)

        return max(0.0, delay)

    def _record_connection_failure(self) -> None:
        """Record a connection failure and update backoff state."""
        self._consecutive_failures += 1
        self._last_failure_time = time.time()
        backoff_delay = self._calculate_backoff()
        self._backoff_until = time.time() + backoff_delay
        logger.debug(
            "Connection failure #%d, backing off for %.2fs",
            self._consecutive_failures,
            backoff_delay,
        )

    def _reset_backoff(self) -> None:
        """Reset backoff state after successful connection."""
        if self._consecutive_failures > 0:
            logger.debug(
                "Connection succeeded after %d failures, resetting backoff",
                self._consecutive_failures,
            )
        self._consecutive_failures = 0
        self._last_failure_time = 0.0
        self._backoff_until = 0.0

    def _ensure_connection(self) -> None:
        with self._connection_lock:
            now = time.time()

            # Check if we're in backoff period
            if self._connection is None and now < self._backoff_until:
                remaining = self._backoff_until - now
                raise ClientBridgeConnectionError(
                    f"Connection in backoff period ({remaining:.1f}s remaining after "
                    f"{self._consecutive_failures} consecutive failures)"
                )

            if self._connection is not None and now - self._last_used > self._connection_max_idle:
                self._close_connection_unsafe()

            if self._connection is None:
                try:
                    self._connection = create_connection(self._endpoint(), timeout=self.timeout)
                    self._reset_backoff()
                    logger.debug("Connected to client bridge at %s", self._endpoint())
                except Exception as exc:
                    self._connection = None
                    self._record_connection_failure()
                    raise ClientBridgeConnectionError(
                        f"Failed to connect to client bridge at {self._endpoint()}: {exc}"
                    ) from exc

            self._start_reader_thread()
            self._last_used = now

    def _close_connection_unsafe(self) -> None:
        if self._connection is not None:
            try:
                self._reader_stop.set()
                self._connection.close()
            except Exception:
                pass
            self._connection = None
        self._reader_thread = None
        self._reader_error = None
        with self._pending_condition:
            self._pending_responses.clear()
            self._pending_request_ids.clear()
            self._pending_condition.notify_all()

    def _start_reader_thread(self) -> None:
        if self._reader_thread and self._reader_thread.is_alive():
            return

        self._reader_stop.clear()
        self._reader_error = None
        self._reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._reader_thread.start()

    def _mark_reader_error(self, error: Exception) -> None:
        self._reader_error = error
        with self._pending_condition:
            self._pending_condition.notify_all()

    def _reader_loop(self) -> None:
        conn = self._connection
        if conn is None:
            return

        while not self._reader_stop.is_set():
            try:
                raw = conn.recv()
            except WebSocketTimeoutException:
                continue
            except WebSocketConnectionClosedException:
                self._mark_reader_error(
                    ClientBridgeConnectionError("Client bridge connection closed")
                )
                return
            except Exception as exc:
                self._mark_reader_error(
                    ClientBridgeConnectionError(f"Client bridge recv failed: {exc}")
                )
                return

            if isinstance(raw, bytes):
                raw = raw.decode("utf-8", errors="ignore")

            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                self._mark_reader_error(
                    ClientBridgeProtocolError(f"Invalid JSON response: {raw!r}")
                )
                return

            message_id = message.get("id")
            if message_id:
                with self._pending_condition:
                    if message_id in self._pending_request_ids:
                        self._pending_responses[message_id] = message
                        self._pending_request_ids.discard(message_id)
                        self._pending_condition.notify_all()
                    else:
                        self._store_inbox_message(message)
            else:
                self._store_inbox_message(message)

    def _validate_request(self, message: Dict[str, Any]) -> None:
        """Validate outgoing request message against schema (logs warnings only)."""
        try:
            validate_request(message)
        except Exception as exc:
            logger.warning("Request schema validation failed: %s", exc)

    def _validate_response(self, response: Dict[str, Any]) -> None:
        """Validate incoming response message against schema (logs warnings only)."""
        try:
            validate_response(response)
        except Exception as exc:
            logger.warning("Response schema validation failed: %s", exc)

    def _request(self, message_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._ensure_connection()

        request_id = uuid.uuid4().hex
        message = {
            "id": request_id,
            "type": message_type,
            "payload": payload,
        }
        if self.token:
            message["token"] = self.token

        # Validate outgoing request
        self._validate_request(message)

        deadline = time.monotonic() + self.timeout

        try:
            with self._pending_condition:
                self._pending_request_ids.add(request_id)

            with self._request_lock:
                self._connection.send(json.dumps(message))

            with self._pending_condition:
                while True:
                    if request_id in self._pending_responses:
                        response = self._pending_responses.pop(request_id)
                        # Validate incoming response
                        self._validate_response(response)
                        return response

                    if self._reader_error:
                        raise self._reader_error

                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise ClientBridgeTimeoutError(
                            f"Client bridge timed out waiting for response to {message_type}"
                        )
                    self._pending_condition.wait(timeout=remaining)
        except Exception as exc:
            with self._connection_lock:
                self._close_connection_unsafe()
            if isinstance(exc, ClientBridgeTimeoutError):
                raise
            if isinstance(exc, ClientBridgeProtocolError):
                raise
            if isinstance(exc, ClientBridgeConnectionError):
                raise
            raise ClientBridgeConnectionError(f"Client bridge request failed: {exc}") from exc
        finally:
            with self._pending_condition:
                self._pending_request_ids.discard(request_id)

    def _store_inbox_message(self, message: Dict[str, Any]) -> None:
        with self._inbox_lock:
            self._inbox.append(message)
            if len(self._inbox) > 100:
                self._inbox.pop(0)

    def drain_inbox(self) -> list[Dict[str, Any]]:
        """Return and clear any out-of-band messages received."""
        with self._inbox_lock:
            messages = list(self._inbox)
            self._inbox.clear()
        return messages

    def _normalize_command(self, command: str) -> str:
        normalized = command.strip()
        if not normalized:
            return normalized
        if normalized.startswith("/") or normalized.startswith("//"):
            return normalized
        return f"/{normalized}"

    def _worldedit_available(self) -> Optional[bool]:
        worldedit = self._capabilities.get("worldedit")
        if isinstance(worldedit, dict):
            available = worldedit.get("available")
            if isinstance(available, bool):
                return available
        if isinstance(worldedit, bool):
            return worldedit
        return None

    def _is_worldedit_command(self, command: str) -> bool:
        if command.startswith("//"):
            return True
        if not command.startswith("/"):
            return False
        verb = command.lstrip("/").split(maxsplit=1)[0].lower()
        return verb in WorldEditConstants.WORLD_EDIT_COMMANDS

    def _enforce_worldedit_policy(self, command: str) -> None:
        if not self._is_worldedit_command(command):
            return

        mode = self.config.worldedit_mode
        fallback = self.config.worldedit_fallback
        available = self._worldedit_available()

        if mode == "off":
            raise ClientBridgeProtocolError("WorldEdit is disabled by configuration.")

        if mode == "force":
            if available is not True:
                raise ClientBridgeProtocolError(
                    "WorldEdit is required but not available for this player."
                )
            return

        if mode == "auto" and available is False and fallback == "disable":
            raise ClientBridgeProtocolError("WorldEdit is unavailable and fallback is disabled.")

    def execute_command(self, command: str) -> str:
        """Execute a Minecraft command via the client bridge.

        Commands are serialized via _command_lock to prevent response mixing.
        The Minecraft client mod uses a 500ms capture window for responses,
        so concurrent commands would have overlapping capture windows,
        causing responses to be attributed to the wrong commands.
        """
        normalized = self._normalize_command(command)
        self._enforce_worldedit_policy(normalized)

        # Serialize command execution to prevent capture window overlap
        with self._command_lock:
            response = self._request("command.execute", {"command": normalized})
            if not response.get("ok", True):
                raise ClientBridgeProtocolError(response.get("error", "Command failed"))
            return str(response.get("result", ""))

    async def execute_command_async(self, command: str) -> str:
        """Async wrapper for execute_command."""
        return await asyncio.to_thread(self.execute_command, command)

    def test_connection(self) -> bool:
        """Test if the client bridge is reachable."""
        try:
            response = self._request("hello", {})
            result = response.get("result", {}) if isinstance(response.get("result"), dict) else {}

            # Validate hello result structure
            try:
                validate_hello_result(result)
            except Exception as exc:
                logger.warning("Hello result schema validation failed: %s", exc)

            capabilities = response.get("capabilities")
            if capabilities is None:
                capabilities = result.get("capabilities", {})

            # Validate capabilities structure
            if capabilities:
                try:
                    validate_capabilities(capabilities)
                except Exception as exc:
                    logger.warning("Capabilities schema validation failed: %s", exc)

            self._capabilities = capabilities or {}
            return bool(response.get("ok", True))
        except Exception as exc:
            logger.warning("Client bridge test failed: %s", exc)
            return False

    def get_capabilities(self) -> Dict[str, Any]:
        """Return cached capability info when available."""
        return self._capabilities

    def get_server_info(self) -> Dict[str, str]:
        """Best-effort server info via client commands."""
        info: Dict[str, str] = {}

        try:
            response = self._request("server.info", {})
            if response.get("ok") and isinstance(response.get("result"), dict):
                return response["result"]
        except Exception:
            pass

        try:
            info["players"] = self.execute_command("list")
        except Exception:
            info["players"] = "Unable to retrieve player list"

        try:
            info["time"] = self.execute_command("time query daytime")
        except Exception:
            info["time"] = "Unable to retrieve time"

        try:
            info["difficulty"] = self.execute_command("difficulty")
        except Exception:
            info["difficulty"] = "Unable to retrieve difficulty"

        return info

    def detect_worldedit_version(self) -> Optional[str]:
        """Detect WorldEdit version if available on the server."""
        try:
            # Use WorldEdit's own //version command
            response = self.execute_command("//version")
        except Exception as exc:
            logger.warning("Failed to detect WorldEdit version: %s", exc)
            return None

        if not response or "WorldEdit" not in response:
            return None

        match = WORLDEDIT_VERSION_PATTERN.search(response)
        if match:
            return match.group(1)
        return None

    def close(self) -> None:
        """Close the client bridge connection."""
        with self._connection_lock:
            self._close_connection_unsafe()

    def reset_backoff(self) -> None:
        """Manually reset the backoff state to allow immediate reconnection."""
        with self._connection_lock:
            self._reset_backoff()

    def get_backoff_status(self) -> Dict[str, Any]:
        """Get current backoff status for debugging/monitoring."""
        now = time.time()
        return {
            "consecutive_failures": self._consecutive_failures,
            "in_backoff": now < self._backoff_until,
            "backoff_remaining": max(0.0, self._backoff_until - now),
            "last_failure_time": self._last_failure_time,
        }

    def send_command(self, command: str) -> str:
        """Backwards-compatible alias for execute_command."""
        return self.execute_command(command)

    # ========== Screenshot ==========

    def capture_screenshot(self, max_width: int = 1920, max_height: int = 1080) -> Dict[str, Any]:
        """Capture a screenshot from the Minecraft client."""
        response = self._request(
            "screenshot.capture",
            {"max_width": max_width, "max_height": max_height},
        )
        if not response.get("ok", True):
            raise ClientBridgeProtocolError(response.get("error", "Screenshot failed"))
        return response.get("result", {})

    async def capture_screenshot_async(
        self, max_width: int = 1920, max_height: int = 1080
    ) -> Dict[str, Any]:
        """Async wrapper for capture_screenshot."""
        return await asyncio.to_thread(self.capture_screenshot, max_width, max_height)

    # ========== Region Scanning ==========

    def scan_region(
        self,
        x1: int,
        y1: int,
        z1: int,
        x2: int,
        y2: int,
        z2: int,
        include_states: bool = False,
    ) -> Dict[str, Any]:
        """Scan blocks in a rectangular region."""
        response = self._request(
            "region.scan",
            {
                "x1": x1,
                "y1": y1,
                "z1": z1,
                "x2": x2,
                "y2": y2,
                "z2": z2,
                "include_states": include_states,
            },
        )
        if not response.get("ok", True):
            raise ClientBridgeProtocolError(response.get("error", "Region scan failed"))
        return response.get("result", {})

    async def scan_region_async(
        self,
        x1: int,
        y1: int,
        z1: int,
        x2: int,
        y2: int,
        z2: int,
        include_states: bool = False,
    ) -> Dict[str, Any]:
        """Async wrapper for scan_region."""
        return await asyncio.to_thread(self.scan_region, x1, y1, z1, x2, y2, z2, include_states)

    def get_heightmap(self, x1: int, z1: int, x2: int, z2: int) -> Dict[str, Any]:
        """Get heightmap for a rectangular area (Y value for each X,Z)."""
        response = self._request(
            "region.heightmap",
            {"x1": x1, "z1": z1, "x2": x2, "z2": z2},
        )
        if not response.get("ok", True):
            raise ClientBridgeProtocolError(response.get("error", "Heightmap failed"))
        return response.get("result", {})

    async def get_heightmap_async(self, x1: int, z1: int, x2: int, z2: int) -> Dict[str, Any]:
        """Async wrapper for get_heightmap."""
        return await asyncio.to_thread(self.get_heightmap, x1, z1, x2, z2)

    # ========== Player Context ==========

    def get_player_context(self, reach: float = 128.0) -> Dict[str, Any]:
        """Get detailed player context including position, rotation, and raycast target."""
        response = self._request("player.context", {"reach": reach})
        if not response.get("ok", True):
            raise ClientBridgeProtocolError(response.get("error", "Player context failed"))
        return response.get("result", {})

    async def get_player_context_async(self, reach: float = 128.0) -> Dict[str, Any]:
        """Async wrapper for get_player_context."""
        return await asyncio.to_thread(self.get_player_context, reach)

    def get_nearby_entities(self, radius: float = 32.0) -> Dict[str, Any]:
        """Get entities near the player."""
        response = self._request("player.entities", {"radius": radius})
        if not response.get("ok", True):
            raise ClientBridgeProtocolError(response.get("error", "Nearby entities failed"))
        return response.get("result", {})

    async def get_nearby_entities_async(self, radius: float = 32.0) -> Dict[str, Any]:
        """Async wrapper for get_nearby_entities."""
        return await asyncio.to_thread(self.get_nearby_entities, radius)

    # ========== Palette Analysis ==========

    def analyze_palette(self, x: int, y: int, z: int, radius: int = 16) -> Dict[str, Any]:
        """Analyze block palette in a spherical radius."""
        response = self._request(
            "palette.analyze",
            {"x": x, "y": y, "z": z, "radius": radius},
        )
        if not response.get("ok", True):
            raise ClientBridgeProtocolError(response.get("error", "Palette analysis failed"))
        return response.get("result", {})

    async def analyze_palette_async(
        self, x: int, y: int, z: int, radius: int = 16
    ) -> Dict[str, Any]:
        """Async wrapper for analyze_palette."""
        return await asyncio.to_thread(self.analyze_palette, x, y, z, radius)

    def analyze_palette_region(
        self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int
    ) -> Dict[str, Any]:
        """Analyze block palette in a rectangular region."""
        response = self._request(
            "palette.region",
            {"x1": x1, "y1": y1, "z1": z1, "x2": x2, "y2": y2, "z2": z2},
        )
        if not response.get("ok", True):
            raise ClientBridgeProtocolError(response.get("error", "Palette region failed"))
        return response.get("result", {})

    async def analyze_palette_region_async(
        self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int
    ) -> Dict[str, Any]:
        """Async wrapper for analyze_palette_region."""
        return await asyncio.to_thread(self.analyze_palette_region, x1, y1, z1, x2, y2, z2)
