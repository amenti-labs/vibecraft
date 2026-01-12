"""
Schematic Building Tool

Implements declarative JSON-based building where the AI provides structured
schematic data and the server translates it to Minecraft commands.

COMPACT FORMAT (recommended - uses ~70% fewer tokens):
{
    "a": [x, y, z],                    # anchor (short key)
    "p": {"S": "stone", "P": "oak_planks"}, # palette (short key)
    "l": [                              # layers (short key)
        [0, "S*10|S P*8 S|S*10"],       # [y_offset, "row|row|row"]
        [1, "S . S~3|S*10"]             # ~N repeats previous pattern N times
    ]
}

Row format: "Symbol*count" for runs, "|" separates rows, "~N" repeats row N times

SHAPE PRIMITIVES (even more compact for common shapes):

2D Shapes (use in layers):
  - fill:WxD:S      -> solid rectangle (W wide, D deep, filled with S)
  - outline:WxD:S   -> hollow rectangle (border only)
  - frame:WxD:S:I   -> border S with interior I
  - walls:WxD:S     -> same as outline

Example: [0, "outline:10x8:S"] creates a 10x8 hollow floor

3D Shapes (use as "s" or "shape" key instead of layers):
  - box:WxHxD:S     -> hollow box (floor, walls, ceiling)
  - room:WxHxD:S:F  -> box with wall S and floor F

Example: {"a": [0,64,0], "p": {"S": "stone"}, "s": "box:10x5x10:S"}

VERBOSE FORMAT (backward compatible):
{
    "anchor": [x, y, z] or "player",
    "facing": "north" | "south" | "east" | "west",  # optional rotation
    "mode": "replace" | "keep" | "destroy",  # optional, default "replace"
    "palette": {
        "<symbol>": "<block_id>[block_states]{nbt}"
    },
    "layers": [
        {
            "y": <y_offset>,
            "grid": [
                ["<symbol>", "<symbol>", ...],  # Z rows (north to south)
                ...
            ]
        }
    ]
}

Grid convention:
- grid[row][col] = grid[z][x]
- Row 0 = north edge (-Z)
- Col 0 = west edge (-X)
- "." or "_" typically means air (skip)
"""

from typing import Dict, Any, List, Tuple, Optional
from mcp.types import TextContent
import logging
import json
import re

from ..minecraft_items_loader import validate_blocks_in_palette

logger = logging.getLogger(__name__)

# Common palette shortcuts that are auto-expanded
DEFAULT_PALETTE = {
    ".": "air",
    "_": "air",
    " ": "air",
}

# Pattern for run-length encoding: "Symbol*count" or just "Symbol"
RLE_PATTERN = re.compile(r"([A-Za-z_][A-Za-z0-9_]*|\.)(?:\*(\d+))?")


def expand_rle_row(row_str: str) -> List[str]:
    """
    Expand a run-length encoded row string into a list of symbols.

    Format: "S*3 P*2 ." expands to ["S", "S", "S", "P", "P", "."]

    Supports:
    - Simple symbols: "S P G" -> ["S", "P", "G"]
    - Run-length: "S*5" -> ["S", "S", "S", "S", "S"]
    - Mixed: "S*3 P . G*2" -> ["S", "S", "S", "P", ".", "G", "G"]
    """
    if not row_str or not row_str.strip():
        return []

    result = []
    # Split by whitespace to get tokens
    tokens = row_str.strip().split()

    for token in tokens:
        # Check for run-length encoding: Symbol*count
        if "*" in token:
            parts = token.split("*", 1)
            symbol = parts[0]
            try:
                count = int(parts[1])
            except (ValueError, IndexError):
                count = 1
            result.extend([symbol] * count)
        else:
            result.append(token)

    return result


# Shape primitive pattern: "shape:WxD:S" or "shape:WxD:S:I"
SHAPE_PATTERN = re.compile(
    r"^(fill|outline|frame|walls):(\d+)x(\d+):([A-Za-z_][A-Za-z0-9_]*)(?::([A-Za-z_][A-Za-z0-9_]*))?$"
)


