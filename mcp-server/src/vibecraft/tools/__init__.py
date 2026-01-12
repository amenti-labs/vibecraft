"""
VibeCraft MCP Tool Handlers

This package contains modular tool handlers extracted from server.py.
Each module handles a specific category of tools.

Tool Handler Interface:
    Each handler function should have signature:
        async def handle_tool_name(
            arguments: Dict[str, Any],
            rcon: Command executor,
            config: VibeCraftConfig,
            logger: logging.Logger
        ) -> List[TextContent]

Tool Registry:
    TOOL_REGISTRY maps tool names to their handler functions.
    Import this in server.py to dispatch tool calls.
"""

from typing import Dict, Callable

# Tool registry - will be populated by importing modules
TOOL_REGISTRY: Dict[str, Callable] = {}


def register_tool(name: str):
    """
    Decorator to register a tool handler.

    Usage:
        @register_tool("worldedit_selection")
        async def handle_worldedit_selection(arguments, rcon, config, logger):
            ...
    """

    def decorator(func: Callable):
        TOOL_REGISTRY[name] = func
        return func

    return decorator


# Import tool modules
from . import spatial
from . import validation
from . import furniture_tools
from . import patterns
from . import terrain_tools
from . import geometry_tools
from . import worldedit_advanced
from . import helper_utils
from . import core_tools
from . import worldedit_wrappers as worldedit_wrappers
from . import build_tools
from . import vision_tools
from . import schematic_tools

# Register spatial tools
TOOL_REGISTRY["spatial_awareness_scan"] = spatial.handle_spatial_awareness_scan

# Register validation tools
TOOL_REGISTRY["validate_mask"] = validation.handle_validate_mask

# Register furniture tools
TOOL_REGISTRY["furniture_lookup"] = furniture_tools.handle_furniture_lookup
TOOL_REGISTRY["place_furniture"] = furniture_tools.handle_place_furniture

# Register pattern tools
TOOL_REGISTRY["building_pattern_lookup"] = patterns.handle_building_pattern_lookup
TOOL_REGISTRY["place_building_pattern"] = patterns.handle_place_building_pattern
TOOL_REGISTRY["terrain_pattern_lookup"] = patterns.handle_terrain_pattern_lookup

# Register terrain tools
TOOL_REGISTRY["generate_terrain"] = terrain_tools.handle_generate_terrain
TOOL_REGISTRY["texture_terrain"] = terrain_tools.handle_texture_terrain
TOOL_REGISTRY["smooth_terrain"] = terrain_tools.handle_smooth_terrain

# Register geometry tools
TOOL_REGISTRY["calculate_shape"] = geometry_tools.handle_calculate_shape

# Register advanced WorldEdit tools
TOOL_REGISTRY["worldedit_deform"] = worldedit_advanced.handle_worldedit_deform
TOOL_REGISTRY["worldedit_vegetation"] = worldedit_advanced.handle_worldedit_vegetation
TOOL_REGISTRY["worldedit_terrain_advanced"] = worldedit_advanced.handle_worldedit_terrain_advanced
TOOL_REGISTRY["worldedit_analysis"] = worldedit_advanced.handle_worldedit_analysis

# Register helper utilities
TOOL_REGISTRY["search_minecraft_item"] = helper_utils.handle_search_minecraft_item
TOOL_REGISTRY["get_player_position"] = helper_utils.handle_get_player_position
TOOL_REGISTRY["get_surface_level"] = helper_utils.handle_get_surface_level

# Register core tools
TOOL_REGISTRY["get_server_info"] = core_tools.handle_get_server_info
TOOL_REGISTRY["building_template"] = core_tools.handle_building_template

# Register build tool
TOOL_REGISTRY["build"] = build_tools.handle_build

# Register vision/client tools
TOOL_REGISTRY["capture_screenshot"] = vision_tools.handle_capture_screenshot
TOOL_REGISTRY["get_heightmap"] = vision_tools.handle_get_heightmap
TOOL_REGISTRY["get_player_context"] = vision_tools.handle_get_player_context
TOOL_REGISTRY["get_nearby_entities"] = vision_tools.handle_get_nearby_entities
TOOL_REGISTRY["scan_region"] = vision_tools.handle_scan_region
TOOL_REGISTRY["analyze_palette"] = vision_tools.handle_analyze_palette
TOOL_REGISTRY["analyze_palette_region"] = vision_tools.handle_analyze_palette_region

# Register schematic building tool
TOOL_REGISTRY["build_schematic"] = schematic_tools.handle_build_schematic

# Register generic WorldEdit tools (20 tools via wrapper)
# Each WorldEdit tool uses the generic handler with its tool_name
for tool_name in core_tools.WORLD_EDIT_TOOL_PREFIXES.keys():
    # Create a closure to capture the tool_name
    def make_worldedit_handler(name):
        async def handler(arguments, rcon, config, logger_instance):
            return await core_tools.handle_worldedit_generic(
                arguments, rcon, config, logger_instance, name
            )

        return handler

    TOOL_REGISTRY[tool_name] = make_worldedit_handler(tool_name)
