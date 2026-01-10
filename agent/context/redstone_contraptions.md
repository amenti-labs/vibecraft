# Redstone Contraptions Guide

Complete reference for redstone mechanisms in Minecraft. Covers circuits, automation, doors, traps, and advanced contraptions.

---

## Redstone Fundamentals

### Signal Basics

```
POWER LEVELS: 0-15
- Redstone dust loses 1 power per block traveled
- Max signal travel: 15 blocks
- Repeaters refresh signal to 15

SIGNAL SOURCES (power level 15):
- Lever (toggle)
- Button (pulse: 1.5s stone, 1s wood)
- Pressure plate (weight-based)
- Tripwire (string-based)
- Daylight detector
- Observer (block change)
- Redstone block (always on)
- Redstone torch (inverted logic)
```

### Component Properties

```
REPEATER:
- Delays: 1, 2, 3, or 4 ticks (0.1s to 0.4s)
- Locks when powered from side
- Refreshes signal strength to 15
- Only accepts signal from back

COMPARATOR:
- Two modes: compare (front unlit) and subtract (front lit)
- Compare: outputs if back >= side
- Subtract: outputs (back - max side)
- Reads container fill levels (0-15 based on fullness)
- Reads item frame rotation

OBSERVER:
- Detects block changes in front
- Outputs 2-tick pulse from back
- Great for BUD switches
- Compact state detection

PISTON:
- Extends/retracts 1 block
- Push limit: 12 blocks
- Sticky piston pulls 1 block back
- Cannot push: obsidian, bedrock, extended pistons
- Spits out blocks if pulse is 1 tick
```

---

## Logic Gates

### NOT Gate (Inverter)
Outputs when input is OFF.

```
Layout (top view):
[input]→[block]→[torch]→[output]

Commands:
/setblock X Y Z redstone_wire
/setblock X+1 Y Z stone
/setblock X+2 Y Z redstone_wall_torch[facing=west]
/setblock X+3 Y Z redstone_wire
```

### OR Gate
Outputs when ANY input is ON.

```
Layout (top view):
[input A]→─┐
           ├→[output]
[input B]→─┘

Commands (simple merge):
/setblock X Y Z redstone_wire        # Input A
/setblock X+1 Y Z redstone_wire      # Junction
/setblock X Y+1 Z-1 redstone_wire    # Input B (elevated)
/setblock X+1 Y+1 Z-1 redstone_wire  # Drops to junction
```

### AND Gate
Outputs ONLY when ALL inputs are ON.

```
Layout (top view - torch AND):
[input A]→[block+torch]─┐
                        ├→[block]→[torch]→[output]
[input B]→[block+torch]─┘

Commands:
# Input A side
/setblock X Y Z redstone_wire
/setblock X+1 Y Z stone
/setblock X+1 Y+1 Z redstone_torch

# Input B side  
/setblock X Y Z+2 redstone_wire
/setblock X+1 Y Z+2 stone
/setblock X+1 Y+1 Z+2 redstone_torch

# Output (double inversion)
/setblock X+2 Y Z+1 stone
/setblock X+3 Y Z+1 redstone_wall_torch[facing=west]
```

### NAND Gate
Outputs when ANY input is OFF.

```
Same as AND gate but without final inverter.
Compact: 2 torches pointing at same block.
```

### XOR Gate
Outputs when inputs are DIFFERENT.

```
Layout (compact XOR):
Uses comparators in subtract mode.

[A]→[comparator→]→┐
                   ├→[OR]→[output]
[B]→[comparator→]→┘

Commands (3x3 footprint):
/setblock X Y Z comparator[facing=east,mode=subtract]
/setblock X Y Z+2 comparator[facing=east,mode=subtract]
/setblock X+2 Y Z+1 redstone_wire
```

### NOR Gate
Outputs ONLY when ALL inputs are OFF.

```
Layout:
[input A]→─┐
           ├→[block]→[torch]→[output]
[input B]→─┘

Simple: merge inputs with OR, then invert.
```

---

## Memory Circuits

### RS Latch (Set/Reset)
Remembers state. Set turns ON, Reset turns OFF.

```
Layout (torch feedback):
[Set]→[block A+torch]←→[block B+torch]←[Reset]
           ↓                   ↓
        [Output]           [Output']

Commands (compact):
/setblock X Y Z stone                    # Block A
/setblock X+2 Y Z stone                  # Block B
/setblock X+1 Y Z redstone_wall_torch[facing=west]   # Torch A
/setblock X+1 Y Z+1 redstone_wall_torch[facing=east] # Torch B (opposite)
```

### T Flip-Flop (Toggle)
Changes state on each input pulse.