def generate_shape_grid(shape_str: str) -> Optional[List[List[str]]]:
    """
    Generate a 2D grid from a shape primitive string.

    Supported shapes:
    - fill:WxD:S     - solid WxD rectangle filled with symbol S
    - outline:WxD:S  - hollow WxD rectangle, border is S, interior is air
    - frame:WxD:S:I  - WxD rectangle with border S and interior I
    - walls:WxD:S    - same as outline (for semantic clarity)

    Examples:
        "fill:5x3:S"     -> 5-wide, 3-deep solid grid of S
        "outline:10x8:B" -> 10x8 hollow rectangle, B border, . interior
        "frame:6x6:S:P"  -> 6x6 with S border and P interior

    Returns:
        2D grid (list of rows) or None if not a shape primitive
    """
    match = SHAPE_PATTERN.match(shape_str.strip())
    if not match:
        return None

    shape_type = match.group(1)
    width = int(match.group(2))
    depth = int(match.group(3))
    border_symbol = match.group(4)
    interior_symbol = match.group(5) if match.group(5) else "."

    if width < 1 or depth < 1:
        return None

    grid = []

    if shape_type == "fill":
        # Solid rectangle
        for _ in range(depth):
            grid.append([border_symbol] * width)

    elif shape_type in ("outline", "walls"):
        # Hollow rectangle - border only, interior is air
        for z in range(depth):
            if z == 0 or z == depth - 1:
                # Top or bottom row - full border
                grid.append([border_symbol] * width)
            else:
                # Middle row - border on sides only
                row = ["."] * width
                row[0] = border_symbol
                row[-1] = border_symbol
                grid.append(row)

    elif shape_type == "frame":
        # Rectangle with border and specified interior
        for z in range(depth):
            if z == 0 or z == depth - 1:
                # Top or bottom row - full border
                grid.append([border_symbol] * width)
            else:
                # Middle row - border on sides, interior in middle
                row = [interior_symbol] * width
                row[0] = border_symbol
                row[-1] = border_symbol
                grid.append(row)

    return grid


def parse_compact_layer(layer_data: Any) -> Tuple[int, List[List[str]]]:
    """
    Parse a compact layer format.

    Formats supported:
    - [y_offset, "row1|row2|row3"]  - pipe-separated rows with RLE
    - [y_offset, "row1|row2~3|row4"] - ~N repeats previous row N times
    - [y_offset, "fill:WxD:S"]      - shape primitive (fill, outline, frame, walls)
    - {"y": offset, "rows": ["row1", "row2"]} - list of RLE rows

    Shape primitives:
    - fill:WxD:S     - solid rectangle
    - outline:WxD:S  - hollow rectangle (border only)
    - frame:WxD:S:I  - border S with interior I
    - walls:WxD:S    - same as outline

    Returns:
        Tuple of (y_offset, grid as 2D list)
    """
    # Format: [y_offset, "row_string"]
    if isinstance(layer_data, list) and len(layer_data) == 2:
        y_offset = int(layer_data[0])
        row_string = str(layer_data[1])

        # Check if it's a shape primitive first
        shape_grid = generate_shape_grid(row_string)
        if shape_grid is not None:
            return y_offset, shape_grid

        # Split by | to get rows
        raw_rows = row_string.split("|")
        grid = []

        for raw_row in raw_rows:
            raw_row = raw_row.strip()
            if not raw_row:
                continue

            # Check for row repetition: "pattern~N"
            if "~" in raw_row:
                parts = raw_row.rsplit("~", 1)
                pattern = parts[0].strip()
                try:
                    repeat_count = int(parts[1])
                except (ValueError, IndexError):
                    repeat_count = 1

                expanded_row = expand_rle_row(pattern)
                for _ in range(repeat_count):
                    grid.append(expanded_row.copy())
            else:
                grid.append(expand_rle_row(raw_row))

        return y_offset, grid

    # Format: {"y": offset, "rows": [...]}
    if isinstance(layer_data, dict) and "rows" in layer_data:
        y_offset = layer_data.get("y", 0)
        rows = layer_data.get("rows", [])
        grid = []

        for row in rows:
            if isinstance(row, str):
                # Check for row repetition
                if "~" in row:
                    parts = row.rsplit("~", 1)
                    pattern = parts[0].strip()
                    try:
                        repeat_count = int(parts[1])
                    except (ValueError, IndexError):
                        repeat_count = 1

                    expanded_row = expand_rle_row(pattern)
                    for _ in range(repeat_count):
                        grid.append(expanded_row.copy())
                else:
                    grid.append(expand_rle_row(row))
            elif isinstance(row, list):
                # Already a list of symbols
                grid.append(row)
            elif isinstance(row, dict) and "r" in row:
                # {"r": "pattern", "n": count} format
                pattern = row.get("r", "")
                count = row.get("n", 1)
                expanded_row = expand_rle_row(pattern)
                for _ in range(count):
                    grid.append(expanded_row.copy())

        return y_offset, grid

    # Fallback: assume it's already in verbose format
    if isinstance(layer_data, dict):
        return layer_data.get("y", 0), layer_data.get("grid", [])

    return 0, []


