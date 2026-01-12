"""Integration tests for ClientBridge with a mock Fabric mod WebSocket server.

This test suite simulates the Java Fabric mod's WebSocket server behavior
to verify the full protocol flow between the Python ClientBridge and the
expected mod responses.
"""

import json
import threading
import time
import pytest
from http.server import HTTPServer
from websocket_server import WebsocketServer

from vibecraft.client_bridge import ClientBridge
from vibecraft.config import VibeCraftConfig
from vibecraft.exceptions import (
    ClientBridgeConnectionError,
    ClientBridgeTimeoutError,
    ClientBridgeProtocolError,
)


class MockFabricMod:
    """Mock implementation of the VibeCraft Fabric mod WebSocket server.

    Simulates the behavior defined in CLIENT_BRIDGE_PROTOCOL.md.
    """

    def __init__(self, port: int = 18766, token: str = "", worldedit_available: bool = True):
        self.port = port
        self.token = token
        self.worldedit_available = worldedit_available
        self.allow_ai_control = True
        self.received_messages: list[dict] = []
        self._server = None
        self._thread = None
        self._running = False

    def start(self):
        """Start the mock WebSocket server."""
        self._server = WebsocketServer(host="127.0.0.1", port=self.port)
        self._server.set_fn_message_received(self._on_message)
        self._server.set_fn_new_client(self._on_connect)
        self._running = True
        self._thread = threading.Thread(target=self._server.run_forever, daemon=True)
        self._thread.start()
        time.sleep(0.1)  # Give server time to start

    def stop(self):
        """Stop the mock WebSocket server."""
        self._running = False
        if self._server:
            self._server.shutdown_gracefully()
        if self._thread:
            self._thread.join(timeout=1.0)

    def _on_connect(self, client, server):
        """Handle new client connection."""
        pass

    def _on_message(self, client, server, message):
        """Handle incoming message and send response."""
        try:
            request = json.loads(message)
        except json.JSONDecodeError:
            self._send_error(client, server, None, "Invalid JSON")
            return

        self.received_messages.append(request)

        msg_id = request.get("id")
        msg_type = request.get("type")
        token = request.get("token")

        # Token validation
        if self.token and token != self.token:
            self._send_error(client, server, msg_id, "Authentication failed")
            return

        # Route message types
        if msg_type == "hello":
            self._handle_hello(client, server, msg_id)
        elif msg_type == "command.execute":
            self._handle_command(client, server, msg_id, request.get("payload", {}))
        elif msg_type == "server.info":
            self._handle_server_info(client, server, msg_id)
        else:
            self._send_error(client, server, msg_id, f"Unknown message type: {msg_type}")

    def _handle_hello(self, client, server, msg_id):
        """Handle hello handshake."""
        response = {
            "id": msg_id,
            "ok": True,
            "result": {
                "client": "fabric",
                "version": "0.1.0",
                "minecraft": "1.21.11",
                "enabled": True,
                "allow_ai_control": self.allow_ai_control,
                "capabilities": {
                    "worldedit": {
                        "available": self.worldedit_available,
                        "reason": "command_tree"
                    },
                    "vision": False,
                    "region_snapshot": False
                }
            }
        }
        server.send_message(client, json.dumps(response))

    def _handle_command(self, client, server, msg_id, payload):
        """Handle command execution."""
        if not self.allow_ai_control:
            self._send_error(client, server, msg_id,
                           "AI control is disabled. Run /vibecraft allow to enable.")
            return

        command = payload.get("command", "")
        if not command or not command.strip():
            self._send_error(client, server, msg_id, "Command cannot be empty.")
            return

        response = {
            "id": msg_id,
            "ok": True,
            "result": "Command dispatched"
        }
        server.send_message(client, json.dumps(response))

    def _handle_server_info(self, client, server, msg_id):
        """Handle server info request."""
        response = {
            "id": msg_id,
            "ok": True,
            "result": {
                "time": "6000",
                "difficulty": "normal",
                "players": "There are 1 players online: TestPlayer"
            }
        }
        server.send_message(client, json.dumps(response))

    def _send_error(self, client, server, msg_id, error_message):
        """Send error response."""
        response = {
            "ok": False,
            "error": error_message
        }
        if msg_id:
            response["id"] = msg_id
        server.send_message(client, json.dumps(response))


