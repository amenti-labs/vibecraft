---
name: generating-terrain
description: Generates Minecraft terrain and landscapes using VibeCraft MCP tools. Use when creating hills, mountains, valleys, rivers, caves, cliffs, or natural terrain features. Handles procedural generation, noise functions, and terrain texturing.
---

# Generating Terrain

## MCP Tools
- `generate_terrain` - rolling_hills, rugged_mountains, valley_network, mountain_range, plateau
- `texture_terrain` - temperate, alpine, desert, volcanic, jungle, swamp
- `smooth_terrain` - Post-process smoothing (iterations 1-5)
- `worldedit_deform` - Math expressions
- `worldedit_terrain_advanced` - smooth, naturalize, regen
- `build(code=...)` - Procedural algorithms

## Quick Start
```python
generate_terrain(type="rolling_hills", center_x=100, center_y=64, center_z=200, size=50, amplitude=8)
texture_terrain(style="temperate", center_x=100, center_y=64, center_z=200, size=50)
smooth_terrain(center_x=100, center_y=64, center_z=200, size=50, iterations=2)
```

## Procedural with build()

### Rolling Hills
```python
build(code="""
commands = []
def noise(x, z, seed=42):
    n = x * 374761393 + z * 668265263 + seed
    n = (n ^ (n >> 13)) * 1274126177
    return ((n ^ (n >> 16)) & 255) / 255.0

base_x, base_z, size, base_y, amplitude = 100, 200, 50, 64, 8
for x in range(base_x, base_x + size):
    for z in range(base_z, base_z + size):
        height = noise(x, z, 1) * amplitude + noise(x*2, z*2, 2) * amplitude * 0.5
        y = int(base_y + height)
        commands.append(f'/setblock {x} {y} {z} grass_block')
        for below in range(base_y - 5, y):
            mat = 'dirt' if y - below <= 3 else 'stone'
            commands.append(f'/setblock {x} {below} {z} {mat}')
""", description="Rolling hills")
```

### Mountain Range
```python
# Use ridged noise: abs(noise(x, z) - 0.5) * 2
# Snow above base+18, stone above base+12, grass below
```

### River Valley
```python
# Sinusoidal path: path_x = base_x + sin(i * 0.1) * 10
# Depth based on distance from center
# Water in deepest part, sand on banks
```

## WorldEdit Expressions
```
//generate -h stone y<perlin(x/10,z/10,0)*5+64  # Noise terrain
//deform y+=sin(x/5)*3+sin(z/5)*3               # Sine wave hills
//generate stone (x*x+z*z)<radius^2 && y<sqrt(radius^2-x*x-z*z)  # Dome
```

## Biome Texturing

**Temperate**: grass_block (Y+0), dirt (Y-1 to -3), stone (Y-4+), flowers/tall_grass
**Alpine**: snow_block (Y>base+18), stone (Y>base+12), grass (Y>base+6), spruce trees
**Desert**: sand (3-4 layers), sandstone below, dead_bush/cactus
**Volcanic**: magma_block/obsidian (Y>base+15), blackstone (Y>base+8), basalt, lava pools

## Common Patterns

**Cliff Face**: Random ledge depth per Y level
**Cave System**: `worldedit_terrain_advanced(command="caves", size=8, freq=40, rarity=7, minY=0, maxY=60)`
**Erosion**: 20% random block removal from surface

## Smoothing
```
//smooth 3  # 3 iterations

# Manual: average neighbor heights
def smooth(heights, x, z):
    return sum(heights.get((x+dx, z+dz), 64) for dx in [-1,0,1] for dz in [-1,0,1]) // 9
```

## Tips
1. Generate in 16×16 chunks
2. Only modify necessary Y levels
3. Use /fill for rectangular areas
4. Preview first: `build(preview_only=True)`
