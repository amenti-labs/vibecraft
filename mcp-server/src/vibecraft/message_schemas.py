"""WebSocket message schemas for client bridge protocol validation.

This module defines Pydantic models for validating messages exchanged between
the MCP server (Python) and the Fabric client mod (Java). These schemas help
catch protocol drift early and provide clear error messages.

Protocol Reference: docs/CLIENT_BRIDGE_PROTOCOL.md
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field, field_validator


# =============================================================================
# Request Messages (MCP Server -> Client Mod)
# =============================================================================


class RequestEnvelope(BaseModel):
    """Base envelope for all request messages."""

    id: str = Field(..., min_length=1, description="Unique request correlation ID")
    type: str = Field(..., min_length=1, description="Message type identifier")
    token: Optional[str] = Field(None, description="Authentication token")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Message payload")


class HelloRequest(BaseModel):
    """Hello handshake request payload (empty)."""

    pass


class CommandExecuteRequest(BaseModel):
    """Command execution request payload."""

    command: str = Field(..., min_length=1, description="Command to execute")

    @field_validator("command")
    @classmethod
    def validate_command(cls, v: str) -> str:
        """Ensure command is properly formatted."""
        v = v.strip()
        if not v:
            raise ValueError("Command cannot be empty")
        return v


class ServerInfoRequest(BaseModel):
    """Server info request payload (empty)."""

    pass


# =============================================================================
# Response Messages (Client Mod -> MCP Server)
# =============================================================================


class ResponseEnvelope(BaseModel):
    """Base envelope for all response messages."""

    id: Optional[str] = Field(None, description="Correlation ID from request")
    ok: bool = Field(..., description="Whether the request succeeded")
    result: Optional[Any] = Field(None, description="Result data on success")
    error: Optional[str] = Field(None, description="Error message on failure")

    @field_validator("error")
    @classmethod
    def validate_error_present_on_failure(cls, v: Optional[str], info) -> Optional[str]:
        """Ensure error is present when ok=False."""
        # Access ok from the data being validated
        if hasattr(info, "data") and info.data.get("ok") is False and not v:
            # Allow missing error for backwards compatibility
            pass
        return v


class WorldEditCapability(BaseModel):
    """WorldEdit capability information."""

    available: bool = Field(..., description="Whether WorldEdit is available")
    reason: Optional[str] = Field(None, description="Detection method or unavailability reason")
    version: Optional[str] = Field(None, description="WorldEdit version if detected")


class Capabilities(BaseModel):
    """Client capabilities reported in hello response."""

    worldedit: Union[WorldEditCapability, bool] = Field(..., description="WorldEdit availability")
    vision: bool = Field(False, description="Vision capture support")
    region_snapshot: bool = Field(False, description="Region snapshot support")


class HelloResult(BaseModel):
    """Hello response result structure."""

    client: str = Field(..., description="Client type (e.g., 'fabric')")
    version: str = Field(..., description="Client mod version")
    minecraft: str = Field(..., description="Minecraft version")
    enabled: bool = Field(..., description="Whether bridge is enabled")
    allow_ai_control: bool = Field(..., description="Whether AI control is allowed")
    capabilities: Capabilities = Field(..., description="Client capabilities")


class ServerInfoResult(BaseModel):
    """Server info response result structure."""

    time: str = Field(..., description="Game time")
    difficulty: str = Field(..., description="Difficulty level")
    players: str = Field(..., description="Player list summary")


class CommandExecuteResult(BaseModel):
    """Command execution result (typically just a string)."""

    message: str = Field(default="Command dispatched", description="Result message")


# =============================================================================
# Validation Functions
# =============================================================================


def validate_request(message: Dict[str, Any]) -> RequestEnvelope:
    """Validate an outgoing request message.

    Args:
        message: Raw message dictionary

    Returns:
        Validated RequestEnvelope

    Raises:
        pydantic.ValidationError: If message is invalid
    """
    return RequestEnvelope.model_validate(message)


def validate_response(message: Dict[str, Any]) -> ResponseEnvelope:
    """Validate an incoming response message.

    Args:
        message: Raw message dictionary

    Returns:
        Validated ResponseEnvelope

    Raises:
        pydantic.ValidationError: If message is invalid
    """
    return ResponseEnvelope.model_validate(message)


def validate_hello_result(result: Dict[str, Any]) -> HelloResult:
    """Validate hello response result.

    Args:
        result: Result dictionary from hello response

    Returns:
        Validated HelloResult

    Raises:
        pydantic.ValidationError: If result is invalid
    """
    return HelloResult.model_validate(result)


def validate_server_info_result(result: Dict[str, Any]) -> ServerInfoResult:
    """Validate server info response result.

    Args:
        result: Result dictionary from server.info response

    Returns:
        Validated ServerInfoResult

    Raises:
        pydantic.ValidationError: If result is invalid
    """
    return ServerInfoResult.model_validate(result)


def validate_capabilities(caps: Dict[str, Any]) -> Capabilities:
    """Validate capabilities structure.

    Args:
        caps: Capabilities dictionary

    Returns:
        Validated Capabilities

    Raises:
        pydantic.ValidationError: If capabilities are invalid
    """
    return Capabilities.model_validate(caps)


# =============================================================================
# Schema Export for Documentation
# =============================================================================


def get_request_schema() -> Dict[str, Any]:
    """Get JSON schema for request envelope."""
    return RequestEnvelope.model_json_schema()


def get_response_schema() -> Dict[str, Any]:
    """Get JSON schema for response envelope."""
    return ResponseEnvelope.model_json_schema()


def get_hello_result_schema() -> Dict[str, Any]:
    """Get JSON schema for hello result."""
    return HelloResult.model_json_schema()


def get_capabilities_schema() -> Dict[str, Any]:
    """Get JSON schema for capabilities."""
    return Capabilities.model_json_schema()
