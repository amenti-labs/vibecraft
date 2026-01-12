---
name: building-with-schematics
description: PRIMARY BUILDING METHOD - Use for ALL construction tasks. Build structures using declarative JSON schematics with 2D layer grids. Describe WHAT to build, the server handles HOW. Supports COMPACT FORMAT (70% fewer tokens) with run-length encoding. Use this instead of WorldEdit commands for reliable, predictable builds.
---

# Building with Schematics

## Why Schematics?

**Schematics are the PREFERRED building method** because:
- You describe WHAT to build, not HOW to execute commands
- Full block state support (facing, axis, half, etc.)
- **COMPACT FORMAT saves ~70% tokens** with run-length encoding
- Automatic rotation of entire builds
- Optimizes commands automatically

## COMPACT FORMAT (Recommended)

**Use this format for token efficiency:**

```json
{
  "a": [x, y, z],
  "p": {"S": "stone", "P": "oak_planks", ".": "air"},
  "l": [
    [0, "S*10|S P*8 S~8|S*10"]
  ]
}
```

### Compact Syntax:
- **Short keys**: `"a"` (anchor), `"p"` (palette), `"l"` (layers), `"f"` (facing)
- **Layers**: `[y_offset, "row|row|row"]` - pipe separates rows
- **Layer range**: `["1-3", "pattern"]` - same pattern at y=1, y=2, y=3 (great for walls!)
- **Run-length**: `S*5` = 5 S blocks in a row
- **Row repeat**: `S P*3 S~8` = repeat this row pattern 8 times

### Compact Examples:

**10x10 floor with border (verbose: ~500 tokens, compact: ~50 tokens):**
```json
{"a": [0,64,0], "p": {"S": "stone", "P": "planks"}, "l": [[0, "S*10|S P*8 S~8|S*10"]]}
```

**5x5x4 hollow room (with layer range for walls):**
```json
{
  "a": [100, 64, 200],
  "p": {"W": "oak_planks", ".": "air"},
  "l": [
    [0, "W*5~5"],
    ["1-2", "W*5|W .*3 W~3|W*5"],
    [3, "W*5~5"]
  ]
}
```
Note: `["1-2", "..."]` creates identical layers at y=1 AND y=2. Great for multi-story walls!

## Verbose Format (Backward Compatible)

```json
{
  "anchor": [x, y, z],
  "facing": "north",
  "mode": "replace",
  "palette": {"<symbol>": "<block>[states]{nbt}"},
  "layers": [
    {"y": 0, "grid": [["S","S"],["S","S"]]}
  ]
}
```

## Grid Convention

```
        North (-Z)
           ^
    Row 0  |
    Row 1  |
    Row 2  v
        South (+Z)

    Col0 Col1 Col2
    <--- West    East --->
    (-X)         (+X)
```

- `grid[row][col]` = `grid[z][x]`
- Row 0 is the NORTH edge
- Column 0 is the WEST edge
- Rows increase going SOUTH
- Columns increase going EAST

## Palette Symbols

Use short symbols for readability:

```json
{
  "palette": {
    ".": "air",
    "S": "stone_bricks",
    "P": "oak_planks",
    "G": "glass",

    "Sn": "oak_stairs[facing=north]",
    "Ss": "oak_stairs[facing=south]",
    "Se": "oak_stairs[facing=east]",
    "Sw": "oak_stairs[facing=west]",

    "Dl": "oak_door[facing=south,half=lower,hinge=left]",
    "Du": "oak_door[facing=south,half=upper,hinge=left]",

    "Lx": "oak_log[axis=x]",
    "Ly": "oak_log[axis=y]",
    "Lz": "oak_log[axis=z]",

    "T": "torch",
    "Tn": "wall_torch[facing=north]",
    "Ln": "ladder[facing=north]",
    "C": "chest[facing=south]"
  }
}
```

## Complete Example: Small House

