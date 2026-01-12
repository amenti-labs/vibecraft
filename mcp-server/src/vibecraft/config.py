"""Configuration management for VibeCraft MCP server"""

from typing import Optional, Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import RCONConstants, ClientBridgeConstants


class VibeCraftConfig(BaseSettings):
    """VibeCraft MCP Server Configuration"""

    # RCON Connection Settings (deprecated)
    rcon_host: str = Field(default=RCONConstants.DEFAULT_HOST, description="Deprecated RCON host")
    rcon_port: int = Field(default=RCONConstants.DEFAULT_PORT, description="Deprecated RCON port")
    rcon_password: str = Field(default="minecraft", description="Deprecated RCON password")
    rcon_timeout: int = Field(
        default=RCONConstants.DEFAULT_TIMEOUT, description="Deprecated RCON timeout in seconds"
    )

    # Client Bridge Settings
    client_host: str = Field(
        default=ClientBridgeConstants.DEFAULT_HOST,
        description="Local Fabric client bridge host",
    )
    client_port: int = Field(
        default=ClientBridgeConstants.DEFAULT_PORT,
        description="Local Fabric client bridge port",
    )
    client_path: str = Field(
        default=ClientBridgeConstants.DEFAULT_PATH,
        description="WebSocket path for the client bridge",
    )
    client_token: str = Field(default="", description="Client bridge auth token")
    client_timeout: int = Field(
        default=ClientBridgeConstants.DEFAULT_TIMEOUT,
        description="Client bridge request timeout in seconds",
    )
    client_use_ssl: bool = Field(default=False, description="Use TLS for client bridge")
    client_max_idle: float = Field(
        default=ClientBridgeConstants.MAX_CONNECTION_IDLE,
        description="Max idle time before reconnecting to client bridge",
    )

    # WorldEdit Capability Policy
    worldedit_mode: Literal["auto", "force", "off"] = Field(
        default="auto",
        description="WorldEdit availability mode: auto, force (require), or off",
    )
    worldedit_fallback: Literal["warn", "disable", "auto"] = Field(
        default="warn",
        description="Behavior when WorldEdit is unavailable in auto mode",
    )

    # Safety Settings
    enable_safety_checks: bool = Field(default=True, description="Enable command safety validation")
    allow_dangerous_commands: bool = Field(
        default=True,
        description="Allow potentially dangerous commands (//delchunks, //regen, etc.)",
    )
    max_command_length: int = Field(
        default=1000, description="Maximum command length in characters"
    )

    # WorldEdit Build Area Constraints (optional)
    build_min_x: Optional[int] = Field(default=None, description="Minimum X coordinate")
    build_max_x: Optional[int] = Field(default=None, description="Maximum X coordinate")
    build_min_y: Optional[int] = Field(default=None, description="Minimum Y coordinate")
    build_max_y: Optional[int] = Field(default=None, description="Maximum Y coordinate")
    build_min_z: Optional[int] = Field(default=None, description="Minimum Z coordinate")
    build_max_z: Optional[int] = Field(default=None, description="Maximum Z coordinate")

    # Feature Flags
    enable_version_detection: bool = Field(
        default=True, description="Detect WorldEdit version on startup"
    )
    enable_command_logging: bool = Field(default=True, description="Log all commands to console")

    model_config = SettingsConfigDict(
        env_prefix="VIBECRAFT_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


def load_config() -> VibeCraftConfig:
    """Load configuration from environment variables and .env file"""
    return VibeCraftConfig()
