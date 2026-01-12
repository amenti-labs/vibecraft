"""
Block State Utilities for VibeCraft

Utilities for querying and analyzing block states via command execution.
"""

import logging
from typing import Dict, Any, Optional

from .command_patterns import BLOCK_STATE_PATTERN

logger = logging.getLogger(__name__)


def fetch_block_state(executor, x: int, y: int, z: int) -> Optional[Dict[str, Any]]:
    """Fetch block state (id + properties) at coordinates via command execution.

    Note: This uses 'data get block' which only returns data for tile entities
    (blocks with NBT like chests, signs, etc.). For regular blocks, this returns None.
    The "target block is not a block entity" response is expected and handled silently.
    """
    try:
        result = executor.send_command(f"execute positioned {x} {y} {z} run data get block ~ ~ ~")
    except Exception as exc:
        # Only log actual errors, not expected "not a block entity" responses
        if "not a block entity" not in str(exc).lower():
            logger.error(f"Error querying block at ({x},{y},{z}): {exc}")
        return None

    if result is None:
        return None

    text = str(result)

    # "not a block entity" is expected for regular blocks - return None silently
    if "not a block entity" in text.lower() or "not an entity" in text.lower():
        return None

    match = BLOCK_STATE_PATTERN.search(text)
    if not match:
        return None

    block_id = match.group(1)
    props_str = match.group(2) or ""
    properties: Dict[str, str] = {}

    if props_str:
        for fragment in props_str.split(","):
            if ":" not in fragment:
                continue
            key, value = fragment.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"')
            properties[key] = value

    if properties:
        ordered = ",".join(f"{k}={properties[k]}" for k in sorted(properties))
        key_repr = f"{block_id}[{ordered}]"
    else:
        ordered = ""
        key_repr = block_id

    return {
        "namespaced_id": f"minecraft:{block_id}",
        "id": block_id,
        "properties": properties,
        "state": ordered,
        "key": key_repr,
        "raw": text.strip(),
    }


def block_is_air(block: Optional[Dict[str, Any]]) -> bool:
    """Check if a block is air (or None/missing)."""
    return block is None or block.get("id") == "air"