@pytest.fixture
def mock_mod():
    """Create and start a mock Fabric mod server."""
    mod = MockFabricMod(port=18766)
    mod.start()
    yield mod
    mod.stop()


@pytest.fixture
def mock_mod_with_token():
    """Create mock mod with token authentication."""
    mod = MockFabricMod(port=18767, token="test-secret-token")
    mod.start()
    yield mod
    mod.stop()


@pytest.fixture
def mock_mod_no_worldedit():
    """Create mock mod without WorldEdit."""
    mod = MockFabricMod(port=18768, worldedit_available=False)
    mod.start()
    yield mod
    mod.stop()


@pytest.fixture
def client_config():
    """Create client config pointing to mock server."""
    return VibeCraftConfig(
        client_host="127.0.0.1",
        client_port=18766,
        client_path="/vibecraft",
        client_timeout=5,
    )


class TestHelloHandshake:
    """Test the hello handshake protocol."""

    def test_hello_returns_capabilities(self, mock_mod, client_config):
        """Verify hello returns proper capability structure."""
        client = ClientBridge(client_config)
        try:
            assert client.test_connection() is True
            caps = client.get_capabilities()

            assert "worldedit" in caps
            assert caps["worldedit"]["available"] is True
            assert caps["worldedit"]["reason"] == "command_tree"
            assert caps.get("vision") is False
            assert caps.get("region_snapshot") is False
        finally:
            client.close()

    def test_hello_with_worldedit_unavailable(self, mock_mod_no_worldedit):
        """Verify capabilities when WorldEdit is not available."""
        config = VibeCraftConfig(
            client_host="127.0.0.1",
            client_port=18768,
            client_timeout=5,
        )
        client = ClientBridge(config)
        try:
            assert client.test_connection() is True
            caps = client.get_capabilities()
            assert caps["worldedit"]["available"] is False
        finally:
            client.close()


class TestCommandExecution:
    """Test command execution protocol."""

    def test_execute_vanilla_command(self, mock_mod, client_config):
        """Test executing a vanilla Minecraft command."""
        client = ClientBridge(client_config)
        try:
            client.test_connection()
            result = client.execute_command("time set day")
            assert result == "Command dispatched"

            # Verify command was normalized with leading slash
            assert mock_mod.received_messages[-1]["payload"]["command"] == "/time set day"
        finally:
            client.close()

    def test_execute_worldedit_command(self, mock_mod, client_config):
        """Test executing a WorldEdit command."""
        client = ClientBridge(client_config)
        try:
            client.test_connection()
            result = client.execute_command("//set stone")
            assert result == "Command dispatched"

            # WorldEdit commands keep their // prefix
            assert mock_mod.received_messages[-1]["payload"]["command"] == "//set stone"
        finally:
            client.close()

    def test_execute_multiple_commands(self, mock_mod, client_config):
        """Test executing multiple commands in sequence."""
        client = ClientBridge(client_config)
        try:
            client.test_connection()

            commands = ["//pos1", "//pos2", "//set stone", "say Done!"]
            for cmd in commands:
                result = client.execute_command(cmd)
                assert result == "Command dispatched"

            # Verify all commands were received
            cmd_messages = [m for m in mock_mod.received_messages if m["type"] == "command.execute"]
            assert len(cmd_messages) == 4
        finally:
            client.close()


