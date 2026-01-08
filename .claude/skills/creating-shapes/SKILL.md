---
name: creating-shapes
description: Creates procedural and organic shapes in Minecraft using VibeCraft MCP tools. Use when building spheres, domes, cylinders, pyramids, torus, arches, curves, spirals, organic shapes, statues, or any complex geometry that requires procedural generation.
---

# Creating Shapes

Build complex geometry using VibeCraft MCP tools.

## MCP Tools

### WorldEdit Shapes
- `worldedit_generation` - sphere, cylinder, pyramid, cone

### Code Generation
- `build(code=...)` - Python code that generates commands (RECOMMENDED)

### Expressions
- `worldedit_deform` - Math expressions

## build() Code Mode (RECOMMENDED)

Write Python code that generates commands. Perfect for complex shapes.

### Basic Sphere

```python
build(code="""
commands = []
cx, cy, cz = 105, 70, 205
radius = 10

for x in range(cx - radius, cx + radius + 1):
    for y in range(cy - radius, cy + radius + 1):
        for z in range(cz - radius, cz + radius + 1):
            dist = ((x-cx)**2 + (y-cy)**2 + (z-cz)**2)**0.5
            if dist <= radius:
                commands.append(f'/setblock {x} {y} {z} stone')
""", description="Solid sphere")
```

### Hollow Sphere

```python
build(code="""
commands = []
cx, cy, cz = 105, 70, 205
radius = 10
thickness = 1

for x in range(cx - radius, cx + radius + 1):
    for y in range(cy - radius, cy + radius + 1):
        for z in range(cz - radius, cz + radius + 1):
            dist = ((x-cx)**2 + (y-cy)**2 + (z-cz)**2)**0.5
            if radius - thickness <= dist <= radius:
                commands.append(f'/setblock {x} {y} {z} glass')
""", description="Hollow glass sphere")
```

### Dome (Half Sphere)

```python
build(code="""
commands = []
cx, cz = 105, 205
base_y = 64
radius = 15

for x in range(cx - radius, cx + radius + 1):
    for y in range(base_y, base_y + radius + 1):
        for z in range(cz - radius, cz + radius + 1):
            dist = ((x-cx)**2 + (y-base_y)**2 + (z-cz)**2)**0.5
            if radius - 1 <= dist <= radius:
                commands.append(f'/setblock {x} {y} {z} quartz_block')
""", description="Quartz dome")
```

### Cylinder

```python
build(code="""
commands = []
cx, cz = 105, 205
base_y = 64
radius = 8
height = 20

for y in range(base_y, base_y + height):
    for x in range(cx - radius, cx + radius + 1):
        for z in range(cz - radius, cz + radius + 1):
            dist = ((x-cx)**2 + (z-cz)**2)**0.5
            if dist <= radius:
                commands.append(f'/setblock {x} {y} {z} stone_bricks')
""", description="Solid cylinder")
```

### Hollow Cylinder (Tower)

```python
build(code="""
commands = []
cx, cz = 105, 205
base_y = 64
radius = 8
height = 20
thickness = 1

for y in range(base_y, base_y + height):
    for x in range(cx - radius, cx + radius + 1):
        for z in range(cz - radius, cz + radius + 1):
            dist = ((x-cx)**2 + (z-cz)**2)**0.5
            if radius - thickness <= dist <= radius:
                commands.append(f'/setblock {x} {y} {z} stone_bricks')
""", description="Hollow tower")
```

### Cone

```python
build(code="""
commands = []
cx, cz = 105, 205
base_y = 64
base_radius = 10
height = 15

for y in range(base_y, base_y + height):
    progress = (y - base_y) / height
    radius = base_radius * (1 - progress)
    
    for x in range(cx - base_radius, cx + base_radius + 1):
        for z in range(cz - base_radius, cz + base_radius + 1):
            dist = ((x-cx)**2 + (z-cz)**2)**0.5
            if dist <= radius:
                commands.append(f'/setblock {x} {y} {z} red_terracotta')
""", description="Cone")
```

### Pyramid

```python
build(code="""
commands = []
cx, cz = 105, 205
base_y = 64
base_size = 21
half = base_size // 2

for layer in range(half + 1):
    y = base_y + layer
    size = half - layer
    for x in range(cx - size, cx + size + 1):
        for z in range(cz - size, cz + size + 1):
            commands.append(f'/setblock {x} {y} {z} sandstone')
""", description="Sandstone pyramid")
```

### Torus (Donut)

```python
build(code="""
commands = []
cx, cy, cz = 105, 70, 205
major_radius = 12
minor_radius = 4

for x in range(cx - major_radius - minor_radius, cx + major_radius + minor_radius + 1):
    for y in range(cy - minor_radius, cy + minor_radius + 1):
        for z in range(cz - major_radius - minor_radius, cz + major_radius + minor_radius + 1):
            dist_xz = ((x-cx)**2 + (z-cz)**2)**0.5
            tube_dist = ((dist_xz - major_radius)**2 + (y-cy)**2)**0.5
            
            if tube_dist <= minor_radius:
                commands.append(f'/setblock {x} {y} {z} gold_block')
""", description="Golden torus")
```

