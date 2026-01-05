"""
Terrain analysis and generation tool handlers.

This module contains handlers for terrain-related operations including
analysis, generation, texturing, and smoothing.
"""

from typing import Dict, Any, List
from mcp.types import TextContent


async def handle_generate_terrain(
    arguments: Dict[str, Any],
    rcon,
    config,
    logger_instance
) -> List[TextContent]:
    """Handle generate_terrain tool."""
    from ..terrain_generation import TerrainGenerator

    terrain_type = arguments.get("type")
    x1, y1, z1 = arguments.get("x1"), arguments.get("y1"), arguments.get("z1")
    x2, y2, z2 = arguments.get("x2"), arguments.get("y2"), arguments.get("z2")

    # Optional parameters (vary by terrain type)
    scale = arguments.get("scale")
    amplitude = arguments.get("amplitude")
    depth = arguments.get("depth")
    height = arguments.get("height")
    direction = arguments.get("direction")
    octaves = arguments.get("octaves")
    smooth_iterations = arguments.get("smooth_iterations")
    seed = arguments.get("seed")

    try:
        generator = TerrainGenerator(rcon)

        # Call appropriate generation method based on type
        if terrain_type == "rolling_hills":
            kwargs = {"x1": x1, "y1": y1, "z1": z1, "x2": x2, "y2": y2, "z2": z2}
            if scale: kwargs["scale"] = scale
            if amplitude: kwargs["amplitude"] = amplitude
            if octaves: kwargs["octaves"] = octaves
            if smooth_iterations: kwargs["smooth_iterations"] = smooth_iterations
            if seed: kwargs["seed"] = seed
            result = generator.generate_hills(**kwargs)

        elif terrain_type == "rugged_mountains":
            kwargs = {"x1": x1, "y1": y1, "z1": z1, "x2": x2, "y2": y2, "z2": z2}
            if scale: kwargs["scale"] = scale
            if amplitude: kwargs["amplitude"] = amplitude
            if octaves: kwargs["octaves"] = octaves
            if smooth_iterations: kwargs["smooth_iterations"] = smooth_iterations
            if seed: kwargs["seed"] = seed
            result = generator.generate_mountains(**kwargs)

        elif terrain_type == "valley_network":
            kwargs = {"x1": x1, "y1": y1, "z1": z1, "x2": x2, "y2": y2, "z2": z2}
            if scale: kwargs["scale"] = scale
            if depth: kwargs["depth"] = depth
            if octaves: kwargs["octaves"] = octaves
            if smooth_iterations: kwargs["smooth_iterations"] = smooth_iterations
            if seed: kwargs["seed"] = seed
            result = generator.generate_valleys(**kwargs)

        elif terrain_type == "mountain_range":
            kwargs = {"x1": x1, "y1": y1, "z1": z1, "x2": x2, "y2": y2, "z2": z2}
            if direction: kwargs["direction"] = direction
            if scale: kwargs["scale"] = scale
            if amplitude: kwargs["amplitude"] = amplitude
            if octaves: kwargs["octaves"] = octaves
            if smooth_iterations: kwargs["smooth_iterations"] = smooth_iterations
            if seed: kwargs["seed"] = seed
            result = generator.generate_mountain_range(**kwargs)

        elif terrain_type == "plateau":
            kwargs = {"x1": x1, "y1": y1, "z1": z1, "x2": x2, "y2": y2, "z2": z2}
            if height: kwargs["height"] = height
            if smooth_iterations: kwargs["smooth_iterations"] = smooth_iterations
            if seed: kwargs["seed"] = seed
            result = generator.generate_plateau(**kwargs)

        else:
            return [TextContent(type="text", text=f"❌ Unknown terrain type: {terrain_type}")]

        if not result.get("success"):
            return [TextContent(type="text", text=f"❌ Error: {result.get('error', 'Unknown error')}")]

        # Format output
        output = "🏔️ Terrain Generation Complete\n\n"
        output += f"**Type:** {result['terrain_type'].replace('_', ' ').title()}\n"
        output += f"**Summary:** {result['summary']}\n\n"

        output += "**Parameters Used:**\n"
        for key, value in result.get('parameters', {}).items():
            output += f"  - {key}: {value}\n"
        output += "\n"

        output += "**Operations Performed:**\n"
        for i, (operation, step_result) in enumerate(result.get('steps', []), 1):
            output += f"  {i}. {operation}\n"
            if operation == "Selection" and step_result.get("success"):
                region = step_result.get("region", {})
                output += f"     Region: {region.get('volume', 0):,} blocks\n"
        output += "\n"

        output += "**Next Steps:**\n"
        output += "  • Apply texturing with texture_terrain() for natural appearance\n"
        output += "  • Add additional smoothing if needed with smooth_terrain()\n"
        output += "  • Overlay vegetation, water features, or structures\n"

        logger_instance.info(f"Terrain generation complete: {terrain_type} at ({x1},{y1},{z1}) to ({x2},{y2},{z2})")

        return [TextContent(type="text", text=output)]

    except Exception as e:
        logger_instance.error(f"Error generating terrain: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Terrain generation failed: {str(e)}")]


