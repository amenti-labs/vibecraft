"""
Minecraft items database loader.

This module loads the Minecraft items database from the context directory
and exposes it for use by tools and the main server.
"""

import json
import logging
from .paths import CONTEXT_DIR
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Context directory path


def load_minecraft_items() -> List[Dict[str, Any]]:
    """Load Minecraft items database from JSON file."""
    items_file = CONTEXT_DIR / "minecraft_items_filtered.json"

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


# Load items once at module import time
minecraft_items = load_minecraft_items()
