"""
Validation Tool Handlers

Pattern/mask validation, symmetry checking, lighting analysis, structure validation.
"""

import logging
from typing import Dict, Any, List
from mcp.types import TextContent

logger = logging.getLogger(__name__)


async def handle_validate_pattern(
    arguments: Dict[str, Any], rcon, config, logger_instance: logging.Logger
) -> List[TextContent]:
    """
    Handle validate_pattern tool.

    Validates WorldEdit pattern syntax before use in commands.
    """
    pattern = arguments.get("pattern", "").strip()

    if not pattern:
        return [TextContent(type="text", text="❌ Pattern cannot be empty")]

    # Basic pattern validation
    analysis = ["Pattern Analysis:", ""]

    # Check for percentages (random pattern)
    if "%" in pattern:
        analysis.append("✓ Random weighted pattern detected")
        parts = pattern.split(",")
        total_weight = 0
        for part in parts:
            if "%" in part:
                weight = part.split("%")[0]
                try:
                    total_weight += int(weight)
                except ValueError:
                    pass
        if total_weight > 0:
            analysis.append(f"  Total weight: {total_weight}%")

    # Check for special patterns
    if pattern.startswith("#"):
        analysis.append("✓ Special pattern detected")
        if pattern == "#clipboard":
            analysis.append("  Uses clipboard contents")
        elif pattern.startswith("##"):
            analysis.append(f"  Block category: {pattern[2:]}")

    # Check for block states
    if "[" in pattern and "]" in pattern:
        analysis.append("✓ Block states detected")

    # Check for asterisk (random state)
    if pattern.startswith("*"):
        analysis.append("✓ Random block state pattern")

    if len(analysis) == 2:  # Only header and empty line
        analysis.append("✓ Simple block pattern")

    analysis.append("")
    analysis.append("Pattern appears valid. Use it in commands like:")
    analysis.append(f"  //set {pattern}")
    analysis.append(f"  //replace stone {pattern}")

    return [TextContent(type="text", text="\n".join(analysis))]


async def handle_validate_mask(
    arguments: Dict[str, Any], rcon, config, logger_instance: logging.Logger
) -> List[TextContent]:
    """
    Handle validate_mask tool.

    Validates WorldEdit mask syntax before use in commands.
    """
    mask = arguments.get("mask", "").strip()

    if not mask:
        return [TextContent(type="text", text="❌ Mask cannot be empty")]

    analysis = ["Mask Analysis:", ""]

    # Check for special masks
    if mask.startswith("#"):
        analysis.append("✓ Special mask detected")
        if mask == "#existing":
            analysis.append("  Matches all non-air blocks")
        elif mask == "#solid":
            analysis.append("  Matches solid blocks")
        elif mask.startswith("##"):
            analysis.append(f"  Block category: {mask[2:]}")

    # Check for negation
    if mask.startswith("!"):
        analysis.append("✓ Negation mask (inverted)")

    # Check for percentage
    if mask.startswith("%"):
        try:
            pct = int(mask[1:])
            analysis.append(f"✓ Random mask: {pct}% chance")
        except ValueError:
            pass

    # Check for expression
    if mask.startswith("="):
        analysis.append("✓ Expression mask detected")
        analysis.append("  Mathematical expression will be evaluated")

    # Check for offset masks
    if mask.startswith(">") or mask.startswith("<"):
        analysis.append("✓ Offset mask detected")
        if mask.startswith(">"):
            analysis.append("  Matches blocks above the specified type")
        else:
            analysis.append("  Matches blocks below the specified type")

    if len(analysis) == 2:
        analysis.append("✓ Simple block mask")

    analysis.append("")
    analysis.append("Mask appears valid. Use it in commands like:")
    analysis.append(f"  //replace {mask} stone")
    analysis.append(f"  //set stone -m {mask}")

    return [TextContent(type="text", text="\n".join(analysis))]


