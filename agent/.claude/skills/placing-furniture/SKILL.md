---
name: placing-furniture
description: Places furniture and decorates Minecraft interiors using JSON schematics. Use when furnishing rooms, placing tables, chairs, beds, lamps, decorations, or designing interior spaces. Reference furniture_catalog.md for 80+ ready-to-use designs.
---

# Placing Furniture

## Critical: SCAN BEFORE PLACING

Avoid furniture embedded in floor!

```python
# 1. Scan area
scan = spatial_awareness_scan(center_x=100, center_y=65, center_z=200, radius=5, detail_level="medium")

# 2. Get placement Y from recommendations
placement_y = scan['recommendations']['floor_placement_y']  # e.g., 65

# 3. Place furniture AT that Y using build_schematic
build_schematic(
    schematic={
        "a": [100, placement_y, 200],
        "p": {"C": "oak_stairs[facing=south]", "L": "oak_wall_sign[facing=east]", "R": "oak_wall_sign[facing=west]"},
        "l": [[0, "L C R"]]
    },
    description="Armchair"
)
```

**Common mistake**: Floor at Y=64, furniture at Y=64 = EMBEDDED! Use Y=65 (ON floor).

## Furniture Catalog

See **furniture_catalog.md** in this skill folder for 80+ ready-to-use schematics:

| Category | Items |
|----------|-------|
| Seating | chair, armchair, bench, stool, sofa, throne |
| Tables | dining, coffee, desk, kitchen counter |
| Bedroom | bed, nightstand, wardrobe, dresser, bunk bed |
| Storage | bookshelf, cabinet, cupboard, barrel rack |
| Lighting | floor lamp, chandelier, wall sconce, hidden light |
| Kitchen | sink, stove, fridge, counter |
| Bathroom | toilet, bathtub, shower, mirror |
| Living Room | TV, fireplace, piano, rug |
| Office | computer, filing cabinet, office chair |
| Outdoor | grill, patio table, fountain, mailbox |

## Quick Placement Examples

### Armchair
```json
{"a": [X, Y, Z], "p": {"C": "oak_stairs[facing=south]", "L": "oak_wall_sign[facing=east]", "R": "oak_wall_sign[facing=west]"}, "l": [[0, "L C R"]]}
```

### Dining Table (2x3)
```json
{"a": [X, Y, Z], "p": {"F": "oak_fence", "S": "oak_slab[type=bottom]"}, "l": [[0, "F . F|. . .|F . F"], [1, "S S S|S S S|S S S"]]}
```

### Floor Lamp
```json
{"a": [X, Y, Z], "p": {"F": "oak_fence", "L": "lantern"}, "l": [[0, "F"], [1, "F"], [2, "L"]]}
```

### Hanging Chandelier
```json
{"a": [X, Y, Z], "p": {"C": "chain", "L": "lantern[hanging=true]"}, "l": [[0, "C"], [-1, "L"]]}
```

### Kitchen Sink
```json
{"a": [X, Y, Z], "p": {"H": "hopper[facing=down]", "L": "lever"}, "l": [[0, "H"], [1, "L"]]}
```

### Toilet
```json
{"a": [X, Y, Z], "p": {"H": "hopper[facing=down]", "T": "oak_trapdoor[facing=south,half=top,open=false]", "L": "lever"}, "l": [[0, "H"], [1, "T L"]]}
```

### Simple Fireplace
```json
{"a": [X, Y, Z], "p": {"S": "stone_bricks", "C": "campfire[lit=true]"}, "l": [[0, "S C S"], [1, "S . S"], [2, "S S S"]]}
```

## Workflow

```python
# 1. Scan room to get correct Y levels
scan = spatial_awareness_scan(center_x=X, center_y=Y, center_z=Z, radius=8, detail_level="medium")
floor_y = scan['recommendations']['floor_placement_y']
ceiling_y = scan['recommendations']['ceiling_placement_y']

# 2. Place floor furniture (tables, chairs, beds)
build_schematic(
    schematic={"a": [100, floor_y, 200], ...},
    description="Dining table"
)

# 3. Place ceiling fixtures (use negative Y offsets from ceiling)
build_schematic(
    schematic={"a": [100, ceiling_y, 200], "p": {"C": "chain", "L": "lantern[hanging=true]"}, "l": [[0, "C"], [-1, "L"]]},
    description="Hanging lantern"
)

# 4. Add wall decorations
build_schematic(
    schematic={"a": [100, floor_y + 1, 200], "p": {"T": "wall_torch[facing=south]"}, "l": [[0, "T"]]},
    description="Wall torch"
)
```