def parse_y_range(y_spec: Any) -> List[int]:
    """
    Parse a Y specification which can be:
    - int: single Y value -> [y]
    - str "N": single Y value -> [N]
    - str "N-M": range -> [N, N+1, ..., M]

    Examples:
        0 -> [0]
        "1" -> [1]
        "1-3" -> [1, 2, 3]
        "0-5" -> [0, 1, 2, 3, 4, 5]
    """
    if isinstance(y_spec, int):
        return [y_spec]

    if isinstance(y_spec, str):
        if "-" in y_spec:
            parts = y_spec.split("-", 1)
            try:
                start = int(parts[0])
                end = int(parts[1])
                return list(range(start, end + 1))
            except ValueError:
                return [0]
        else:
            try:
                return [int(y_spec)]
            except ValueError:
                return [0]

    return [0]


# 3D shape pattern: "shape:WxHxD:S" or "shape:WxHxD:S:I"
SHAPE_3D_PATTERN = re.compile(
    r"^(box|room):(\d+)x(\d+)x(\d+):([A-Za-z_][A-Za-z0-9_]*)(?::([A-Za-z_][A-Za-z0-9_]*))?$"
)


def generate_3d_shape_layers(shape_str: str) -> Optional[List[Dict[str, Any]]]:
    """
    Generate layers for a 3D shape primitive.

    Supported 3D shapes:
    - box:WxHxD:S     - hollow box (floor, walls, ceiling)
    - room:WxHxD:S:F  - box with wall S and floor F

    Examples:
        "box:10x5x8:S"      -> 10 wide, 5 tall, 8 deep hollow box
        "room:12x4x12:B:P"  -> 12x4x12 room with B walls and P floor

    Returns:
        List of layer dicts or None if not a 3D shape
    """
    match = SHAPE_3D_PATTERN.match(shape_str.strip())
    if not match:
        return None

    shape_type = match.group(1)
    width = int(match.group(2))
    height = int(match.group(3))
    depth = int(match.group(4))
    wall_symbol = match.group(5)
    floor_symbol = match.group(6) if match.group(6) else wall_symbol

    if width < 1 or height < 1 or depth < 1:
        return None

    layers = []

    if shape_type in ("box", "room"):
        # Floor (y=0) - solid or with different material
        floor_grid = []
        for _ in range(depth):
            floor_grid.append([floor_symbol] * width)
        layers.append({"y": 0, "grid": floor_grid})

        # Walls (y=1 to height-2) - hollow
        if height > 2:
            wall_grid = []
            for z in range(depth):
                if z == 0 or z == depth - 1:
                    wall_grid.append([wall_symbol] * width)
                else:
                    row = ["."] * width
                    row[0] = wall_symbol
                    row[-1] = wall_symbol
                    wall_grid.append(row)

            for y in range(1, height - 1):
                # Deep copy for each layer
                layers.append({"y": y, "grid": [row.copy() for row in wall_grid]})

        # Ceiling (y=height-1) - solid
        if height > 1:
            ceiling_grid = []
            for _ in range(depth):
                ceiling_grid.append([wall_symbol] * width)
            layers.append({"y": height - 1, "grid": ceiling_grid})

    return layers