async def handle_check_symmetry(
    arguments: Dict[str, Any], rcon, config, logger_instance: logging.Logger
) -> List[TextContent]:
    """
    Handle check_symmetry tool.

    Analyzes structural symmetry across an axis for quality assurance.
    """
    from ..validation_algorithms import SymmetryChecker
    from ..server import workflow

    x1 = arguments.get("x1")
    y1 = arguments.get("y1")
    z1 = arguments.get("z1")
    x2 = arguments.get("x2")
    y2 = arguments.get("y2")
    z2 = arguments.get("z2")
    axis = arguments.get("axis", "x")
    tolerance = arguments.get("tolerance", 0)
    resolution = arguments.get("resolution", 1)

    try:
        checker = SymmetryChecker(rcon)
        result = checker.check_symmetry(x1, y1, z1, x2, y2, z2, axis, tolerance, resolution)

        if "error" in result:
            return [TextContent(type="text", text=f"❌ Error: {result['error']}")]

        # Format output
        output = f"🔄 Symmetry Check: {axis.upper()} Axis\n\n"
        output += f"**Symmetry Score:** {result['symmetry_score']}% ({result['verdict']})\n"
        output += f"**Center Plane:** {axis.upper()}={result['center_plane']}\n"
        output += f"**Blocks Checked:** {result['total_blocks_checked']:,}\n"
        output += f"**Symmetric:** {result['symmetric_blocks']:,} blocks\n"
        output += f"**Asymmetric:** {result['asymmetric_blocks']:,} blocks\n"
        output += f"**Tolerance:** {result['tolerance']} blocks allowed\n\n"

        output += f"**Summary:** {result['summary']}\n\n"

        if result["differences"]:
            output += f"**Asymmetric Blocks** (showing first {min(len(result['differences']), 50)} of {result['total_differences']}):\n"
            for i, diff in enumerate(result["differences"][:10], 1):
                output += f"  {i}. ({diff['position1'][0]},{diff['position1'][1]},{diff['position1'][2]}): {diff['block1']} ≠ "
                output += f"({diff['position2'][0]},{diff['position2'][1]},{diff['position2'][2]}): {diff['block2']}\n"
                output += f"     → {diff['recommendation']}\n"

            if len(result["differences"]) > 10:
                output += f"  ... and {len(result['differences']) - 10} more differences\n"
        else:
            output += "✅ **Perfect Symmetry!** No asymmetries detected.\n"

        logger_instance.info(f"Symmetry check complete: {result['symmetry_score']}% on {axis} axis")

        workflow.record_validation(
            "symmetry_check",
            {
                "region": {
                    "x1": x1,
                    "y1": y1,
                    "z1": z1,
                    "x2": x2,
                    "y2": y2,
                    "z2": z2,
                },
                "axis": axis,
                "resolution": resolution,
                "symmetry_score": result["symmetry_score"],
                "differences": result["asymmetric_blocks"],
            },
        )

        return [TextContent(type="text", text=output)]

    except Exception as e:
        logger_instance.error(f"Error in symmetry check: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Symmetry check failed: {str(e)}")]


async def handle_analyze_lighting(
    arguments: Dict[str, Any], rcon, config, logger_instance: logging.Logger
) -> List[TextContent]:
    """
    Handle analyze_lighting tool.

    Analyzes lighting levels and suggests optimal torch/lantern placement.
    """
    from ..validation_algorithms import LightingAnalyzer
    from ..server import workflow

    x1 = arguments.get("x1")
    y1 = arguments.get("y1")
    z1 = arguments.get("z1")
    x2 = arguments.get("x2")
    y2 = arguments.get("y2")
    z2 = arguments.get("z2")
    resolution = arguments.get("resolution", 2)

    try:
        analyzer = LightingAnalyzer(rcon)
        result = analyzer.analyze_lighting(x1, y1, z1, x2, y2, z2, resolution)

        if "error" in result:
            return [TextContent(type="text", text=f"❌ Error: {result['error']}")]

        # Format output
        output = "💡 Lighting Analysis\n\n"
        output += f"**Average Light Level:** {result['average_light_level']}\n"
        output += f"**Total Samples:** {result['total_samples']:,}\n"
        output += f"**Dark Spots:** {result['dark_spots_count']:,}\n"
        output += f"**Mob Spawn Risk:** {result['mob_spawn_risk']}\n\n"

        dist = result["light_distribution"]
        output += "**Light Distribution:**\n"
        output += (
            f"  - Well-lit (≥12): {dist['well_lit']:,} blocks ({dist['well_lit_percentage']}%)\n"
        )
        output += f"  - Dim (8-11): {dist['dim']:,} blocks ({dist['dim_percentage']}%)\n"
        output += f"  - Dark (<8): {dist['dark']:,} blocks ({dist['dark_percentage']}%)\n\n"

        output += f"**Summary:** {result['summary']}\n\n"

        if result["optimal_placements"]:
            output += f"**Recommended Light Placements** ({len(result['optimal_placements'])} suggested):\n"
            for i, placement in enumerate(result["optimal_placements"][:15], 1):
                pos = placement["position"]
                output += f"  {i}. {placement['suggested_source'].capitalize()} at ({pos[0]},{pos[1]},{pos[2]}) - {placement['reason']}\n"

            if len(result["optimal_placements"]) > 15:
                output += f"  ... and {len(result['optimal_placements']) - 15} more placements\n"
        else:
            output += "✅ **Lighting adequate!** No additional light sources needed.\n"

        logger_instance.info(
            f"Lighting analysis complete: {result['average_light_level']} avg light, {result['dark_spots_count']} dark spots"
        )

        workflow.record_validation(
            "lighting_analysis",
            {
                "region": {
                    "x1": x1,
                    "y1": y1,
                    "z1": z1,
                    "x2": x2,
                    "y2": y2,
                    "z2": z2,
                },
                "resolution": resolution,
                "average_light": result["average_light_level"],
                "dark_spots": result["dark_spots_count"],
            },
        )

        return [TextContent(type="text", text=output)]

    except Exception as e:
        logger_instance.error(f"Error in lighting analysis: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Lighting analysis failed: {str(e)}")]


