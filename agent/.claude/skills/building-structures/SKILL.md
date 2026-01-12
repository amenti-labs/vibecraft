---
name: building-structures
description: Builds Minecraft structures using VibeCraft MCP tools. Use when building houses, castles, towers, cottages, temples, or any architectural structure. Works with build_schematic for precise control. Handles room dimensions, floor placement, wall construction, roofing, and architectural style matching.
---

# Building Structures

## Primary Method: Schematics

**Use `build_schematic()` for all structures.** See `building-with-schematics` skill for schema details.

## Critical: Floor Y = Ground Y

Floor REPLACES ground, NOT sits on top!

```
WRONG: Y=65 floor, Y=64 foundation, Y=63 grass (elevated!)
RIGHT: Y=65 walls, Y=64 floor REPLACES grass, Y=63 dirt
```

**Workflow:** `get_surface_level(x,z)` → anchor at that Y

## Pre-Build Checklist

- [ ] `get_surface_level()` called
- [ ] anchor_y = ground_y (NOT +1)
- [ ] All blocks have orientations
- [ ] Doors have lower + upper
- [ ] Preview first (`preview_only=true`)

## Building Workflow

```python
# 1. Get ground level
y = get_surface_level(x=100, z=200)

# 2. Design schematic
schematic = {
  "anchor": [100, y, 200],
  "palette": {
    "S": "stone_bricks",
    "P": "oak_planks",
    "W": "oak_planks",
    "G": "glass_pane",
    "Dl": "oak_door[facing=south,half=lower]",
    "Du": "oak_door[facing=south,half=upper]",
    "Sn": "oak_stairs[facing=north,half=bottom]",
    "Ss": "oak_stairs[facing=south,half=bottom]",
    ".": "air"
  },
  "layers": [
    # y=0: Foundation/Floor
    {"y": 0, "grid": [
      ["S", "S", "S", "S", "S"],
      ["S", "P", "P", "P", "S"],
      ["S", "P", "P", "P", "S"],
      ["S", "S", "S", "S", "S"]
    ]},
    # y=1-3: Walls
    {"y": 1, "grid": [
      ["W", "W", "W", "W", "W"],
      ["W", ".", ".", ".", "W"],
      ["G", ".", ".", ".", "G"],
      ["W", "W", "Dl", "W", "W"]
    ]},
    # ... more layers
  ]
}

# 3. Preview
build_schematic(schematic=schematic, preview_only=true, description="Cottage")

# 4. Execute
build_schematic(schematic=schematic, description="Cottage")
```

## Dimensions Reference

| Room Type | Minimum | Comfortable |
|-----------|---------|-------------|
| Bedroom | 5×6 | 6×7 |
| Kitchen | 5×7 | 6×8 |
| Living Room | 7×9 | 8×10 |
| Dining | 7×9 | 8×10 |
| Great Hall | 15×20 | 20×25 |

| Ceiling Height | Feel |
|----------------|------|
| 3 blocks | Minimum |
| 4 blocks | Comfortable |
| 5-6 blocks | Grand |
| 8+ blocks | Cathedral |

## Architectural Styles

### Medieval
```json
{
  "palette": {
    "W": "oak_planks",
    "S": "cobblestone",
    "P": "stripped_oak_log",
    "R": "dark_oak_stairs[facing=...]"
  }
}
```

### Gothic
```json
{
  "palette": {
    "W": "stone_bricks",
    "D": "deepslate_bricks",
    "P": "polished_deepslate",
    "R": "deepslate_tile_stairs[facing=...]"
  }
}
```

### Japanese
```json
{
  "palette": {
    "W": "spruce_planks",
    "P": "dark_oak_log[axis=...]",
    "R": "dark_oak_stairs[facing=...]",
    "F": "white_wool"
  }
}
```

### Modern
```json
{
  "palette": {
    "W": "white_concrete",
    "G": "glass",
    "A": "gray_concrete",
    "R": "smooth_stone_slab[type=bottom]"
  }
}
```

## Roof Patterns

### Gabled Roof
```
Layer 0: Se P P P Sw   (stairs facing out)
Layer 1:  . Se P Sw .
Layer 2:  .  . P  . .  (ridge)
```

### Hip Roof
```
Layer 0: Sse Ss Ss Ss Ssw  (corners use shape=outer_*)
Layer 1: Se   P  P  P  Sw
Layer 2:  .  Se  P Sw   .
```

### Flat Roof (Modern)
```
Layer 0: Sb Sb Sb Sb Sb   (slab[type=bottom] on ceiling)
```

## Corner Pillars (REQUIRED)

Always use contrasting corner pillars:
```json
{
  "palette": {
    "W": "oak_planks",
    "P": "stripped_oak_log[axis=y]"  // Corner pillar
  },
  "layers": [
    {"y": 1, "grid": [
      ["P", "W", "W", "W", "P"],
      ["W", ".", ".", ".", "W"],
      ["W", ".", ".", ".", "W"],
      ["P", "W", "W", "W", "P"]
    ]}
  ]
}
```

## 60-30-10 Rule

- **60% Primary**: Walls (oak_planks, stone_bricks)
- **30% Secondary**: Roof, trim (stairs, logs)
- **10% Accent**: Details (doors, windows, lights)

## Window Placement

```json
{
  "palette": {
    "W": "oak_planks",
    "G": "glass_pane",
    "F": "oak_trapdoor[facing=north,half=top,open=true]"  // Frame
  }
}
```

## Door Placement

**Always place both parts:**
```json
{
  "palette": {
    "Dl": "oak_door[facing=south,half=lower,hinge=left]",
    "Du": "oak_door[facing=south,half=upper,hinge=left]"
  },
  "layers": [
    {"y": 1, "grid": [["W", "Dl", "W"]]},
    {"y": 2, "grid": [["W", "Du", "W"]]}
  ]
}
```

## Stairs Orientation

**Facing = direction player walks UP:**
- `facing=north`: Walk north to go up
- `facing=south`: Walk south to go up
- `half=bottom`: Normal stairs
- `half=top`: Upside-down (for roof undersides)

## Quick Templates

### Tiny Hut (5×5)
```
Floor:  SSSSS    Walls: WWWWW    Roof: SsSsSsSsSs
        SPPPS           W...W          Se P P Sw
        SPPPS           W...W          Se P P Sw
        SPPPS           W...W          Se P P Sw
        SSSSS           WWDWW          SnSnSnSn
```

### Tower (7×7 circular)
```
         .SSS.
        S.....S
        S.....S
        S.....S
        S.....S
        S.....S
         .SSS.
```

## For Bulk Operations

Use WorldEdit for:
- Clearing large areas: `//pos1`, `//pos2`, `//set air`
- Terrain prep: `//smooth`
- Large fills: `//set stone`

Then use `build_schematic()` for the detailed structure.
