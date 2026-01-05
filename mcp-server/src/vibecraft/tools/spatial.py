"""
Spatial Analysis Tool Handlers

Handles spatial awareness scanning for precise block placement.
"""

import json
import logging
from typing import Dict, Any, List
from mcp.types import TextContent

logger = logging.getLogger(__name__)


async def handle_spatial_awareness_scan(
    arguments: Dict[str, Any], rcon, config, logger_instance: logging.Logger
) -> List[TextContent]:
    """
    Handle spatial_awareness_scan tool - Advanced V2 spatial analysis.

    Args:
        arguments: Tool arguments (center_x, center_y, center_z, radius, detail_level)
        rcon: RCON manager instance
        config: Server configuration
        logger_instance: Logger instance

    Returns:
        List of TextContent responses
    """
    from ..spatial_analyzer import SpatialAnalyzerV2

    # Get parameters
    center_x = arguments.get("center_x")
    center_y = arguments.get("center_y")
    center_z = arguments.get("center_z")
    radius = arguments.get("radius", 5)
    detail_level = arguments.get("detail_level", "medium")

    # Validate required parameters
    if center_x is None or center_y is None or center_z is None:
        return [
            TextContent(type="text", text="❌ Error: center_x, center_y, and center_z are required")
        ]

    # Create spatial analyzer V2
    analyzer = SpatialAnalyzerV2(rcon)

    try:
        logger_instance.info(
            f"Starting spatial awareness scan V2: center=({center_x},{center_y},{center_z}), "
            f"radius={radius}, detail={detail_level}"
        )

        # Perform analysis
        result = analyzer.analyze_area(
            center_x=center_x,
            center_y=center_y,
            center_z=center_z,
            radius=radius,
            detail_level=detail_level,
        )

        # Use the built-in summary from the analyzer
        summary_text = result.get("summary", "Analysis complete")

        # Add JSON data at the end
        full_text = summary_text + "\n\n**📊 Complete Analysis Data (JSON)**:\n```json\n"
        full_text += json.dumps(result, indent=2)
        full_text += "\n```"

        logger_instance.info("Spatial awareness scan V2 complete")
        return [TextContent(type="text", text=full_text)]

    except Exception as e:
        logger_instance.error(f"Error in spatial_awareness_scan: {e}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Spatial awareness scan failed: {e}")]
