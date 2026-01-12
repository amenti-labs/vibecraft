"""
Centralized constants for VibeCraft MCP Server.

This module contains all magic numbers, configuration defaults, and
constant values used throughout the codebase. Having them in one place
makes it easy to:
- Understand the system's limits and defaults
- Adjust values for different environments
- Maintain consistency across modules
"""

from typing import Set, Dict


# =============================================================================
# RCON Connection Constants
# =============================================================================


class RCONConstants:
    """Constants for RCON connection management."""

    # Connection settings
    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = 25575
    DEFAULT_TIMEOUT = 10  # seconds
    MAX_CONNECTION_IDLE = 300.0  # 5 minutes before reconnecting

    # Circuit breaker settings
    CIRCUIT_FAILURE_THRESHOLD = 5  # failures before opening
    CIRCUIT_RECOVERY_TIMEOUT = 30.0  # seconds before attempting recovery
    CIRCUIT_HALF_OPEN_MAX_CALLS = 3  # test calls in half-open state

    # Retry settings
    MAX_RETRIES = 2


# =============================================================================
# Client Bridge Constants
# =============================================================================


class ClientBridgeConstants:
    """Constants for the client bridge connection."""

    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = 8766
    DEFAULT_PATH = "/vibecraft"
    DEFAULT_TIMEOUT = 10
    MAX_CONNECTION_IDLE = 300.0


# =============================================================================
# WorldEdit Constants
# =============================================================================


class WorldEditConstants:
    """Constants for WorldEdit operations."""

    # Command prefixes
    COMMAND_PREFIX = "//"  # Double slash for tool handlers

    # Region limits
    MAX_REGION_SIZE = 100000  # Maximum blocks in a region
    MAX_SELECTION_DIMENSION = 500  # Maximum dimension (X, Y, or Z)

    # Build limits (Minecraft world boundaries)
    MIN_Y = -64  # 1.18+ minimum Y
    MAX_Y = 319  # 1.18+ maximum Y
    SEA_LEVEL = 64

    # WorldEdit commands that require world context
    WORLD_CONTEXT_COMMANDS = {
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
    }

    # Broad set of WorldEdit command roots for client policy checks.
    WORLD_EDIT_COMMANDS = WORLD_CONTEXT_COMMANDS.union(
        {
            "hpos1",
            "hpos2",
            "size",
            "count",
            "distr",
            "overlay",
            "center",
            "line",
            "curve",
            "move",
            "stack",
            "copy",
            "cut",
            "paste",
            "rotate",
            "flip",
            "wand",
            "schem",
            "schematic",
            "snapshot",
            "snap",
            "biomelist",
            "biomeinfo",
            "setbiome",
            "chunkinfo",
            "listchunks",
            "delchunks",
            "undo",
            "redo",
            "clearhistory",
            "br",
            "brush",
            "tool",
            "forestgen",
            "flora",
            "drain",
            "fixwater",
            "fixlava",
            "naturalize",
            "pyramid",
            "hpyramid",
            "sphere",
            "hsphere",
            "cyl",
            "hcyl",
            "generate",
            "deform",
        }
    )


# =============================================================================
# Build Validation Constants
# =============================================================================


class BuildConstants:
    """Constants for building and validation."""

    # Lighting
    LIGHT_SOURCE_RADIUS = 10  # blocks for light analysis
    MIN_LIGHT_LEVEL = 8  # minimum to prevent mob spawns
    MOB_SPAWN_LIGHT_THRESHOLD = 7

    # Structure validation
    MAX_FLOATING_BLOCKS = 10  # before warning
    SYMMETRY_TOLERANCE = 0.05  # 5% tolerance for symmetry check

    # Room sizes (Minecraft scale reference)
    MIN_ROOM_WIDTH = 4
    MIN_ROOM_DEPTH = 5
    MIN_CEILING_HEIGHT = 3
    COMFORTABLE_CEILING = 4
    GRAND_CEILING = 6

    # Player dimensions
    PLAYER_HEIGHT = 1.8  # blocks
    PLAYER_WIDTH = 0.6  # blocks


# =============================================================================
# Terrain Constants
# =============================================================================


class TerrainConstants:
    """Constants for terrain generation and analysis."""

    # Sampling
    DEFAULT_RESOLUTION = 5  # sample every Nth block
    MAX_SAMPLES = 10000
    MAX_AMPLITUDE = 50

    # Terrain classification (std dev thresholds)
    FLAT_THRESHOLD = 2
    GENTLE_THRESHOLD = 5
    HILLY_THRESHOLD = 10
    MOUNTAINOUS_THRESHOLD = 20

    # Hazard detection
    WATER_WARNING_THRESHOLD = 10  # percentage
    WATER_HIGH_THRESHOLD = 30  # percentage
    VEGETATION_DENSE_THRESHOLD = 20  # percentage
    CAVITY_WARNING_THRESHOLD = 5  # percentage


