# Minecraft Vanilla Commands Reference

Complete reference for vanilla Minecraft commands useful for building, beyond WorldEdit. These commands work via RCON and complement WorldEdit for precision work.

## Block Placement Commands

### /setblock - Single Block Placement

**Syntax:**
```
/setblock <x> <y> <z> <block>[blockStates] [destroy|keep|replace]
```

**Modes:**
- `replace` (default) - Replace existing block
- `destroy` - Break existing block (drops items)
- `keep` - Only place if air

**Examples:**
```bash
# Basic placement
/setblock 100 64 200 stone

# With block states
/setblock 100 64 200 oak_stairs[facing=north,half=bottom]

# Button on wall
/setblock 100 65 200 oak_button[facing=east,face=wall]

# Hanging lantern
/setblock 100 70 200 lantern[hanging=true]

# Door (two parts)
/setblock 100 64 200 oak_door[facing=south,half=lower,hinge=right]
/setblock 100 65 200 oak_door[facing=south,half=upper,hinge=right]

# Chest facing player
/setblock 100 64 200 chest[facing=north]

# Redstone torch on wall
/setblock 100 65 200 redstone_wall_torch[facing=east]
```

### /fill - Region Fill

**Syntax:**
```
/fill <x1> <y1> <z1> <x2> <y2> <z2> <block>[states] [destroy|hollow|keep|outline|replace]
/fill <x1> <y1> <z1> <x2> <y2> <z2> <block> replace <filter>
```

**Modes:**
- `replace` (default) - Fill entire region
- `destroy` - Fill but drop existing blocks as items
- `keep` - Only fill air blocks
- `hollow` - Fill outer shell, make inside air
- `outline` - Only outer shell, don't modify inside
- `replace <filter>` - Only replace specific block types

**Examples:**
```bash
# Solid floor
/fill 100 64 200 110 64 210 oak_planks

# Hollow room
/fill 100 64 200 110 70 210 stone_bricks hollow

# Just the walls (outline)
/fill 100 64 200 110 70 210 cobblestone outline

# Replace only dirt with grass
/fill 100 60 200 110 64 210 grass_block replace dirt

# Replace stone with random mix
/fill 100 60 200 110 64 210 cobblestone replace stone

# Clear area (fill with air)
/fill 100 64 200 110 70 210 air

# Keep mode - only fill empty spaces
/fill 100 64 200 110 70 210 water keep
```

### /clone - Copy Regions

**Syntax:**
```
/clone <x1> <y1> <z1> <x2> <y2> <z2> <destX> <destY> <destZ> [masked|replace] [force|move|normal]
```

**Filter modes:**
- `replace` (default) - Copy all blocks
- `masked` - Only copy non-air blocks
- `filtered <block>` - Only copy specific block type

**Clone modes:**
- `normal` (default) - Standard copy
- `force` - Allow overlapping regions
- `move` - Copy and clear source

**Examples:**
```bash
# Basic clone
/clone 100 64 200 110 70 210 200 64 200

# Clone only the structure (not air)
/clone 100 64 200 110 70 210 200 64 200 masked

# Move structure (clone + delete original)
/clone 100 64 200 110 70 210 200 64 200 replace move

# Clone with overlap allowed
/clone 100 64 200 110 70 210 105 64 200 replace force
```

---

## Entity Commands

### /summon - Spawn Entities

**Syntax:**
```
/summon <entity> [x] [y] [z] [nbt]
```

**Useful for builds:**
```bash
# Armor stand (statue/decoration)
/summon armor_stand 100 64 200 {Invisible:1b,NoGravity:1b,ShowArms:1b}

# Item frame (wall decoration)
/summon item_frame 100 65 200 {Facing:3,Item:{id:"minecraft:diamond_sword",Count:1b}}

# Painting
/summon painting 100 65 200 {Facing:2,variant:"minecraft:sunset"}

# Invisible marker
/summon marker 100 64 200 {Tags:["my_marker"]}
```

### /kill - Remove Entities

```bash
# Kill all entities of type
/kill @e[type=armor_stand]

# Kill entities in radius
/kill @e[distance=..10]

# Kill entities with tag
/kill @e[tag=temporary]
```

---

## Execute Command (Advanced)

The `/execute` command runs other commands with modified context. Essential for complex builds.

### Basic Syntax
```
/execute <subcommand> ... run <command>
```

### Subcommands

