---
name: generating-terrain
description: Generates Minecraft terrain and landscapes using VibeCraft MCP tools. Use when creating hills, mountains, valleys, rivers, caves, cliffs, or natural terrain features. Handles procedural generation, noise functions, and terrain texturing.
---

# Generating Terrain

Create natural Minecraft landscapes using VibeCraft MCP tools.

## MCP Tools

### Terrain Tools
- `generate_terrain` - Procedural terrain: rolling_hills, rugged_mountains, valley_network, mountain_range, plateau
- `texture_terrain` - Apply biome textures: temperate, alpine, desert, volcanic, jungle, swamp
- `smooth_terrain` - Post-process smoothing (iterations 1-5)

### WorldEdit
- `worldedit_generation` - sphere, cylinder, pyramid shapes
- `worldedit_deform` - Math expressions for terrain deformation
- `worldedit_terrain_advanced` - smooth, naturalize, regen

### Code Generation
- `build(code=...)` - Procedural algorithms with loops and math

## Quick Start

```python
# Generate rolling hills
generate_terrain(
    type="rolling_hills",
    center_x=100, center_y=64, center_z=200,
    size=50,
    amplitude=8
)

# Apply grass/dirt texturing
texture_terrain(
    style="temperate",
    center_x=100, center_y=64, center_z=200,
    size=50
)

# Smooth edges
smooth_terrain(
    center_x=100, center_y=64, center_z=200,
    size=50,
    iterations=2
)
```

## Procedural Generation with build()

### Rolling Hills

```python
build(code="""
commands = []

def noise(x, z, seed=42):
    n = x * 374761393 + z * 668265263 + seed
    n = (n ^ (n >> 13)) * 1274126177
    return ((n ^ (n >> 16)) & 255) / 255.0

base_x, base_z = 100, 200
size = 50
base_y = 64
amplitude = 8

for x in range(base_x, base_x + size):
    for z in range(base_z, base_z + size):
        # Multi-octave noise
        height = noise(x, z, 1) * amplitude
        height += noise(x*2, z*2, 2) * amplitude * 0.5
        height += noise(x*4, z*4, 3) * amplitude * 0.25
        
        y = int(base_y + height)
        
        # Layered materials
        commands.append(f'/setblock {x} {y} {z} grass_block')
        for below in range(base_y - 5, y):
            if y - below <= 3:
                commands.append(f'/setblock {x} {below} {z} dirt')
            else:
                commands.append(f'/setblock {x} {below} {z} stone')
""", description="Rolling hills with proper layers")
```

### Mountain Range

```python
build(code="""
commands = []

def noise(x, z, seed=42):
    n = x * 374761393 + z * 668265263 + seed
    n = (n ^ (n >> 13)) * 1274126177
    return ((n ^ (n >> 16)) & 255) / 255.0

base_x, base_z = 100, 200
size = 40
base_y = 64
amplitude = 25

for x in range(base_x, base_x + size):
    for z in range(base_z, base_z + size):
        # Ridged noise for peaks
        n1 = abs(noise(x * 0.1, z * 0.1, 1) - 0.5) * 2
        n2 = abs(noise(x * 0.2, z * 0.2, 2) - 0.5) * 2
        height = (n1 + n2 * 0.5) * amplitude
        
        y = int(base_y + height)
        
        # Snow above certain height
        if y > base_y + 18:
            commands.append(f'/setblock {x} {y} {z} snow_block')
        elif y > base_y + 12:
            commands.append(f'/setblock {x} {y} {z} stone')
        else:
            commands.append(f'/setblock {x} {y} {z} grass_block')
        
        # Fill below
        for below in range(base_y - 10, y):
            commands.append(f'/setblock {x} {below} {z} stone')
""", description="Mountain range with snow caps")
```

### River Valley

```python
build(code="""
commands = []
import math

base_x, base_z = 100, 200
length = 60
width = 15
base_y = 64

for i in range(length):
    # Sinusoidal path
    path_z = base_z + i
    path_x = base_x + int(math.sin(i * 0.1) * 10)
    
    for dx in range(-width//2, width//2 + 1):
        x = path_x + dx
        # Depth based on distance from center
        depth = int((1 - abs(dx) / (width/2)) * 5)
        y = base_y - depth
        
        # Water in deepest part
        if abs(dx) <= 2:
            commands.append(f'/setblock {x} {y} {path_z} water')
        else:
            commands.append(f'/setblock {x} {y} {path_z} sand')
""", description="Meandering river valley")
```

For more algorithms, see [algorithms.md](algorithms.md).

## WorldEdit Expressions

### Dome/Bowl

```
//generate stone (x*x+z*z)<radius^2 && y<sqrt(radius^2-x*x-z*z)
```

### Noise Terrain

```
//generate -h stone y<perlin(x/10,z/10,0)*5+64
```

### Sine Wave Hills

```
//deform y+=sin(x/5)*3+sin(z/5)*3
```

For expression reference, see [expressions.md](expressions.md).

## Biome Texturing

### Temperate
```
Y+0: grass_block
Y-1 to Y-3: dirt
Y-4 and below: stone
Scattered: flowers, tall_grass
```

### Alpine
```
Y > base+18: snow_block
Y > base+12: stone
Y > base+6: grass_block
Y <= base+6: dirt
Scattered: spruce trees
```

### Desert
```
Y+0: sand (3-4 layers)
Below sand: sandstone
Scattered: dead_bush, cactus
```

### Volcanic
```
Y > base+15: magma_block, obsidian
Y > base+8: blackstone
Y <= base+8: basalt
Scattered: fire, lava pools
```

## Common Patterns

### Cliff Face
```python
# Vertical face with ledges
for y in range(base_y, base_y + height):
    # Random ledge depth
    depth = random.randint(0, 2)
    for d in range(depth + 1):
        commands.append(f'/setblock {base_x + d} {y} {base_z} stone')
```

### Cave System
Use `worldedit_terrain_advanced`:
```
worldedit_terrain_advanced(
    command="caves",
    size=8,
    freq=40,
    rarity=7,
    minY=0,
    maxY=60
)
```

### Erosion Effect
```python
# Random block removal from surface
for x in range(size):
    for z in range(size):
        if random.random() < 0.2:  # 20% chance
            # Remove top block
            commands.append(f'/setblock {base_x+x} {surface_y} {base_z+z} air')
```

## Smoothing

### WorldEdit Smooth
```
//smooth 3  # 3 iterations
```

### Manual Smoothing
```python
# Average neighbor heights
def smooth_height(heights, x, z):
    total = 0
    count = 0
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            if (x+dx, z+dz) in heights:
                total += heights[(x+dx, z+dz)]
                count += 1
    return total // count if count > 0 else heights.get((x,z), 64)
```

## Performance Tips

1. **Chunk boundaries**: Generate in 16x16 sections
2. **Y-range**: Only modify necessary Y levels
3. **Batch operations**: Use /fill for rectangular areas
4. **Preview first**: `build(preview_only=True)`
