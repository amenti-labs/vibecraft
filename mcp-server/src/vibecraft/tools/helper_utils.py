"""
Helper utility tool handlers.

This module contains handlers for utility operations including
item search, player positioning, surface detection, and region calculations.
"""

from typing import Dict, Any, List
from mcp.types import TextContent
import math

from ..rcon_manager import PLAYER_POS_PATTERN, PLAYER_ROT_PATTERN, BLOCK_ID_PATTERN


async def handle_calculate_region_size(
    arguments: Dict[str, Any], rcon, config, logger_instance
) -> List[TextContent]:
    """Handle calculate_region_size tool."""
    x1, y1, z1 = arguments["x1"], arguments["y1"], arguments["z1"]
    x2, y2, z2 = arguments["x2"], arguments["y2"], arguments["z2"]

    # Calculate dimensions
    width = abs(x2 - x1) + 1
    height = abs(y2 - y1) + 1
    depth = abs(z2 - z1) + 1

    # Calculate block count
    block_count = width * height * depth

    # Estimate operation time (very rough)
    # Assume ~100k blocks/second for simple operations
    estimated_seconds = block_count / 100000
    if estimated_seconds < 0.1:
        time_estimate = "< 0.1 seconds"
    elif estimated_seconds < 60:
        time_estimate = f"~{estimated_seconds:.1f} seconds"
    else:
        time_estimate = f"~{estimated_seconds/60:.1f} minutes"

    result = [
        "📐 Region Size Calculation:",
        "",
        f"Corner 1: ({x1}, {y1}, {z1})",
        f"Corner 2: ({x2}, {y2}, {z2})",
        "",
        "Dimensions:",
        f"  Width (X): {width} blocks",
        f"  Height (Y): {height} blocks",
        f"  Depth (Z): {depth} blocks",
        "",
        f"Total Blocks: {block_count:,}",
        f"Estimated Time: {time_estimate}",
        "",
    ]

    # Warnings for large operations
    if block_count > 1000000:
        result.append("⚠️ WARNING: Very large region! Operation may take significant time.")
        result.append("   Consider breaking into smaller operations.")
    elif block_count > 100000:
        result.append("⚠️ Note: Large region. Operation may take some time.")

    logger_instance.info(f"Region size calculated: {block_count:,} blocks")
    return [TextContent(type="text", text="\n".join(result))]


async def handle_search_minecraft_item(
    arguments: Dict[str, Any], rcon, config, logger_instance
) -> List[TextContent]:
    """Handle search_minecraft_item tool."""
    from ..minecraft_items_loader import minecraft_items

    query = arguments.get("query", "").strip().lower()
    limit = arguments.get("limit", 20)

    if not query:
        return [TextContent(type="text", text="❌ Search query cannot be empty")]

    # Limit bounds checking
    if limit < 1:
        limit = 1
    elif limit > 50:
        limit = 50

    # Search through minecraft items
    matches = []
    for item in minecraft_items:
        # Case-insensitive partial match on name or displayName
        if query in item.get("name", "").lower() or query in item.get("displayName", "").lower():
            matches.append(item)

        if len(matches) >= limit:
            break

    if not matches:
        return [
            TextContent(
                type="text",
                text=f"❌ No items found matching '{query}'\n\nTry a different search term or check spelling.",
            )
        ]

    # Format results
    result = [
        f"🔍 Found {len(matches)} item(s) matching '{query}':",
        "",
    ]

    for item in matches:
        result.append(f"• **{item['displayName']}** (`{item['name']}`)")
        result.append(f"  - ID: {item['id']}")

        # Add usage hints for common blocks
        name = item["name"]
        if "concrete" in name:
            result.append("  - Use: Modern builds, clean aesthetic")
        elif "stone_bricks" in name or "stone_brick" in name:
            result.append("  - Use: Medieval, refined builds")
        elif "cobblestone" in name:
            result.append("  - Use: Medieval, rustic, foundations")
        elif "planks" in name or "plank" in name:
            result.append("  - Use: Warm interiors, traditional builds")
        elif "glass" in name:
            result.append("  - Use: Windows, modern walls, transparency")
        elif "terracotta" in name:
            result.append("  - Use: Colorful accents, southwestern style")
        elif "wool" in name:
            result.append("  - Use: Colorful builds, soft textures")

        result.append("")

    if len(matches) >= limit:
        result.append(f"💡 Showing first {limit} results. Use limit parameter for more.")

    logger_instance.info(f"Search completed: {len(matches)} items found for '{query}'")
    return [TextContent(type="text", text="\n".join(result))]


