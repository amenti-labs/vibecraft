---
name: building-redstone
description: Builds redstone circuits, mechanisms, and automation in Minecraft using VibeCraft MCP tools. Use when building logic gates, memory circuits, piston doors, automatic farms, item sorters, clocks, or any redstone contraption.
---

# Building Redstone

Build redstone circuits and automation using VibeCraft MCP tools.

## Critical Rule: Block Placement Order

**Support blocks FIRST, then dependent blocks!**

Blocks drop as items if their support doesn't exist:

```
WRONG ORDER (breaks!):        CORRECT ORDER (works!):
1. redstone_wire              1. solid blocks (platform)
2. button                     2. solid blocks (walls)
3. solid blocks               3. redstone_wire
   → Wire breaks!             4. button (on wall)
```

## Attachment Rules

```
BLOCK TYPE              SUPPORT LOCATION
─────────────────────────────────────────
redstone_wire           Y-1 (block below)
repeater/comparator     Y-1 (block below)
redstone_wall_torch     Same Y, offset by facing
stone_button            Same Y, offset by facing
wall_sign               Same Y, offset by facing
carpet/pressure_plate   Y-1 (block below)
```

**Wall torch/button facing:**
- `facing=east` → block to WEST (X-1)
- `facing=west` → block to EAST (X+1)
- `facing=north` → block to SOUTH (Z+1)
- `facing=south` → block to NORTH (Z-1)

## MCP Tools

Use `build()` for redstone circuits:

```python
build(commands=[
    # Phase 1: Support blocks
    "/fill X Y Z X2 Y Z2 stone",
    # Phase 2: Redstone
    "/setblock X Y+1 Z redstone_wire",
    # Phase 3: Attachments
    "/setblock X+1 Y+1 Z stone_button[facing=west,face=wall]",
])
```

## Logic Gates

### NOT (Inverter)
```
[input]→[block]→[torch]→[output]

/setblock X Y Z redstone_wire
/setblock X+1 Y Z stone
/setblock X+2 Y Z redstone_wall_torch[facing=west]
```

### OR Gate
```
[A]→─┐
     ├→[output]
[B]→─┘

Merge two wires at same block.
```

### AND Gate
```
[A]→[block+torch]─┐
                  ├→[block]→[torch]→[output]
[B]→[block+torch]─┘

Two torches pointing at same block, then invert.
```

### XOR Gate
```
[A]→[comparator subtract]→┐
                           ├→[OR]→[output]
[B]→[comparator subtract]→┘
```

For detailed gate implementations, see [gates.md](gates.md).

## Memory Circuits

### RS Latch (Set/Reset)
```python
# Two torches in feedback loop
build(commands=[
    "/setblock X Y Z stone",
    "/setblock X+2 Y Z stone",
    "/setblock X+1 Y Z redstone_wall_torch[facing=west]",
    "/setblock X+1 Y Z+1 redstone_wall_torch[facing=east]",
])
```

### T Flip-Flop (Toggle)
```
[input]→[dropper↔dropper]→[comparator]→[output]

Two droppers facing each other with 1 item.
Comparator reads which dropper has item.
```

## Timing Circuits

### Repeater Clock
```python
# 3-repeater clock (minimum stable)
build(commands=[
    "/setblock X Y Z repeater[facing=east,delay=1]",
    "/setblock X+1 Y Z repeater[facing=south,delay=1]",
    "/setblock X+1 Y Z+1 repeater[facing=west,delay=1]",
    "/setblock X Y Z+1 redstone_wire",
])
```

### Hopper Clock
```
[hopper→]→[hopper]
    ↑         ↓
    └←comparator←┘

Timing = items × 0.4s per item
```

## Piston Mechanisms

### 2x2 Piston Door
```python
# Simple retract door
build(commands=[
    # Door blocks
    "/setblock X Y Z stone_bricks",
    "/setblock X Y+1 Z stone_bricks",
    # Pistons (sticky, facing toward door)
    "/setblock X-1 Y Z sticky_piston[facing=east]",
    "/setblock X-1 Y+1 Z sticky_piston[facing=east]",
    # Redstone behind pistons
    "/setblock X-2 Y Z redstone_wire",
    "/setblock X-2 Y+1 Z redstone_wire",
])
```

### Flying Machine
```
[slime][observer][slime][piston→]

Observer detects motion → activates piston → moves assembly
```

## Automatic Farms

### Sugar Cane Farm
```
[water][dirt][cane][piston→][observer]

Observer detects growth → piston breaks cane
```

### Pumpkin/Melon Farm
```
[stem][dirt][observer]
       ↓        ↓
   (grows)  (detects)
       ↓
    [piston]→[hoppers]→[chest]
```

For farm designs, see [farms.md](farms.md).

## Block States Reference

### Repeater
```
repeater[facing=north,delay=1,locked=false,powered=false]
# delay: 1-4 ticks
# locked: powered from side
```

### Comparator
```
comparator[facing=south,mode=compare,powered=false]
# mode: compare or subtract
```

### Piston
```
piston[facing=up,extended=false]
sticky_piston[facing=east,extended=true]
```

### Observer
```
observer[facing=north,powered=false]
# facing: direction it watches
```

### Lever/Button
```
lever[face=wall,facing=north,powered=false]
stone_button[face=wall,facing=east,powered=false]
# face: floor, wall, ceiling
```

## Signal Travel

| Method | Distance | Speed |
|--------|----------|-------|
| Redstone dust | 15 blocks | 1 block/tick |
| Repeater chain | Unlimited | 1-4 ticks each |
| Instant wire (observer) | 15+ blocks | Instant |
| Torch ladder | Unlimited | 1 tick per torch |

## Component Delays

| Component | Delay |
|-----------|-------|
| Redstone dust | ~0 ticks |
| Repeater | 1-4 ticks |
| Comparator | 1 tick |
| Torch | 1 tick |
| Piston | 0-3 ticks |
| Observer | 2 ticks |

## Debugging

1. Check signal strength (target block shows power)
2. Check timing (add repeaters to slow down)
3. Common issues:
   - Signal too weak → add repeater
   - Wrong facing direction
   - Component not attached to block