### Spiral Staircase

```python
build(code="""
commands = []
import math

cx, cz = 105, 205
base_y = 64
height = 20
radius = 4
steps_per_rotation = 12

for step in range(height * steps_per_rotation // 4):
    angle = step * (2 * math.pi / steps_per_rotation)
    y = base_y + step // 3
    
    x = int(cx + math.cos(angle) * radius)
    z = int(cz + math.sin(angle) * radius)
    
    if 0 <= angle < math.pi/2:
        facing = 'west'
    elif angle < math.pi:
        facing = 'north'
    elif angle < 3*math.pi/2:
        facing = 'east'
    else:
        facing = 'south'
    
    commands.append(f'/setblock {x} {y} {z} oak_stairs[facing={facing},half=bottom]')
""", description="Spiral staircase")
```

### Gothic Arch

```python
build(code="""
commands = []
import math

base_x, base_y, base_z = 100, 64, 200
width = 7
height = 10

half_w = width // 2

for y in range(height):
    if y < height - 3:
        # Vertical sides
        commands.append(f'/setblock {base_x} {base_y + y} {base_z} stone_bricks')
        commands.append(f'/setblock {base_x + width - 1} {base_y + y} {base_z} stone_bricks')
    else:
        # Pointed top
        progress = (y - (height - 3)) / 3
        left_inset = int(half_w * progress)
        right_inset = int(half_w * progress)
        
        for x_off in range(left_inset, width - right_inset):
            commands.append(f'/setblock {base_x + x_off} {base_y + y} {base_z} stone_bricks')
""", description="Gothic arch")
```

### Bridge Arc

```python
build(code="""
commands = []
import math

start_x, end_x = 100, 130
base_y = 64
z = 200
arc_height = 8

length = end_x - start_x

for x in range(start_x, end_x + 1):
    progress = (x - start_x) / length
    arc = math.sin(progress * math.pi) * arc_height
    y = int(base_y + arc)
    
    # Bridge surface
    for dz in range(-2, 3):
        commands.append(f'/setblock {x} {y} {z + dz} stone_brick_slab[type=top]')
    
    # Railings
    commands.append(f'/setblock {x} {y + 1} {z - 2} stone_brick_wall')
    commands.append(f'/setblock {x} {y + 1} {z + 2} stone_brick_wall')
""", description="Arched bridge")
```

For more shapes, see [shapes.md](shapes.md).

## WorldEdit Shapes

### Simple Shapes
```
/sphere stone 10          # Sphere r=10
/hsphere glass 10         # Hollow sphere
/cyl stone 5 10           # Cylinder r=5 h=10
/hcyl glass 5 10          # Hollow cylinder
/pyramid sandstone 15     # Pyramid
```

### With Expressions
```
# Torus
/generate gold_block (sqrt(x*x+z*z)-12)^2+y*y<16

# Ellipsoid
/generate stone (x*x)/100+(y*y)/25+(z*z)/100<1

# Sine wave
/generate stone y<sin(x/5)*3+64
```

## Code Sandbox Limits

The `build(code=...)` sandbox has restrictions:

**Allowed:**
- `for` loops with `range()`
- List comprehensions
- Math operations
- `math` module functions (sin, cos, sqrt, etc.)

**NOT Allowed:**
- `while` loops
- Function definitions (`def`)
- Lambda expressions
- Imports (except math)
- `try`/`except`

**Limits:**
- Max 10,000 commands
- Max 100,000 loop iterations

## Distance Functions

```python
# Euclidean (spheres)
dist = ((x-cx)**2 + (y-cy)**2 + (z-cz)**2)**0.5

# 2D distance (cylinders)
dist = ((x-cx)**2 + (z-cz)**2)**0.5

# Manhattan (diamonds)
dist = abs(x-cx) + abs(y-cy) + abs(z-cz)

# Chebyshev (cubes)
dist = max(abs(x-cx), abs(y-cy), abs(z-cz))
```

## Shape Formulas

| Shape | Formula |
|-------|---------|
| Sphere | `x² + y² + z² ≤ r²` |
| Ellipsoid | `(x/a)² + (y/b)² + (z/c)² ≤ 1` |
| Cylinder | `x² + z² ≤ r²` |
| Cone | `x² + z² ≤ (r(1-y/h))²` |
| Torus | `(√(x²+z²) - R)² + y² ≤ r²` |
| Paraboloid | `y ≤ a(x² + z²)` |

## Performance Tips

1. **Hollow > Solid**: Much fewer blocks
2. **Preview first**: `build(preview_only=True)`
3. **Chunk sections**: Process 16x16 at a time
4. **Use /fill for rectangles**: Faster than setblock
