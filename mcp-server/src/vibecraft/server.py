#!/usr/bin/env python3
"""
VibeCraft MCP Server - Main Server Implementation
Exposes ALL WorldEdit commands via MCP for AI-powered building in Minecraft
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Sequence, List

from mcp.server import Server
from mcp.types import Resource, Tool, TextContent
import mcp.server.stdio

from .config import load_config, VibeCraftConfig
from .client_bridge import ClientBridge
from .workflow import BuildWorkflowCoordinator
from .resources import (
    PATTERN_SYNTAX_GUIDE,
    MASK_SYNTAX_GUIDE,
    EXPRESSION_SYNTAX_GUIDE,
    COORDINATE_GUIDE,
    COMMON_WORKFLOWS,
    PLAYER_CONTEXT_WARNING,
)
from .paths import DATA_DIR
from .tools import TOOL_REGISTRY

# Logger will be initialized in setup_logging()
logger = logging.getLogger("vibecraft")


def setup_logging() -> Path:
    """
    Configure logging to both console and file.
    Returns the log file path.
    Should be called from main() before any logging operations.
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    # Create log file with timestamp
    log_file = log_dir / f"vibecraft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    # Configure logging to both console and file
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),  # Console output (for when run manually)
            logging.FileHandler(log_file),  # File output (always available)
        ],
    )

    logger.info(f"Logging to file: {log_file}")
    return log_file


# Import Minecraft items data from loader module

# Initialize server
app = Server("vibecraft")

# Global config and execution engine (initialized in main)
config: VibeCraftConfig
rcon: ClientBridge


# Cached context loaders ----------------------------------------------------