```
Layout (dropper-based, most reliable):
[input]→[dropper↔dropper]→[comparator]→[output]
         └──item───┘

How it works:
- Droppers face each other
- Single item bounces between them
- Comparator reads which dropper has item

Commands:
/setblock X Y Z dropper[facing=east]
/setblock X+1 Y Z dropper[facing=west]
# Add 1 item to either dropper
/setblock X+2 Y Z comparator[facing=east]
```

### D Flip-Flop (Data Latch)
Captures input state on clock edge.

```
Uses RS latch with edge detector.
Stores data input when clock pulses.
Common in combination locks.
```

### Counter
Counts input pulses.

```
Dropper chain method:
- Each dropper holds items
- Comparator reads fill level
- Full dropper = count threshold reached

Hopper counter:
- Items flow through hopper chain
- Comparators read progress
- More items = higher count
```

---

## Timing Circuits

### Repeater Clock
Simple oscillator.

```
Layout (2-tick clock):
[repeater→]→[repeater→]→[repeater→]↓
↑←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←┘

Minimum: 2 repeaters at 1 tick each = 4 tick period (0.4s)

Commands (3-repeater clock):
/setblock X Y Z repeater[facing=east,delay=1]
/setblock X+1 Y Z repeater[facing=south,delay=1]
/setblock X+1 Y Z+1 repeater[facing=west,delay=1]
/setblock X Y Z+1 redstone_wire
```

### Hopper Clock
Precise, adjustable timing.

```
Layout:
[hopper→]→[hopper]
    ↑         ↓
    └←comparator←┘

Timing = items × 0.4s per item
64 items = ~25 seconds

Commands:
/setblock X Y Z hopper[facing=east]
/setblock X+1 Y Z hopper[facing=west]
/setblock X+2 Y Z comparator[facing=west]
/setblock X+2 Y Z+1 redstone_wire
# Connect wire back to first hopper with redstone
```

### Pulse Extender
Lengthens short pulses.

```
Repeater chain method:
[input]→[repeater]→[repeater]→[repeater]→[output]
                                          ↓
           [←←←←←←←←←←←←←←←←←redstone←←←←←┘]

Each repeater adds 1-4 ticks.
Merge input and delayed signal with OR.
```

### Pulse Limiter
Shortens long signals.

```
Layout:
[input]→────────────→[AND]→[output]
    ↓                  ↑
    └→[delay+NOT]──────┘

Outputs only for duration of delay.
```

### Edge Detector (Rising)
Outputs brief pulse when input turns ON.

```
Layout:
[input]→──────→[AND]→[output]
    ↓            ↑
    └→[delay+NOT]┘

Commands:
/setblock X Y Z redstone_wire              # Input
/setblock X+1 Y Z redstone_wire            # To AND
/setblock X Y Z+1 repeater[facing=east,delay=2]  # Delay
/setblock X+1 Y Z+1 stone
/setblock X+2 Y Z+1 redstone_wall_torch[facing=west]  # NOT
/setblock X+2 Y Z redstone_wire            # AND junction
```

### Edge Detector (Falling)
Outputs brief pulse when input turns OFF.

```
Same as rising, but use comparator:
[input]→[comparator in subtract mode]→[output]
    ↓
    └→[delay]→[to comparator side]

When input drops, delayed signal > input briefly.
```

---

## Piston Contraptions

### Piston Door (2x2)
Classic hidden door.

```
Layout (cross-section, door closed):
[wall][door][door][wall]
  ↑    ←P  P→    ↑
pistons push door blocks

Opening sequence:
1. Pistons retract (pull door blocks)
2. Pistons extend downward (push blocks down)
3. Or use sticky pistons to pull directly

Commands (simple retract version):
# Door blocks
/setblock X Y Z stone_bricks
/setblock X Y+1 Z stone_bricks

# Pistons behind (sticky, facing toward door)
/setblock X-1 Y Z sticky_piston[facing=east]
/setblock X-1 Y+1 Z sticky_piston[facing=east]

# Redstone behind pistons
/setblock X-2 Y Z redstone_wire
/setblock X-2 Y+1 Z redstone_wire
```

### Piston Door (3x3)
Larger flush door.

```
Requires sequenced pistons:
1. Top row retracts
2. Middle row retracts
3. Bottom row retracts
4. All slide sideways

Use repeater delays:
- Top: 0 tick delay
- Middle: 2 tick delay
- Bottom: 4 tick delay
```

### Piston Extender (Double)
Pushes block 2 spaces.

```
Layout (side view):
[piston A→][piston B→][block]

Sequence:
1. Power A (extends, pushing B and block)
2. Power B (extends, pushing block further)
3. Retract B first
4. Retract A

Commands:
/setblock X Y Z sticky_piston[facing=east]
/setblock X+1 Y Z sticky_piston[facing=east]
/setblock X+2 Y Z stone
# Add delays for proper sequencing
```

