# Minecraft Building Guide for AI

Build structures in Minecraft using the `build()` tool. Two approaches available:

1. **Code Generation** (RECOMMENDED) - Write Python code that generates commands
2. **Direct Commands** - Provide command list manually

---

## 🎯 Code Generation (RECOMMENDED - Like voxel-test!)

**The Pattern**: Write Python code that populates a `commands` list.

This is the SAME pattern as the successful voxel-test project - natural code generation!

### Why Code Generation?

✅ **Natural for AI** - Writing code IS what LLMs do best
✅ **Procedural** - Use loops, math, algorithms, randomness
✅ **Scalable** - 50 lines of code → 1000s of commands
✅ **Creative** - Organic shapes, variations, complex patterns

### Example - Dragon Statue

```python
build(code="""
commands = []

# Body (sphere using procedural loop)
for x in range(100, 106):
    for y in range(65, 68):
        for z in range(200, 206):
            distance = ((x-103)**2 + (y-66)**2 + (z-203)**2)**0.5
            if distance < 3:
                commands.append(f"/setblock {x} {y} {z} red_concrete")

# Wings (procedural with offsets)
for wing_offset in [-3, 3]:  # Left and right
    for i in range(5):
        x = 103 + wing_offset + i
        y = 67 + i // 2
        commands.append(f"/setblock {x} {y} 203 orange_concrete")

# Head details
commands.append("/setblock 103 70 203 red_concrete")
commands.append("/setblock 102 70 203 yellow_concrete")  # Left eye
commands.append("/setblock 104 70 203 yellow_concrete")  # Right eye
""")
```

Result: **Beautiful dragon statue from 20 lines of code!**

---

## Code Patterns

### Pattern 1: Spheres & Organic Shapes

```python
build(code="""
commands = []
radius = 10
center = (105, 70, 205)

for x in range(center[0] - radius, center[0] + radius + 1):
    for y in range(center[1] - radius, center[1] + radius + 1):
        for z in range(center[2] - radius, center[2] + radius + 1):
            distance = ((x-center[0])**2 + (y-center[1])**2 + (z-center[2])**2)**0.5

            # Hollow sphere
            if abs(distance - radius) < 1:
                commands.append(f"/setblock {x} {y} {z} glass")
""")
```

### Pattern 2: Pyramids & Layered Structures

```python
build(code="""
commands = []
base_x, base_y, base_z = 100, 64, 200
size = 15

for layer in range(size):
    y = base_y + layer
    for x in range(base_x - size + layer, base_x + size - layer + 1):
        for z in range(base_z - size + layer, base_z + size - layer + 1):
            commands.append(f"/setblock {x} {y} {z} sandstone")
""")
```

### Pattern 3: Towers & Vertical Structures

```python
build(code="""
commands = []
center_x, base_y, center_z = 100, 64, 200
radius = 5
height = 20

for y in range(base_y, base_y + height):
    for x in range(center_x - radius, center_x + radius + 1):
        for z in range(center_z - radius, center_z + radius + 1):
            # Circular tower
            distance = ((x-center_x)**2 + (z-center_z)**2)**0.5
            if distance <= radius:
                # Hollow interior
                if distance >= radius - 1 or y == base_y:
                    commands.append(f"/setblock {x} {y} {z} stone_bricks")
""")
```

### Pattern 4: Walls & Paths

```python
build(code="""
commands = []

# Wall (straight line)
for x in range(100, 120):
    for y in range(64, 70):
        commands.append(f"/setblock {x} {y} 200 cobblestone")

# Path (with variation)
for x in range(100, 150):
    for z in range(200, 203):
        # Slightly irregular path
        if (x + z) % 5 != 0:
            commands.append(f"/setblock {x} 64 {z} gravel")
""")
```

### Pattern 5: With Randomness & Variation

