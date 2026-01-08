---
name: building-structures
description: Builds Minecraft structures using VibeCraft MCP tools. Use when building houses, castles, towers, cottages, temples, or any architectural structure. Handles room dimensions, floor placement, wall construction, roofing, and architectural style matching.
---

# Building Structures

Build professional Minecraft structures using VibeCraft MCP tools.

## Critical Rules

### Floor Placement (MOST COMMON ERROR)

**Floor Y = Ground Y** - Floor REPLACES ground, does NOT sit on top!

```
WRONG (elevated):          CORRECT (flush):
Y=65: floor                Y=65: walls
Y=64: foundation           Y=64: floor (REPLACES grass)
Y=63: grass                Y=63: dirt (underground)
```

**Workflow:**
1. `get_surface_level(x, z)` → returns ground_y (e.g., 64)
2. Floor at Y=64, NOT Y=65
3. Walls start at Y=64

### Pre-Build Checklist

Before every build:
- [ ] `get_surface_level` called
- [ ] floor_y = ground_y (NOT +1)
- [ ] NO "foundation" unless requested
- [ ] Corners use contrasting pillars

## MCP Tools

### Location
- `get_player_position` - Position, rotation, target block
- `get_surface_level(x, z)` - Ground Y at coordinates

### Building
- `worldedit_selection` - pos1, pos2, expand, contract
- `worldedit_region` - set, replace, walls, faces, hollow
- `worldedit_generation` - sphere, cylinder, pyramid
- `build(code=..., commands=[...])` - Batch commands or code generation

### Templates
- `building_template` - 5 parametric templates (tower, cottage, barn)
- `building_pattern_lookup` - 29 patterns (roofs, windows, doors)
- `place_building_pattern` - Auto-place patterns

### Spatial
- `spatial_awareness_scan` - Floor/ceiling detection, clearance

## Building Workflow

### Phase 1: Foundation
```python
ground_y = get_surface_level(x=100, z=200)
# VERIFY: floor_y = ground_y (NOT ground_y + 1!)

# Floor
//pos1 100,{ground_y},200
//pos2 110,{ground_y},210
//set oak_planks
```

### Phase 2: Walls
```python
# Walls start AT floor level
//pos1 100,{ground_y},200
//pos2 110,{ground_y+height},210
//walls cobblestone

# Corner pillars (REQUIRED - contrasting material)
//pos1 100,{ground_y},200
//pos2 100,{ground_y+height},200
//set stripped_oak_log
```

### Phase 3: Roof

Use `building_pattern_lookup(action="search", query="roof")` to find patterns.

**Stair Roofs:**
- Each layer: Y+1, inward by 1 block
- Proper facing: `oak_stairs[facing=north,half=bottom]`
- Corner shapes for hip roofs: `shape=outer_left`, `shape=outer_right`

**Slab Roofs:**
- ALWAYS `oak_slab[type=bottom]` (sits ON ceiling)
- NEVER `type=top` (creates gap)

## Room Dimensions

| Room | Minimum | Comfortable | Spacious |
|------|---------|-------------|----------|
| Bedroom | 4×5 | 5×6 | 7×8 |
| Kitchen | 4×5 | 5×7 | 7×9 |
| Living | 5×6 | 7×9 | 10×12 |
| Dining | 5×6 | 7×9 | 10×14 |
| Great Hall | 10×15 | 15×20 | 20×30 |

**Ceiling heights:** 3 (min), 4 (comfortable), 5-6 (grand), 8+ (cathedral)

## Architectural Styles

For style-specific details, see [styles.md](styles.md).

| Style | Primary | Secondary | Roof |
|-------|---------|-----------|------|
| Medieval | Oak planks | Cobblestone | Steep gable |
| Gothic | Stone bricks | Deepslate | Pointed spires |
| Japanese | Spruce | Dark oak | Low hip |
| Modern | Concrete | Glass | Flat |
| Castle | Stone bricks | Deepslate tiles | Battlements |

## Material Palette (60-30-10 Rule)

- **60% Primary**: Walls, main structure
- **30% Secondary**: Roof, accents, trim
- **10% Details**: Decorations, contrast

**Always include:**
- Contrasting corner pillars
- Window frames (1-block trim)
- Roof overhangs (1-2 blocks)
- Proper door placement

## Quick Reference

```python
# Simple cottage workflow
ground_y = get_surface_level(x=100, z=200)

build(commands=[
    f"/fill 100 {ground_y} 200 110 {ground_y} 210 oak_planks",  # Floor
    f"/fill 100 {ground_y} 200 110 {ground_y+5} 210 cobblestone hollow",  # Walls
    # Corner pillars
    f"/fill 100 {ground_y} 200 100 {ground_y+5} 200 stripped_oak_log",
    f"/fill 110 {ground_y} 200 110 {ground_y+5} 200 stripped_oak_log",
    f"/fill 100 {ground_y} 210 100 {ground_y+5} 210 stripped_oak_log",
    f"/fill 110 {ground_y} 210 110 {ground_y+5} 210 stripped_oak_log",
])
```
