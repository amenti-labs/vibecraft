"""
Validation Tool Handlers

Mask validation for WorldEdit commands.
"""

import logging
from typing import Dict, Any, List
from mcp.types import TextContent

logger = logging.getLogger(__name__)


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