**COMPACT FORMAT (recommended):**
```json
{
  "a": [100, 64, 200],
  "p": {
    "S": "stone_bricks", "P": "oak_planks", "W": "oak_planks", "G": "glass_pane",
    "Dl": "oak_door[facing=south,half=lower]", "Du": "oak_door[facing=south,half=upper]",
    "Sn": "oak_stairs[facing=north,half=bottom]", "Ss": "oak_stairs[facing=south,half=bottom]",
    "Se": "oak_stairs[facing=east,half=bottom]", "Sw": "oak_stairs[facing=west,half=bottom]",
    "Ln": "oak_stairs[facing=north,half=top]", "Ls": "oak_stairs[facing=south,half=top]"
  },
  "l": [
    [0, "S*7|S P*5 S~4|S*7"],
    [1, "W*7|W .*5 W|G .*5 G~2|W .*5 W|W*3 Dl W*3"],
    [2, "W*7|W .*5 W|G .*5 G~2|W .*5 W|W*3 Du W*3"],
    [3, "W*7|W .*5 W~4|W*7"],
    [4, "Ss*7|Se P*5 Sw|Se P .*3 P Sw~2|Se P*5 Sw|Sn*7"],
    [5, ".*7|. Ss*5 .|. Se P*3 Sw .~2|. Sn*5 .|.*7"],
    [6, ".*7~2|.*2 Ls*3 .*2|.*2 Ln*3 .*2|.*7~2"]
  ]
}
```

**Verbose format (same result, more tokens):**
```json
{
  "anchor": [100, 64, 200],
  "palette": {
    ".": "air", "S": "stone_bricks", "P": "oak_planks", "W": "oak_planks", "G": "glass_pane",
    "Dl": "oak_door[facing=south,half=lower]", "Du": "oak_door[facing=south,half=upper]",
    "Sn": "oak_stairs[facing=north,half=bottom]", "Ss": "oak_stairs[facing=south,half=bottom]",
    "Se": "oak_stairs[facing=east,half=bottom]", "Sw": "oak_stairs[facing=west,half=bottom]",
    "Ln": "oak_stairs[facing=north,half=top]", "Ls": "oak_stairs[facing=south,half=top]"
  },
  "layers": [
    {"y": 0, "grid": [["S","S","S","S","S","S","S"],["S","P","P","P","P","P","S"],["S","P","P","P","P","P","S"],["S","P","P","P","P","P","S"],["S","P","P","P","P","P","S"],["S","S","S","S","S","S","S"]]},
    {"y": 1, "grid": [["W","W","W","W","W","W","W"],["W",".",".",".",".",".", "W"],["G",".",".",".",".",".","G"],["G",".",".",".",".",".","G"],["W",".",".",".",".",".","W"],["W","W","W","Dl","W","W","W"]]},
    {"y": 2, "grid": [["W","W","W","W","W","W","W"],["W",".",".",".",".",".", "W"],["G",".",".",".",".",".","G"],["G",".",".",".",".",".","G"],["W",".",".",".",".",".","W"],["W","W","W","Du","W","W","W"]]},
    {"y": 3, "grid": [["W","W","W","W","W","W","W"],["W",".",".",".",".",".", "W"],["W",".",".",".",".",".","W"],["W",".",".",".",".",".","W"],["W",".",".",".",".",".","W"],["W","W","W","W","W","W","W"]]},
    {"y": 4, "grid": [["Ss","Ss","Ss","Ss","Ss","Ss","Ss"],["Se","P","P","P","P","P","Sw"],["Se","P",".",".",".", "P","Sw"],["Se","P",".",".",".","P","Sw"],["Se","P","P","P","P","P","Sw"],["Sn","Sn","Sn","Sn","Sn","Sn","Sn"]]},
    {"y": 5, "grid": [[".",".",".",".",".",".","."],[".","Ss","Ss","Ss","Ss","Ss","."],[".","Se","P","P","P","Sw","."],[".","Se","P","P","P","Sw","."],[".","Sn","Sn","Sn","Sn","Sn","."],[".",".",".",".",".",".","."]]},
    {"y": 6, "grid": [[".",".",".",".",".",".","."],[".",".",".",".",".",".","."],[".",".", "Ls","Ls","Ls",".","."],[".",".", "Ln","Ln","Ln",".","."],[".",".",".",".",".",".","."],[".",".",".",".",".",".","."]]}
  ]
}
```

## Block States Reference