### Piston Extender (Triple)
Pushes block 3 spaces. Same principle, more pistons and delays.

### Flying Machine
Self-propelling mechanism.

```
Basic 2-way flying machine:
[slime][observer][slime][piston→]
         ↑
    (detects motion)

Commands:
/setblock X Y Z slime_block
/setblock X+1 Y Z observer[facing=east]
/setblock X+2 Y Z slime_block
/setblock X+3 Y Z sticky_piston[facing=east]

Start by updating observer (place block in front of it).
```

---

## Automatic Farms

### Sugar Cane Farm

```
Layout (row):
[water][dirt][sugar_cane][piston→][observer]
              ↑                        ↓
         (grows here)          (detects growth)

Observer detects cane growth → activates piston → breaks cane.

Commands (one cell):
/setblock X Y Z water
/setblock X+1 Y Z dirt
# Sugar cane grows naturally on dirt next to water
/setblock X+3 Y+2 Z observer[facing=west]
/setblock X+2 Y+2 Z sticky_piston[facing=west]
```

### Pumpkin/Melon Farm

```
Layout:
[stem][dirt][observer]
       ↑        ↓
   (grows)  (detects)
       ↓
    [piston]→[hoppers]→[chest]

Observer watches dirt block, piston breaks fruit.
```

### Chicken Farm (Egg-based)

```
Hopper feeds eggs to dispenser.
Dispenser shoots eggs at wall.
Baby chickens fall through slabs.
Adults too big, stay on slabs.
Lava above adults cooks them.
Cooked chicken drops to hopper.
```

### Iron Farm (Simple)

```
Villager pods with beds.
Zombie scares villagers.
Iron golem spawns to protect.
Golem falls into lava/cacti.
Iron drops to hoppers.

Critical spacing:
- Villagers need line of sight to zombie
- 3+ villagers per pod
- 3+ beds per pod
- Zombie at least 3 blocks away
```

---

## Traps & Defense

### Arrow Trap

```
Layout:
[pressure_plate]→[wire]→[dispenser→]
                           ↑
                        (arrows)

Player steps on plate, dispenser fires arrows.

Commands:
/setblock X Y Z stone_pressure_plate
/setblock X+1 Y-1 Z redstone_wire
/setblock X+5 Y Z dispenser[facing=south]
# Fill dispenser with arrows
```

### Lava Trap

```
Layout:
[tripwire_hook]─────[tripwire_hook]
        ↓                   ↓
    [wire]              [wire]
        └→[piston]→[block holding lava]

Tripwire activates piston, releases lava.
```

### TNT Trap

```
Hidden TNT under pressure plate:
[stone]
[tnt]
[stone_pressure_plate]

Plate powers TNT, 4-second fuse, explosion.

Commands:
/setblock X Y-1 Z tnt
/setblock X Y Z stone_pressure_plate
```

### Pitfall Trap

```
Pistons retract floor:
[floor][floor][floor]
  ↑P    ↑P    ↑P
  
Trigger → pistons retract → victim falls.
Add water at bottom to collect items.
```

---

## Advanced Contraptions

### Combination Lock

```
Uses levers in specific positions.
Each lever connects to AND gate.
Only correct combination outputs signal.

Example (3-lever):
[lever1]→[NOT if should be OFF]→┐
[lever2]→[NOT if should be OFF]→├→[AND]→[output]
[lever3]→[NOT if should be OFF]→┘

Secret: which levers need NOT gates = the code.
```

### Item Sorter

```
Hopper filters by item type:
[input hopper]
     ↓
[filter hopper (locked)]→[comparator]→[redstone]→[unlock signal]
     ↓
[output hopper]→[chest]

Filter hopper contains:
- 1 target item in first slot
- 21 of same item in other slots (to reach comparator threshold)

Commands (one filter):
/setblock X Y Z hopper[facing=south]           # Input
/setblock X Y-1 Z hopper[facing=east]          # Filter
/setblock X+1 Y-1 Z comparator[facing=east]    # Detect
/setblock X+2 Y-1 Z repeater[facing=east]      # Boost signal
/setblock X+3 Y-1 Z redstone_torch             # Invert
/setblock X+1 Y-2 Z hopper[facing=south]       # Output
```

### Piston Elevator

```
0-tick piston trick:
Fast pulse causes piston to extend and retract instantly.
Block gets launched upward.

Layout (column):
[piston↑]
[slime]
  ...
[piston↑]
[slime]

Timed pulses launch player/entity up column.
```

### Ender Pearl Stasis Chamber

