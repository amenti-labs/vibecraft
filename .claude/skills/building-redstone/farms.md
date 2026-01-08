# Automatic Farm Designs

Complete farm builds using redstone automation.

## Sugar Cane Farm (Zero-Tick)

Observer detects cane growth, piston breaks it.

```python
# Single cell
build(commands=[
    # Water source
    "/setblock X Y Z water",
    # Dirt for cane
    "/setblock X+1 Y Z dirt",
    # Observer watching cane position
    "/setblock X+3 Y+2 Z observer[facing=west]",
    # Piston to break cane
    "/setblock X+2 Y+2 Z sticky_piston[facing=west]",
    # Connect observer to piston
    "/setblock X+3 Y+2 Z+1 redstone_wire",
])

# Place sugar cane manually or wait for growth
# Hopper minecart below for collection
```

### Tileable Design
```
Repeat every 2 blocks on X axis:
[water][dirt][cane][piston][observer]
[water][dirt][cane][piston][observer]
...

Collection: hopper minecart rail below dirt row
```

## Pumpkin/Melon Farm

Observer watches growth block, piston harvests.

```python
build(commands=[
    # Farmland for stem
    "/setblock X Y Z farmland",
    # Dirt for fruit growth
    "/setblock X+1 Y Z dirt",
    # Observer watching growth spot
    "/setblock X+1 Y+1 Z observer[facing=down]",
    # Piston to break fruit
    "/setblock X+2 Y Z sticky_piston[facing=west]",
    # Connect observer to piston
    "/setblock X+1 Y+2 Z redstone_wire",
    "/setblock X+2 Y+2 Z redstone_wire",
])
```

### Double-Sided Design
```
[piston][growth][stem][growth][piston]
         ↑                ↑
    [observer]       [observer]

Stem can grow fruit on either side.
Both observers connect to respective pistons.
```

## Chicken Farm (Egg-Based)

Chickens lay eggs → dispenser shoots → baby chickens → grow → lava cooks.

```python
build(commands=[
    # Chicken containment (2x2x2 glass box)
    "/fill X Y Z X+2 Y+2 Z+2 glass hollow",
    # Hopper floor to collect eggs
    "/setblock X+1 Y Z+1 hopper[facing=south]",
    # Dispenser shoots eggs into cooking area
    "/setblock X+1 Y-1 Z+3 dispenser[facing=north]",
    # Slab ceiling (babies fall through, adults don't)
    "/setblock X+1 Y-1 Z+4 stone_slab[type=bottom]",
    # Lava above slab (cooks adults)
    "/setblock X+1 Y Z+4 lava",
    # Collection hopper below
    "/setblock X+1 Y-2 Z+4 hopper[facing=south]",
    "/setblock X+1 Y-3 Z+4 chest[facing=south]",
])

# Clock to fire dispenser
# Eggs → dispenser → 1/8 chance of chicken
```

## Iron Farm (Simple)

Villagers + zombie = iron golem spawns.

```
Layout (side view):
[bed][bed][bed]     ← Villager pod (3 beds)
[villager pods]      ← 3+ villagers with line of sight
    ↓
[zombie]             ← Scares villagers (3+ blocks away)
    ↓
[spawn platform]     ← Golem spawns here
    ↓
[lava/cacti]         ← Kills golem
    ↓
[hoppers]→[chest]    ← Collects iron
```

### Key Requirements
- 3+ villagers per pod
- 3+ beds per pod
- Villagers must see zombie
- Zombie must be 3+ blocks from villagers
- Spawn platform clear of blocks above

## Crop Farm (Wheat/Carrot/Potato)

Water stream harvests, hopper collects.

```python
build(commands=[
    # 9x9 farmland with water center
    "/fill X Y Z X+8 Y Z+8 farmland",
    "/setblock X+4 Y Z+4 water",
    # Dispensers with water buckets
    "/setblock X-1 Y+1 Z+4 dispenser[facing=east]",
    # Redstone clock triggers harvest
    # Water flows, breaks crops
    # Hopper line at end collects
    "/fill X+9 Y-1 Z X+9 Y-1 Z+8 hopper[facing=south]",
])
```

## Mob Farm (Spawner-Based)

Dark room spawns mobs, water pushes to kill chamber.

```
[dark room 9x9x3]
    ↓ (water channels)
[collection point]
    ↓
[drop shaft 22+ blocks]
    ↓
[landing pad]
    ↓
[hoppers]→[chest]
```

### Key Points
- Light level 0 in spawn room
- Water pushes mobs to edge
- 22-block drop = 1-hit kill
- Trapdoors fool mob pathfinding

## Item Sorter

Hopper filtering system.

```python
# Single filter cell
build(commands=[
    # Input hopper (items flow down)
    "/setblock X Y Z hopper[facing=south]",
    # Filter hopper (locked by default)
    "/setblock X Y-1 Z hopper[facing=east]",
    # Comparator reads filter hopper
    "/setblock X+1 Y-1 Z comparator[facing=east]",
    # Redstone dust to repeater
    "/setblock X+2 Y-1 Z redstone_wire",
    # Repeater boosts signal
    "/setblock X+3 Y-1 Z repeater[facing=east]",
    # Torch inverts (unlocks hopper when item detected)
    "/setblock X+4 Y-1 Z redstone_torch",
    # Output hopper
    "/setblock X Y-2 Z hopper[facing=south]",
    # Output chest
    "/setblock X Y-3 Z chest[facing=south]",
])

# Filter hopper contains:
# - Slot 1: 1x target item
# - Slots 2-5: 21x target item each (or junk items to fill)
# Total: 22 items to trigger comparator at right level
```

## Wool Farm

Sheep regrow wool, observer detects, dispenser shears.

```python
build(commands=[
    # Sheep pen (glass walls)
    "/fill X Y Z X+3 Y+2 Z+3 glass hollow",
    # Grass floor (sheep eat to regrow wool)
    "/fill X+1 Y Z+1 X+2 Y Z+2 grass_block",
    # Observer watching sheep
    "/setblock X+4 Y+1 Z+2 observer[facing=west]",
    # Dispenser with shears
    "/setblock X+4 Y+1 Z+1 dispenser[facing=west]",
    # Connect observer to dispenser
    "/setblock X+4 Y+2 Z+1 redstone_wire",
    "/setblock X+4 Y+2 Z+2 redstone_wire",
])
```

## Honey Farm

Bees fill hive, dispenser harvests.

```
[hive][dispenser with bottle]
   ↓
[observer facing hive]
   ↓
[redstone to dispenser]

Observer detects honey_level=5, dispenser bottles it.
```

## Performance Tips

1. **Chunk loading**: Farms only work in loaded chunks
2. **Mob caps**: Too many mobs stop spawns
3. **Hopper lag**: Minimize hopper count
4. **Water streams**: Use ice for faster flow
5. **Clock speed**: Slower clocks = less lag
