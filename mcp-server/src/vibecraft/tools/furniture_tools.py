"""
Furniture Tool Handlers

Search and place furniture from the furniture catalog and layout library.
"""

import json
import logging
from typing import Dict, Any, List
from mcp.types import TextContent

logger = logging.getLogger(__name__)


async def handle_furniture_lookup(
    arguments: Dict[str, Any],
    rcon,
    config,
    logger_instance: logging.Logger
) -> List[TextContent]:
    """
    Handle furniture_lookup tool.

    Search and retrieve furniture layouts for automated building.
    """
    from ..server import load_furniture_layouts, load_furniture_catalog

    action = arguments.get("action")

    if not action:
        return [TextContent(type="text", text="❌ Error: 'action' parameter is required (must be 'search' or 'get')")]

    layouts = load_furniture_layouts()
    catalog = load_furniture_catalog()

    if not layouts and not catalog:
        return [TextContent(type="text", text="❌ Error: No furniture data available (both layouts and catalog missing)")]

    # Create lookup index: map IDs to layouts
    {layout['id']: layout for layout in layouts}

    # Filter catalog to only actual furniture (not category headings)
    furniture_items = [item for item in catalog if item.get('heading_level', 2) >= 3]

    if action == "search":
        # Search for furniture by query, category, or tags
        query = arguments.get("query", "").lower()
        category_filter = arguments.get("category", "").lower()
        tags_filter = arguments.get("tags", [])
        tags_filter = [tag.lower() for tag in tags_filter] if tags_filter else []

        results = []
        seen_ids = set()

        # First, search through layouts (these have precise coordinates)
        for layout in layouts:
            # Check if matches search criteria
            matches = True

            if query:
                # Search in name, category, subcategory, and tags
                name_match = query in layout.get("name", "").lower()
                id_match = query in layout.get("id", "").lower()
                cat_match = query in layout.get("category", "").lower()
                subcat_match = query in layout.get("subcategory", "").lower()
                tags_match = any(query in tag.lower() for tag in layout.get("tags", []))

                matches = matches and (name_match or id_match or cat_match or subcat_match or tags_match)

            if category_filter:
                matches = matches and (category_filter in layout.get("category", "").lower())

            if tags_filter:
                layout_tags = [tag.lower() for tag in layout.get("tags", [])]
                # Check if ALL filter tags are present
                matches = matches and all(tag in layout_tags for tag in tags_filter)

            if matches:
                seen_ids.add(layout.get("id"))
                # Add to results (summary only, not full layout)
                results.append({
                    "name": layout.get("name"),
                    "id": layout.get("id"),
                    "category": layout.get("category"),
                    "subcategory": layout.get("subcategory"),
                    "tags": layout.get("tags", []),
                    "bounds": layout.get("bounds"),
                    "materials_count": sum(layout.get("materials", {}).values()),
                    "notes": layout.get("notes", "")[:100] + "..." if len(layout.get("notes", "")) > 100 else layout.get("notes", ""),
                    "has_layout": True,
                    "source": "layout"
                })

        # Then, search through catalog items (text-based instructions)
        for item in furniture_items:
            # Skip if already in layouts
            if item.get("id") in seen_ids:
                continue

            matches = True

            if query:
                # Search in name and category
                name_match = query in item.get("name", "").lower()
                id_match = query in item.get("id", "").lower()
                cat_match = query in item.get("category", "").lower()

                matches = matches and (name_match or id_match or cat_match)

            if category_filter:
                matches = matches and (category_filter in item.get("category", "").lower())

            # Catalog items don't have tags, so skip tag filtering for them

            if matches:
                # Extract first sentence from content_blocks
                description = ""
                for block in item.get("content_blocks", []):
                    if block.get("type") == "paragraph":
                        text = block.get("text", "")
                        description = text[:100] + "..." if len(text) > 100 else text
                        break

                results.append({
                    "name": item.get("name"),
                    "id": item.get("id"),
                    "category": item.get("category"),
                    "subcategory": item.get("subcategory"),
                    "tags": [],
                    "bounds": None,
                    "materials_count": 0,
                    "notes": description,
                    "has_layout": False,
                    "source": "catalog"
                })

        if not results:
            search_params = []
            if query:
                search_params.append(f"query='{query}'")
            if category_filter:
                search_params.append(f"category='{category_filter}'")
            if tags_filter:
                search_params.append(f"tags={tags_filter}")

            return [TextContent(type="text", text=f"🔍 No furniture found matching: {', '.join(search_params)}\n\nTry:\n- Broader search terms\n- Different category (bedroom, kitchen, living_room, etc.)\n- Fewer tag filters")]

        # Format results
        layout_count = sum(1 for r in results if r['has_layout'])
        catalog_count = sum(1 for r in results if not r['has_layout'])

        result_text = f"🪑 Found {len(results)} furniture item(s):\n"
        result_text += f"   - {layout_count} with automated layouts\n"
        result_text += f"   - {catalog_count} with manual instructions only\n\n"

        for i, item in enumerate(results, 1):
            # Indicate if has layout or catalog only
            status_icon = "✅" if item['has_layout'] else "📝"

            result_text += f"{i}. {status_icon} **{item['name']}** (ID: `{item['id']}`)\n"
            result_text += f"   - Category: {item['category']}"
            if item.get('subcategory'):
                result_text += f" > {item['subcategory']}"
            result_text += "\n"

            if item['has_layout']:
                bounds = item['bounds']
                result_text += f"   - Size: {bounds['width']}×{bounds['height']}×{bounds['depth']} blocks (W×H×D)\n"
                result_text += f"   - Materials: {item['materials_count']} total blocks\n"
                if item.get('tags'):
                    result_text += f"   - Tags: {', '.join(item['tags'])}\n"
                result_text += "   - ✅ Automated layout available\n"
            else:
                result_text += "   - 📝 Manual instructions only (no automated layout yet)\n"

            if item.get('notes'):
                result_text += f"   - Notes: {item['notes']}\n"
            result_text += "\n"

        result_text += "\n💡 Legend:\n"
        result_text += "   ✅ = Has automated layout (can be placed with furniture_placer)\n"
        result_text += "   📝 = Manual instructions only (build by hand using catalog)\n\n"
        result_text += "To get details, use: `furniture_lookup` with action='get' and furniture_id='<id>'"

        return [TextContent(type="text", text=result_text)]

    elif action == "get":
        # Get specific furniture layout or catalog item by ID
        furniture_id = arguments.get("furniture_id")

        if not furniture_id:
            return [TextContent(type="text", text="❌ Error: 'furniture_id' parameter is required for action='get'")]

        # Try to find in layouts first
        layout = None
        for item in layouts:
            if item.get("id") == furniture_id:
                layout = item
                break

        # If not in layouts, try catalog
        catalog_item = None
        if not layout:
            for item in furniture_items:
                if item.get("id") == furniture_id:
                    catalog_item = item
                    break

        if not layout and not catalog_item:
            return [TextContent(type="text", text=f"❌ Furniture not found: '{furniture_id}'\n\nUse action='search' to find available furniture IDs.")]

        # If found in catalog but not layouts, return catalog info
        if catalog_item and not layout:
            result_text = f"📝 **{catalog_item['name']}** (ID: `{catalog_item['id']}`)\n\n"
            result_text += "**Status:** Manual instructions only (no automated layout yet)\n\n"

            result_text += "**Category:** " + catalog_item['category']
            if catalog_item.get('subcategory'):
                result_text += f" > {catalog_item['subcategory']}"
            result_text += "\n\n"

            result_text += "**Build Instructions:**\n\n"

            # Extract all content blocks
            for block in catalog_item.get('content_blocks', []):
                if block.get('type') == 'paragraph':
                    result_text += block.get('text', '') + "\n\n"
                elif block.get('type') == 'list':
                    style = block.get('style', 'unordered')
                    for i, item_text in enumerate(block.get('items', []), 1):
                        if style == 'ordered':
                            result_text += f"{i}. {item_text}\n"
                        else:
                            result_text += f"- {item_text}\n"
                    result_text += "\n"
                elif block.get('type') == 'table':
                    result_text += "\n**Table:**\n"
                    headers = block.get('headers', [])
                    if headers:
                        result_text += "| " + " | ".join(headers) + " |\n"
                        result_text += "| " + " | ".join(['---'] * len(headers)) + " |\n"
                    for row in block.get('rows', []):
                        result_text += "| " + " | ".join(row) + " |\n"
                    result_text += "\n"

            result_text += "\n💡 This furniture currently only has manual build instructions.\n"
            result_text += "To create an automated layout, define precise block coordinates in minecraft_furniture_layouts.json"

            return [TextContent(type="text", text=result_text)]

        # Return full layout as formatted JSON
        result_text = f"🪑 **{layout['name']}** (ID: `{layout['id']}`)\n\n"

        # Basic info
        result_text += "**Category:** " + layout['category']
        if layout.get('subcategory'):
            result_text += f" > {layout['subcategory']}"
        result_text += "\n\n"

        # Dimensions
        bounds = layout['bounds']
        result_text += f"**Dimensions:** {bounds['width']}×{bounds['height']}×{bounds['depth']} blocks (Width × Height × Depth)\n\n"

        # Origin
        origin = layout.get('origin', {})
        result_text += f"**Origin:** {origin.get('type', 'front_left_bottom')} (facing {origin.get('facing', 'north')})\n\n"

        # Materials
        materials = layout.get('materials', {})
        if materials:
            result_text += "**Materials Required:**\n"
            for block, count in materials.items():
                result_text += f"  - {block}: {count}\n"
            result_text += f"  Total: {sum(materials.values())} blocks\n\n"

        # Placements
        placements = layout.get('placements', [])
        result_text += f"**Placements:** ({len(placements)} operations)\n"
        for i, placement in enumerate(placements[:10], 1):  # Show first 10
            ptype = placement.get('type')
            if ptype == 'block':
                pos = placement['pos']
                block = placement['block']
                state = placement.get('state', '')
                result_text += f"  {i}. Block at ({pos['x']},{pos['y']},{pos['z']}): {block}{state}\n"
            elif ptype == 'fill':
                from_pos = placement['from']
                to_pos = placement['to']
                block = placement['block']
                result_text += f"  {i}. Fill ({from_pos['x']},{from_pos['y']},{from_pos['z']}) to ({to_pos['x']},{to_pos['y']},{to_pos['z']}): {block}\n"
            elif ptype == 'line':
                from_pos = placement['from']
                to_pos = placement['to']
                block = placement['block']
                result_text += f"  {i}. Line ({from_pos['x']},{from_pos['y']},{from_pos['z']}) to ({to_pos['x']},{to_pos['y']},{to_pos['z']}): {block}\n"
            elif ptype == 'layer':
                y = placement['y']
                pattern = placement['pattern']
                result_text += f"  {i}. Layer at Y={y}: {pattern}\n"

        if len(placements) > 10:
            result_text += f"  ... and {len(placements) - 10} more placements\n"
        result_text += "\n"

        # Clearance
        clearance = layout.get('clearance')
        if clearance:
            result_text += "**Clearance Required:**\n"
            result_text += f"  - Front: {clearance.get('front', 0)} blocks\n"
            result_text += f"  - Back: {clearance.get('back', 0)} blocks\n"
            result_text += f"  - Left: {clearance.get('left', 0)} blocks\n"
            result_text += f"  - Right: {clearance.get('right', 0)} blocks\n"
            result_text += f"  - Top: {clearance.get('top', 0)} blocks\n\n"

        # Notes
        if layout.get('notes'):
            result_text += f"**Notes:** {layout['notes']}\n\n"

        # Variants
        variants = layout.get('variants', [])
        if variants:
            result_text += f"**Variants:** ({len(variants)} available)\n"
            for variant in variants:
                result_text += f"  - {variant['name']} (ID: `{variant['id']}`): {variant['changes']}\n"
            result_text += "\n"

        # Tags
        if layout.get('tags'):
            result_text += f"**Tags:** {', '.join(layout['tags'])}\n\n"

        # Full layout data as JSON
        result_text += "**Full Layout Data (JSON):**\n```json\n"
        result_text += json.dumps(layout, indent=2)
        result_text += "\n```\n\n"

        result_text += "💡 Use the placement helper tool to build this furniture at specific coordinates."

        return [TextContent(type="text", text=result_text)]

    else:
        return [TextContent(type="text", text=f"❌ Invalid action: '{action}'. Must be 'search' or 'get'.")]


