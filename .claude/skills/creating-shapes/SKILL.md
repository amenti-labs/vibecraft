---
name: creating-shapes
description: Creates procedural and organic shapes in Minecraft using VibeCraft MCP tools. Use when building spheres, domes, cylinders, pyramids, torus, arches, curves, spirals, organic shapes, statues, or any complex geometry that requires procedural generation.
---

# Creating Shapes

## MCP Tools
- `worldedit_generation` - sphere, cylinder, pyramid, cone
- `build(code=...)` - Python code that generates commands (RECOMMENDED)
- `worldedit_deform` - Math expressions

## build() Code Mode (RECOMMENDED)

### Sphere
```python
build(code="""
commands = []
cx, cy, cz, radius = 105, 70, 205, 10
for x in range(cx - radius, cx + radius + 1):
    for y in range(cy - radius, cy + radius + 1):
        for z in range(cz - radius, cz + radius + 1):
            if ((x-cx)**2 + (y-cy)**2 + (z-cz)**2)**0.5 <= radius:
                commands.append(f'/setblock {x} {y} {z} stone')
""", description="Solid sphere")
```

### Hollow Sphere
```python
# Add: if radius - thickness <= dist <= radius:
```

### Dome (Half Sphere)
```python
# Limit y range: for y in range(base_y, base_y + radius + 1):
# Use: dist = ((x-cx)**2 + (y-base_y)**2 + (z-cz)**2)**0.5
```

### Cylinder
```python
build(code="""
commands = []
cx, cz, base_y, radius, height = 105, 205, 64, 8, 20
for y in range(base_y, base_y + height):
    for x in range(cx - radius, cx + radius + 1):
        for z in range(cz - radius, cz + radius + 1):
            if ((x-cx)**2 + (z-cz)**2)**0.5 <= radius:
                commands.append(f'/setblock {x} {y} {z} stone_bricks')
""", description="Solid cylinder")
# Hollow: if radius - thickness <= dist <= radius:
```

### Cone
```python
# Per layer: radius = base_radius * (1 - (y - base_y) / height)
```

### Pyramid
```python
build(code="""
commands = []
cx, cz, base_y, half = 105, 205, 64, 10
for layer in range(half + 1):
    size = half - layer
    for x in range(cx - size, cx + size + 1):
        for z in range(cz - size, cz + size + 1):
            commands.append(f'/setblock {x} {base_y + layer} {z} sandstone')
""", description="Pyramid")
```

### Torus (Donut)
```python
build(code="""
commands = []
cx, cy, cz, major_r, minor_r = 105, 70, 205, 12, 4
for x in range(cx - major_r - minor_r, cx + major_r + minor_r + 1):
    for y in range(cy - minor_r, cy + minor_r + 1):
        for z in range(cz - major_r - minor_r, cz + major_r + minor_r + 1):
            dist_xz = ((x-cx)**2 + (z-cz)**2)**0.5
            tube_dist = ((dist_xz - major_r)**2 + (y-cy)**2)**0.5
            if tube_dist <= minor_r:
                commands.append(f'/setblock {x} {y} {z} gold_block')
""", description="Torus")
```

### Spiral Staircase
```python
# Use: angle = step * (2 * pi / steps_per_rotation)
# x = cx + cos(angle) * radius, z = cz + sin(angle) * radius
# Facing based on angle quadrant
```

### Arched Bridge
```python
# Use: arc = sin(progress * pi) * arc_height where progress = (x - start) / length
```

## WorldEdit Shapes
```
/sphere stone 10       # Solid sphere r=10
/hsphere glass 10      # Hollow sphere
/cyl stone 5 10        # Cylinder r=5 h=10
/hcyl glass 5 10       # Hollow cylinder
/pyramid sandstone 15  # Pyramid
```

## Expression Shapes
```
/generate gold_block (sqrt(x*x+z*z)-12)^2+y*y<16  # Torus
/generate stone (x*x)/100+(y*y)/25+(z*z)/100<1    # Ellipsoid
/generate stone y<sin(x/5)*3+64                    # Sine wave
```

## Code Sandbox Limits
**Allowed**: `for` loops, list comprehensions, math ops, `math` module
**NOT Allowed**: `while`, `def`, `lambda`, imports (except math), `try/except`
**Limits**: 10,000 commands max, 100,000 iterations max

## Distance Functions
```python
# Euclidean (spheres): ((x-cx)**2 + (y-cy)**2 + (z-cz)**2)**0.5
# 2D (cylinders): ((x-cx)**2 + (z-cz)**2)**0.5
# Manhattan (diamonds): abs(x-cx) + abs(y-cy) + abs(z-cz)
# Chebyshev (cubes): max(abs(x-cx), abs(y-cy), abs(z-cz))
```

## Shape Formulas
| Shape | Formula |
|-------|---------|
| Sphere | x² + y² + z² ≤ r² |
| Ellipsoid | (x/a)² + (y/b)² + (z/c)² ≤ 1 |
| Cylinder | x² + z² ≤ r² |
| Cone | x² + z² ≤ (r(1-y/h))² |
| Torus | (√(x²+z²) - R)² + y² ≤ r² |

## Tips
1. Hollow > Solid (fewer blocks)
2. Preview first: `build(preview_only=True)`
3. Use /fill for rectangular parts