**Positioning:**
```bash
# At specific coordinates
/execute positioned 100 64 200 run setblock ~ ~ ~ stone

# Relative to entity
/execute at @p run setblock ~ ~1 ~ torch

# Facing direction
/execute facing 100 64 200 run setblock ^ ^ ^5 stone
```

**Conditional:**
```bash
# If block exists
/execute if block 100 64 200 stone run say Found stone!

# Unless block exists
/execute unless block 100 64 200 air run setblock 100 65 200 torch

# If blocks match (compare regions)
/execute if blocks 100 64 200 105 68 205 200 64 200 all run say Regions match!
```

**As entity:**
```bash
# Run as each player
/execute as @a run setblock ~ ~-1 ~ glowstone

# Run at each entity position
/execute as @e[type=armor_stand] at @s run setblock ~ ~ ~ redstone_block
```

### Complex Examples

**Place blocks in a line from player facing:**
```bash
/execute at @p anchored eyes facing 100 64 200 run fill ^ ^ ^1 ^ ^ ^10 stone
```

**Replace all stone near player with granite:**
```bash
/execute at @p run fill ~-5 ~-5 ~-5 ~5 ~5 ~5 granite replace stone
```

**Conditional building:**
```bash
# Only place torch if block below is solid
/execute if block 100 63 200 stone run setblock 100 64 200 torch
```

---

## Data Commands (NBT)

### /data - Read/Modify NBT

**Get data:**
```bash
/data get block 100 64 200
/data get block 100 64 200 Items
/data get entity @e[type=armor_stand,limit=1]
```

**Modify data:**
```bash
# Set sign text
/data merge block 100 64 200 {front_text:{messages:['{"text":"Line 1"}','{"text":"Line 2"}','{"text":""}','{"text":""}']}}

# Modify chest contents
/data modify block 100 64 200 Items append value {Slot:0b,id:"minecraft:diamond",Count:64b}

# Set armor stand pose
/data merge entity @e[type=armor_stand,limit=1] {Pose:{RightArm:[0f,0f,0f]}}
```

---

## Particle Commands

Add visual effects to builds:

```bash
# Basic particle
/particle flame 100 65 200 0.5 0.5 0.5 0.01 100

# Dust (custom color) - RGB values 0-1
/particle dust 1 0.5 0 1 100 65 200 0.5 0.5 0.5 0.01 50

# Block break particles
/particle block stone 100 65 200 0.5 0.5 0.5 0 20

# Enchantment particles (magical effect)
/particle enchant 100 65 200 1 1 1 1 100

# Campfire smoke
/particle campfire_cosy_smoke 100 65 200 0.2 0.2 0.2 0.001 10
```

---

## Structure Commands

### /structure - Save/Load Structures

**Save structure:**
```bash
/structure save my_building 100 64 200 110 80 210 true disk
```

**Load structure:**
```bash
/structure load my_building 200 64 200
/structure load my_building 200 64 200 0_degrees none true false
```

**Parameters for load:**
- Rotation: `0_degrees`, `90_degrees`, `180_degrees`, `270_degrees`
- Mirror: `none`, `x`, `z`, `xz`
- Include entities: `true`/`false`
- Include blocks: `true`/`false`

---

## Block State Quick Reference

### Facing Blocks

```bash
# Stairs
oak_stairs[facing=north|south|east|west,half=bottom|top,shape=straight|outer_left|outer_right|inner_left|inner_right]

# Doors
oak_door[facing=north|south|east|west,half=lower|upper,hinge=left|right,open=true|false]

# Trapdoors  
oak_trapdoor[facing=north|south|east|west,half=bottom|top,open=true|false]

# Buttons
oak_button[facing=north|south|east|west,face=floor|ceiling|wall]

# Levers
lever[facing=north|south|east|west,face=floor|ceiling|wall]

# Torches
wall_torch[facing=north|south|east|west]
redstone_wall_torch[facing=north|south|east|west,lit=true|false]

# Chests
chest[facing=north|south|east|west,type=single|left|right]

# Furnace/Blast Furnace/Smoker
furnace[facing=north|south|east|west,lit=true|false]

# Barrels
barrel[facing=north|south|east|west|up|down,open=true|false]

# Dispensers/Droppers
dispenser[facing=north|south|east|west|up|down]

# Observers
observer[facing=north|south|east|west|up|down,powered=true|false]

# Pistons
piston[facing=north|south|east|west|up|down,extended=true|false]
```

### Axis Blocks