def normalize_schematic(schematic: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a schematic from compact or verbose format to standard format.

    Supports:
    - Short keys: "a" -> "anchor", "p" -> "palette", "l" -> "layers", "s" -> "shape"
    - Layer ranges: ["1-3", "pattern"] expands to layers at y=1, y=2, y=3
    - 3D shapes: "shape": "box:10x5x8:S" generates a hollow box
    """
    # Map short keys to long keys
    key_map = {
        "a": "anchor",
        "p": "palette",
        "l": "layers",
        "f": "facing",
        "m": "mode",
        "s": "shape",
    }

    normalized = {}

    for key, value in schematic.items():
        # Expand short keys
        long_key = key_map.get(key, key)
        normalized[long_key] = value

    # Handle 3D shape primitives - generates layers automatically
    if "shape" in normalized and "layers" not in normalized:
        shape_str = normalized["shape"]
        generated_layers = generate_3d_shape_layers(shape_str)
        if generated_layers:
            normalized["layers"] = generated_layers
        del normalized["shape"]  # Remove shape key after processing

    # Convert compact layers to standard format
    if "layers" in normalized:
        layers = normalized["layers"]
        standard_layers = []

        for layer in layers:
            # Check if it's compact format with potential Y range
            if isinstance(layer, list) and len(layer) == 2 and isinstance(layer[1], str):
                y_values = parse_y_range(layer[0])
                _, grid = parse_compact_layer([0, layer[1]])  # Parse with dummy y

                # Create a layer for each Y in the range
                for y_val in y_values:
                    # Deep copy grid for each layer
                    grid_copy = [row.copy() for row in grid]
                    standard_layers.append({"y": y_val, "grid": grid_copy})

            elif isinstance(layer, dict) and "rows" in layer:
                y_offset, grid = parse_compact_layer(layer)
                standard_layers.append({"y": y_offset, "grid": grid})
            else:
                # Already standard format
                standard_layers.append(layer)

        normalized["layers"] = standard_layers

    return normalized


# Direction rotations for block states
FACING_ROTATIONS = {
    "north": {"north": "north", "south": "south", "east": "east", "west": "west"},
    "south": {"north": "south", "south": "north", "east": "west", "west": "east"},
    "east": {"north": "east", "south": "west", "east": "south", "west": "north"},
    "west": {"north": "west", "south": "east", "east": "north", "west": "south"},
}

# Axis rotations
AXIS_ROTATIONS = {
    "north": {"x": "x", "y": "y", "z": "z"},
    "south": {"x": "x", "y": "y", "z": "z"},
    "east": {"x": "z", "y": "y", "z": "x"},
    "west": {"x": "z", "y": "y", "z": "x"},
}


def rotate_block_state(block: str, from_facing: str, to_facing: str) -> str:
    """
    Rotate block states when the entire build is rotated.

    Handles:
    - facing=north/south/east/west
    - axis=x/y/z
    - rotation=0-15 (for signs)
    - hinge=left/right (complex, simplified)
    """
    if from_facing == to_facing:
        return block

    # Parse block: block_id[states]{nbt}
    match = re.match(r"^([a-z_:]+)(\[.*?\])?(\{.*\})?$", block)
    if not match:
        return block

    block_id = match.group(1)
    states_str = match.group(2) or ""
    nbt_str = match.group(3) or ""

    if not states_str:
        return block

    # Parse states
    states_inner = states_str[1:-1]  # Remove [ ]
    states = {}
    for part in states_inner.split(","):
        if "=" in part:
            key, val = part.split("=", 1)
            states[key.strip()] = val.strip()

    # Calculate rotation steps (90 degrees each)
    directions = ["north", "east", "south", "west"]
    from_idx = directions.index(from_facing) if from_facing in directions else 0
    to_idx = directions.index(to_facing) if to_facing in directions else 0
    rotation_steps = (to_idx - from_idx) % 4

    # Rotate facing
    if "facing" in states and states["facing"] in directions:
        current_idx = directions.index(states["facing"])
        new_idx = (current_idx + rotation_steps) % 4
        states["facing"] = directions[new_idx]

    # Rotate axis
    if "axis" in states:
        axis = states["axis"]
        if rotation_steps in [1, 3]:  # 90 or 270 degrees
            if axis == "x":
                states["axis"] = "z"
            elif axis == "z":
                states["axis"] = "x"
            # y stays y

    # Rotate sign rotation (0-15, each step is 22.5 degrees)
    if "rotation" in states:
        try:
            rot = int(states["rotation"])
            # Each 90 degree turn = 4 rotation steps
            rot = (rot + rotation_steps * 4) % 16
            states["rotation"] = str(rot)
        except ValueError:
            pass

    # Rebuild states string
    if states:
        new_states = "[" + ",".join(f"{k}={v}" for k, v in states.items()) + "]"
    else:
        new_states = ""

    return f"{block_id}{new_states}{nbt_str}"


def rotate_grid(grid: List[List[str]], rotation_steps: int) -> List[List[str]]:
    """
    Rotate a 2D grid clockwise by 90 degree increments.

    Args:
        grid: 2D list of symbols
        rotation_steps: Number of 90-degree clockwise rotations (0-3)

    Returns:
        Rotated grid
    """
    rotation_steps = rotation_steps % 4

    if rotation_steps == 0:
        return grid

    result = grid
    for _ in range(rotation_steps):
        # Rotate 90 degrees clockwise: transpose then reverse each row
        rows = len(result)
        cols = len(result[0]) if rows > 0 else 0
        rotated = []
        for col in range(cols):
            new_row = []
            for row in range(rows - 1, -1, -1):
                if col < len(result[row]):
                    new_row.append(result[row][col])
                else:
                    new_row.append(".")
            rotated.append(new_row)
        result = rotated

    return result


def parse_schematic(
    schematic: Dict[str, Any], player_pos: Optional[Tuple[int, int, int]] = None
) -> Tuple[List[str], Dict[str, Any]]:
    """
    Parse a schematic JSON and generate Minecraft commands.

    Supports both compact and verbose formats - automatically detects and normalizes.

    Args:
        schematic: The schematic data (compact or verbose format)
        player_pos: Player position for "player" anchor

    Returns:
        Tuple of (commands list, stats dict)
    """
    # Normalize compact format to standard format
    schematic = normalize_schematic(schematic)

    commands = []
    stats = {
        "blocks_placed": 0,
        "layers": 0,
        "errors": [],
        "warnings": [],
    }

    # Parse anchor
    anchor = schematic.get("anchor", [0, 64, 0])
    if anchor == "player":
        if player_pos:
            anchor = list(player_pos)
        else:
            stats["errors"].append("anchor='player' but no player position available")
            return commands, stats

    if not isinstance(anchor, list) or len(anchor) != 3:
        stats["errors"].append(f"Invalid anchor: {anchor}")
        return commands, stats

    anchor_x, anchor_y, anchor_z = int(anchor[0]), int(anchor[1]), int(anchor[2])

    # Parse facing/rotation
    facing = schematic.get("facing", "north").lower()
    if facing not in ["north", "south", "east", "west"]:
        stats["warnings"].append(f"Unknown facing '{facing}', using 'north'")
        facing = "north"

    # Calculate rotation steps from north
    directions = ["north", "east", "south", "west"]
    rotation_steps = directions.index(facing) if facing in directions else 0

    # Parse mode
    mode = schematic.get("mode", "replace")
    if mode not in ["replace", "keep", "destroy"]:
        stats["warnings"].append(f"Unknown mode '{mode}', using 'replace'")
        mode = "replace"

    # Parse palette
    palette = {**DEFAULT_PALETTE}  # Start with defaults
    user_palette = schematic.get("palette", {})
    palette.update(user_palette)

    # Validate all blocks in palette
    block_errors = validate_blocks_in_palette(user_palette)
    if block_errors:
        stats["errors"].extend(block_errors)
        return commands, stats

    # Parse layers
    layers = schematic.get("layers", [])
    if not layers:
        stats["errors"].append("No layers defined")
        return commands, stats

    for layer in layers:
        y_offset = layer.get("y", 0)
        grid = layer.get("grid", [])

        if not grid:
            continue

        stats["layers"] += 1

        # Rotate grid if needed
        if rotation_steps > 0:
            grid = rotate_grid(grid, rotation_steps)

        # Process grid
        for z_idx, row in enumerate(grid):
            for x_idx, symbol in enumerate(row):
                # Skip empty/air symbols
                if symbol in [".", "_", " ", ""]:
                    continue

                # Look up block from palette
                block = palette.get(symbol)
                if block is None:
                    # Try as direct block ID
                    if ":" in symbol or symbol.replace("_", "").isalnum():
                        block = symbol
                    else:
                        stats["warnings"].append(
                            f"Unknown symbol '{symbol}' at layer y={y_offset}, z={z_idx}, x={x_idx}"
                        )
                        continue

                # Skip air blocks
                if block == "air":
                    continue

                # Rotate block states if needed
                if rotation_steps > 0:
                    block = rotate_block_state(block, "north", facing)

                # Calculate world coordinates
                # For rotation, we need to rotate the offset from anchor
                world_x = anchor_x + x_idx
                world_y = anchor_y + y_offset
                world_z = anchor_z + z_idx

                # Generate setblock command
                if mode == "replace":
                    cmd = f"/setblock {world_x} {world_y} {world_z} {block}"
                else:
                    cmd = f"/setblock {world_x} {world_y} {world_z} {block} {mode}"

                commands.append(cmd)
                stats["blocks_placed"] += 1

    return commands, stats


def optimize_commands(commands: List[str]) -> List[str]:
    """
    Optimize a list of setblock commands by combining adjacent blocks into fill commands.

    Uses a smart algorithm to find:
    1. 3D rectangular boxes (best optimization)
    2. 2D rectangular planes
    3. 1D lines

    Prioritizes larger regions first for maximum command reduction.
    """
    if len(commands) < 2:
        return commands

    # Parse commands into structured data
    blocks = []
    other_commands = []

    for cmd in commands:
        match = re.match(r"^/setblock\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(.+)$", cmd)
        if match:
            x, y, z, block = (
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3)),
                match.group(4),
            )
            blocks.append({"x": x, "y": y, "z": z, "block": block})
        else:
            other_commands.append(cmd)

    if not blocks:
        return other_commands

    # Group blocks by block type for efficient processing
    by_type: Dict[str, List[Dict]] = {}
    for b in blocks:
        block_type = b["block"]
        if block_type not in by_type:
            by_type[block_type] = []
        by_type[block_type].append(b)

    optimized = list(other_commands)

    # Process each block type separately
    for block_type, block_list in by_type.items():
        # Create a set of positions for fast lookup
        positions = {(b["x"], b["y"], b["z"]) for b in block_list}
        used = set()

        # Find rectangular regions using greedy algorithm
        # Sort by position for consistent results
        sorted_blocks = sorted(block_list, key=lambda b: (b["y"], b["z"], b["x"]))

        for b in sorted_blocks:
            pos = (b["x"], b["y"], b["z"])
            if pos in used:
                continue

            # Try to find the largest box starting from this position
            x1, y1, z1 = b["x"], b["y"], b["z"]

            # Find max extent in X direction
            x2 = x1
            while (x2 + 1, y1, z1) in positions and (x2 + 1, y1, z1) not in used:
                x2 += 1

            # Find max extent in Z direction (maintaining full X width)
            z2 = z1
            while True:
                # Check if entire row at z2+1 exists
                can_extend = True
                for x in range(x1, x2 + 1):
                    if (x, y1, z2 + 1) not in positions or (x, y1, z2 + 1) in used:
                        can_extend = False
                        break
                if can_extend:
                    z2 += 1
                else:
                    break

            # Find max extent in Y direction (maintaining full XZ plane)
            y2 = y1
            while True:
                # Check if entire plane at y2+1 exists
                can_extend = True
                for z in range(z1, z2 + 1):
                    for x in range(x1, x2 + 1):
                        if (x, y2 + 1, z) not in positions or (x, y2 + 1, z) in used:
                            can_extend = False
                            break
                    if not can_extend:
                        break
                if can_extend:
                    y2 += 1
                else:
                    break

            # Mark all positions in this box as used
            for y in range(y1, y2 + 1):
                for z in range(z1, z2 + 1):
                    for x in range(x1, x2 + 1):
                        used.add((x, y, z))

            # Calculate volume for stats
            volume = (x2 - x1 + 1) * (y2 - y1 + 1) * (z2 - z1 + 1)

            # Generate command
            if volume == 1:
                # Single block
                optimized.append(f"/setblock {x1} {y1} {z1} {block_type}")
            else:
                # Fill command
                optimized.append(f"/fill {x1} {y1} {z1} {x2} {y2} {z2} {block_type}")

    return optimized


def optimize_commands_aggressive(commands: List[str]) -> List[str]:
    """
    More aggressive optimization that tries multiple starting points
    to find better rectangle packings.

    Uses a scoring system to prioritize larger fills.
    """
    if len(commands) < 2:
        return commands

    # Parse commands
    blocks = []
    other_commands = []

    for cmd in commands:
        match = re.match(r"^/setblock\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(.+)$", cmd)
        if match:
            x, y, z, block = (
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3)),
                match.group(4),
            )
            blocks.append({"x": x, "y": y, "z": z, "block": block})
        else:
            other_commands.append(cmd)

    if not blocks:
        return other_commands

    # Group by block type
    by_type: Dict[str, set] = {}
    for b in blocks:
        block_type = b["block"]
        if block_type not in by_type:
            by_type[block_type] = set()
        by_type[block_type].add((b["x"], b["y"], b["z"]))

    optimized = list(other_commands)

    for block_type, positions in by_type.items():
        remaining = set(positions)

        while remaining:
            # Find the best rectangle (largest volume)
            best_rect = None
            best_volume = 0

            for pos in list(remaining)[:100]:  # Limit search for performance
                x1, y1, z1 = pos

                # Try to expand in all directions
                rect = find_max_rectangle(remaining, x1, y1, z1)
                volume = (rect[3] - rect[0] + 1) * (rect[4] - rect[1] + 1) * (rect[5] - rect[2] + 1)

                if volume > best_volume:
                    best_volume = volume
                    best_rect = rect

            if best_rect is None:
                break

            x1, y1, z1, x2, y2, z2 = best_rect

            # Remove positions from remaining
            for y in range(y1, y2 + 1):
                for z in range(z1, z2 + 1):
                    for x in range(x1, x2 + 1):
                        remaining.discard((x, y, z))

            # Generate command
            if best_volume == 1:
                optimized.append(f"/setblock {x1} {y1} {z1} {block_type}")
            else:
                optimized.append(f"/fill {x1} {y1} {z1} {x2} {y2} {z2} {block_type}")

    return optimized


def find_max_rectangle(
    positions: set, x1: int, y1: int, z1: int
) -> Tuple[int, int, int, int, int, int]:
    """Find the maximum rectangle starting from (x1, y1, z1)."""
    # Expand X
    x2 = x1
    while (x2 + 1, y1, z1) in positions:
        x2 += 1

    # Expand Z maintaining X width
    z2 = z1
    while all((x, y1, z2 + 1) in positions for x in range(x1, x2 + 1)):
        z2 += 1

    # Expand Y maintaining XZ plane
    y2 = y1
    while all((x, y2 + 1, z) in positions for z in range(z1, z2 + 1) for x in range(x1, x2 + 1)):
        y2 += 1

    return (x1, y1, z1, x2, y2, z2)


async def handle_build_schematic(
    arguments: Dict[str, Any], rcon, config, logger_instance
) -> List[TextContent]:
    """
    Handle the build_schematic tool.

    Accepts a JSON schematic and translates it to Minecraft commands.
    """
    schematic = arguments.get("schematic")
    preview_only = arguments.get("preview_only", False)
    optimize = arguments.get("optimize", True)
    description = arguments.get("description", "Building from schematic")

    # Parse schematic
    if isinstance(schematic, str):
        try:
            schematic = json.loads(schematic)
        except json.JSONDecodeError as e:
            return [TextContent(type="text", text=f"❌ Invalid JSON schematic: {e}")]

    if not isinstance(schematic, dict):
        return [TextContent(type="text", text="❌ Schematic must be a JSON object")]

    # Get player position if needed
    player_pos = None
    if schematic.get("anchor") == "player":
        try:
            result = rcon.send_command("/data get entity @p Pos")
            # Parse position from result
            match = re.search(r"\[(-?[\d.]+)d,\s*(-?[\d.]+)d,\s*(-?[\d.]+)d\]", result)
            if match:
                player_pos = (
                    int(float(match.group(1))),
                    int(float(match.group(2))),
                    int(float(match.group(3))),
                )
        except Exception as e:
            logger_instance.warning(f"Could not get player position: {e}")

    # Parse schematic to commands
    commands, stats = parse_schematic(schematic, player_pos)

    if stats["errors"]:
        error_msg = "\n".join(f"  - {e}" for e in stats["errors"])
        return [TextContent(type="text", text=f"❌ Schematic errors:\n{error_msg}")]

    if not commands:
        return [TextContent(type="text", text="❌ Schematic produced no commands")]

    # Optimize commands
    if optimize:
        original_count = len(commands)
        commands = optimize_commands(commands)
        stats["optimized_from"] = original_count
        stats["optimized_to"] = len(commands)

    # Preview mode
    if preview_only:
        result_lines = [
            f"🏗️ Schematic Preview: {description}",
            "",
            f"**Blocks:** {stats['blocks_placed']}",
            f"**Layers:** {stats['layers']}",
            f"**Commands:** {len(commands)}",
        ]

        if optimize and stats.get("optimized_from"):
            result_lines.append(
                f"**Optimized:** {stats['optimized_from']} → {stats['optimized_to']} commands"
            )

        if stats["warnings"]:
            result_lines.append("")
            result_lines.append("**Warnings:**")
            for w in stats["warnings"][:5]:
                result_lines.append(f"  ⚠️ {w}")

        if len(commands) <= 30:
            result_lines.append("")
            result_lines.append("**Commands:**")
            result_lines.append("```")
            result_lines.extend(commands)
            result_lines.append("```")
        else:
            result_lines.append("")
            result_lines.append(f"**Sample Commands (first 15 of {len(commands)}):**")
            result_lines.append("```")
            result_lines.extend(commands[:15])
            result_lines.append("...")
            result_lines.append("```")

        return [TextContent(type="text", text="\n".join(result_lines))]

    # Execute commands
    logger_instance.info(f"Executing schematic: {description} ({len(commands)} commands)")

    errors = []
    executed = 0

    for i, cmd in enumerate(commands):
        try:
            result = rcon.send_command(cmd)
            executed += 1

            # Check for errors
            if result and any(err in result.lower() for err in ["error", "unknown", "invalid"]):
                errors.append(f"Command {i + 1}: {result}")
        except Exception as e:
            errors.append(f"Command {i + 1}: {e}")

    # Build result
    result_lines = [
        f"🏗️ Built: {description}",
        "",
        f"**Blocks:** {stats['blocks_placed']}",
        f"**Commands:** {executed}/{len(commands)} executed",
    ]

    if stats["warnings"]:
        result_lines.append("")
        result_lines.append("**Warnings:**")
        for w in stats["warnings"][:3]:
            result_lines.append(f"  ⚠️ {w}")

    if errors:
        result_lines.append("")
        result_lines.append("**Errors:**")
        for e in errors[:5]:
            result_lines.append(f"  ❌ {e}")
        if len(errors) > 5:
            result_lines.append(f"  ... and {len(errors) - 5} more")
    else:
        result_lines.append("")
        result_lines.append("✅ Build completed successfully!")

    return [TextContent(type="text", text="\n".join(result_lines))]
