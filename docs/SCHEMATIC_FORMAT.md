# VibeCraft Schematic Format

This document describes the JSON schematic format used by the `build_schematic` tool for declarative building in Minecraft.

## Overview

The schematic format allows AI agents to define structures as JSON data, which the server translates into Minecraft commands. It supports:

- **Layer-by-layer building** with Y-offset control
- **Block palettes** for symbol-to-block mapping
- **Rotation** to face structures in any cardinal direction
- **Shape primitives** for common geometric patterns
- **Compact syntax** to minimize token usage

## Format Variants

### Compact Format (Recommended)

Uses short keys and RLE (run-length encoding) for ~70% fewer tokens:

```json
{
  "a": [100, 64, 200],
  "p": {"S": "stone_bricks", "P": "oak_planks", "G": "glass_pane"},
  "l": [
    [0, "S*10|S P*8 S~8|S*10"],
    ["1-3", "S*10|S .*8 S|G .*8 G~3|S .*8 S|S*10"],
    [4, "S*10~10"]
  ]
}
```

### Verbose Format (Backward Compatible)

Uses full key names and explicit grids:

```json
{
  "anchor": [100, 64, 200],
  "facing": "north",
  "mode": "replace",
  "palette": {
    "S": "stone_bricks",
    "P": "oak_planks"
  },
  "layers": [
    {
      "y": 0,
      "grid": [
        ["S", "S", "S", "S", "S"],
        ["S", "P", "P", "P", "S"],
        ["S", "P", "P", "P", "S"],
        ["S", "P", "P", "P", "S"],
        ["S", "S", "S", "S", "S"]
      ]
    }
  ]
}
```

## Key Reference

| Short | Full | Type | Description |
|-------|------|------|-------------|
| `a` | `anchor` | `[x, y, z]` or `"player"` | Build origin point |
| `p` | `palette` | `{symbol: block}` | Symbol-to-block mapping |
| `l` | `layers` | `array` | Layer definitions |
| `f` | `facing` | `string` | Rotation: `"north"`, `"south"`, `"east"`, `"west"` |
| `m` | `mode` | `string` | Build mode: `"replace"`, `"keep"`, `"destroy"` |
| `s` | `shape` | `string` | 3D shape primitive (alternative to layers) |

## Anchor

The anchor defines where the structure's origin (0,0,0) maps to in the world.

```json
"a": [100, 64, 200]      // Absolute coordinates
"anchor": "player"       // Player's current position
```

**Important:** The anchor is the **northwest corner** (minimum X, minimum Z) at the specified Y level.

## Palette

Maps single-character or short symbols to Minecraft block IDs:

```json
"p": {
  "S": "stone_bricks",
  "P": "oak_planks",
  "G": "glass_pane",
  "Dl": "oak_door[facing=south,half=lower,hinge=left]",
  "Du": "oak_door[facing=south,half=upper,hinge=left]",
  ".": "air",
  "_": "air"
}
```

### Block Specifications

Blocks can include:
- **Simple name:** `"stone"`
- **With namespace:** `"minecraft:stone"`
- **Block states:** `"oak_stairs[facing=north,half=bottom]"`
- **NBT data:** `"chest[facing=north]{Items:[{Slot:0b,id:\"diamond\",Count:64b}]}"`

### Reserved Symbols

- `.` (dot) - Air (skip placement)
- `_` (underscore) - Air (skip placement)
- ` ` (space) - Air (skip placement)

## Layers

Layers define the structure from bottom to top. Each layer specifies a Y offset and a 2D grid.

### Verbose Layer Format

```json
{
  "y": 0,
  "grid": [
    ["S", "S", "S"],    // Row 0 (north edge, -Z)
    ["S", ".", "S"],    // Row 1
    ["S", "S", "S"]     // Row 2 (south edge, +Z)
  ]
}
```

### Compact Layer Format

```json
[y_offset, "row|row|row"]
```

Example:
```json
[0, "S*3|S . S|S*3"]    // Same as verbose example above
```

### Y-Range Syntax

Apply the same pattern to multiple Y levels:

```json
["1-3", "S*10|S .*8 S~8|S*10"]   // Layers at y=1, y=2, y=3
```

## Run-Length Encoding (RLE)

Compact row syntax uses RLE to reduce repetition:

| Syntax | Meaning | Example |
|--------|---------|---------|
| `S` | Single symbol | `S` = one stone |
| `S*5` | Repeat symbol N times | `S*5` = five stones |
| `S P G` | Space-separated symbols | Three different blocks |
| `~N` | Repeat entire row N times | `S .*3 S~5` = row repeated 5 times |
| `\|` | Row separator | `row1\|row2\|row3` |

### RLE Examples

```
"S*10"              → 10 stone blocks
"S P*3 S"           → stone, 3 planks, stone (5 blocks)
"S*10|S .*8 S~8|S*10"  → 10-wide floor with border
```

The `~N` suffix repeats the **entire preceding row pattern** N times:
```
"S P*3 S~5"  →  Row "S P P P S" repeated 5 times
```

## Shape Primitives

Shape primitives provide ultra-compact syntax for common geometric patterns.

### 2D Shapes (Use in Layers)