def _load_json_list(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        logger.warning(f"Context file not found: {path}")
        return []

    try:
        with open(path, "r") as handle:
            data = json.load(handle)
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "patterns" in data:
                # For pattern files that store entries under a dict key
                return list(data["patterns"].values())
            logger.warning(f"Unexpected data format in {path}")
    except Exception as exc:  # pragma: no cover - logging path for runtime
        logger.error(f"Unable to load context file {path}: {exc}")
    return []


def load_furniture_layouts() -> List[Dict[str, Any]]:
    return _load_json_list(DATA_DIR / "minecraft_furniture_layouts.json")


def load_furniture_catalog() -> List[Dict[str, Any]]:
    return _load_json_list(DATA_DIR / "minecraft_furniture_catalog.json")


def load_structured_patterns() -> List[Dict[str, Any]]:
    return _load_json_list(DATA_DIR / "building_patterns_structured.json")


workflow_state_path = Path(__file__).parent.parent.parent / "logs" / "workflow_state.json"
workflow = BuildWorkflowCoordinator(workflow_state_path)


def format_terrain_analysis(result: Dict[str, Any]) -> str:
    """Format terrain analysis results for display."""
    output = []

    # Title
    output.append("🗺️ **Terrain Analysis Report**\n")

    # Summary first (natural language)
    if "summary" in result:
        output.append(result["summary"])
        output.append("\n---\n")

    # Region information
    region = result.get("region", {})
    output.append("**Region Details:**")
    output.append(
        f"- Coordinates: ({region['min'][0]}, {region['min'][1]}, {region['min'][2]}) to ({region['max'][0]}, {region['max'][1]}, {region['max'][2]})"
    )
    output.append(
        f"- Dimensions: {region['dimensions'][0]}×{region['dimensions'][1]}×{region['dimensions'][2]} blocks (W×H×D)"
    )
    output.append(f"- Total volume: {region.get('total_blocks', 0):,} blocks")
    output.append(
        f"- Samples collected: {region.get('samples_taken', 0):,} (resolution: {region.get('resolution', 1)})"
    )
    output.append("")

    # Elevation statistics
    elevation = result.get("elevation", {})
    if elevation and "error" not in elevation:
        output.append("**Elevation Analysis:**")
        output.append(f"- Terrain type: {elevation.get('terrain_type', 'Unknown')}")
        output.append(
            f"- Height range: Y={elevation.get('min_y')} to Y={elevation.get('max_y')} ({elevation.get('range')} blocks)"
        )
        output.append(f"- Average height: Y={elevation.get('avg_y')}")
        output.append(f"- Variation (std dev): {elevation.get('std_dev')} blocks")
        output.append(f"- Slope index: {elevation.get('slope_index')}")
        output.append("")

    # Block composition
    composition = result.get("composition", {})
    if composition:
        output.append("**Block Composition:**")
        output.append(f"- Unique block types: {composition.get('unique_blocks', 0)}")

        top_blocks = composition.get("top_blocks", [])
        if top_blocks:
            output.append("- Top 5 blocks:")
            for block_info in top_blocks[:5]:
                output.append(
                    f"  - {block_info['block']}: {block_info['count']} ({block_info['percentage']}%)"
                )

        liquids = composition.get("liquids", {})
        if liquids.get("count", 0) > 0:
            output.append(f"- Liquids: {liquids['count']} blocks ({liquids['percentage']}%)")

        vegetation = composition.get("vegetation", {})
        if vegetation.get("count", 0) > 0:
            output.append(
                f"- Vegetation: {vegetation['count']} blocks ({vegetation['percentage']}%)"
            )

        cavities = composition.get("air_cavities", {})
        if cavities.get("count", 0) > 0:
            output.append(
                f"- Air cavities (caves): {cavities['count']} blocks ({cavities['percentage']}%)"
            )

        output.append("")

    # Biomes
    biomes = result.get("biomes", {})
    if biomes.get("detected"):
        output.append("**Biome Distribution:**")
        biome_list = biomes.get("biomes", [])
        for biome_info in biome_list:
            output.append(
                f"- {biome_info['biome']}: {biome_info['count']} samples ({biome_info['percentage']}%)"
            )
        output.append("")
    elif not biomes.get("detected"):
        output.append(
            "**Biomes:** Detection not available (use WorldEdit //biomeinfo for biome data)"
        )
        output.append("")

    # Hazards
    hazards = result.get("hazards", [])
    if hazards:
        output.append("⚠️ **Hazards Detected:**")
        for hazard in hazards:
            severity_icon = (
                "🔴"
                if hazard.get("severity") == "high"
                else "🟡"
                if hazard.get("severity") == "medium"
                else "🟢"
            )
            output.append(
                f"{severity_icon} **{hazard['type']}** ({hazard.get('severity', 'unknown')} severity)"
            )
            if "count" in hazard:
                output.append(
                    f"   - Affected blocks: {hazard['count']} ({hazard.get('percentage', 0)}%)"
                )
            if "details" in hazard:
                output.append(f"   - Details: {hazard['details']}")
            if "recommendation" in hazard:
                output.append(f"   - 💡 {hazard['recommendation']}")
        output.append("")
    else:
        output.append("✅ **No hazards detected** - area appears safe for building")
        output.append("")

    # Opportunities
    opportunities = result.get("opportunities", [])
    if opportunities:
        output.append("🌟 **Building Opportunities:**")
        for opp in opportunities:
            quality_icon = (
                "⭐⭐⭐"
                if opp.get("quality") == "excellent"
                else "⭐⭐"
                if opp.get("quality") == "good"
                else "⭐"
            )
            output.append(
                f"{quality_icon} **{opp['type']}** ({opp.get('quality', 'fair')} quality)"
            )
            output.append(f"   - {opp.get('description', '')}")
            if "use_cases" in opp:
                output.append(f"   - 💡 Ideal for: {opp['use_cases']}")
        output.append("")

    # JSON data reference
    output.append("---")
    output.append("💾 **Full JSON data available in result object for programmatic use**")

    return "\n".join(output)


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available documentation resources for AI"""
    return [
        Resource(
            uri="vibecraft://guide/patterns",
            name="WorldEdit Pattern Syntax Guide",
            mimeType="text/markdown",
            description="Complete guide to WorldEdit pattern syntax with examples",
        ),
        Resource(
            uri="vibecraft://guide/masks",
            name="WorldEdit Mask Syntax Guide",
            mimeType="text/markdown",
            description="Complete guide to WorldEdit mask syntax with examples",
        ),
        Resource(
            uri="vibecraft://guide/expressions",
            name="WorldEdit Expression Syntax Guide",
            mimeType="text/markdown",
            description="Complete guide to WorldEdit expression syntax with examples",
        ),
        Resource(
            uri="vibecraft://guide/coordinates",
            name="WorldEdit Coordinate System Guide",
            mimeType="text/markdown",
            description="Guide to coordinate systems and console command syntax",
        ),
        Resource(
            uri="vibecraft://guide/workflows",
            name="Common WorldEdit Workflows",
            mimeType="text/markdown",
            description="Common building workflows and command sequences",
        ),
        Resource(
            uri="vibecraft://guide/player-context",
            name="Player Context Commands Warning",
            mimeType="text/markdown",
            description="Important information about commands that require player context",
        ),
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read documentation resource by URI"""
    resource_map = {
        "vibecraft://guide/patterns": PATTERN_SYNTAX_GUIDE,
        "vibecraft://guide/masks": MASK_SYNTAX_GUIDE,
        "vibecraft://guide/expressions": EXPRESSION_SYNTAX_GUIDE,
        "vibecraft://guide/coordinates": COORDINATE_GUIDE,
        "vibecraft://guide/workflows": COMMON_WORKFLOWS,
        "vibecraft://guide/player-context": PLAYER_CONTEXT_WARNING,
    }

    if uri not in resource_map:
        raise ValueError(f"Unknown resource URI: {uri}")

    return resource_map[uri]


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools for AI to use"""
    from .tool_schemas import get_tool_schemas

    return get_tool_schemas()


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls from AI"""

    try:
        # Look up tool handler in registry
        handler = TOOL_REGISTRY.get(name)

        if handler is None:
            return [TextContent(type="text", text=f"❌ Unknown tool: {name}")]

        # Call handler with standard parameters
        return await handler(arguments, rcon, config, logger)

    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]


