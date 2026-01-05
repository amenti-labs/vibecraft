"""
Advanced WorldEdit tool handlers.

This module contains handlers for advanced WorldEdit operations including
deformations, vegetation, terrain generation, and analysis.
"""

from typing import Dict, Any, List
from mcp.types import TextContent


async def handle_worldedit_deform(
    arguments: Dict[str, Any], rcon, config, logger_instance
) -> List[TextContent]:
    """Handle worldedit_deform tool."""
    expression = arguments.get("expression", "").strip()

    if not expression:
        return [TextContent(type="text", text="❌ Deformation expression cannot be empty")]

    command = f"//deform {expression}"

    # Add safety warning for deformations
    warning = "⚠️ **Deformation Warning**: //deform modifies terrain mathematically. Ensure you have a selection set and understand the expression.\n\n"

    try:
        # Execute RCON command
        result = rcon.send_command(command)
        output = warning + f"**Command:** `{command}`\n\n**Result:**\n{result}"

        logger_instance.info(f"Deform command executed: {command}")
        return [TextContent(type="text", text=output)]
    except Exception as e:
        logger_instance.error(f"Error in deform: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Deform failed: {str(e)}")]


async def handle_worldedit_vegetation(
    arguments: Dict[str, Any], rcon, config, logger_instance
) -> List[TextContent]:
    """Handle worldedit_vegetation tool."""
    cmd = arguments.get("command")

    if not cmd:
        return [
            TextContent(
                type="text", text="❌ Command type must be specified (flora, forest, or tool_tree)"
            )
        ]

    if cmd == "flora":
        density = arguments.get("density", 10)
        if density < 0 or density > 100:
            return [TextContent(type="text", text="❌ Density must be between 0 and 100")]
        command = f"//flora {density}"

    elif cmd == "forest":
        tree_type = arguments.get("type", "oak").lower()
        density = arguments.get("density", 5)

        if density < 0 or density > 100:
            return [TextContent(type="text", text="❌ Density must be between 0 and 100")]

        # Validate tree type
        valid_types = [
            "oak",
            "birch",
            "spruce",
            "jungle",
            "acacia",
            "dark_oak",
            "mangrove",
            "cherry",
            "random",
        ]
        if tree_type not in valid_types:
            return [
                TextContent(
                    type="text", text=f"❌ Invalid tree type. Valid types: {', '.join(valid_types)}"
                )
            ]

        command = f"//forest {tree_type} {density}"

    elif cmd == "tool_tree":
        tree_type = arguments.get("type", "oak").lower()
        size = arguments.get("size", "medium").lower()

        # Validate tree type
        valid_types = [
            "oak",
            "birch",
            "spruce",
            "jungle",
            "acacia",
            "dark_oak",
            "mangrove",
            "cherry",
        ]
        if tree_type not in valid_types:
            return [
                TextContent(
                    type="text", text=f"❌ Invalid tree type. Valid types: {', '.join(valid_types)}"
                )
            ]

        # Validate size
        valid_sizes = ["small", "medium", "large"]
        if size not in valid_sizes:
            return [
                TextContent(
                    type="text", text=f"❌ Invalid size. Valid sizes: {', '.join(valid_sizes)}"
                )
            ]

        # Map size to tree type suffix
        size_suffix = ""
        if size == "small":
            size_suffix = "_small"
        elif size == "large":
            size_suffix = "_large"

        tree_with_size = tree_type + size_suffix if size_suffix else tree_type
        command = f"/tool tree {tree_with_size}"

    else:
        return [TextContent(type="text", text=f"❌ Unknown vegetation command: {cmd}")]

    try:
        # Execute RCON command
        result = rcon.send_command(command)
        output = f"**Command:** `{command}`\n\n**Result:**\n{result}"

        logger_instance.info(f"Vegetation command executed: {command}")
        return [TextContent(type="text", text=output)]
    except Exception as e:
        logger_instance.error(f"Error in vegetation: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Vegetation command failed: {str(e)}")]


async def handle_worldedit_terrain_advanced(
    arguments: Dict[str, Any], rcon, config, logger_instance
) -> List[TextContent]:
    """Handle worldedit_terrain_advanced tool."""
    cmd = arguments.get("command")

    if not cmd:
        return [
            TextContent(
                type="text", text="❌ Command type must be specified (caves, ore, or regen)"
            )
        ]

    warning = ""

    if cmd == "caves":
        size = arguments.get("size", 8)
        freq = arguments.get("freq", 40)
        rarity = arguments.get("rarity", 7)
        minY = arguments.get("minY", 0)
        maxY = arguments.get("maxY", 128)

        # Validate parameters
        if freq < 1 or freq > 100:
            return [TextContent(type="text", text="❌ Frequency must be between 1 and 100")]
        if rarity < 1 or rarity > 100:
            return [TextContent(type="text", text="❌ Rarity must be between 1 and 100")]

        command = f"//caves {size} {freq} {rarity} {minY} {maxY}"

    elif cmd == "ore":
        pattern = arguments.get("pattern", "").strip()
        size = arguments.get("size", 4)
        freq = arguments.get("freq", 10)
        rarity = arguments.get("rarity", 100)
        minY = arguments.get("minY", -64)
        maxY = arguments.get("maxY", 64)

        if not pattern:
            return [TextContent(type="text", text="❌ Pattern (ore type) must be specified")]

        # Validate parameters
        if freq < 1 or freq > 100:
            return [TextContent(type="text", text="❌ Frequency must be between 1 and 100")]
        if rarity < 1 or rarity > 100:
            return [TextContent(type="text", text="❌ Rarity must be between 1 and 100")]

        command = f"//ore {pattern} {size} {freq} {rarity} {minY} {maxY}"

    elif cmd == "regen":
        # Add warning for destructive command
        warning = "⚠️ **Regeneration Warning**: //regen will DESTROY all modifications in the selection and restore original terrain. This cannot be undone (except with //undo).\n\n"
        command = "//regen"

    else:
        return [TextContent(type="text", text=f"❌ Unknown terrain command: {cmd}")]

    try:
        # Execute RCON command
        result = rcon.send_command(command)
        output = warning + f"**Command:** `{command}`\n\n**Result:**\n{result}"

        logger_instance.info(f"Terrain advanced command executed: {command}")
        return [TextContent(type="text", text=output)]
    except Exception as e:
        logger_instance.error(f"Error in terrain advanced: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Terrain advanced command failed: {str(e)}")]


async def handle_worldedit_analysis(
    arguments: Dict[str, Any], rcon, config, logger_instance
) -> List[TextContent]:
    """Handle worldedit_analysis tool."""
    cmd = arguments.get("command")

    if not cmd:
        return [TextContent(type="text", text="❌ Command type must be specified (distr or calc)")]

    if cmd == "distr":
        command = "//distr"

    elif cmd == "calc":
        expression = arguments.get("expression", "").strip()

        if not expression:
            return [TextContent(type="text", text="❌ Expression for calculation must be provided")]

        command = f"//calc {expression}"

    else:
        return [TextContent(type="text", text=f"❌ Unknown analysis command: {cmd}")]

    try:
        # Execute RCON command
        result = rcon.send_command(command)
        output = f"**Command:** `{command}`\n\n**Result:**\n{result}"

        logger_instance.info(f"Analysis command executed: {command}")
        return [TextContent(type="text", text=output)]
    except Exception as e:
        logger_instance.error(f"Error in analysis: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Analysis command failed: {str(e)}")]
