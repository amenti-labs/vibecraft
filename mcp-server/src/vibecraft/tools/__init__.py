"""
VibeCraft MCP Tool Handlers

This package contains modular tool handlers extracted from server.py.
Each module handles a specific category of tools.

Tool Handler Interface:
    Each handler function should have signature:
        async def handle_tool_name(
            arguments: Dict[str, Any],
            rcon: RCONManager,
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
from . import workflow_tools
from . import helper_utils
from . import core_tools
from . import worldedit_wrappers
from . import build_tools

# Register spatial tools
TOOL_REGISTRY["spatial_awareness_scan"] = spatial.handle_spatial_awareness_scan

# Register validation tools
TOOL_REGISTRY["validate_pattern"] = validation.handle_validate_pattern
TOOL_REGISTRY["validate_mask"] = validation.handle_validate_mask
TOOL_REGISTRY["check_symmetry"] = validation.handle_check_symmetry
TOOL_REGISTRY["analyze_lighting"] = validation.handle_analyze_lighting
TOOL_REGISTRY["validate_structure"] = validation.handle_validate_structure

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
TOOL_REGISTRY["calculate_window_spacing"] = geometry_tools.handle_calculate_window_spacing

# Register advanced WorldEdit tools
TOOL_REGISTRY["worldedit_deform"] = worldedit_advanced.handle_worldedit_deform
TOOL_REGISTRY["worldedit_vegetation"] = worldedit_advanced.handle_worldedit_vegetation
TOOL_REGISTRY["worldedit_terrain_advanced"] = worldedit_advanced.handle_worldedit_terrain_advanced
TOOL_REGISTRY["worldedit_analysis"] = worldedit_advanced.handle_worldedit_analysis

# Register workflow tools
TOOL_REGISTRY["workflow_status"] = workflow_tools.handle_workflow_status
TOOL_REGISTRY["workflow_advance"] = workflow_tools.handle_workflow_advance
TOOL_REGISTRY["workflow_reset"] = workflow_tools.handle_workflow_reset

# Register helper utilities
TOOL_REGISTRY["calculate_region_size"] = helper_utils.handle_calculate_region_size
TOOL_REGISTRY["search_minecraft_item"] = helper_utils.handle_search_minecraft_item
TOOL_REGISTRY["get_player_position"] = helper_utils.handle_get_player_position
TOOL_REGISTRY["get_surface_level"] = helper_utils.handle_get_surface_level

# Register core tools
TOOL_REGISTRY["rcon_command"] = core_tools.handle_rcon_command
TOOL_REGISTRY["get_server_info"] = core_tools.handle_get_server_info
TOOL_REGISTRY["building_template"] = core_tools.handle_building_template

# Register build tool
TOOL_REGISTRY["build"] = build_tools.handle_build

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
