"""
Geometry calculation tool handlers.

This module contains handlers for geometric calculations including
shapes (circles, spheres, domes, arches) and window spacing.
"""

from typing import Dict, Any, List
from mcp.types import TextContent


async def handle_calculate_shape(
    arguments: Dict[str, Any], rcon, config, logger_instance
) -> List[TextContent]:
    """Handle calculate_shape tool."""
    from ..geometric_algorithms import CircleCalculator

    shape_type = arguments.get("shape")

    try:
        if shape_type == "circle":
            radius = arguments.get("radius")
            filled = arguments.get("filled", False)

            if radius is None:
                return [
                    TextContent(
                        type="text", text="❌ Error: 'radius' parameter required for circle"
                    )
                ]

            result = CircleCalculator.calculate_circle(radius=radius, filled=filled)

        elif shape_type == "sphere":
            radius = arguments.get("radius")
            hollow = arguments.get("hollow", True)

            if radius is None:
                return [
                    TextContent(
                        type="text", text="❌ Error: 'radius' parameter required for sphere"
                    )
                ]

            result = CircleCalculator.calculate_sphere(radius=radius, hollow=hollow)

        elif shape_type == "dome":
            radius = arguments.get("radius")
            style = arguments.get("style", "hemisphere")

            if radius is None:
                return [
                    TextContent(type="text", text="❌ Error: 'radius' parameter required for dome")
                ]

            result = CircleCalculator.calculate_dome(radius=radius, style=style)

        elif shape_type == "ellipse":
            width = arguments.get("width")
            height = arguments.get("height")
            filled = arguments.get("filled", False)

            if width is None or height is None:
                return [
                    TextContent(
                        type="text",
                        text="❌ Error: 'width' and 'height' parameters required for ellipse",
                    )
                ]

            result = CircleCalculator.calculate_ellipse(width=width, height=height, filled=filled)

        elif shape_type == "arch":
            width = arguments.get("width")
            height = arguments.get("height")
            depth = arguments.get("depth", 1)

            if width is None or height is None:
                return [
                    TextContent(
                        type="text",
                        text="❌ Error: 'width' and 'height' parameters required for arch",
                    )
                ]

            result = CircleCalculator.calculate_arch(width=width, height=height, depth=depth)

        else:
            return [TextContent(type="text", text=f"❌ Error: Unknown shape type '{shape_type}'")]

        # Format output
        output = f"🔷 {result['shape'].upper()} Calculation\n\n"

        # Add shape-specific info
        if "radius" in result:
            output += f"**Radius:** {result['radius']} blocks\n"
        if "width" in result:
            output += f"**Width:** {result['width']} blocks\n"
        if "height" in result:
            output += f"**Height:** {result['height']} blocks\n"
        if "depth" in result:
            output += f"**Depth:** {result['depth']} blocks\n"
        if "style" in result:
            output += f"**Style:** {result['style']}\n"
        if "filled" in result:
            output += f"**Filled:** {'Yes' if result['filled'] else 'No (hollow outline)'}\n"
        if "hollow" in result:
            output += f"**Hollow:** {'Yes' if result['hollow'] else 'No (filled solid)'}\n"

        output += f"\n**Blocks Required:** {result['blocks_count']}\n\n"

        # Add ASCII preview for 2D shapes
        if "ascii_preview" in result and result["ascii_preview"]:
            output += "**Preview:**\n```\n" + result["ascii_preview"] + "\n```\n\n"

        # Add usage tip
        if "usage_tip" in result:
            output += f"💡 **Tip:** {result['usage_tip']}\n\n"

        # Add WorldEdit command if available
        if "worldedit_command" in result:
            output += f"**WorldEdit Command:** `{result['worldedit_command']}`\n\n"

        # Add coordinate sample (first 20 coordinates)
        coords = result["coordinates"][:20]
        output += f"**Coordinates** (showing first 20 of {result['blocks_count']}):\n"
        for i, coord in enumerate(coords, 1):
            if len(coord) == 2:
                output += f"  {i}. ({coord[0]}, {coord[1]})\n"
            else:
                output += f"  {i}. ({coord[0]}, {coord[1]}, {coord[2]})\n"

        if len(result["coordinates"]) > 20:
            output += f"  ... and {len(result['coordinates']) - 20} more coordinates\n"

        output += "\n**Next Steps:**\n"
        output += "1. Use these coordinates to place blocks manually with setblock commands\n"
        output += "2. Or use WorldEdit's shape commands (//sphere, //cyl) as reference\n"
        output += "3. Build layer by layer for 3D shapes\n"

        logger_instance.info(
            f"Shape calculation complete: {result['shape']} with {result['blocks_count']} blocks"
        )

        return [TextContent(type="text", text=output)]

    except Exception as e:
        logger_instance.error(f"Error in shape calculation: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Calculation failed: {str(e)}")]
