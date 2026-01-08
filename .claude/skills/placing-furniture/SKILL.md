---
name: placing-furniture
description: Places furniture and decorates Minecraft interiors using VibeCraft MCP tools. Use when furnishing rooms, placing tables, chairs, beds, lamps, decorations, or designing interior spaces. Handles furniture positioning, spatial awareness, and style coordination.
---

# Placing Furniture

Furnish Minecraft interiors using VibeCraft MCP tools.

## Critical Rule: Floor Placement

**SCAN BEFORE PLACING** to avoid furniture embedded in floor!

```python
# 1. Scan the area
scan = spatial_awareness_scan(
    center_x=100, center_y=65, center_z=200,
    radius=5, detail_level="medium"
)

# 2. Get placement Y from recommendations
placement_y = scan['recommendations']['floor_placement_y']  # e.g., 65

# 3. Place furniture AT that Y
place_furniture(
    furniture_id="simple_dining_table",
    origin_x=100,
    origin_y=placement_y,  # NOT floor_y!
    origin_z=200
)
```

**Common mistake:**
```
Floor block:  Y=64
Furniture:    Y=64  ← WRONG! Embedded in floor!

Floor block:  Y=64
Furniture:    Y=65  ← CORRECT! Sits on floor!
```

## MCP Tools

### Furniture
- `furniture_lookup(action="browse/search/get")` - 60+ furniture designs
- `place_furniture(furniture_id, origin_x, origin_y, origin_z)` - Auto-place

### Spatial
- `spatial_awareness_scan` - Find floor/ceiling levels
- `get_surface_level(x, z)` - Ground Y at coordinates

### Building
- `build(commands=[...])` - Manual furniture construction

## Furniture Catalog

Use `furniture_lookup(action="browse")` to see all categories.

### By Category

**Seating:**
- chair, armchair, bench, stool

**Tables:**
- simple_dining_table, coffee_table, corner_table, desk

**Bedroom:**
- bed, nightstand, wardrobe, closet

**Storage:**
- chest, barrel, bookshelf, wall_cabinet

**Lighting:**
- floor_lamp, hanging_lantern, chandelier, wall_sconce

**Kitchen:**
- sink, stove, counter, cabinet

## Workflow

### 1. Scan Room
```python
scan = spatial_awareness_scan(
    center_x=room_x,
    center_y=room_y,
    center_z=room_z,
    radius=8,
    detail_level="medium"
)

floor_y = scan['floor_y']
ceiling_y = scan['ceiling_y']
placement_y = scan['recommendations']['floor_placement_y']
```

### 2. Search Furniture
```python
# Browse categories
furniture_lookup(action="browse")

# Search by keyword
furniture_lookup(action="search", query="table")

# Get specific item
furniture_lookup(action="get", furniture_id="simple_dining_table")
```

### 3. Place Furniture
```python
# Automated placement
place_furniture(
    furniture_id="simple_dining_table",
    origin_x=100,
    origin_y=placement_y,
    origin_z=200,
    preview_only=True  # Check first!
)

# Execute
place_furniture(
    furniture_id="simple_dining_table",
    origin_x=100,
    origin_y=placement_y,
    origin_z=200,
    preview_only=False
)
```

### 4. Add Details with build()
```python
# Decorative details
build(commands=[
    f"/setblock 102 {placement_y} 205 flower_pot",
    f"/setblock 102 {placement_y+1} 205 potted_poppy",
    f"/setblock 104 {placement_y} 208 item_frame[facing=north]",
])
```

## Room Layouts

### Bedroom (5×6)
```
┌──────────────┐
│ [bed]        │
│              │
│ [nightstand] │
│ [wardrobe]   │
└──────────────┘

Placement:
- Bed against wall
- Nightstand beside bed
- Wardrobe opposite wall
- Lamp on nightstand
```

### Living Room (7×9)
```
┌──────────────────┐
│                  │
│ [sofa]           │
│     [coffee_table]
│ [armchair]       │
│                  │
│ [bookshelf]      │
└──────────────────┘

Placement:
- Sofa against wall
- Coffee table in front
- Armchairs angled
- Bookshelf/decor
```

