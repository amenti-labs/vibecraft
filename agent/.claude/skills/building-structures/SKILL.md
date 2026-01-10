---
name: building-structures
description: Builds Minecraft structures using VibeCraft MCP tools. Use when building houses, castles, towers, cottages, temples, or any architectural structure. Handles room dimensions, floor placement, wall construction, roofing, and architectural style matching.
---

# Building Structures

## Critical: Floor Y = Ground Y

Floor REPLACES ground, NOT sits on top!

```
WRONG: Y=65 floor, Y=64 foundation, Y=63 grass (elevated!)
RIGHT: Y=65 walls, Y=64 floor REPLACES grass, Y=63 dirt
```

**Workflow:** `get_surface_level(x,z)` → floor at that Y, walls start same Y

## Pre-Build Checklist
- `get_surface_level` called
- floor_y = ground_y (NOT +1)
- Corner pillars (contrasting material)

## Tools
- `get_surface_level(x,z)`, `get_player_position`
- `worldedit_selection`, `worldedit_region`, `worldedit_generation`
- `build(code=..., commands=[...])`, `building_template`, `building_pattern_lookup`
- `spatial_awareness_scan`

## Build Phases

```python
y = get_surface_level(x=100, z=200)  # e.g., 64

# Floor at ground
//pos1 100,{y},200 → //pos2 110,{y},210 → //set oak_planks

# Walls from floor up
//pos1 100,{y},200 → //pos2 110,{y+5},210 → //walls cobblestone

# Corner pillars (REQUIRED)
//pos1 100,{y},200 → //pos2 100,{y+5},200 → //set stripped_oak_log
# Repeat for other 3 corners
```

## Roof
Use `building_pattern_lookup(action="search", query="roof")`

**Stairs:** Each layer Y+1, inward 1 block. `oak_stairs[facing=north,half=bottom]`
**Hip corners:** `shape=outer_left/outer_right`
**Slabs:** ALWAYS `type=bottom` (sits ON ceiling)

## Dimensions
Room: Bedroom 5×6, Kitchen 5×7, Living 7×9, Dining 7×9, Great Hall 15×20
Ceiling: 3 min, 4 comfortable, 5-6 grand, 8+ cathedral

## Styles (see [styles.md](styles.md))
Medieval: oak_planks + cobblestone + dark_oak_stairs
Gothic: stone_bricks + deepslate + pointed spires
Japanese: spruce + dark_oak + low hip roof
Modern: concrete + glass + flat roof
Castle: stone_bricks + deepslate_tiles + battlements

## 60-30-10 Rule
60% primary (walls), 30% secondary (roof/trim), 10% details
Always: corner pillars, window frames, roof overhangs, proper doors