| Primitive | Description | Parameters |
|-----------|-------------|------------|
| `fill:WxD:S` | Solid rectangle | Width x Depth, filled with S |
| `outline:WxD:S` | Hollow rectangle | Width x Depth, border only |
| `frame:WxD:S:I` | Framed rectangle | Border S, interior I |
| `walls:WxD:S` | Same as outline | For semantic clarity |

**Examples:**

```json
[0, "fill:10x8:S"]       // 10x8 solid floor
[0, "outline:12x12:B"]   // 12x12 hollow rectangle
["1-3", "walls:10x8:S"]  // Walls for 3 layers
[0, "frame:8x8:S:P"]     // Stone border, plank interior
```

### 3D Shapes (Use as `"s"` Key)

3D shapes generate multiple layers automatically:

| Primitive | Description | Parameters |
|-----------|-------------|------------|
| `box:WxHxD:S` | Hollow box | Width x Height x Depth |
| `room:WxHxD:W:F` | Room with different floor | Walls W, Floor F |

**Examples:**

```json
{
  "a": [100, 64, 200],
  "p": {"S": "stone_bricks"},
  "s": "box:10x5x10:S"
}
```

This generates a 10-wide, 5-tall, 10-deep hollow box with:
- Solid floor at y=0
- Hollow walls at y=1 through y=3
- Solid ceiling at y=4

```json
{
  "a": [100, 64, 200],
  "p": {"B": "stone_bricks", "P": "oak_planks"},
  "s": "room:12x4x12:B:P"
}
```

This generates a room with stone brick walls and oak plank floor.

## Grid Convention

The grid uses a specific orientation:

```
        North (-Z)
           ↑
           |
    +------+------+
    | [0,0]| [0,1]|  ← Row 0
West|------+------|East (+X)
(-X)| [1,0]| [1,1]|  ← Row 1
    +------+------+
           |
           ↓
        South (+Z)
```

- `grid[row][col]` = `grid[z][x]`
- Row 0 = North edge (minimum Z)
- Column 0 = West edge (minimum X)
- Rows increase South (+Z)
- Columns increase East (+X)

## Rotation (Facing)

The `facing` parameter rotates the entire structure:

```json
"f": "north"   // Default, no rotation
"f": "south"   // Rotated 180°
"f": "east"    // Rotated 90° clockwise
"f": "west"    // Rotated 90° counter-clockwise
```

Rotation affects:
- Grid orientation (rows/columns swap for east/west)
- Block states (`facing=north` becomes `facing=south` when rotated 180°)
- Axis states (`axis=x` becomes `axis=z` when rotated 90°)

## Build Mode

Controls how blocks interact with existing blocks:

| Mode | Description |
|------|-------------|
| `replace` | Replace all blocks (default) |
| `keep` | Only place in air |
| `destroy` | Drop existing blocks as items |

## Complete Examples

### Simple 5x5 House

```json
{
  "a": [100, 64, 200],
  "p": {
    "S": "stone_bricks",
    "P": "oak_planks",
    "G": "glass_pane",
    "D": "oak_door[facing=south,half=lower,hinge=left]",
    "d": "oak_door[facing=south,half=upper,hinge=left]"
  },
  "l": [
    [0, "S*5~5"],
    [1, "S*5|S G . G S|S . D . S|S G . G S|S*5"],
    [2, "S*5|S G . G S|S . d . S|S G . G S|S*5"],
    [3, "S*5|S . . . S~3|S*5"],
    [4, "P*5~5"]
  ]
}
```

### 10x10 Room Using Shape

```json
{
  "a": [100, 64, 200],
  "p": {"S": "stone_bricks", "P": "oak_planks"},
  "s": "room:10x4x10:S:P"
}
```

### Tower with Mixed Syntax

```json
{
  "a": [100, 64, 200],
  "p": {"S": "stone_bricks", "G": "glass_pane"},
  "l": [
    [0, "fill:6x6:S"],
    ["1-5", "outline:6x6:S"],
    [3, "S G S G S G|G . . . . G~4|S G S G S G"],
    [6, "fill:6x6:S"]
  ]
}
```

## Validation

The server validates:
- All block names in the palette exist in Minecraft
- Coordinates are within world bounds
- Palette symbols are defined before use

Invalid blocks return helpful suggestions:
```
Invalid block 'cyan_terracotta_stairs'. Did you mean: cyan_terracotta, acacia_stairs, cyan_glazed_terracotta?
```

## Performance

For large structures, the server:
- Batches adjacent blocks into `/fill` commands where possible
- Optimizes command count (e.g., 100 blocks might become 5-10 fill commands)
- Reports statistics on blocks placed and commands executed

## Tips for AI Agents

1. **Use compact format** - Saves tokens significantly
2. **Use shape primitives** for rectangular structures
3. **Group similar blocks** in layers for better fill optimization
4. **Use Y-ranges** (`"1-3"`) for repeated wall patterns
5. **Define doors as pairs** - Lower (Dl) and upper (Du) halves
6. **Use `.` for air** - Don't place air blocks explicitly
7. **Validate first** - Use `search_minecraft_item()` if unsure about block names