async def handle_get_player_position(
    arguments: Dict[str, Any], rcon, config, logger_instance
) -> List[TextContent]:
    """Handle get_player_position tool."""
    player_name = arguments.get("player_name", "").strip()

    # If no player specified, get first online player
    if not player_name:
        info = rcon.get_server_info()
        players = info.get("players", "")
        if not players or players == "0":
            return [
                TextContent(
                    type="text",
                    text="❌ No players online. Please specify a player name or have someone join the server.",
                )
            ]

        # Try to extract first player name from the players string
        if ":" in players:
            player_name = players.split(":", 1)[1].strip().split(",")[0].strip()
        else:
            list_result = rcon.send_command("list")
            if ":" in list_result:
                player_list = list_result.split(":", 1)[1].strip()
                if player_list:
                    player_name = player_list.split(",")[0].strip()

        if not player_name:
            return [
                TextContent(
                    type="text",
                    text="❌ Could not determine player name. Please specify player_name parameter.",
                )
            ]

    try:
        # Get player position
        pos_result = rcon.send_command(f"data get entity {player_name} Pos")
        coord_match = PLAYER_POS_PATTERN.search(pos_result)

        if not coord_match:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Player '{player_name}' not found or error getting position",
                )
            ]

        x = float(coord_match.group(1))
        y = float(coord_match.group(2))
        z = float(coord_match.group(3))

        # Get player rotation (yaw, pitch)
        rot_result = rcon.send_command(f"data get entity {player_name} Rotation")
        rot_match = PLAYER_ROT_PATTERN.search(rot_result)

        yaw = 0.0
        pitch = 0.0
        direction = "unknown"

        if rot_match:
            yaw = float(rot_match.group(1))
            pitch = float(rot_match.group(2))

            # Convert yaw to cardinal direction
            # Yaw: -180 to 180, where 0=south, 90=west, -90=east, 180/-180=north
            yaw_normalized = yaw % 360
            if 315 <= yaw_normalized or yaw_normalized < 45:
                direction = "South (+Z)"
            elif 45 <= yaw_normalized < 135:
                direction = "West (-X)"
            elif 135 <= yaw_normalized < 225:
                direction = "North (-Z)"
            else:
                direction = "East (+X)"

        # Attempt to find target block using raycast
        # Execute at player, position relative to look direction
        target_info = "Not detected (no block in range)"

        # Calculate look vector from pitch and yaw
        # Raycast up to 5 blocks
        yaw_rad = math.radians(yaw)
        pitch_rad = math.radians(pitch)

        # Try execute raycast - position 1-5 blocks in look direction
        for distance in [1, 2, 3, 4, 5]:
            # Calculate offset using look direction
            dx = -math.sin(yaw_rad) * math.cos(pitch_rad) * distance
            dz = math.cos(yaw_rad) * math.cos(pitch_rad) * distance
            dy = -math.sin(pitch_rad) * distance

            target_x = int(x + dx)
            target_y = int(y + 1.62 + dy)  # Eye level
            target_z = int(z + dz)

            # Check if there's a non-air block at this position
            block_check = rcon.send_command(
                f"execute positioned {target_x} {target_y} {target_z} run data get block ~ ~ ~ id"
            )

            if "air" not in block_check.lower() and "has the following" in block_check:
                # Found a non-air block
                block_match = BLOCK_ID_PATTERN.search(block_check)
                if block_match:
                    block_type = block_match.group(1)
                    target_info = (
                        f"{block_type} at {target_x},{target_y},{target_z} ({distance} blocks away)"
                    )
                    break

        # Use player Y position as ground reference (simpler and more reliable)
        # Player is always standing on solid ground, so their feet Y IS the ground level
        player_y = int(y)

        # Check block directly below player's feet to identify surface type
        surface_block = "unknown"
        block_check = rcon.send_command(
            f"execute positioned {int(x)} {player_y - 1} {int(z)} run data get block ~ ~ ~ id"
        )
        if "has the following" in block_check:
            block_match = BLOCK_ID_PATTERN.search(block_check)
            if block_match:
                surface_block = block_match.group(1)

        # Build surface info section
        surface_info = f"""**Ground Level (Player-based):**
Player feet at: Y={player_y}
Block below feet: {surface_block}
Ground level: Y={player_y - 1}"""

        # Build suggestions section - simplified, using player Y as reference
        suggestions = f"""**Building Coordinates:**
- On ground (RECOMMENDED): {int(x)},{player_y},{int(z)} - builds at player's feet level
- Foundation layer: {int(x)},{player_y - 1},{int(z)} - replaces block below player
- Elevated (1 block up): {int(x)},{player_y + 1},{int(z)} - builds above player
- Where player is looking: Use target block if available"""

        logger_instance.info(
            f"Player position retrieved: {player_name} at ({x:.2f}, {y:.2f}, {z:.2f})"
        )
        return [
            TextContent(
                type="text",
                text=f"""📍 Comprehensive Player Context: {player_name}

**Position:**
X: {x:.2f} → {int(x)}
Y: {y:.2f} → {int(y)}
Z: {z:.2f} → {int(z)}

**Rotation:**
Yaw: {yaw:.1f}°
Pitch: {pitch:.1f}°
Facing: {direction}

**Looking At:**
{target_info}

{surface_info}

{suggestions}

**Orientation Note:**
Player facing {direction} - structure front should face this direction for alignment
""",
            )
        ]

    except Exception as e:
        logger_instance.error(f"Error in get_player_position: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Error getting player position: {str(e)}")]