### Dining Room (7×9)
```
┌──────────────────┐
│                  │
│ [chair]          │
│ [table][table]   │
│ [chair]          │
│                  │
│ [cabinet]        │
└──────────────────┘

Placement:
- Table centered
- Chairs around table
- Lantern above table
- Cabinet against wall
```

### Kitchen (5×7)
```
┌────────────────┐
│ [counter]      │
│ [stove]        │
│ [sink]         │
│                │
│ [table][chair] │
└────────────────┘

Placement:
- Counters along wall
- Stove recessed
- Sink with water texture
- Small dining area
```

## Manual Furniture Builds

### Simple Table
```python
build(commands=[
    # Legs (fence posts)
    f"/setblock {x} {y} {z} oak_fence",
    f"/setblock {x+2} {y} {z} oak_fence",
    f"/setblock {x} {y} {z+1} oak_fence",
    f"/setblock {x+2} {y} {z+1} oak_fence",
    # Top (pressure plates)
    f"/fill {x} {y+1} {z} {x+2} {y+1} {z+1} oak_pressure_plate",
])
```

### Chair
```python
build(commands=[
    # Seat (stairs)
    f"/setblock {x} {y} {z} oak_stairs[facing=south]",
    # Back (sign or trapdoor)
    f"/setblock {x} {y+1} {z-1} oak_trapdoor[facing=south,half=bottom,open=true]",
])
```

### Bed (decorative)
```python
build(commands=[
    # Base (slabs)
    f"/fill {x} {y} {z} {x+1} {y} {z+2} oak_slab[type=bottom]",
    # Blanket (carpet)
    f"/fill {x} {y+1} {z} {x+1} {y+1} {z+1} red_carpet",
    # Pillow (wool)
    f"/setblock {x} {y+1} {z+2} white_wool",
    f"/setblock {x+1} {y+1} {z+2} white_wool",
])
```

### Bookshelf Wall
```python
build(commands=[
    # Full bookshelves
    f"/fill {x} {y} {z} {x+3} {y+2} {z} bookshelf",
    # Random gaps for variety
    f"/setblock {x+1} {y+1} {z} oak_planks",
])
```

## Lighting

### Floor Placement
```python
# Floor lamp
build(commands=[
    f"/setblock {x} {y} {z} oak_fence",
    f"/setblock {x} {y+1} {z} lantern",
])
```

### Ceiling Placement
```python
# Get ceiling Y first
ceiling_y = scan['recommendations']['ceiling_placement_y']

# Hanging lantern
build(commands=[
    f"/setblock {x} {ceiling_y} {z} chain",
    f"/setblock {x} {ceiling_y-1} {z} lantern[hanging=true]",
])
```

### Wall Sconce
```python
# Torch on wall
build(commands=[
    f"/setblock {x} {y} {z} wall_torch[facing=north]",
])
```

## Decorative Details

### Carpet Placement
```python
# Area rug
build(commands=[
    f"/fill {x} {y} {z} {x+3} {y} {z+2} red_carpet",
])
```

### Item Frames
```python
# Picture on wall
build(commands=[
    f"/setblock {x} {y} {z} item_frame[facing=north]",
])
```

### Flower Pots
```python
# Potted plant
build(commands=[
    f"/setblock {x} {y} {z} flower_pot",
    f"/setblock {x} {y} {z} potted_oak_sapling",
])
```

## Style Coordination

| Style | Wood | Accents | Textiles |
|-------|------|---------|----------|
| Rustic | Oak, Spruce | Barrels, lanterns | Brown carpet |
| Modern | Birch, Quartz | Sea lanterns | White carpet |
| Medieval | Dark Oak | Chains, anvils | Red carpet |
| Japanese | Bamboo, Spruce | Paper lanterns | Cyan carpet |

## Spacing Guidelines

- **Tables**: 1 block clearance around
- **Chairs**: Push against table
- **Beds**: 1 block on access side
- **Walkways**: 2 blocks minimum
- **Ceiling lights**: Every 4-5 blocks
