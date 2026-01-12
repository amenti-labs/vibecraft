"""
Client Vision and Context Tools

Tools that leverage the Fabric client mod's enhanced capabilities:
- Screenshot capture
- Heightmap analysis
- Player context (raycast, position)
- Entity detection
"""

import logging
from typing import Any, Dict, List

from mcp.types import TextContent

from ..config import VibeCraftConfig
from ..client_bridge import ClientBridge
from ..exceptions import ClientBridgeProtocolError

logger = logging.getLogger(__name__)


# ========== Screenshot Tools ==========


async def handle_capture_screenshot(
    arguments: Dict[str, Any],
    rcon: ClientBridge,
    config: VibeCraftConfig,
    logger_instance: logging.Logger,
) -> List[TextContent]:
    """Capture a screenshot from the Minecraft client."""
    max_width = arguments.get("max_width", 1920)
    max_height = arguments.get("max_height", 1080)

    try:
        result = await rcon.capture_screenshot_async(max_width, max_height)

        if "error" in result:
            return [TextContent(type="text", text=f"Screenshot failed: {result['error']}")]

        # Return metadata (not the full base64 image for token efficiency)
        width = result.get("width", 0)
        height = result.get("height", 0)
        original_w = result.get("original_width", 0)
        original_h = result.get("original_height", 0)

        response = {
            "success": True,
            "width": width,
            "height": height,
            "original_width": original_w,
            "original_height": original_h,
            "player_position": result.get("player_position"),
            "player_rotation": result.get("player_rotation"),
            # Include image data for vision models
            "image": result.get("image"),
        }

        return [TextContent(type="text", text=str(response))]

    except ClientBridgeProtocolError as e:
        return [TextContent(type="text", text=f"Screenshot error: {e}")]
    except Exception as e:
        logger_instance.exception("Screenshot capture failed")
        return [TextContent(type="text", text=f"Screenshot failed: {e}")]


# ========== Heightmap Tools ==========


async def handle_get_heightmap(
    arguments: Dict[str, Any],
    rcon: ClientBridge,
    config: VibeCraftConfig,
    logger_instance: logging.Logger,
) -> List[TextContent]:
    """Get heightmap for a rectangular area."""
    x1 = arguments.get("x1", 0)
    z1 = arguments.get("z1", 0)
    x2 = arguments.get("x2", 0)
    z2 = arguments.get("z2", 0)

    try:
        result = await rcon.get_heightmap_async(x1, z1, x2, z2)

        if "error" in result:
            return [TextContent(type="text", text=f"Heightmap failed: {result['error']}")]

        return [TextContent(type="text", text=str(result))]

    except ClientBridgeProtocolError as e:
        return [TextContent(type="text", text=f"Heightmap error: {e}")]
    except Exception as e:
        logger_instance.exception("Heightmap failed")
        return [TextContent(type="text", text=f"Heightmap failed: {e}")]


# ========== Player Context Tools ==========


async def handle_get_player_context(
    arguments: Dict[str, Any],
    rcon: ClientBridge,
    config: VibeCraftConfig,
    logger_instance: logging.Logger,
) -> List[TextContent]:
    """Get detailed player context including position, rotation, and raycast target."""
    reach = arguments.get("reach", 128.0)

    try:
        result = await rcon.get_player_context_async(reach)

        if "error" in result:
            return [TextContent(type="text", text=f"Player context failed: {result['error']}")]

        return [TextContent(type="text", text=str(result))]

    except ClientBridgeProtocolError as e:
        return [TextContent(type="text", text=f"Player context error: {e}")]
    except Exception as e:
        logger_instance.exception("Player context failed")
        return [TextContent(type="text", text=f"Player context failed: {e}")]


async def handle_get_nearby_entities(
    arguments: Dict[str, Any],
    rcon: ClientBridge,
    config: VibeCraftConfig,
    logger_instance: logging.Logger,
) -> List[TextContent]:
    """Get entities near the player."""
    radius = arguments.get("radius", 32.0)

    try:
        result = await rcon.get_nearby_entities_async(radius)

        if "error" in result:
            return [TextContent(type="text", text=f"Nearby entities failed: {result['error']}")]

        return [TextContent(type="text", text=str(result))]

    except ClientBridgeProtocolError as e:
        return [TextContent(type="text", text=f"Nearby entities error: {e}")]
    except Exception as e:
        logger_instance.exception("Nearby entities failed")
        return [TextContent(type="text", text=f"Nearby entities failed: {e}")]


# ========== Region Scanning Tools ==========


async def handle_scan_region(
    arguments: Dict[str, Any],
    rcon: ClientBridge,
    config: VibeCraftConfig,
    logger_instance: logging.Logger,
) -> List[TextContent]:
    """Scan blocks in a rectangular region using the client's chunk cache."""
    x1 = arguments.get("x1", 0)
    y1 = arguments.get("y1", 0)
    z1 = arguments.get("z1", 0)
    x2 = arguments.get("x2", 0)
    y2 = arguments.get("y2", 0)
    z2 = arguments.get("z2", 0)
    include_states = arguments.get("include_states", False)

    try:
        result = await rcon.scan_region_async(x1, y1, z1, x2, y2, z2, include_states)

        if "error" in result:
            return [TextContent(type="text", text=f"Region scan failed: {result['error']}")]

        return [TextContent(type="text", text=str(result))]

    except ClientBridgeProtocolError as e:
        return [TextContent(type="text", text=f"Region scan error: {e}")]
    except Exception as e:
        logger_instance.exception("Region scan failed")
        return [TextContent(type="text", text=f"Region scan failed: {e}")]


# ========== Palette Analysis Tools ==========


async def handle_analyze_palette(
    arguments: Dict[str, Any],
    rcon: ClientBridge,
    config: VibeCraftConfig,
    logger_instance: logging.Logger,
) -> List[TextContent]:
    """Analyze block distribution in a spherical area around a point."""
    x = arguments.get("x", 0)
    y = arguments.get("y", 0)
    z = arguments.get("z", 0)
    radius = arguments.get("radius", 16)

    try:
        result = await rcon.analyze_palette_async(x, y, z, radius)

        if "error" in result:
            return [TextContent(type="text", text=f"Palette analysis failed: {result['error']}")]

        return [TextContent(type="text", text=str(result))]

    except ClientBridgeProtocolError as e:
        return [TextContent(type="text", text=f"Palette analysis error: {e}")]
    except Exception as e:
        logger_instance.exception("Palette analysis failed")
        return [TextContent(type="text", text=f"Palette analysis failed: {e}")]


async def handle_analyze_palette_region(
    arguments: Dict[str, Any],
    rcon: ClientBridge,
    config: VibeCraftConfig,
    logger_instance: logging.Logger,
) -> List[TextContent]:
    """Analyze block distribution in a rectangular region."""
    x1 = arguments.get("x1", 0)
    y1 = arguments.get("y1", 0)
    z1 = arguments.get("z1", 0)
    x2 = arguments.get("x2", 0)
    y2 = arguments.get("y2", 0)
    z2 = arguments.get("z2", 0)

    try:
        result = await rcon.analyze_palette_region_async(x1, y1, z1, x2, y2, z2)

        if "error" in result:
            return [TextContent(type="text", text=f"Palette region failed: {result['error']}")]

        return [TextContent(type="text", text=str(result))]

    except ClientBridgeProtocolError as e:
        return [TextContent(type="text", text=f"Palette region error: {e}")]
    except Exception as e:
        logger_instance.exception("Palette region failed")
        return [TextContent(type="text", text=f"Palette region failed: {e}")]