async def handle_get_surface_level(
    arguments: Dict[str, Any], rcon, config, logger_instance
) -> List[TextContent]:
    """Handle get_surface_level tool."""
    x = arguments["x"]
    z = arguments["z"]

    try:
        # SIMPLIFIED SURFACE DETECTION
        # Uses player Y position as baseline reference for ground level
        # This avoids complex raycasting that often fails

        logger_instance.info(f"Detecting surface level at X={x}, Z={z}")

        # Get player position as baseline reference
        player_y_baseline = 64  # Default fallback (typical overworld surface)

        try:
            info = rcon.get_server_info()
            players_str = info.get("players", "")

            if players_str and ":" in players_str:
                player_list = players_str.split(":")[1].strip().split(",")
                if player_list:
                    player_name = player_list[0].strip()
                    player_data = rcon.send_command(f"data get entity {player_name} Pos")

                    if "has the following entity data" in player_data:
                        pos_match = PLAYER_POS_PATTERN.search(player_data)
                        if pos_match:
                            player_y_baseline = int(float(pos_match.group(2)))
                            logger_instance.info(
                                f"Using player Y position {player_y_baseline} as baseline reference"
                            )
        except Exception as e:
            logger_instance.warning(f"Could not get player position, using default Y=64: {e}")

        # Use player Y as the ground level for the target coordinates
        # This assumes terrain doesn't vary drastically across the world
        surface_y = player_y_baseline - 1  # Ground is typically 1 block below player feet

        # Check what block is at that level
        surface_block = "unknown"
        block_check = rcon.send_command(
            f"execute positioned {x} {surface_y} {z} run data get block ~ ~ ~ id"
        )
        if "has the following" in block_check:
            block_match = BLOCK_ID_PATTERN.search(block_check)
            if block_match:
                surface_block = block_match.group(1)

        logger_instance.info(f"Surface at ({x}, {z}): Y={surface_y}, block={surface_block}")

        return [
            TextContent(
                type="text",
                text=f"""🏔️ Surface Detection at X={x}, Z={z}

**Surface Level:** Y={surface_y}
**Block Type:** {surface_block}
**Detection Method:** Player Y baseline ({player_y_baseline})

**Building Coordinates:**
- On surface (RECOMMENDED): {x},{surface_y + 1},{z} - builds on top of ground
- Foundation level: {x},{surface_y},{z} - replaces surface block
- Elevated: {x},{surface_y + 2},{z} - builds 1 block above surface

**Note:** This uses player's current Y position as reference for ground level.
For best results, be near your build location before checking surface.
If terrain varies significantly, use `get_player_position` while standing at the exact build site.
""",
            )
        ]

    except Exception as e:
        logger_instance.error(f"Error in get_surface_level: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Error finding surface level: {str(e)}")]
