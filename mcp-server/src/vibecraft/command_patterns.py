"""Shared regex patterns for parsing Minecraft command responses."""

import re

WORLDEDIT_VERSION_PATTERN = re.compile(r"WorldEdit.*?(\d+\.\d+\.\d+)")
PLAYER_POS_PATTERN = re.compile(r"\[([-\d.]+)d?,\s*([-\d.]+)d?,\s*([-\d.]+)d?\]")
PLAYER_ROT_PATTERN = re.compile(r"\[([-\d.]+)f?,\s*([-\d.]+)f?\]")
BLOCK_ID_PATTERN = re.compile(r'"minecraft:([^"]+)"')
BLOCK_STATE_PATTERN = re.compile(r"minecraft:([a-z0-9_/]+)(?:\{([^}]*)\})?")
DISTR_LINE_PATTERN = re.compile(r"([\d.]+)%\s+([a-z_:]+)\s+\((\d+)", re.IGNORECASE)
COUNT_BLOCKS_PATTERN = re.compile(r"(\d+)\s+block", re.IGNORECASE)
