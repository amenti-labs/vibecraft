"""
Path Configuration for VibeCraft

Centralized path management to avoid duplication and inconsistency.
All paths relative to the VibeCraft project root.
"""

from pathlib import Path

# Project root directory (vibecraft/)
# From this file: src/vibecraft/paths.py -> ../../.. -> vibecraft/
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# MCP server root directory
MCP_SERVER_ROOT = Path(__file__).parent.parent.parent

# Data directory containing JSON data files (loaded by MCP server)
DATA_DIR = MCP_SERVER_ROOT / "data"

# Schemas directory containing .schem files
SCHEMAS_DIR = PROJECT_ROOT / "schemas"

# MCP server source directory
SRC_DIR = MCP_SERVER_ROOT / "src"


def get_data_file(filename: str) -> Path:
    """
    Get path to a data file.

    Args:
        filename: Name of file in data/ directory

    Returns:
        Full path to data file

    Example:
        >>> get_data_file("building_patterns_complete.json")
        Path('/Users/.../vibecraft/mcp-server/data/building_patterns_complete.json')
    """
    return DATA_DIR / filename


def get_schema_file(filename: str) -> Path:
    """
    Get path to a schematic file.

    Args:
        filename: Name of .schem file

    Returns:
        Full path to schematic file

    Example:
        >>> get_schema_file("modern_villa_1.schem")
        Path('/Users/.../vibecraft/schemas/modern_villa_1.schem')
    """
    if not filename.endswith(".schem"):
        filename += ".schem"
    return SCHEMAS_DIR / filename