```python
build(code="""
commands = []

# Tree cluster (random positions)
import random  # NOT allowed! Use deterministic approach instead

# Deterministic "randomness" using math
for tree_num in range(10):
    offset_x = (tree_num * 17) % 20 - 10  # Pseudo-random spread
    offset_z = (tree_num * 13) % 20 - 10

    x = 100 + offset_x
    z = 200 + offset_z

    # Tree trunk
    for y in range(64, 70):
        commands.append(f"/setblock {x} {y} {z} oak_log[axis=y]")

    # Tree leaves (sphere)
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            for dz in range(-2, 3):
                if dx*dx + dy*dy + dz*dz < 7:
                    commands.append(f"/setblock {x+dx} {68+dy} {z+dz} oak_leaves")
""")
```

---

## Code Limitations & Safety

**Allowed:**
- ✅ Loops: `for`, `while`
- ✅ Conditionals: `if`, `else`, `elif`
- ✅ Math: `+`, `-`, `*`, `/`, `**`, `%`, `abs()`, `min()`, `max()`
- ✅ Strings: f-strings, concatenation
- ✅ Lists: append, extend, indexing
- ✅ Functions: `range()`, `len()`, `enumerate()`, `zip()`

**NOT Allowed:**
- ❌ Imports: `import`, `from`
- ❌ File operations: `open()`, `read()`, `write()`
- ❌ Network: `requests`, `urllib`
- ❌ System: `os`, `sys`, `subprocess`
- ❌ Randomness: `random` module (use deterministic math instead)

**Limits:**
- Max 10,000 commands generated
- Max 100,000 loop iterations
- 5 second timeout

---

## Direct Commands (Alternative)

For simple builds, you can provide commands directly:

```python
build(commands=[
    "/fill 100 64 200 110 64 210 oak_planks",              # Floor
    "/fill 100 65 200 110 70 210 cobblestone hollow",      # Walls
    "/setblock 105 65 205 oak_door[half=lower]",           # Door
    "/fill 100 71 200 110 71 210 oak_slab[type=bottom]"    # Roof
])
```

### Command Types

**1. Single Block: `/setblock X Y Z block[states]`**
```
/setblock 100 64 200 crafting_table
/setblock 105 68 210 lantern[hanging=true]
/setblock 100 65 202 oak_door[half=lower,facing=east]
```

**2. Bulk Region: `/fill X1 Y1 Z1 X2 Y2 Z2 block [mode]`**
```
/fill 100 64 200 110 64 210 oak_planks              # Solid
/fill 100 65 200 110 70 210 cobblestone hollow     # Hollow box
/fill 100 71 200 110 71 210 oak_slab[type=bottom]  # Roof
```

**Modes:**
- (no mode) - Fill solid
- `hollow` - Hollow box (only walls)
- `outline` - Frame (only edges)
- `replace` - Replace specific blocks
- `keep` - Only fill air

**3. WorldEdit: `//command`**
```
//pos1 100,64,100
//pos2 110,70,110
//set stone_bricks
//sphere stone 10
//cylinder glass 5 10
```

---

## Preview Mode

Always preview first to check your commands/code:

```python
build(
    code="""...""",
    preview_only=True  # Shows commands without executing
)
```

---

## Best Practices

1. **Use code for complex builds** - Spheres, curves, organic shapes
2. **Use direct commands for simple builds** - Cottages, boxes, floors
3. **Preview first** - Always use `preview_only=True` initially
4. **Think procedurally** - Loops and math > manual enumeration
5. **Layer by layer** - Build from bottom to top

---

## Examples by Complexity

**Simple (Direct Commands):**
- Cottage, box, platform, path

**Medium (Code):**
- Tower, pyramid, wall, dome

**Complex (Code):**
- Dragon, castle, city, organic sculpture

---

## Summary

**The voxel-test pattern:** Write code that generates the thing.

This is NATURAL for AI and produces AMAZING results!

```python
# Simple prompt → Natural code → Beautiful builds
build(code="""
commands = []
# Your creative procedural code here...
""")
```