async def handle_texture_terrain(
    arguments: Dict[str, Any],
    rcon,
    config,
    logger_instance
) -> List[TextContent]:
    """Handle texture_terrain tool."""
    from ..terrain_generation import TerrainGenerator

    style = arguments.get("style")
    x1, y1, z1 = arguments.get("x1"), arguments.get("y1"), arguments.get("z1")
    x2, y2, z2 = arguments.get("x2"), arguments.get("y2"), arguments.get("z2")

    try:
        generator = TerrainGenerator(rcon)
        result = generator.texture_natural_slopes(x1, y1, z1, x2, y2, z2, style)

        if not result.get("success"):
            return [TextContent(type="text", text=f"❌ Error: {result.get('error', 'Unknown error')}")]

        # Format output
        output = "🎨 Terrain Texturing Complete\n\n"
        output += f"**Style:** {style.title()}\n"
        output += f"**Summary:** {result['summary']}\n\n"

        recipe = result.get('recipe', {})
        output += "**Materials Applied:**\n"
        output += f"  - Base: {recipe.get('base', 'N/A')}\n"
        output += f"  - Surface: {recipe.get('surface', 'N/A')}\n\n"

        output += "**Operations Performed:**\n"
        for i, (operation, step_result) in enumerate(result.get('steps', []), 1):
            output += f"  {i}. {operation}\n"
        output += "\n"

        output += "**Texture applied successfully!** Your terrain now has a natural appearance.\n"

        logger_instance.info(f"Terrain texturing complete: {style} style at ({x1},{y1},{z1}) to ({x2},{y2},{z2})")

        return [TextContent(type="text", text=output)]

    except Exception as e:
        logger_instance.error(f"Error texturing terrain: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Terrain texturing failed: {str(e)}")]


async def handle_smooth_terrain(
    arguments: Dict[str, Any],
    rcon,
    config,
    logger_instance
) -> List[TextContent]:
    """Handle smooth_terrain tool."""
    from ..terrain_generation import TerrainGenerator

    x1, y1, z1 = arguments.get("x1"), arguments.get("y1"), arguments.get("z1")
    x2, y2, z2 = arguments.get("x2"), arguments.get("y2"), arguments.get("z2")
    iterations = arguments.get("iterations", 2)
    mask = arguments.get("mask")

    try:
        generator = TerrainGenerator(rcon)

        # Set selection first
        select_result = generator.set_selection(x1, y1, z1, x2, y2, z2)
        if not select_result.get("success"):
            return [TextContent(type="text", text=f"❌ Error: {select_result.get('error', 'Selection failed')}")]

        # Apply smoothing
        result = generator.smooth(iterations, mask)

        if not result.get("success"):
            return [TextContent(type="text", text=f"❌ Error: {result.get('error', 'Unknown error')}")]

        # Format output
        output = "✨ Terrain Smoothing Complete\n\n"
        output += f"**Iterations:** {result['iterations']}\n"
        output += f"**Region:** {select_result['region']['volume']:,} blocks\n"
        if mask:
            output += f"**Mask:** {mask}\n"
        output += "\n"

        output += f"**Result:** {result['output']}\n\n"
        output += "Terrain has been smoothed for a more natural appearance.\n"

        logger_instance.info(f"Terrain smoothing complete: {iterations} iterations at ({x1},{y1},{z1}) to ({x2},{y2},{z2})")

        return [TextContent(type="text", text=output)]

    except Exception as e:
        logger_instance.error(f"Error smoothing terrain: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Terrain smoothing failed: {str(e)}")]
