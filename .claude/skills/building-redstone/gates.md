# Logic Gates Reference

Detailed implementations of all logic gates.

## NOT Gate (Inverter)

Outputs when input is OFF.

```
Layout (top view):
[input]→[solid]→[torch]→[output]

Build sequence:
1. /setblock X Y Z redstone_wire              # Input
2. /setblock X+1 Y Z stone                    # Solid block
3. /setblock X+2 Y Z redstone_wall_torch[facing=west]  # Torch
4. /setblock X+3 Y Z redstone_wire            # Output
```

## OR Gate

Outputs when ANY input is ON.

```
Layout (top view):
[A]→─┐
     ├→[output]
[B]→─┘

Simple merge at junction block.
Both wires connect to same output wire.
```

## NOR Gate

Outputs ONLY when ALL inputs are OFF (OR + NOT).

```
Layout:
[A]→─┐
     ├→[block]→[torch]→[output]
[B]→─┘

Build:
1. Merge inputs to single wire
2. Wire powers solid block
3. Torch on block (inverts)
```

## AND Gate

Outputs ONLY when ALL inputs are ON.

```
Layout (torch-based):
[A]→[block]→[torch A]─┐
                       ├→[block]→[torch]→[output]
[B]→[block]→[torch B]─┘

Build sequence:
1. Input A wire to solid block
2. Torch on that block (inverts A)
3. Input B wire to solid block  
4. Torch on that block (inverts B)
5. Both torches power junction block
6. Final torch on junction (double inversion = AND)
```

Alternative (comparator AND):
```
[A]→─────────→[comparator]→[output]
                   ↑
[B]→─────────────→│

Comparator in compare mode.
Output only if back signal >= side signal.
If both 15, output is 15.
```

## NAND Gate

Outputs when ANY input is OFF (AND + NOT).

```
Same as AND but without final inverter.
Two torches point at same block.
Block output is NAND of inputs.
```

## XOR Gate

Outputs when inputs are DIFFERENT.

```
Layout (comparator subtraction):
[A]→[comparator subtract]→─┐
                            ├→[output]
[B]→[comparator subtract]→─┘

Each comparator:
- Back = one input
- Side = other input
- Output = |A-B| (positive only)

OR the two comparator outputs.
```

Compact XOR (3x3):
```
1. /setblock X Y Z comparator[facing=east,mode=subtract]
2. /setblock X Y Z+2 comparator[facing=east,mode=subtract]  
3. Connect A to back of first, side of second
4. Connect B to back of second, side of first
5. OR the outputs at X+2 Y Z+1
```

## XNOR Gate

Outputs when inputs are SAME (XOR + NOT).

```
XOR gate output → torch → output
```

## Implications Gate (A → B)

Outputs when A implies B (NOT A OR B).

```
[A]→[NOT]→─┐
            ├→[output]
[B]→───────┘

If A is true, B must be true.
If A is false, output is true regardless.
```

## RS NOR Latch

Set-Reset memory using NOR gates.

```
     ┌───[torch A]←──[block A]←─[Set]
     │        ↓
     │   [block B]→[torch B]
     │        ↑
     └───────→┘
              └─→[Reset]

Feedback loop creates memory.
Set pulse → output ON (stays)
Reset pulse → output OFF (stays)
```

## Building Tips

### Compactness
- Use observers for vertical signal transfer
- Comparators are more compact than torch logic
- Slabs/stairs can carry signal in tight spaces

### Reliability  
- Avoid 1-tick pulses unless intended
- Repeaters prevent signal decay
- Lock repeaters to hold state

### Testing
1. Build one gate at a time
2. Test with lever before connecting
3. Add indicators (redstone lamp) for debugging