async def handle_validate_structure(
    arguments: Dict[str, Any], rcon, config, logger_instance: logging.Logger
) -> List[TextContent]:
    """
    Handle validate_structure tool.

    Validates structural integrity and detects physics violations.
    """
    from ..validation_algorithms import StructureValidator
    from ..server import workflow

    x1 = arguments.get("x1")
    y1 = arguments.get("y1")
    z1 = arguments.get("z1")
    x2 = arguments.get("x2")
    y2 = arguments.get("y2")
    z2 = arguments.get("z2")
    resolution = arguments.get("resolution", 1)

    try:
        validator = StructureValidator(rcon)
        result = validator.validate_structure(x1, y1, z1, x2, y2, z2, resolution)

        if "error" in result:
            return [TextContent(type="text", text=f"❌ Error: {result['error']}")]

        # Format output
        output = "🏗️ Structure Integrity Validation\n\n"
        output += f"**Status:** {'✅ VALID' if result['structure_valid'] else '⚠️ ISSUES FOUND'}\n"
        output += f"**Blocks Checked:** {result['total_blocks_checked']:,}\n"
        output += f"**Issues Found:** {result['issues_found']}\n\n"

        output += f"**Summary:** {result['summary']}\n\n"

        if result["gravity_violations"]:
            output += f"**Gravity Violations** ({len(result['gravity_violations'])} found):\n"
            for i, violation in enumerate(result["gravity_violations"][:10], 1):
                pos = violation["position"]
                output += f"  {i}. {violation['block']} at ({pos[0]},{pos[1]},{pos[2]})\n"
                output += f"     ⚠️ {violation['severity']}: {violation['issue']}\n"
                output += f"     → {violation['recommendation']}\n"

            if len(result["gravity_violations"]) > 10:
                output += f"  ... and {len(result['gravity_violations']) - 10} more violations\n"
            output += "\n"

        if result["floating_blocks"]:
            output += f"**Floating Blocks** ({result['total_floating']} found, showing first 10):\n"
            for i, floating in enumerate(result["floating_blocks"][:10], 1):
                pos = floating["position"]
                output += f"  {i}. {floating['block']} at ({pos[0]},{pos[1]},{pos[2]})\n"
                output += f"     ⚠️ {floating['severity']}: {floating['issue']}\n"
                output += f"     → {floating['recommendation']}\n"

            if result["total_floating"] > 10:
                output += f"  ... and {result['total_floating'] - 10} more floating blocks\n"
            output += "\n"

        if result["structure_valid"]:
            output += "✅ **Structure passed all validation checks!**\n"
            output += "No physics violations or floating blocks detected.\n"

        logger_instance.info(
            f"Structure validation complete: {result['issues_found']} issues found"
        )

        workflow.record_validation(
            "structure_validation",
            {
                "region": {
                    "x1": x1,
                    "y1": y1,
                    "z1": z1,
                    "x2": x2,
                    "y2": y2,
                    "z2": z2,
                },
                "resolution": resolution,
                "issues_found": result["issues_found"],
                "valid": result["structure_valid"],
            },
        )

        return [TextContent(type="text", text=output)]

    except Exception as e:
        logger_instance.error(f"Error in structure validation: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Structure validation failed: {str(e)}")]