## Room Layouts

### Bedroom (5x6)
- Bed against wall (head at wall)
- Nightstand beside bed head
- Wardrobe on opposite wall
- Lamp on nightstand
- Rug beside bed

### Living Room (7x9)
- Sofa against wall
- Coffee table in front of sofa
- Armchairs angled toward sofa
- Bookshelf on side wall
- Fireplace on focal wall
- Chandelier centered

### Dining Room (7x9)
- Table centered
- Chairs around table (facing inward)
- Chandelier above table
- Cabinet/sideboard against wall

### Kitchen (5x7)
- Counters along walls (L or U shape)
- Stove recessed into counter
- Sink with lever tap
- Fridge in corner
- Small table or island

## Block State Reference

### Stairs (seats, backs)
```
oak_stairs[facing=north,half=bottom]  # Player sits facing north
oak_stairs[facing=south,half=top]     # Upside-down (table legs)
```

### Trapdoors (backs, doors, shelves)
```
oak_trapdoor[facing=south,half=bottom,open=true]   # Backrest
oak_trapdoor[facing=south,half=top,open=false]     # Lid/cover
```

### Signs (armrests)
```
oak_wall_sign[facing=east]   # Sign on west side of block
oak_wall_sign[facing=west]   # Sign on east side of block
```

### Slabs (tabletops, seats)
```
oak_slab[type=bottom]  # On floor
oak_slab[type=top]     # Near ceiling
```

### Lanterns
```
lantern              # Standing
lantern[hanging=true] # Hanging from above
```

### Wall Torches
```
wall_torch[facing=north]  # On south wall, points north
wall_torch[facing=south]  # On north wall, points south
```

## Furniture Orientations

When placing furniture, consider which way it faces:

| Facing | Meaning |
|--------|---------|
| north | Player faces north when using |
| south | Player faces south when using |
| east | Player faces east when using |
| west | Player faces west when using |

**Stairs as chairs**: `facing` = direction player faces when sitting
**Doors/chests**: `facing` = direction they open toward

## Style Coordination

| Style | Wood | Accents | Textiles |
|-------|------|---------|----------|
| Rustic | Oak, Spruce | Barrels, lanterns | Brown carpet |
| Modern | Birch, Quartz | Sea lanterns | White carpet |
| Medieval | Dark Oak | Chains, anvils | Red carpet |
| Asian | Bamboo, Cherry | Paper lanterns | Cyan carpet |
| Nether | Crimson, Warped | Soul lanterns | Black carpet |

## Spacing Guidelines

- **Tables**: 1 block clearance around for movement
- **Chairs**: Push against table edge
- **Beds**: 1 block on access side
- **Walkways**: 2 blocks minimum width
- **Ceiling lights**: Every 4-5 blocks for even lighting
- **Wall decor**: Eye level (Y+1 or Y+2 from floor)

## Common Mistakes

1. **Furniture in floor**: Always scan first, place ON floor_placement_y
2. **Wrong facing**: Stairs face where player looks when sitting
3. **Missing states**: Always specify `[type=bottom]` for slabs
4. **Floating furniture**: Ensure solid block beneath
5. **Cramped layout**: Leave walking space between items

## Decorative Details

### Rugs
```json
{"a": [X, Y, Z], "p": {"C": "red_carpet"}, "l": [[0, "C*5|C*5|C*5"]]}
```

### Potted Plants
```json
{"a": [X, Y, Z], "p": {"P": "potted_fern"}, "l": [[0, "P"]]}
```
Options: `potted_oak_sapling`, `potted_fern`, `potted_bamboo`, `potted_cactus`, `potted_red_tulip`, `potted_azure_bluet`

### Picture Frame
```json
{"a": [X, Y, Z], "p": {"F": "item_frame[facing=south]"}, "l": [[0, "F"]]}
```

### Flower Vase
```json
{"a": [X, Y, Z], "p": {"P": "flower_pot", "F": "potted_poppy"}, "l": [[0, "F"]]}
```