```
Holds ender pearl in bubble column until needed.
Breaking bubble column = pearl lands = player teleports.

Layout:
[soul_sand][water column][player throws pearl in]
    ↓
[piston] ← remote trigger

Piston blocks water, pearl falls, player teleports.
```

### Shulker Box Loader

```
Automatic shulker box filling:
1. Hopper feeds items into shulker box
2. Comparator detects when full
3. Piston breaks shulker box
4. New empty shulker dispensed

Requires: droppers, hoppers, pistons, comparators.
```

---

## Redstone Block States Reference

### Component Placement

```
REDSTONE WIRE:
redstone_wire  # Automatically connects to neighbors
# Power property: 0-15

REPEATER:
repeater[facing=north,delay=1,locked=false,powered=false]
# facing: direction output points
# delay: 1-4 ticks
# locked: powered from side
# powered: currently active

COMPARATOR:
comparator[facing=south,mode=compare,powered=false]
# mode: compare or subtract
# compare: output if back >= side
# subtract: output back - side

PISTON:
piston[facing=up,extended=false]
sticky_piston[facing=east,extended=true]
# facing: direction it pushes
# extended: currently pushed out

OBSERVER:
observer[facing=north,powered=false]
# facing: direction it watches
# powered: briefly true when triggered

DISPENSER/DROPPER:
dispenser[facing=south,triggered=false]
dropper[facing=down,triggered=false]
# facing: direction it fires/drops

HOPPER:
hopper[facing=south,enabled=true]
# facing: direction items flow
# enabled: true = items flow, false = locked

REDSTONE TORCH:
redstone_torch[lit=true]                    # On ground
redstone_wall_torch[facing=north,lit=true]  # On wall
# facing (wall): direction it points (from wall it's on)

LEVER:
lever[face=floor,facing=north,powered=false]
lever[face=wall,facing=east,powered=true]
lever[face=ceiling,facing=south,powered=false]
# face: floor, wall, or ceiling
# facing: direction lever points when OFF

BUTTON:
stone_button[face=wall,facing=north,powered=false]
oak_button[face=floor,facing=east,powered=true]
# Same as lever
```

### Attachment Rules

```
WALL ATTACHMENTS (torch, button, lever[face=wall]):
facing=north → block must be to SOUTH (Z+1)
facing=south → block must be to NORTH (Z-1)
facing=east  → block must be to WEST (X-1)
facing=west  → block must be to EAST (X+1)

FLOOR ATTACHMENTS:
Need solid block at Y-1

REDSTONE ON BLOCKS:
Wire, repeaters, comparators need solid block at Y-1
```

---

## Tips & Best Practices

### Debugging Redstone

```
1. Check signal strength
   - Use target block to see exact power level
   - Redstone ore also shows power

2. Check timing
   - Add temporary repeaters to slow down
   - Observers help detect when things fire

3. Common issues:
   - Signal too weak (add repeater)
   - Signal too slow/fast (adjust delays)
   - Wrong facing direction
   - Component not attached to block
```

### Optimization

```
1. Minimize dust
   - Dust causes lag (recalculates paths)
   - Use direct component connections where possible

2. Use instant wire
   - Pistons + observer chains
   - Much faster than dust

3. Chunk loading
   - Redstone unloads when chunk unloads
   - Use spawn chunks for always-on machines
   - Or use chunk loaders (nether portal trick)
```

### Compact Designs

```
1. Vertical stacking
   - Use observers for vertical signal
   - Torch towers for inverting signals

2. 0-tick pulses
   - Comparator + piston tricks
   - Instant on/off for fast circuits

3. Slime/honey blocks
   - Move multiple components at once
   - Create moving circuits
```

---

## Quick Reference Tables

### Signal Travel

| Method | Distance | Speed |
|--------|----------|-------|
| Redstone dust | 15 blocks | 1 block/tick |
| Repeater chain | Unlimited | 1-4 ticks per repeater |
| Instant wire (observer) | 15+ blocks | Instant |
| Torch ladder | Unlimited | 1 tick per torch |

### Component Delays

| Component | Delay |
|-----------|-------|
| Redstone dust | ~0 ticks (instant) |
| Repeater | 1-4 ticks |
| Comparator | 1 tick |
| Torch | 1 tick |
| Piston | 0-3 ticks |
| Observer | 2 ticks |
| Dispenser/Dropper | 2 ticks |

### Power Levels by Source

| Source | Power Level |
|--------|-------------|
| Lever (on) | 15 |
| Button (pressed) | 15 |
| Redstone block | 15 |
| Pressure plate (full) | 15 |
| Daylight sensor (max) | 15 |
| Comparator reading full chest | 15 |
| Comparator reading item frame | 1-8 |

---

**Use with RedScript DSL for automated circuit building!**