### Stairs
```json
"Sn": "oak_stairs[facing=north,half=bottom]",    // Normal stairs
"S^": "oak_stairs[facing=north,half=top]",       // Upside-down
"Sc": "oak_stairs[facing=north,shape=inner_left]" // Corner
```

### Doors (always place lower then upper)
```json
"Dl": "oak_door[facing=south,half=lower,hinge=left]",
"Du": "oak_door[facing=south,half=upper,hinge=left]"
```

### Slabs
```json
"Sb": "oak_slab[type=bottom]",  // On floor
"St": "oak_slab[type=top]",     // On ceiling
"Sd": "oak_slab[type=double]"   // Full block
```

### Logs/Pillars
```json
"Lx": "oak_log[axis=x]",  // Horizontal east-west
"Ly": "oak_log[axis=y]",  // Vertical (default)
"Lz": "oak_log[axis=z]"   // Horizontal north-south
```

### Containers
```json
"Cn": "chest[facing=north]",
"Cs": "chest[facing=south]",
"B": "barrel[facing=up]"
```

### Signs (with NBT)
```json
"T": "oak_sign[rotation=8]{Text1:'\"Welcome\"',Text2:'\"Home\"'}"
```

### Beds
```json
"Bf": "red_bed[facing=south,part=foot]",
"Bh": "red_bed[facing=south,part=head]"
```

### Wall-Mounted Blocks (IMPORTANT)
**Floor vs Wall versions are DIFFERENT blocks!**

```json
// TORCHES - floor torch vs wall torch
"Tf": "torch",                        // Floor (on ground)
"Tn": "wall_torch[facing=north]",     // Wall (facing=which way it sticks OUT)
"Ts": "wall_torch[facing=south]",
"Te": "wall_torch[facing=east]",
"Tw": "wall_torch[facing=west]",

// SOUL TORCHES
"STf": "soul_torch",                  // Floor
"STn": "soul_wall_torch[facing=north]", // Wall

// LADDERS (always wall-mounted, facing=direction player faces when climbing)
"Ln": "ladder[facing=north]",         // Climb facing north
"Ls": "ladder[facing=south]",
"Le": "ladder[facing=east]",
"Lw": "ladder[facing=west]",

// LEVERS (face=which surface, facing=orientation on that surface)
"LVn": "lever[face=wall,facing=north]",  // Wall lever
"LVf": "lever[face=floor,facing=north]", // Floor lever
"LVc": "lever[face=ceiling,facing=north]", // Ceiling lever

// BUTTONS
"Bn": "stone_button[face=wall,facing=north]",
"Bf": "stone_button[face=floor]",
"Bc": "stone_button[face=ceiling]",

// LANTERNS
"La": "lantern",                      // Floor/ceiling (auto-hangs)
"Lh": "lantern[hanging=true]",        // Explicitly hanging

// CHAINS (vertical by default)
"Ch": "chain",                        // Vertical
"Chx": "chain[axis=x]",               // Horizontal E-W
"Chz": "chain[axis=z]",               // Horizontal N-S

// ITEM FRAMES (facing=which way they face OUT from wall)
"IFn": "item_frame[facing=north]",    // On south wall, faces north
"IFs": "item_frame[facing=south]"     // On north wall, faces south
```

**Key concept**: `facing` for wall blocks means "which direction does it stick out/face toward", NOT which wall it's on.
- `wall_torch[facing=north]` = torch on a SOUTH wall, sticking out toward north
- `ladder[facing=north]` = ladder on SOUTH wall, player faces north to climb

## Workflow

1. **Get position**: `get_surface_level(x, z)` or `get_player_position()`
2. **Design schematic**: Create palette + layers
3. **Preview first**: `build_schematic(schematic=..., preview_only=true)`
4. **Execute**: `build_schematic(schematic=..., description="...")`

## Tips

### Orientation Symbols
Use consistent naming:
- `n/s/e/w` = facing direction
- `l/u` = lower/upper (doors)
- `t/b` = top/bottom (slabs, stairs)
- `x/y/z` = axis (logs)

### Visual Alignment
Draw grids as you'd see them from above, looking down:
- North is UP in your text editor
- South is DOWN
- West is LEFT
- East is RIGHT

