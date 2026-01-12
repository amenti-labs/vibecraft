# VibeCraft - Minecraft Building AI

Building assistant using WorldEdit and JSON Schematics. Check `.claude/skills/` for detailed workflows.

## CRITICAL RULES

### Rule 1: FLOOR = GROUND (NOT GROUND + 1!)
```
WRONG: floor_y = ground_y + 1    CORRECT: floor_y = ground_y
```
Floor REPLACES ground. Mnemonic: "FLOOR EATS GRASS"

### Rule 2: Furniture ON Floor (NOT IN Floor!)
```
Floor: Y=64 → Furniture: Y=65 (ON TOP)
```
Use `spatial_awareness_scan` → `recommendations.floor_placement_y`

### Rule 3: Roof Slabs Use type=bottom
```
oak_slab[type=bottom]  # Sits ON ceiling
oak_slab[type=top]     # Creates gap - WRONG
```

### Rule 4: Block Placement Order
Support blocks FIRST, then dependent blocks. Wire/buttons drop without support!

### Rule 5: Trees = WorldEdit //forest
```
WRONG: Manually placing logs + leaves
CORRECT: //forest cherry 100  or  //forestgen 50 oak 5
```

### Rule 6: WorldEdit via Client Bridge
```
WRONG: execute as <player> at @s run /pos1 100,64,100
CORRECT: //pos1 100,64,100
```
Send `//` commands directly. Do NOT wrap with `execute as`. NEVER teleport the player.

## WorldEdit Client Bridge

- Send commands directly with `//`
- Use comma-separated coordinates: `//pos1 100,64,100`
- Do NOT use `execute as` wrappers
- NEVER teleport player - use coordinate-based selections

For spheres/cylinders at specific location:
```python
build(commands=[
    "//pos1 90,54,190",
    "//pos2 110,74,210",
    "//sphere stone 10"
], description="Sphere at location")
```

## Skills

Skills in `.claude/skills/` are auto-loaded. Multiple often apply together.

| Skill | When | What |
|-------|------|------|
| using-worldedit | Terrain, bulk fills, shapes, copy/paste | WorldEdit commands, patterns, masks |
| building-with-schematics | Structures with oriented blocks (doors/stairs) | JSON schematic format, block states |
| building-structures | Houses, castles, towers | Building workflow, ground detection |
| creating-shapes | Spheres, domes, pyramids | WorldEdit generation, procedural code |
| generating-terrain | Mountains, hills, landscape | Terrain tools, noise, smoothing |
| choosing-materials | Palettes, colors | 60-30-10 rule, curated palettes |
| placing-furniture | Interiors, decoration | 80+ furniture schematics, room layouts |
| building-redstone | Circuits, farms | Logic gates, placement order |

**Choose the right tool:**
- **Schematics** (`build_schematic`) → Structures with oriented blocks (doors, stairs, furniture), precise placement
- **WorldEdit** → Terrain, bulk fills, spheres, patterns, copy/paste, organic shapes

**DON'T use schematics for:** Organic terrain, large terraforming, freeform/artistic builds, spheres/cylinders, random patterns

## MCP Tools

**Core**: `get_server_info`, `get_player_position`, `get_surface_level`, `get_player_context`

**WorldEdit**: `worldedit_selection`, `worldedit_region`, `worldedit_generation`, `worldedit_clipboard`, `worldedit_history`, `worldedit_utility`, `worldedit_biome`, `worldedit_brush`, `worldedit_deform`, `worldedit_vegetation`, `worldedit_terrain_advanced`, `worldedit_analysis`

**Building**: `build_schematic()` (JSON schematics), `build()` (code or commands), `building_template`, `place_building_pattern`

**Furniture**: Use `build_schematic()` with designs from `placing-furniture` skill catalog (80+ items)

**Spatial**: `spatial_awareness_scan` (MANDATORY before furniture/roofs)

**Terrain**: `generate_terrain`, `texture_terrain`, `smooth_terrain`

**Validation**: `validate_mask`, `search_minecraft_item`

## Pre-Build Checklist
```
ground_y = get_surface_level(x, z)
floor_y = ground_y (NOT ground_y + 1!)
Walls start at ground_y
```

## build() Tool

Code Sandbox - NO function definitions:
```python
# NOT allowed: def build_house(), lambda
# OK: for loops, variables
```

