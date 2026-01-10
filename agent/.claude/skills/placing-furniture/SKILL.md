---
name: placing-furniture
description: Places furniture and decorates Minecraft interiors using VibeCraft MCP tools. Use when furnishing rooms, placing tables, chairs, beds, lamps, decorations, or designing interior spaces. Handles furniture positioning, spatial awareness, and style coordination.
---

# Placing Furniture

## Critical: SCAN BEFORE PLACING

Avoid furniture embedded in floor!

```python
# 1. Scan area
scan = spatial_awareness_scan(center_x=100, center_y=65, center_z=200, radius=5, detail_level="medium")

# 2. Get placement Y from recommendations
placement_y = scan['recommendations']['floor_placement_y']  # e.g., 65

# 3. Place furniture AT that Y
place_furniture(furniture_id="simple_dining_table", origin_x=100, origin_y=placement_y, origin_z=200)
```

**Common mistake**: Floor at Y=64, furniture at Y=64 = EMBEDDED! Use Y=65 (on floor).

## MCP Tools
- `furniture_lookup(action="browse/search/get")` - 60+ designs
- `place_furniture(furniture_id, origin_x, origin_y, origin_z)` - Auto-place
- `spatial_awareness_scan` - Find floor/ceiling levels
- `build(commands=[...])` - Manual construction

## Furniture Categories

**Seating**: chair, armchair, bench, stool
**Tables**: simple_dining_table, coffee_table, desk
**Bedroom**: bed, nightstand, wardrobe
**Storage**: chest, barrel, bookshelf, wall_cabinet
**Lighting**: floor_lamp, hanging_lantern, chandelier, wall_sconce
**Kitchen**: sink, stove, counter, cabinet

## Workflow

```python
# 1. Scan room
scan = spatial_awareness_scan(center_x=X, center_y=Y, center_z=Z, radius=8, detail_level="medium")
placement_y = scan['recommendations']['floor_placement_y']

# 2. Search furniture
furniture_lookup(action="browse")
furniture_lookup(action="search", query="table")

# 3. Place (preview first!)
place_furniture(furniture_id="simple_dining_table", origin_x=100, origin_y=placement_y, origin_z=200, preview_only=True)
place_furniture(furniture_id="simple_dining_table", origin_x=100, origin_y=placement_y, origin_z=200)

# 4. Add details
build(commands=[f"/setblock 102 {placement_y} 205 flower_pot"])
```

## Room Layouts

**Bedroom (5×6)**: Bed against wall, nightstand beside, wardrobe opposite, lamp on nightstand
**Living (7×9)**: Sofa against wall, coffee table in front, armchairs angled, bookshelf
**Dining (7×9)**: Table centered, chairs around, lantern above, cabinet against wall
**Kitchen (5×7)**: Counters along wall, stove recessed, sink with water, small dining area

## Manual Builds

**Table**: Fence posts as legs + pressure plates on top
**Chair**: Stairs block + trapdoor back
**Bed**: Slabs base + carpet blanket + wool pillows
**Bookshelf wall**: Fill with bookshelf, random oak_planks gaps

## Lighting

**Floor**: `oak_fence` + `lantern` on top
**Ceiling**: `chain` + `lantern[hanging=true]` (use ceiling_placement_y from scan)
**Wall**: `wall_torch[facing=north]`

## Decorative Details
- Area rug: `/fill X Y Z X+3 Y Z+2 red_carpet`
- Picture: `/setblock X Y Z item_frame[facing=north]`
- Potted plant: `/setblock X Y Z potted_oak_sapling`

## Style Coordination

| Style | Wood | Accents | Textiles |
|-------|------|---------|----------|
| Rustic | Oak, Spruce | Barrels, lanterns | Brown carpet |
| Modern | Birch, Quartz | Sea lanterns | White carpet |
| Medieval | Dark Oak | Chains, anvils | Red carpet |

## Spacing
- Tables: 1 block clearance around
- Chairs: Push against table
- Beds: 1 block on access side
- Walkways: 2 blocks minimum
- Ceiling lights: Every 4-5 blocks