async def handle_place_furniture(
    arguments: Dict[str, Any],
    rcon,
    config,
    logger_instance: logging.Logger
) -> List[TextContent]:
    """
    Handle place_furniture tool.

    Place furniture layout at specified coordinates in the world.
    """
    from ..server import load_furniture_layouts
    from ..furniture_placer import FurniturePlacer

    furniture_id = arguments.get("furniture_id")
    origin_x = arguments.get("origin_x")
    origin_y = arguments.get("origin_y")
    origin_z = arguments.get("origin_z")
    facing = arguments.get("facing")
    place_on_surface = arguments.get("place_on_surface", True)
    preview_only = arguments.get("preview_only", False)

    missing = [field for field in ("furniture_id", "origin_x", "origin_y", "origin_z") if arguments.get(field) is None]
    if missing:
        return [TextContent(type="text", text=f"❌ Missing required field(s): {', '.join(missing)}")]

    if facing:
        facing = facing.lower()
        if facing not in FurniturePlacer.ROTATIONS:
            valid = ", ".join(FurniturePlacer.ROTATIONS.keys())
            return [TextContent(type="text", text=f"❌ Invalid facing '{facing}'. Valid options: {valid}")]

    layout = next((item for item in load_furniture_layouts() if item.get('id') == furniture_id), None)
    if not layout:
        return [TextContent(type="text", text=f"❌ Furniture layout '{furniture_id}' not found or does not have an automated blueprint.")]

    try:
        commands = FurniturePlacer.get_placement_commands(
            layout=layout,
            origin_x=int(origin_x),
            origin_y=int(origin_y),
            origin_z=int(origin_z),
            facing=facing,
            place_on_surface=place_on_surface,
        )
    except ValueError as exc:
        logger_instance.error(f"Error generating placement commands: {exc}")
        return [TextContent(type="text", text=f"❌ Failed to generate commands: {exc}")]

    summary = FurniturePlacer.get_command_summary(commands)
    final_facing = facing or layout.get('origin', {}).get('facing', 'north')

    if preview_only:
        command_listing = '\n'.join(commands)
        preview_text = [
            "🛋️ **Furniture Placement Preview**",
            f"Layout: {layout.get('name')} (`{layout.get('id')}`)",
            f"Origin: ({origin_x},{origin_y},{origin_z})",
            f"Facing: {final_facing}",
            "",
            summary,
            "Commands:",
            "```plain",
            command_listing,
            "```",
            "Set `preview_only` to false to execute these commands.",
        ]
        return [TextContent(type="text", text='\n'.join(preview_text))]

    executed_commands: List[str] = []
    try:
        for command in commands:
            stripped = command.strip()
            if not stripped or stripped.startswith('#'):
                continue
            executed_commands.append(stripped)
            rcon.execute_command(stripped)
    except Exception as exc:
        logger_instance.error(f"Furniture placement failed: {exc}", exc_info=True)
        failure_output = [
            "❌ **Furniture placement failed**",
            f"Layout: {layout.get('name')} (`{layout.get('id')}`)",
            f"Origin: ({origin_x},{origin_y},{origin_z})",
            f"Facing: {final_facing}",
            "",
            "Commands executed before failure:",
        ]
        for cmd in executed_commands[-10:]:
            failure_output.append(f"- `{cmd}`")
        failure_output.extend([
            "",
            f"Error: {exc}",
            "Use `//undo` to revert the changes if necessary.",
        ])
        return [TextContent(type="text", text='\n'.join(failure_output))]

    materials = layout.get('materials', {})
    clearance = layout.get('clearance', {})

    material_lines = []
    if materials:
        for block, count in sorted(materials.items(), key=lambda item: item[0])[:10]:
            material_lines.append(f"- {block}: {count}")
        if len(materials) > 10:
            material_lines.append(f"- … ({len(materials) - 10} more entries)")

    clearance_lines = []
    if clearance:
        for side, distance in clearance.items():
            clearance_lines.append(f"- {side.title()}: {distance}")

    success_lines = [
        "✅ **Furniture placed successfully**",
        f"Layout: {layout.get('name')} (`{layout.get('id')}`)",
        f"Origin: ({origin_x},{origin_y},{origin_z})",
        f"Facing: {final_facing}",
        "",
        summary,
    ]

    if material_lines:
        success_lines.extend(["**Materials Used:**"] + material_lines + [""])

    if clearance_lines:
        success_lines.extend(["**Recommended Clearance:**"] + clearance_lines + [""])

    displayed_commands = executed_commands[:10]
    if displayed_commands:
        success_lines.append("**Executed Commands (first 10):**")
        for cmd in displayed_commands:
            success_lines.append(f"- `{cmd}`")
        if len(executed_commands) > 10:
            success_lines.append(f"- … ({len(executed_commands) - 10} more)")
        success_lines.append("")

    success_lines.append("Undo tip: run `//undo` if you need to revert this placement.")

    return [TextContent(type="text", text='\n'.join(success_lines))]
