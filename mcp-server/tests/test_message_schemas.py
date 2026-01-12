"""Tests for WebSocket message schema validation."""

import pytest
from pydantic import ValidationError

from vibecraft.message_schemas import (
    RequestEnvelope,
    ResponseEnvelope,
    HelloResult,
    Capabilities,
    WorldEditCapability,
    CommandExecuteRequest,
    validate_request,
    validate_response,
    validate_hello_result,
    validate_capabilities,
    get_request_schema,
    get_response_schema,
)


class TestRequestEnvelope:
    """Test request envelope validation."""

    def test_valid_request(self):
        """Valid request passes validation."""
        msg = {
            "id": "abc123",
            "type": "command.execute",
            "payload": {"command": "/say hello"},
        }
        envelope = validate_request(msg)
        assert envelope.id == "abc123"
        assert envelope.type == "command.execute"

    def test_request_with_token(self):
        """Request with token is valid."""
        msg = {
            "id": "abc123",
            "type": "hello",
            "token": "secret-token",
            "payload": {},
        }
        envelope = validate_request(msg)
        assert envelope.token == "secret-token"

    def test_missing_id_fails(self):
        """Request without ID fails validation."""
        msg = {"type": "hello", "payload": {}}
        with pytest.raises(ValidationError):
            validate_request(msg)

    def test_empty_id_fails(self):
        """Request with empty ID fails validation."""
        msg = {"id": "", "type": "hello", "payload": {}}
        with pytest.raises(ValidationError):
            validate_request(msg)

    def test_missing_type_fails(self):
        """Request without type fails validation."""
        msg = {"id": "abc123", "payload": {}}
        with pytest.raises(ValidationError):
            validate_request(msg)


class TestResponseEnvelope:
    """Test response envelope validation."""

    def test_valid_success_response(self):
        """Valid success response passes validation."""
        msg = {"id": "abc123", "ok": True, "result": "Command dispatched"}
        envelope = validate_response(msg)
        assert envelope.ok is True
        assert envelope.result == "Command dispatched"

    def test_valid_error_response(self):
        """Valid error response passes validation."""
        msg = {"id": "abc123", "ok": False, "error": "Permission denied"}
        envelope = validate_response(msg)
        assert envelope.ok is False
        assert envelope.error == "Permission denied"

    def test_missing_ok_fails(self):
        """Response without ok field fails validation."""
        msg = {"id": "abc123", "result": "test"}
        with pytest.raises(ValidationError):
            validate_response(msg)

    def test_response_without_id_is_valid(self):
        """Response can omit ID (for broadcasts)."""
        msg = {"ok": True, "result": "event data"}
        envelope = validate_response(msg)
        assert envelope.id is None


class TestHelloResult:
    """Test hello result validation."""

    def test_valid_hello_result(self):
        """Valid hello result passes validation."""
        result = {
            "client": "fabric",
            "version": "0.1.0",
            "minecraft": "1.21.11",
            "enabled": True,
            "allow_ai_control": True,
            "capabilities": {
                "worldedit": {"available": True, "reason": "command_tree"},
                "vision": False,
                "region_snapshot": False,
            },
        }
        hello = validate_hello_result(result)
        assert hello.client == "fabric"
        assert hello.minecraft == "1.21.11"
        assert hello.capabilities.vision is False

    def test_missing_client_fails(self):
        """Hello result without client fails."""
        result = {
            "version": "0.1.0",
            "minecraft": "1.21.11",
            "enabled": True,
            "allow_ai_control": True,
            "capabilities": {"worldedit": False, "vision": False, "region_snapshot": False},
        }
        with pytest.raises(ValidationError):
            validate_hello_result(result)


class TestCapabilities:
    """Test capabilities validation."""

    def test_worldedit_as_object(self):
        """WorldEdit capability as object is valid."""
        caps = {
            "worldedit": {"available": True, "reason": "command_tree", "version": "7.3.0"},
            "vision": False,
            "region_snapshot": False,
        }
        validated = validate_capabilities(caps)
        assert validated.worldedit.available is True
        assert validated.worldedit.version == "7.3.0"

    def test_worldedit_as_boolean(self):
        """WorldEdit capability as boolean is valid (backwards compat)."""
        caps = {"worldedit": True, "vision": False, "region_snapshot": False}
        validated = validate_capabilities(caps)
        assert validated.worldedit is True

    def test_missing_worldedit_fails(self):
        """Capabilities without worldedit fails."""
        caps = {"vision": False, "region_snapshot": False}
        with pytest.raises(ValidationError):
            validate_capabilities(caps)


class TestCommandExecuteRequest:
    """Test command execute request validation."""

    def test_valid_command(self):
        """Valid command passes validation."""
        request = CommandExecuteRequest(command="/say hello")
        assert request.command == "/say hello"

    def test_empty_command_fails(self):
        """Empty command fails validation."""
        with pytest.raises(ValidationError):
            CommandExecuteRequest(command="")

    def test_whitespace_only_fails(self):
        """Whitespace-only command fails validation."""
        with pytest.raises(ValidationError):
            CommandExecuteRequest(command="   ")


class TestSchemaExport:
    """Test schema export functions."""

    def test_request_schema_export(self):
        """Request schema can be exported as JSON schema."""
        schema = get_request_schema()
        assert "properties" in schema
        assert "id" in schema["properties"]
        assert "type" in schema["properties"]

    def test_response_schema_export(self):
        """Response schema can be exported as JSON schema."""
        schema = get_response_schema()
        assert "properties" in schema
        assert "ok" in schema["properties"]


class TestProtocolCompliance:
    """Test that schemas match the documented protocol."""

    def test_hello_request_payload_is_empty(self):
        """Hello request has empty payload per protocol."""
        msg = {"id": "test", "type": "hello", "payload": {}}
        envelope = validate_request(msg)
        assert envelope.payload == {}

    def test_command_execute_payload_has_command(self):
        """Command execute payload has command field."""
        msg = {
            "id": "test",
            "type": "command.execute",
            "payload": {"command": "/time set day"},
        }
        envelope = validate_request(msg)
        assert envelope.payload["command"] == "/time set day"

    def test_full_protocol_flow(self):
        """Test a complete request/response flow."""
        # Request
        request = {
            "id": "req-001",
            "type": "hello",
            "token": "test-token",
            "payload": {},
        }
        req_envelope = validate_request(request)
        assert req_envelope.id == "req-001"

        # Response
        response = {
            "id": "req-001",
            "ok": True,
            "result": {
                "client": "fabric",
                "version": "0.1.0",
                "minecraft": "1.21.11",
                "enabled": True,
                "allow_ai_control": True,
                "capabilities": {
                    "worldedit": {"available": True, "reason": "command_tree"},
                    "vision": False,
                    "region_snapshot": False,
                },
            },
        }
        res_envelope = validate_response(response)
        assert res_envelope.id == req_envelope.id
        assert res_envelope.ok is True

        # Validate result structure
        hello_result = validate_hello_result(res_envelope.result)
        assert hello_result.client == "fabric"
        assert hello_result.capabilities.worldedit.available is True
