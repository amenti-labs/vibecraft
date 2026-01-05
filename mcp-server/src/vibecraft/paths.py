"""
Path Configuration for VibeCraft

Centralized path management to avoid duplication and inconsistency.
All paths relative to the VibeCraft project root.
"""

from pathlib import Path

# Project root directory (vibecraft/)
# From this file: src/vibecraft/paths.py -> ../../.. -> vibecraft/
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Context directory containing JSON data files
CONTEXT_DIR = PROJECT_ROOT / "context"

# Schemas directory containing .schem files
SCHEMAS_DIR = PROJECT_ROOT / "schemas"

# MCP server source directory
SRC_DIR = PROJECT_ROOT / "mcp-server" / "src"


def get_context_file(filename: str) -> Path:
    """
    Get path to a context file.

    Args:
        filename: Name of file in context/ directory

    Returns:
        Full path to context file

    Example:
        >>> get_context_file("building_patterns_complete.json")
        Path('/Users/.../vibecraft/context/building_patterns_complete.json')
    """
    return CONTEXT_DIR / filename


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