# =============================================================================
# Code Sandbox Constants
# =============================================================================


class SandboxConstants:
    """Constants for code sandbox execution."""

    # Execution limits
    MAX_COMMANDS = 10000
    MAX_ITERATIONS = 100000
    MAX_CODE_LENGTH = 50000
    MAX_NESTING_DEPTH = 10
    TIMEOUT_SECONDS = 5

    # Per-range limits
    MAX_RANGE_SIZE = 10000

    # Command validation
    MAX_COMMAND_LENGTH = 1000

    # Blocked server commands
    BLOCKED_COMMAND_PATTERNS = {
        "stop",
        "ban",
        "kick",
        "op ",
        "deop",
        "whitelist",
        "save-all",
        "save-off",
        "save-on",
        "reload",
    }


# =============================================================================
# Spatial Analysis Constants
# =============================================================================


class SpatialConstants:
    """Constants for spatial awareness scanning."""

    # Detail levels and their command counts
    DETAIL_LOW_COMMANDS = 50
    DETAIL_MEDIUM_COMMANDS = 100
    DETAIL_HIGH_COMMANDS = 200

    # Timing estimates (seconds)
    DETAIL_LOW_TIME = 3
    DETAIL_MEDIUM_TIME = 5
    DETAIL_HIGH_TIME = 10

    # Scan defaults
    DEFAULT_RADIUS = 5
    MIN_RADIUS = 1
    MAX_RADIUS = 20


# =============================================================================
# Furniture & Patterns Constants
# =============================================================================


class PatternConstants:
    """Constants for furniture and building patterns."""

    # Pattern counts (for reference)
    BUILDING_PATTERNS = 70
    TERRAIN_PATTERNS = 41
    FURNITURE_DESIGNS = 60

    # Minecraft items catalog
    TOTAL_ITEMS = 1375


# =============================================================================
# Minecraft Block Categories
# =============================================================================


class BlockCategories:
    """Block categories for terrain and building analysis."""

    LIQUID_BLOCKS: Set[str] = {"water", "lava", "flowing_water", "flowing_lava"}

    VEGETATION_BLOCKS: Set[str] = {
        "oak_log",
        "birch_log",
        "spruce_log",
        "jungle_log",
        "acacia_log",
        "dark_oak_log",
        "mangrove_log",
        "cherry_log",
        "oak_leaves",
        "birch_leaves",
        "spruce_leaves",
        "jungle_leaves",
        "acacia_leaves",
        "dark_oak_leaves",
        "mangrove_leaves",
        "cherry_leaves",
        "grass",
        "tall_grass",
        "fern",
        "large_fern",
        "dead_bush",
        "vine",
        "lily_pad",
        "sea_grass",
        "tall_seagrass",
        "kelp",
    }

    NATURAL_SURFACE_BLOCKS: Set[str] = {
        "grass_block",
        "dirt",
        "coarse_dirt",
        "podzol",
        "mycelium",
        "sand",
        "red_sand",
        "gravel",
        "stone",
        "deepslate",
        "sandstone",
        "red_sandstone",
        "terracotta",
        "snow",
        "ice",
        "packed_ice",
        "blue_ice",
        "netherrack",
        "soul_sand",
        "soul_soil",
        "end_stone",
        "moss_block",
        "mud",
        "clay",
    }

    AIR_BLOCKS: Set[str] = {"air", "cave_air", "void_air"}

    LIGHT_SOURCES: Set[str] = {
        "torch",
        "wall_torch",
        "soul_torch",
        "soul_wall_torch",
        "lantern",
        "soul_lantern",
        "sea_lantern",
        "glowstone",
        "shroomlight",
        "end_rod",
        "campfire",
        "soul_campfire",
        "redstone_lamp",
        "jack_o_lantern",
        "beacon",
        "conduit",
        "crying_obsidian",
        "respawn_anchor",
        "magma_block",
        "lava",
        "fire",
        "soul_fire",
    }

    HAZARD_BLOCKS: Dict[str, str] = {
        "lava": "Lava flow",
        "magma_block": "Magma blocks",
        "fire": "Fire",
        "sweet_berry_bush": "Berry bushes (damage)",
        "cactus": "Cacti",
        "powder_snow": "Powder snow",
    }


# =============================================================================
# Logging and Debug Constants
# =============================================================================


class LogConstants:
    """Constants for logging configuration."""

    # Log formats
    DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Truncation limits
    MAX_COMMAND_LOG_LENGTH = 50
    MAX_ERROR_MESSAGE_LENGTH = 200


# =============================================================================
# API Response Constants
# =============================================================================


class APIConstants:
    """Constants for API responses and formatting."""

    # Command prefixes for sanitization
    WORLDEDIT_PREFIX = "//"
    VANILLA_PREFIX = "/"

    # Response formatting
    SUCCESS_PREFIX = "✅"
    ERROR_PREFIX = "❌"
    WARNING_PREFIX = "⚠️"
    INFO_PREFIX = "💡"
