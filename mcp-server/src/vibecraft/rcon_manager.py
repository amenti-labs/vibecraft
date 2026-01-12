"""RCON Connection Manager for Minecraft server communication (legacy).

This module provides a robust RCON connection manager with:
- Persistent connection with automatic reconnection
- Circuit breaker pattern for fail-fast behavior
- Thread-safe connection handling
- Async support via asyncio.to_thread

Deprecated: kept for legacy server mode.
"""

import asyncio
import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from mcrcon import MCRcon

from .config import VibeCraftConfig
from .exceptions import RCONConnectionError, RCONCircuitOpenError, RCONTimeoutError
from .command_patterns import WORLDEDIT_VERSION_PATTERN

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing fast, not attempting connections
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""

    failure_threshold: int = 5  # Failures before opening circuit
    recovery_timeout: float = 30.0  # Seconds before attempting recovery
    half_open_max_calls: int = 3  # Test calls in half-open state


@dataclass
class CircuitBreakerState:
    """Tracks circuit breaker state."""

    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: float = 0.0
    half_open_calls: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock)


class RCONManager:
    """Manages RCON connections to Minecraft server.

    Features:
    - Persistent connection with automatic reconnection
    - Circuit breaker for fail-fast behavior when server is down
    - Thread-safe operations
    - Connection health monitoring
    """

    def __init__(self, config: VibeCraftConfig):
        self.config = config
        self.host = config.rcon_host
        self.port = config.rcon_port
        self.password = config.rcon_password
        self.timeout = config.rcon_timeout

        # Persistent connection
        self._connection: Optional[MCRcon] = None
        self._connection_lock = threading.Lock()
        self._last_used: float = 0.0
        self._connection_max_idle: float = 300.0  # 5 minutes max idle

        # Circuit breaker
        self._circuit_config = CircuitBreakerConfig()
        self._circuit = CircuitBreakerState()

        # World context tracking (for WorldEdit)
        self._world_context_set = False

    def _check_circuit(self) -> None:
        """Check circuit breaker state and raise if open."""
        with self._circuit.lock:
            if self._circuit.state == CircuitState.OPEN:
                # Check if we should transition to half-open
                elapsed = time.time() - self._circuit.last_failure_time
                if elapsed >= self._circuit_config.recovery_timeout:
                    logger.info("Circuit breaker transitioning to HALF_OPEN")
                    self._circuit.state = CircuitState.HALF_OPEN
                    self._circuit.half_open_calls = 0
                else:
                    remaining = self._circuit_config.recovery_timeout - elapsed
                    raise RCONCircuitOpenError(
                        f"Circuit breaker is OPEN. Server appears down. Retry in {remaining:.1f}s"
                    )

            if self._circuit.state == CircuitState.HALF_OPEN:
                if self._circuit.half_open_calls >= self._circuit_config.half_open_max_calls:
                    # Too many test calls, go back to open
                    self._circuit.state = CircuitState.OPEN
                    self._circuit.last_failure_time = time.time()
                    raise RCONCircuitOpenError("Circuit breaker returned to OPEN state")
                self._circuit.half_open_calls += 1

    def _record_success(self) -> None:
        """Record successful operation, potentially closing circuit."""
        with self._circuit.lock:
            if self._circuit.state == CircuitState.HALF_OPEN:
                logger.info("Circuit breaker transitioning to CLOSED (service recovered)")
            self._circuit.state = CircuitState.CLOSED
            self._circuit.failure_count = 0

    def _record_failure(self) -> None:
        """Record failed operation, potentially opening circuit."""
        with self._circuit.lock:
            self._circuit.failure_count += 1
            self._circuit.last_failure_time = time.time()

            if self._circuit.state == CircuitState.HALF_OPEN:
                # Failed during recovery test
                logger.warning("Circuit breaker returning to OPEN (recovery failed)")
                self._circuit.state = CircuitState.OPEN
            elif self._circuit.failure_count >= self._circuit_config.failure_threshold:
                logger.warning(
                    f"Circuit breaker OPENING after {self._circuit.failure_count} failures"
                )
                self._circuit.state = CircuitState.OPEN

    def _ensure_connection(self) -> MCRcon:
        """Ensure we have a valid connection, reconnecting if necessary."""
        with self._connection_lock:
            current_time = time.time()

            # Check if connection is stale (idle too long)
            if (
                self._connection is not None
                and current_time - self._last_used > self._connection_max_idle
            ):
                logger.debug("Connection idle too long, reconnecting")
                self._close_connection_unsafe()

            # Create new connection if needed
            if self._connection is None:
                try:
                    self._connection = MCRcon(
                        self.host, self.password, port=self.port, timeout=self.timeout
                    )
                    self._connection.connect()
                    self._world_context_set = False
                    logger.debug(f"Established RCON connection to {self.host}:{self.port}")
                except Exception as e:
                    self._connection = None
                    raise RCONConnectionError(
                        f"Failed to connect to {self.host}:{self.port}: {e}"
                    ) from e

            self._last_used = current_time
            return self._connection

    def _close_connection_unsafe(self) -> None:
        """Close connection without lock (caller must hold lock)."""
        if self._connection is not None:
            try:
                self._connection.disconnect()
            except Exception:
                pass  # Ignore errors on disconnect
            self._connection = None
            self._world_context_set = False

    def _ensure_world_context(self) -> None:
        """Ensure WorldEdit world context is set."""
        if not self._world_context_set:
            try:
                # Set world context for WorldEdit commands
                if self._connection:
                    self._connection.command("world world")
                    self._world_context_set = True
            except Exception as e:
                logger.debug(f"Could not set world context: {e}")

    def execute_command(self, command: str) -> str:
        """Execute a command on the Minecraft server via RCON.

        Uses persistent connection with automatic reconnection.
        Implements circuit breaker pattern for fail-fast behavior.

        Args:
            command: The command to execute (without leading slash)

        Returns:
            The server's response

        Raises:
            RCONConnectionError: If connection fails
            RCONCircuitOpenError: If circuit breaker is open
            TimeoutError: If command times out
        """
        # Check circuit breaker
        self._check_circuit()

        # Normalize command
        cmd = command.strip()
        if cmd.startswith("/"):
            cmd = cmd[1:]

        if self.config.enable_command_logging:
            logger.info(f"Executing: {cmd}")

        max_retries = 2
        last_error: Optional[Exception] = None

        for attempt in range(max_retries):
            try:
                conn = self._ensure_connection()

                # Set world context for WorldEdit commands
                if cmd.startswith("/") or any(
                    cmd.startswith(we_cmd)
                    for we_cmd in [
                        "pos1",
                        "pos2",
                        "set",
                        "replace",
                        "copy",
                        "paste",
                        "undo",
                        "redo",
                        "expand",
                        "contract",
                        "sphere",
                        "cyl",
                        "walls",
                        "faces",
                        "hollow",
                        "smooth",
                        "distr",
                        "count",
                        "generate",
                        "deform",
                        "flora",
                        "forest",
                        "gmask",
                        "sel",
                    ]
                ):
                    self._ensure_world_context()

                response = conn.command(cmd)

                if self.config.enable_command_logging:
                    logger.info(f"Response: {response}")

                self._record_success()
                return response

            except (BrokenPipeError, ConnectionResetError, OSError) as e:
                # Connection lost, try to reconnect
                logger.warning(f"Connection lost (attempt {attempt + 1}): {e}")
                with self._connection_lock:
                    self._close_connection_unsafe()
                last_error = e

            except TimeoutError as e:
                self._record_failure()
                raise RCONTimeoutError(f"Command timed out after {self.timeout}s: {cmd}") from e

            except Exception as e:
                self._record_failure()
                with self._connection_lock:
                    self._close_connection_unsafe()
                raise RCONConnectionError(f"Command failed: {e}") from e

        # All retries exhausted
        self._record_failure()
        raise RCONConnectionError(f"Failed after {max_retries} attempts: {last_error}")

    async def execute_command_async(self, command: str) -> str:
        """Async wrapper for execute_command.

        Runs the synchronous RCON operation in a thread pool
        to avoid blocking the event loop.
        """
        return await asyncio.to_thread(self.execute_command, command)

    def test_connection(self) -> bool:
        """Test the RCON connection to the Minecraft server.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.execute_command("list")
            logger.info(f"RCON connection test successful: {response}")
            return True
        except Exception as e:
            logger.error(f"RCON connection test failed: {e}")
            return False

    def detect_worldedit_version(self) -> Optional[str]:
        """Detect WorldEdit version installed on the server.

        Returns:
            WorldEdit version string or None if detection fails
        """
        try:
            # Use WorldEdit's own //version command
            response = self.execute_command("//version")

            if response and "WorldEdit" in response:
                match = WORLDEDIT_VERSION_PATTERN.search(response)
                if match:
                    version = match.group(1)
                    logger.info(f"Detected WorldEdit version: {version}")
                    return version

            logger.warning(f"Could not detect WorldEdit version: {response}")
            return None

        except Exception as e:
            logger.warning(f"Failed to detect WorldEdit version: {e}")
            return None

    def get_server_info(self) -> dict[str, str]:
        """Get basic server information.

        Returns:
            Dictionary with server info (players, time, etc.)
        """
        info = {}

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

    def get_circuit_status(self) -> dict:
        """Get current circuit breaker status."""
        with self._circuit.lock:
            return {
                "state": self._circuit.state.value,
                "failure_count": self._circuit.failure_count,
                "last_failure": self._circuit.last_failure_time,
                "threshold": self._circuit_config.failure_threshold,
                "recovery_timeout": self._circuit_config.recovery_timeout,
            }

    def reset_circuit(self) -> None:
        """Manually reset circuit breaker to closed state."""
        with self._circuit.lock:
            self._circuit.state = CircuitState.CLOSED
            self._circuit.failure_count = 0
            logger.info("Circuit breaker manually reset to CLOSED")

    def close(self) -> None:
        """Close the RCON connection and cleanup resources."""
        with self._connection_lock:
            self._close_connection_unsafe()
        logger.info("RCON manager closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    # Backwards-compatibility alias
    def send_command(self, command: str) -> str:
        """Backwards-compatible alias for execute_command.

        Note: This method is deprecated. Use execute_command instead.
        """
        return self.execute_command(command)
