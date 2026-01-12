"""
Centralized custom exceptions for VibeCraft MCP Server.

This module defines all custom exceptions used throughout the codebase,
providing a consistent error handling interface.
"""


class VibeCraftError(Exception):
    """Base exception for all VibeCraft errors."""

    pass


# =============================================================================
# RCON Connection Errors
# =============================================================================


class RCONError(VibeCraftError):
    """Base exception for RCON-related errors."""

    pass


class RCONConnectionError(RCONError):
    """Raised when RCON connection fails or times out."""

    pass


class RCONCircuitOpenError(RCONError):
    """Raised when circuit breaker is open and rejecting requests."""

    pass


class RCONTimeoutError(RCONError):
    """Raised when RCON command times out."""

    pass


# =============================================================================
# Code Sandbox Errors
# =============================================================================


class CodeSandboxError(VibeCraftError):
    """Base exception for code sandbox errors."""

    pass


class SandboxSecurityError(CodeSandboxError):
    """Raised when code violates sandbox security constraints."""

    pass


class SandboxTimeoutError(CodeSandboxError):
    """Raised when sandboxed code execution times out."""

    pass


class SandboxResourceError(CodeSandboxError):
    """Raised when sandboxed code exceeds resource limits."""

    pass


# =============================================================================
# Pattern and Building Errors
# =============================================================================


class PatternError(VibeCraftError):
    """Base exception for pattern-related errors."""

    pass


class PatternValidationError(PatternError):
    """Raised when a pattern definition is invalid."""

    pass


class PatternNotFoundError(PatternError):
    """Raised when a requested pattern does not exist."""

    pass


# =============================================================================
# WorldEdit Errors
# =============================================================================


class WorldEditError(VibeCraftError):
    """Base exception for WorldEdit-related errors."""

    pass


class WorldEditSelectionError(WorldEditError):
    """Raised when WorldEdit selection is invalid or missing."""

    pass


class WorldEditRegionError(WorldEditError):
    """Raised when region size exceeds limits."""

    pass


# =============================================================================
# Validation Errors
# =============================================================================


class ValidationError(VibeCraftError):
    """Base exception for validation errors."""

    pass


class CommandValidationError(ValidationError):
    """Raised when a command fails validation."""

    pass


class CoordinateValidationError(ValidationError):
    """Raised when coordinates are out of bounds."""

    pass


# =============================================================================
# Configuration Errors
# =============================================================================


class ConfigurationError(VibeCraftError):
    """Raised when configuration is invalid or missing."""

    pass


# =============================================================================
# Client Bridge Errors
# =============================================================================


class ClientBridgeError(VibeCraftError):
    """Base exception for client bridge errors."""

    pass


class ClientBridgeConnectionError(ClientBridgeError):
    """Raised when the client bridge connection fails."""

    pass


class ClientBridgeTimeoutError(ClientBridgeError):
    """Raised when the client bridge times out."""

    pass


class ClientBridgeProtocolError(ClientBridgeError):
    """Raised when client bridge responses are invalid or unexpected."""

    pass