WorldEdit Mode (commands starting with `//` are auto-wrapped):
```python
build(commands=[
    "//pos1 100,64,200",
    "//pos2 120,80,220",
    "//set stone_bricks",
    "//walls oak_planks",
    "//hollow"
], description="Castle structure")
```

WorldEdit + Code Mode:
```python
build(code="""
commands = []
commands.append("//pos1 100,64,200")
commands.append("//pos2 120,80,220")
commands.append("//set 80%stone_bricks,20%cracked_stone_bricks")
for i in range(5):
    commands.append(f"/setblock {105+i} 81 210 torch")
""", description="Castle with torches")
```

## Spatial Awareness

Before placing furniture, roofs, or aligned blocks:
```python
scan = spatial_awareness_scan(center_x=100, center_y=65, center_z=200, radius=5, detail_level="medium")
placement_y = scan['recommendations']['floor_placement_y']
```
Detail levels: `"low"` (2-3s), `"medium"` (4-5s), `"high"` (8-10s)

## Block States
```
oak_stairs[facing=north,half=bottom]
oak_log[axis=y]
oak_slab[type=bottom]
barrel[facing=up]
oak_door[facing=north,half=lower,hinge=right]
```
Always specify orientation.

## Reference Image Analysis

Extract: Style (Medieval/Gothic/Modern), Proportions, Materials (60/30/10), Features (roof/windows/doors)
Map to Minecraft blocks → Plan → Execute

## Context Files (in /context/)
| Task | File |
|------|------|
| Room sizes | minecraft_scale_reference.md |
| Materials | block_palette_guide.md |
| Styles | architectural_styles.md |
| Shapes | procedural_generation_guide.md |
| WorldEdit | worldedit_expression_guide.md |

## Critical Warnings

- NEVER `floor_y = ground_y + 1`
- NEVER place furniture without scanning
- NEVER use `oak_slab` without `[type=...]`
- NEVER stack stairs vertically (offset horizontally!)
- NEVER random block orientation
- NEVER teleport player for WorldEdit
- NEVER use `/brush`, `/br`, `/tool` - require player right-click
- Large ops (>10k blocks): Warn first
- `/regen` is DESTRUCTIVE

## Troubleshooting

**"You need to provide a world"**: Ensure WorldEdit installed, player has permissions

**WorldEdit not working**: Check WorldEdit installed, permissions, use `//` with comma coords

**Brushes/Tools error**: Use `//forest`, `//forestgen`, or `build(code=...)` instead

## Quick Workflows

**WorldEdit Build:**
```python
build(commands=[
    "//pos1 X,ground_y,Z",
    "//pos2 X2,ground_y+height,Z2",
    "//set floor_material",
    "//walls wall_material",
    "//hollow",
], description="Building structure")
```

**WorldEdit Power Features:**
- `//set 70%stone_bricks,30%cracked_stone_bricks` - Random patterns
- `//replace air glass` - Windows
- `//walls` + `//hollow` - Fast structural work
- `//stack 3 up` - Duplicate floors

**Furniture:** `spatial_awareness_scan()` → copy from `placing-furniture` skill catalog → `build_schematic()`
```python
# 1. Scan for floor level
scan = spatial_awareness_scan(center_x=100, center_y=65, center_z=200, radius=5)
floor_y = scan['recommendations']['floor_placement_y']

# 2. Place furniture using schematic (from catalog)
build_schematic(schematic={
    "a": [100, floor_y, 200],
    "p": {"C": "oak_stairs[facing=south]", "L": "oak_wall_sign[facing=east]", "R": "oak_wall_sign[facing=west]"},
    "l": [[0, "L C R"]]
}, description="Armchair")
```

**Terrain:** `generate_terrain()` → `texture_terrain()` → `smooth_terrain()`

**Roofing:** Layer by layer: Y+1 AND X/Z±1 (step up AND inward). See building-structures skill.

## Architecture Standards

**60-30-10 Rule**: Primary 60% (walls), Secondary 30% (roof/trim), Accent 10% (details)

**Must-Haves**: Corner pillars, window frames (1-block trim), roof overhangs (1-2 blocks)

**Scales**: Player=1.8 blocks, ceiling≥3, rooms≥5×6

## Response: Plan → Execute → Report → Offer enhancements
