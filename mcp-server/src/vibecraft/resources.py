"""Resource content for AI assistance with WorldEdit commands"""

PATTERN_SYNTAX_GUIDE = """# WorldEdit Pattern Syntax Guide

## Basic Patterns
- Single Block: `stone`, `oak_planks`, `red_wool`
- Block States: `oak_stairs[facing=north,half=top]`
- Block NBT: `chest{'Items':[{id:'diamond',Count:1}]}`

## Advanced Patterns
- Random: `50%stone,30%diorite,20%granite`
- Random State: `*oak_log` (all orientations)
- Clipboard: `#clipboard` or `#clipboard@0,5,0`
- Type Apply: `^acacia_planks` (change type, keep state)
- State Apply: `^[waterlogged=true]` (change state, keep type)
- Block Category: `##wool`, `##*slabs`

## Special Syntax
- Sign Text: `oak_sign|Line1|Line2|Line3|Line4`
- Player Head: `player_head|username`
- Mob Spawner: `spawner|zombie`

## Examples
```
//set stone
//set 50%grass_block,30%dirt,20%coarse_dirt
//replace dirt ##wool
//overlay *snow[layers=1]
//set oak_sign|Welcome|to|VibeCraft|!
```
"""

MASK_SYNTAX_GUIDE = """# WorldEdit Mask Syntax Guide

## Basic Masks
- Block Type: `stone`, `!air`, `stone,diorite`
- Existing Blocks: `#existing`
- Solid Blocks: `#solid`
- Block Categories: `##wool`, `##logs`

## Advanced Masks
- Offset: `>stone` (blocks above stone), `<grass_block` (blocks below grass)
- Region: `#region`, `#sel`, `#selection`
- Random: `%50` (50% of blocks)
- Block State: `^[waterlogged=true]`, `^=[powered=false]`
- Expression: `=y<64`, `=x^2+z^2<100`
- Biome: `$plains`, `$desert`
- Surface: `#surface`, `#exposed`

## Mask Combination
- Intersection (AND): `stone grass_block` (space-separated)
- Negation (NOT): `!stone`, `!##wool`

## Examples
```
//replace #existing stone
//set stone -m %50
//replace !air,water stone
//gmask =y<64
//replace ##wool air -m >air
```
"""

EXPRESSION_SYNTAX_GUIDE = """# WorldEdit Expression Syntax Guide

## Variables
- `x`, `y`, `z` - Current position coordinates
- In clipboard: `source_x`, `source_y`, `source_z`

## Operators
- Arithmetic: `+`, `-`, `*`, `/`, `%`, `^` (power)
- Comparison: `<`, `>`, `<=`, `>=`, `==`, `!=`, `~=`
- Logical: `&&`, `||`, `!`

## Math Functions
- Trig: `sin()`, `cos()`, `tan()`, `asin()`, `acos()`, `atan()`
- Utility: `abs()`, `sqrt()`, `cbrt()`, `ceil()`, `floor()`, `round()`
- Special: `min()`, `max()`, `exp()`, `ln()`, `log()`

## Noise Functions
- `perlin()`, `voronoi()`, `ridgedmulti()`

## Constants
- `pi` = 3.14159..., `e` = 2.71828..., `true` = 1, `false` = 0

## Examples
```
//generate stone (y-64)/10
//generate stone x^2+z^2<100
//deform y+=0.2*sin(x*0.1)
//gmask =y<64&&sqrt(x^2+z^2)<50
```
"""

COORDINATE_GUIDE = """# WorldEdit Coordinate System Guide

## Client vs In-Game Commands
From the client bridge, WorldEdit uses comma-separated coordinates:
```
//pos1 100,64,100
//pos2 120,80,120
```

In-game, you can use relative coordinates:
```
~0 ~0 ~0  (current position)
~1 ~0 ~-1 (1 block east, same height, 1 block north)
```

## Coordinate System
- X: East (positive) / West (negative)
- Y: Up (positive) / Down (negative)
- Z: South (positive) / North (negative)

## Build Height Limits (1.18+)
- Minimum Y: -64
- Maximum Y: 319
- Sea Level: 64

## Tips for AI Building
1. Always set pos1 and pos2 before region commands
2. Use absolute coordinates with comma-separated syntax
3. Remember Y=64 is typically ground level
4. Structures should fit within coordinate bounds
"""

COMMON_WORKFLOWS = """# Common WorldEdit Workflows

## 1. Building a Simple Structure
```
# Set the region corners
//pos1 100,64,100
//pos2 110,70,110

# Create walls
//walls stone_bricks

# Add a floor
//set minecraft:oak_planks

# Make it hollow
//hollow 1

# Add a roof
//pos1 100,70,100
//pos2 110,70,110
//set stone_brick_stairs[facing=north]
```

## 2. Creating Terrain
```
# Generate a hill
//pos1 0,64,0
//pos2 30,80,30
//generate stone (30-sqrt((x-15)^2+(z-15)^2))*0.5+y-64<5

# Smooth the terrain
//smooth 5

# Add grass on top
//replace >stone grass_block
```

## 3. Copy and Paste
```
# Select the structure
//pos1 x1,y1,z1
//pos2 x2,y2,z2

# Copy it
//copy

# Move to new location (set a corner first)
//pos1 new_x,new_y,new_z

# Paste
//paste
```

## 4. Replacing Blocks
```
# Replace in selection
//replace old_block new_block

# Replace multiple types
//replace dirt,grass_block stone

# Replace with pattern
//replace stone 50%stone,25%cobblestone,25%andesite
```

## 5. Working with Schematics
```
# Save a structure
//copy
//schem save my_structure

# Load and place
//schem load my_structure
//paste
```
"""

PLAYER_CONTEXT_WARNING = """
⚠️ IMPORTANT: Player Context Commands

Some WorldEdit navigation commands require a player to be logged in and looking at blocks:
- //jumpto - Teleport to block you're looking at
- //thru - Pass through walls
- //ascend / //descend - Move up/down through floors
- //hpos1 / //hpos2 - Set position to block you're looking at
- Navigation wands and tools

**Workarounds:**
- Use coordinate-based commands: /pos1 X,Y,Z and /pos2 X,Y,Z
- Use vanilla /tp for teleportation
- For selections, specify coordinates explicitly

**From Client Bridge:**
✅ Works: //pos1 100,64,100 ; //pos2 200,100,200 ; //set stone ; //copy ; //paste
❌ Requires Player Input: //hpos1 ; //jumpto ; //thru ; //ascend ; //descend

Note: Commands run as the local player, so coordinate-based WorldEdit commands work directly.
"""