class TestAuthentication:
    """Test token authentication."""

    def test_connection_with_valid_token(self, mock_mod_with_token):
        """Test connection succeeds with correct token."""
        config = VibeCraftConfig(
            client_host="127.0.0.1",
            client_port=18767,
            client_token="test-secret-token",
            client_timeout=5,
        )
        client = ClientBridge(config)
        try:
            assert client.test_connection() is True
        finally:
            client.close()

    def test_connection_with_invalid_token(self, mock_mod_with_token):
        """Test connection fails with wrong token."""
        config = VibeCraftConfig(
            client_host="127.0.0.1",
            client_port=18767,
            client_token="wrong-token",
            client_timeout=5,
        )
        client = ClientBridge(config)
        try:
            # test_connection catches exceptions and returns False
            assert client.test_connection() is False
        finally:
            client.close()


class TestServerInfo:
    """Test server info retrieval."""

    def test_get_server_info(self, mock_mod, client_config):
        """Test retrieving server info."""
        client = ClientBridge(client_config)
        try:
            client.test_connection()
            info = client.get_server_info()

            assert "time" in info
            assert "difficulty" in info
            assert "players" in info
            assert info["difficulty"] == "normal"
        finally:
            client.close()


class TestWorldEditPolicy:
    """Test WorldEdit policy enforcement with mock server."""

    def test_policy_force_with_unavailable_worldedit(self, mock_mod_no_worldedit):
        """Test force policy blocks when WorldEdit unavailable."""
        config = VibeCraftConfig(
            client_host="127.0.0.1",
            client_port=18768,
            client_timeout=5,
            worldedit_mode="force",
        )
        client = ClientBridge(config)
        try:
            client.test_connection()

            with pytest.raises(ClientBridgeProtocolError):
                client.execute_command("//set stone")
        finally:
            client.close()

    def test_policy_auto_allows_with_available_worldedit(self, mock_mod, client_config):
        """Test auto policy allows when WorldEdit is available."""
        client = ClientBridge(client_config)
        try:
            client.test_connection()
            result = client.execute_command("//set stone")
            assert result == "Command dispatched"
        finally:
            client.close()


class TestConnectionHandling:
    """Test connection lifecycle and error handling."""

    def test_connection_refused(self):
        """Test handling when no server is running."""
        config = VibeCraftConfig(
            client_host="127.0.0.1",
            client_port=19999,  # No server on this port
            client_timeout=2,
        )
        client = ClientBridge(config)
        try:
            assert client.test_connection() is False
        finally:
            client.close()

    def test_reconnect_after_close(self, mock_mod, client_config):
        """Test client can reconnect after explicit close."""
        client = ClientBridge(client_config)
        try:
            # First connection
            assert client.test_connection() is True
            client.execute_command("say hello")

            # Close and reconnect
            client.close()

            # Should reconnect automatically
            result = client.execute_command("say world")
            assert result == "Command dispatched"
        finally:
            client.close()


class TestProtocolCompliance:
    """Test protocol message format compliance."""

    def test_request_envelope_format(self, mock_mod, client_config):
        """Verify request message envelope matches protocol spec."""
        client = ClientBridge(client_config)
        try:
            client.test_connection()
            client.execute_command("test")

            # Find command message
            cmd_msg = next(m for m in mock_mod.received_messages if m["type"] == "command.execute")

            # Verify envelope fields
            assert "id" in cmd_msg
            assert "type" in cmd_msg
            assert "payload" in cmd_msg
            assert isinstance(cmd_msg["id"], str)
            assert len(cmd_msg["id"]) > 0
        finally:
            client.close()

    def test_message_ids_are_unique(self, mock_mod, client_config):
        """Verify each request has a unique ID."""
        client = ClientBridge(client_config)
        try:
            client.test_connection()

            for i in range(5):
                client.execute_command(f"say {i}")

            ids = [m["id"] for m in mock_mod.received_messages]
            assert len(ids) == len(set(ids)), "Message IDs should be unique"
        finally:
            client.close()