async def main() -> None:
    """Main entry point for the MCP server"""
    global config, rcon

    # Initialize logging first
    setup_logging()

    # Load configuration
    config = load_config()

    logger.info("=" * 60)
    logger.info("🎮 VibeCraft MCP Server Starting...")
    logger.info("=" * 60)
    logger.info(
        f"Client Bridge: ws://{config.client_host}:{config.client_port}{config.client_path}"
    )
    logger.info(f"Safety Checks: {'Enabled' if config.enable_safety_checks else 'Disabled'}")
    logger.info(
        f"Dangerous Commands: {'Allowed' if config.allow_dangerous_commands else 'Blocked'}"
    )

    # Initialize client bridge
    rcon = ClientBridge(config)

    # Test connection
    logger.info("Testing client bridge connection...")
    if rcon.test_connection():
        logger.info("✅ Client bridge connection successful!")

        # Detect WorldEdit version if enabled
        if config.enable_version_detection:
            version = rcon.detect_worldedit_version()
            if version:
                logger.info(f"✅ WorldEdit {version} detected")
            else:
                logger.warning("⚠️ Could not detect WorldEdit version")
    else:
        logger.warning("⚠️ Client bridge test failed. Is the Fabric client mod running?")
        logger.warning(
            "   The MCP server will start anyway, but commands will fail until connection is established."
        )

    logger.info("=" * 60)
    logger.info("🚀 VibeCraft MCP Server Ready!")
    logger.info("   AI can now build in Minecraft using WorldEdit commands")
    logger.info("=" * 60)

    # Run the MCP server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
