"""
WorldEdit command wrappers that handle player context and selections automatically.

This module provides intelligent wrappers for WorldEdit commands that need
player position or selection context when run from RCON/console.
"""

from typing import Dict, Any, List
from mcp.types import TextContent

from ..rcon_manager import PLAYER_POS_PATTERN


async def handle_worldedit_generation_smart(
    arguments: Dict[str, Any],
    rcon,
    config,
    logger_instance
) -> List[TextContent]:
    """
    Handle WorldEdit generation commands with automatic selection setup.

    This wrapper:
    1. Gets the player's current position
    2. Automatically sets a selection based on the command and size
    3. Runs the generation command
    """
    command = arguments.get("command", "").strip()

    if not command:
        return [TextContent(type="text", text="❌ Command cannot be empty")]

    # Normalize command (remove leading slashes)
    normalized = command.lstrip("/")

    # Parse the command to understand what we're building
    parts = normalized.split()
    if not parts:
        return [TextContent(type="text", text="❌ Invalid command")]

    cmd_type = parts[0].lower()

    try:
        # CRITICAL: Set world context first
        # WorldEdit from RCON requires world context to be set before selection commands
        # Use execute_command (not send_command which strips leading slash)
        result = rcon.execute_command("/world world")
        logger_instance.debug(f"WorldEdit world context set: {result}")

        # Get player position first
        pos_result = rcon.send_command("data get entity @p Pos")
        logger_instance.info(f"Player position query result: {pos_result}")

        # Parse position from response like: "ereidjustpeed has the following entity data: [1364.5d, -60.0d, 87.5d]"
        pos_match = PLAYER_POS_PATTERN.search(pos_result)

        if not pos_match:
            return [TextContent(type="text", text=f"❌ Could not get player position. Make sure a player is online.\nResponse: {pos_result}")]

        x = int(float(pos_match.group(1)))
        y = int(float(pos_match.group(2)))
        z = int(float(pos_match.group(3)))

        logger_instance.info(f"Player at: ({x}, {y}, {z})")

        # Set selection based on command type
        if cmd_type in ['pyramid', 'hpyramid']:
            # Pyramid needs a square base centered at player position
            if len(parts) < 3:
                return [TextContent(type="text", text="❌ Pyramid requires: pyramid <pattern> <size>")]

            size = int(parts[2])
            # Create a selection for the pyramid base
            x1, z1 = x - size, z - size
            x2, z2 = x + size, z + size
            y1 = y
            y2 = y + size

            # Set selection
            rcon.send_command(f"//pos1 {x1},{y1},{z1}")
            rcon.send_command(f"//pos2 {x2},{y2},{z2}")
            logger_instance.info(f"Set pyramid selection: ({x1},{y1},{z1}) to ({x2},{y2},{z2})")

        elif cmd_type in ['sphere', 'hsphere']:
            # Sphere centered at player
            if len(parts) < 3:
                return [TextContent(type="text", text="❌ Sphere requires: sphere <pattern> <radius>")]

            radius = int(parts[2])
            # Create a cubic selection around player
            x1, y1, z1 = x - radius, y - radius, z - radius
            x2, y2, z2 = x + radius, y + radius, z + radius

            rcon.send_command(f"//pos1 {x1},{y1},{z1}")
            rcon.send_command(f"//pos2 {x2},{y2},{z2}")
            logger_instance.info(f"Set sphere selection: ({x1},{y1},{z1}) to ({x2},{y2},{z2})")

        elif cmd_type in ['cyl', 'hcyl', 'cylinder', 'hcylinder']:
            # Cylinder at player position
            if len(parts) < 3:
                return [TextContent(type="text", text="❌ Cylinder requires: cyl <pattern> <radius> [height]")]

            radius = int(parts[2])
            height = int(parts[3]) if len(parts) > 3 else 1

            # Create a selection for the cylinder
            x1, z1 = x - radius, z - radius
            x2, z2 = x + radius, z + radius
            y1 = y
            y2 = y + height - 1

            rcon.send_command(f"//pos1 {x1},{y1},{z1}")
            rcon.send_command(f"//pos2 {x2},{y2},{z2}")
            logger_instance.info(f"Set cylinder selection: ({x1},{y1},{z1}) to ({x2},{y2},{z2})")

        # Now run the actual generation command
        full_command = "//" + normalized
        result = rcon.send_command(full_command)

        logger_instance.info(f"Generation command result: {result}")

        return [TextContent(
            type="text",
            text=f"✅ Command executed: {full_command}\n\nResponse: {result}"
        )]

    except ValueError as e:
        logger_instance.error(f"Error parsing command parameters: {str(e)}")
        return [TextContent(type="text", text=f"❌ Error parsing command: {str(e)}\nCommand: {command}")]
    except Exception as e:
        logger_instance.error(f"Error executing generation command: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]
