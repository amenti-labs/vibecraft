"""
Minecraft items database loader.

This module loads the Minecraft items database from the data directory
and exposes it for use by tools and the main server.
"""

import json
import logging
from .paths import DATA_DIR
from typing import List, Dict, Any, Set, Optional, Tuple

logger = logging.getLogger(__name__)


def load_minecraft_items() -> List[Dict[str, Any]]:
    """Load Minecraft items database from JSON file."""
    items_file = DATA_DIR / "minecraft_items_filtered.json"

    if not items_file.exists():
        logger.warning(f"Minecraft items file not found at {items_file}")
        return []

    try:
        with open(items_file) as f:
            items = json.load(f)
        logger.info(f"Loaded {len(items)} Minecraft items from database")
        return items
    except Exception as e:
        logger.error(f"Error loading Minecraft items: {e}")
        return []


def build_block_name_set(items: List[Dict[str, Any]]) -> Set[str]:
    """Build a set of valid block names for fast lookup."""
    names = set()
    for item in items:
        name = item.get("name", "")
        if name:
            names.add(name)
            # Also add with minecraft: prefix
            names.add(f"minecraft:{name}")
    return names


# Load items once at module import time
minecraft_items = load_minecraft_items()
valid_block_names = build_block_name_set(minecraft_items)


def parse_block_spec(block_spec: str) -> Tuple[str, str]:
    """Parse a block specification into base name and states/NBT.

    Examples:
        "stone" -> ("stone", "")
        "oak_stairs[facing=north]" -> ("oak_stairs", "[facing=north]")
        "minecraft:chest[facing=south]" -> ("chest", "[facing=south]")
        "oak_sign{Text1:'Hello'}" -> ("oak_sign", "{Text1:'Hello'}")
    """
    # Remove minecraft: prefix if present
    if block_spec.startswith("minecraft:"):
        block_spec = block_spec[10:]

    # Split on [ or { to separate block name from states/NBT
    bracket_idx = block_spec.find("[")
    nbt_idx = block_spec.find("{")

    # Find the earliest delimiter
    if bracket_idx == -1 and nbt_idx == -1:
        return block_spec, ""

    if bracket_idx == -1:
        return block_spec[:nbt_idx], block_spec[nbt_idx:]
    if nbt_idx == -1:
        return block_spec[:bracket_idx], block_spec[bracket_idx:]

    # Both present - use the earlier one
    split_idx = min(bracket_idx, nbt_idx)
    return block_spec[:split_idx], block_spec[split_idx:]


def is_valid_block(block_spec: str) -> bool:
    """Check if a block name is valid (exists in Minecraft).

    Handles block states like oak_stairs[facing=north].
    """
    if not block_spec or block_spec in (".", "_", "air", "minecraft:air"):
        return True

    base_name, _ = parse_block_spec(block_spec)
    return base_name in valid_block_names or f"minecraft:{base_name}" in valid_block_names


def validate_block(block_spec: str) -> Optional[str]:
    """Validate a block and return error message if invalid, None if valid."""
    if is_valid_block(block_spec):
        return None

    base_name, states = parse_block_spec(block_spec)

    # Try to suggest similar blocks
    suggestions = find_similar_blocks(base_name, limit=3)

    if suggestions:
        return f"Invalid block '{base_name}'. Did you mean: {', '.join(suggestions)}?"
    return f"Invalid block '{base_name}'. This block does not exist in Minecraft."


def find_similar_blocks(query: str, limit: int = 5) -> List[str]:
    """Find blocks with similar names to the query."""
    query_lower = query.lower()
    matches = []

    # Split query into parts (e.g., "cyan_terracotta_stairs" -> ["cyan", "terracotta", "stairs"])
    query_parts = query_lower.split("_")

    for item in minecraft_items:
        name = item.get("name", "").lower()

        # Check if any query part is in the name
        match_score = sum(1 for part in query_parts if part in name)
        if match_score > 0:
            matches.append((match_score, name))

    # Sort by match score descending, then alphabetically
    matches.sort(key=lambda x: (-x[0], x[1]))

    return [name for _, name in matches[:limit]]


def validate_blocks_in_palette(palette: Dict[str, str]) -> List[str]:
    """Validate all blocks in a schematic palette. Returns list of errors."""
    errors = []
    for symbol, block_spec in palette.items():
        if symbol in (".", "_", " "):
            continue
        error = validate_block(block_spec)
        if error:
            errors.append(f"Palette '{symbol}': {error}")
    return errors
