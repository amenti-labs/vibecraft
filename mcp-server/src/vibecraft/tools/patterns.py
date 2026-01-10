"""
Pattern Tool Handlers

Building and terrain pattern lookup and placement.
"""

import logging
from typing import Dict, Any, List
from mcp.types import TextContent

from .pattern_lookup_base import PatternLookupHandler
from ..paths import DATA_DIR

logger = logging.getLogger(__name__)


async def handle_building_pattern_lookup(
    arguments: Dict[str, Any], rcon, config, logger_instance: logging.Logger
) -> List[TextContent]:
    """
    Handle building_pattern_lookup tool.

    Search and retrieve building patterns (roofs, windows, doors, etc.).
    """
    from ..server import load_structured_patterns

    # Load structured patterns for structure check
    structured_patterns = {p.get("id"): p for p in load_structured_patterns() if p.get("id")}

    def has_structure(pattern_id: str) -> bool:
        """Check if pattern has structured placement data."""
        return pattern_id in structured_patterns

    # Create handler with building-specific parameters
    handler = PatternLookupHandler(
        patterns_file=DATA_DIR / "building_patterns_complete.json",
        emoji_prefix="🏗️",
        category_name="Building",
        logger_instance=logger_instance,
        has_structure_check=has_structure,
    )

    return handler.handle(arguments)


async def handle_place_building_pattern(
    arguments: Dict[str, Any], rcon, config, logger_instance: logging.Logger
) -> List[TextContent]:
    """
    Handle place_building_pattern tool.

    Place a building pattern at specified coordinates.
    """
    from ..server import _load_json_list, load_structured_patterns
    from ..furniture_placer import FurniturePlacer
    from ..pattern_placer import PatternPlacer

    pattern_id = arguments.get("pattern_id")
    origin_x = arguments.get("origin_x")
    origin_y = arguments.get("origin_y")
    origin_z = arguments.get("origin_z")
    facing = arguments.get("facing")
    preview_only = arguments.get("preview_only", False)

    missing = [
        field
        for field in ("pattern_id", "origin_x", "origin_y", "origin_z")
        if arguments.get(field) is None
    ]
    if missing:
        return [
            TextContent(type="text", text=f"❌ Missing required field(s): {', '.join(missing)}")
        ]

    if facing:
        facing = facing.lower()
        if facing not in FurniturePlacer.ROTATIONS:
            valid = ", ".join(FurniturePlacer.ROTATIONS.keys())
            return [
                TextContent(
                    type="text", text=f"❌ Invalid facing '{facing}'. Valid options: {valid}"
                )
            ]

    structured = next((p for p in load_structured_patterns() if p.get("id") == pattern_id), None)
    if not structured:
        return [
            TextContent(
                type="text",
                text=f"❌ Pattern '{pattern_id}' does not have structured placement data yet.",
            )
        ]

    metadata_pattern = next(
        (
            p
            for p in _load_json_list(DATA_DIR / "building_patterns_complete.json")
            if p.get("id") == pattern_id
        ),
        None,
    )
    pattern_name = structured.get("name") or (metadata_pattern or {}).get("name") or pattern_id

    try:
        commands = PatternPlacer.get_placement_commands(
            pattern=structured,
            origin_x=int(origin_x),
            origin_y=int(origin_y),
            origin_z=int(origin_z),
            facing=facing,
        )
    except ValueError as exc:
        logger_instance.error(f"Error generating pattern placement commands: {exc}")
        return [TextContent(type="text", text=f"❌ Failed to generate commands: {exc}")]

    summary = PatternPlacer.get_command_summary(commands)
    final_facing = facing or structured.get("origin", {}).get("facing", "north")

    if preview_only:
        command_block = "\n".join(commands)
        output = [
            "🏗️ **Building Pattern Preview**",
            f"Pattern: {pattern_name} (`{pattern_id}`)",
            f"Origin: ({origin_x},{origin_y},{origin_z})",
            f"Facing: {final_facing}",
            "",
            summary,
            "Commands:",
            "```plain",
            command_block,
            "```",
            "Set `preview_only` to false to execute these commands.",
        ]
        return [TextContent(type="text", text="\n".join(output))]

    executed_commands: List[str] = []
    try:
        for command in commands:
            stripped = command.strip()
            if not stripped or stripped.startswith("#"):
                continue
            executed_commands.append(stripped)
            rcon.execute_command(stripped)
    except Exception as exc:
        logger_instance.error(f"Pattern placement failed: {exc}", exc_info=True)
        failure_output = [
            "❌ **Pattern placement failed**",
            f"Pattern: {pattern_name} (`{pattern_id}`)",
            f"Origin: ({origin_x},{origin_y},{origin_z})",
            f"Facing: {final_facing}",
            "",
            "Commands executed before failure:",
        ]
        for cmd in executed_commands[-10:]:
            failure_output.append(f"- `{cmd}`")
        failure_output.extend(
            [
                "",
                f"Error: {exc}",
                "Use `//undo` to revert the changes if necessary.",
            ]
        )
        return [TextContent(type="text", text="\n".join(failure_output))]

    palette = structured.get("palette", {})
    materials = (metadata_pattern or {}).get("materials", {})

    palette_lines = []
    if palette:
        palette_lines.append("**Palette Legend:**")
        for symbol, block in palette.items():
            printable = symbol if symbol.strip() else "<space>"
            palette_lines.append(f"- `{printable}` → {block}")

    material_lines = []
    if materials:
        material_lines.append("**Metadata Materials:**")
        for block, count in sorted(materials.items(), key=lambda item: item[0])[:10]:
            material_lines.append(f"- {block}: {count}")
        if len(materials) > 10:
            material_lines.append(f"- … ({len(materials) - 10} more)")

    success_lines = [
        "✅ **Pattern placed successfully**",
        f"Pattern: {pattern_name} (`{pattern_id}`)",
        f"Origin: ({origin_x},{origin_y},{origin_z})",
        f"Facing: {final_facing}",
        "",
        summary,
    ]

    if palette_lines:
        success_lines.append("")
        success_lines.extend(palette_lines)

    if material_lines:
        success_lines.append("")
        success_lines.extend(material_lines)

    displayed_commands = executed_commands[:10]
    if displayed_commands:
        success_lines.append("")
        success_lines.append("**Executed Commands (first 10):**")
        for cmd in displayed_commands:
            success_lines.append(f"- `{cmd}`")
        if len(executed_commands) > 10:
            success_lines.append(f"- … ({len(executed_commands) - 10} more)")

    success_lines.append("")
    success_lines.append("Undo tip: run `//undo` if you need to revert this placement.")

    return [TextContent(type="text", text="\n".join(success_lines))]


async def handle_terrain_pattern_lookup(
    arguments: Dict[str, Any], rcon, config, logger_instance: logging.Logger
) -> List[TextContent]:
    """
    Handle terrain_pattern_lookup tool.

    Search and retrieve terrain patterns (trees, rocks, ponds, etc.).
    """
    # Create handler with terrain-specific parameters
    handler = PatternLookupHandler(
        patterns_file=DATA_DIR / "terrain_patterns_complete.json",
        emoji_prefix="🌲",
        category_name="Terrain",
        logger_instance=logger_instance,
        has_structure_check=None,  # Terrain patterns don't have structured placement
    )

    return handler.handle(arguments)