### Air Blocks
Use `.` for air - it's skipped (no command generated).
Don't fill interiors with air unless you need to clear existing blocks.

### Non-Solid Blocks (IMPORTANT)
These blocks do NOT support furniture/entities and should NOT be used as floors:
- **Carpet** - decorative overlay, place ON TOP of solid floor at same y-level
- **Snow layers** - partial blocks
- **Pressure plates** - place on top of solid blocks
- **Rails, redstone** - need solid block beneath

**Correct floor + carpet + furniture pattern:**
```json
{
  "layers": [
    {"y": 0, "comment": "Solid floor", "grid": [["P", "P", "P"]]},
    {"y": 0, "comment": "Carpet ON floor (same y!)", "grid": [["Cr", "Cr", "Cr"]]},
    {"y": 1, "comment": "Furniture ON floor", "grid": [[".", "Bed", "."]]}
  ]
}
```
Or simpler - just use solid floor without carpet:
```json
{
  "layers": [
    {"y": 0, "comment": "Solid floor", "grid": [["P", "P", "P"]]},
    {"y": 1, "comment": "Furniture", "grid": [[".", "Bed", "."]]}
  ]
}
```

**Wrong (furniture will float):**
```json
{
  "layers": [
    {"y": 0, "grid": [["Carpet", "Carpet", "Carpet"]]},  // NO solid floor!
    {"y": 1, "grid": [[".", "Bed", "."]]}  // Bed floats!
  ]
}
```

### Rotation
Set `"facing": "east"` to rotate the entire build 90° clockwise.
All block states with facing/axis are automatically rotated!

## Common Patterns

### Hollow Box (Walls Only)
```json
{
  "layers": [
    {"y": 0, "grid": [["W","W","W"],["W",".","W"],["W","W","W"]]},
    {"y": 1, "grid": [["W","W","W"],["W",".","W"],["W","W","W"]]},
    {"y": 2, "grid": [["W","W","W"],["W",".","W"],["W","W","W"]]}
  ]
}
```

### Gabled Roof
```json
{
  "layers": [
    {"y": 0, "grid": [["Se","P","P","P","Sw"],["Se","P","P","P","Sw"]]},
    {"y": 1, "grid": [[".","Se","P","Sw","."],[".","Se","P","Sw","."]]},
    {"y": 2, "grid": [[".",".","P",".","."],[".",".",".P",".","."]}
  ]
}
```

### Circular Floor (approximation)
```json
{
  "layers": [
    {"y": 0, "grid": [
      [".", "P", "P", "P", "."],
      ["P", "P", "P", "P", "P"],
      ["P", "P", "P", "P", "P"],
      ["P", "P", "P", "P", "P"],
      [".", "P", "P", "P", "."]
    ]}
  ]
}
```

## When to Use Schematics vs WorldEdit

### ✅ USE SCHEMATICS FOR:
- **Structured buildings**: Houses, castles, towers, bridges
- **Oriented blocks**: Doors, stairs, chests, beds, torches
- **Precise placement**: Furniture, decorations, redstone
- **Repeatable patterns**: Walls, floors, roofs with detail
- **Multi-block structures**: Anything that needs exact block states

### ❌ DON'T USE SCHEMATICS FOR:
- **Organic terrain**: Mountains, rivers, caves, natural landscapes
- **Large-scale terraforming**: Flattening, raising, smoothing land
- **Freeform/artistic builds**: Abstract sculptures, flowing shapes
- **Random patterns**: Natural-looking stone walls (`50%stone,50%cobble`)
- **Geometric primitives**: Spheres, cylinders, pyramids at scale
- **Copy/paste operations**: Duplicating existing structures

### Use WorldEdit Instead:
| Task | WorldEdit Command |
|------|-------------------|
| Large fills | `//set stone` |
| Terrain smoothing | `//smooth 3` |
| Spheres/cylinders | `//sphere stone 10` |
| Random patterns | `//set 50%stone,50%cobble` |
| Copy/paste | `//copy`, `//paste` |
| Hollow shapes | `//hsphere`, `//hcyl` |

**Rule of thumb**:
- **Schematic** = Precise, structured, oriented blocks
- **WorldEdit** = Bulk, organic, random, geometric
