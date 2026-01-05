"""Configuration management for VibeCraft MCP server"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import RCONConstants


class VibeCraftConfig(BaseSettings):
    """VibeCraft MCP Server Configuration"""

    # RCON Connection Settings
    rcon_host: str = Field(default=RCONConstants.DEFAULT_HOST, description="Minecraft server RCON host")
    rcon_port: int = Field(default=RCONConstants.DEFAULT_PORT, description="Minecraft server RCON port")
    rcon_password: str = Field(default="minecraft", description="RCON password")
    rcon_timeout: int = Field(default=RCONConstants.DEFAULT_TIMEOUT, description="RCON command timeout in seconds")

    # Safety Settings
    enable_safety_checks: bool = Field(
        default=True, description="Enable command safety validation"
    )
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
    enable_command_logging: bool = Field(
        default=True, description="Log all commands to console"
    )

    model_config = SettingsConfigDict(
        env_prefix="VIBECRAFT_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


def load_config() -> VibeCraftConfig:
    """Load configuration from environment variables and .env file"""
    return VibeCraftConfig()