```bash
# Logs
oak_log[axis=x|y|z]
stripped_oak_log[axis=x|y|z]

# Pillars
quartz_pillar[axis=x|y|z]
purpur_pillar[axis=x|y|z]

# Chains
chain[axis=x|y|z]

# Hay bales
hay_block[axis=x|y|z]
```

### Slabs

```bash
oak_slab[type=bottom|top|double,waterlogged=true|false]
stone_slab[type=bottom|top|double,waterlogged=true|false]
```

### Walls

```bash
cobblestone_wall[north=none|low|tall,south=none|low|tall,east=none|low|tall,west=none|low|tall,up=true|false]
```

### Fences

```bash
oak_fence[north=true|false,south=true|false,east=true|false,west=true|false,waterlogged=true|false]
```

### Rails

```bash
rail[shape=north_south|east_west|ascending_north|ascending_south|ascending_east|ascending_west|north_east|north_west|south_east|south_west]

powered_rail[shape=...,powered=true|false]
detector_rail[shape=...,powered=true|false]
activator_rail[shape=...,powered=true|false]
```

### Beds

```bash
red_bed[facing=north|south|east|west,part=head|foot,occupied=true|false]
```

### Signs

```bash
oak_sign[rotation=0-15,waterlogged=true|false]
oak_wall_sign[facing=north|south|east|west,waterlogged=true|false]
```

### Redstone

```bash
# Redstone wire
redstone_wire[north=none|side|up,south=none|side|up,east=none|side|up,west=none|side|up,power=0-15]

# Repeater
repeater[facing=north|south|east|west,delay=1-4,locked=true|false,powered=true|false]

# Comparator
comparator[facing=north|south|east|west,mode=compare|subtract,powered=true|false]

# Redstone lamp
redstone_lamp[lit=true|false]
```

### Lanterns & Campfires

```bash
lantern[hanging=true|false,waterlogged=true|false]
soul_lantern[hanging=true|false,waterlogged=true|false]

campfire[facing=north|south|east|west,lit=true|false,signal_fire=true|false]
```

### Pointed Dripstone

```bash
pointed_dripstone[thickness=tip|frustum|middle|base|tip_merge,vertical_direction=up|down,waterlogged=true|false]
```

---

## Command Blocks (Automation)

### Place and Configure

```bash
# Place command block
/setblock 100 64 200 command_block

# Set command (use /data)
/data merge block 100 64 200 {Command:"/say Hello!"}

# Chain command block
/setblock 100 64 201 chain_command_block[facing=south]{Command:"/say Second!",auto:1b}

# Repeating command block
/setblock 100 64 200 repeating_command_block{Command:"/particle flame ~ ~1 ~ 0.2 0.2 0.2 0.01 5",auto:1b}
```

### Command Block Types

| Type | Behavior |
|------|----------|
| `command_block` | Impulse - Runs once when activated |
| `chain_command_block` | Chain - Runs when previous in chain runs |
| `repeating_command_block` | Repeat - Runs every tick when active |

---

## Performance Tips

1. **Use /fill for bulk operations** - Much faster than individual /setblock
2. **Clone instead of rebuild** - /clone is faster than recreating blocks
3. **Avoid /fill replace in tick loops** - Can cause lag
4. **Use structure blocks for templates** - More efficient than commands
5. **Batch commands** - Execute multiple operations before giving updates

## Common Patterns

### Floor with Border

```bash
# Fill floor
/fill 100 64 200 120 64 220 oak_planks
# Add border
/fill 100 64 200 120 64 200 stone_bricks
/fill 100 64 220 120 64 220 stone_bricks
/fill 100 64 200 100 64 220 stone_bricks
/fill 120 64 200 120 64 220 stone_bricks
```

### Room with Door

```bash
# Hollow room
/fill 100 64 200 110 70 210 stone_bricks hollow
# Cut door hole
/fill 105 64 200 106 65 200 air
# Place door
/setblock 105 64 200 oak_door[facing=south,half=lower,hinge=left]
/setblock 105 65 200 oak_door[facing=south,half=upper,hinge=left]
```

### Window with Frame

```bash
# Frame
/fill 102 66 200 104 68 200 stone_brick_slab
# Glass
/fill 103 67 200 103 67 200 glass_pane
```

### Spiral Pattern

```bash
# Use execute with positioned for spirals
/execute positioned 100 64 200 run setblock ~2 ~ ~ stone
/execute positioned 100 64 200 run setblock ~1 ~1 ~1 stone
/execute positioned 100 64 200 run setblock ~ ~2 ~2 stone
# ... continue pattern
```
