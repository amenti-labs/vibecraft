# Procedural Generation Guide

Algorithms and techniques for generating terrain, structures, and organic shapes in Minecraft using the `build()` tool with code generation.

---

## Foundations

### Coordinate Systems

```python
# Minecraft coordinates
# X: East (+) / West (-)
# Y: Up (+) / Down (-)  (64 = sea level in most worlds)
# Z: South (+) / North (-)

# Common anchor points
base_x, base_y, base_z = 100, 64, 200  # Starting position
center = (base_x + size//2, base_y, base_z + size//2)  # Center of build
```

### Distance Functions

```python
# Euclidean distance (sphere, circle)
def distance_3d(x, y, z, cx, cy, cz):
    return ((x-cx)**2 + (y-cy)**2 + (z-cz)**2)**0.5

def distance_2d(x, z, cx, cz):
    return ((x-cx)**2 + (z-cz)**2)**0.5

# Manhattan distance (diamond shapes)
def manhattan_3d(x, y, z, cx, cy, cz):
    return abs(x-cx) + abs(y-cy) + abs(z-cz)

# Chebyshev distance (cube shapes)
def chebyshev_3d(x, y, z, cx, cy, cz):
    return max(abs(x-cx), abs(y-cy), abs(z-cz))
```

---

## Basic Shapes

### Solid Sphere

```python
build(code="""
commands = []
cx, cy, cz = 105, 70, 205  # Center
radius = 10

for x in range(cx - radius, cx + radius + 1):
    for y in range(cy - radius, cy + radius + 1):
        for z in range(cz - radius, cz + radius + 1):
            dist = ((x-cx)**2 + (y-cy)**2 + (z-cz)**2)**0.5
            if dist <= radius:
                commands.append(f'/setblock {x} {y} {z} stone')
""", description="Solid stone sphere r=10")
```

### Hollow Sphere

```python
build(code="""
commands = []
cx, cy, cz = 105, 70, 205
radius = 10
thickness = 1  # Wall thickness

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
cx, cy, cz = 105, 64, 205  # cy = floor level
radius = 15

for x in range(cx - radius, cx + radius + 1):
    for y in range(cy, cy + radius + 1):  # Only upper half
        for z in range(cz - radius, cz + radius + 1):
            dist = ((x-cx)**2 + (y-cy)**2 + (z-cz)**2)**0.5
            if radius - 1 <= dist <= radius:
                commands.append(f'/setblock {x} {y} {z} quartz_block')
""", description="Quartz dome")
```

### Cylinder

```python
build(code="""
commands = []
cx, cz = 105, 205  # Center on XZ plane
base_y = 64
radius = 8
height = 20

for x in range(cx - radius, cx + radius + 1):
    for y in range(base_y, base_y + height):
        for z in range(cz - radius, cz + radius + 1):
            dist_2d = ((x-cx)**2 + (z-cz)**2)**0.5
            if dist_2d <= radius:
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

for x in range(cx - radius, cx + radius + 1):
    for y in range(base_y, base_y + height):
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
    # Radius shrinks linearly with height
    progress = (y - base_y) / height
    radius = base_radius * (1 - progress)
    
    for x in range(cx - base_radius, cx + base_radius + 1):
        for z in range(cz - base_radius, cz + base_radius + 1):
            dist = ((x-cx)**2 + (z-cz)**2)**0.5
            if dist <= radius:
                commands.append(f'/setblock {x} {y} {z} red_terracotta')
""", description="Cone shape")
```

### Pyramid

```python
build(code="""
commands = []
cx, cz = 105, 205
base_y = 64
base_size = 21  # Odd number for center point
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
major_radius = 12  # Distance from center to tube center
minor_radius = 4   # Tube radius

for x in range(cx - major_radius - minor_radius, cx + major_radius + minor_radius + 1):
    for y in range(cy - minor_radius, cy + minor_radius + 1):
        for z in range(cz - major_radius - minor_radius, cz + major_radius + minor_radius + 1):
            # Distance from center in XZ plane
            dist_xz = ((x-cx)**2 + (z-cz)**2)**0.5
            # Distance from torus tube center
            tube_dist = ((dist_xz - major_radius)**2 + (y-cy)**2)**0.5
            
            if tube_dist <= minor_radius:
                commands.append(f'/setblock {x} {y} {z} gold_block')
""", description="Golden torus")
```

---

## Organic Shapes

### Tree (Procedural)

```python
build(code="""
commands = []
import random
random.seed(42)  # Reproducible

base_x, base_y, base_z = 100, 64, 200
trunk_height = 8

# Trunk
for y in range(base_y, base_y + trunk_height):
    commands.append(f'/setblock {base_x} {y} {base_z} oak_log[axis=y]')

# Crown (irregular sphere)
crown_center_y = base_y + trunk_height
crown_radius = 5

for x in range(base_x - crown_radius, base_x + crown_radius + 1):
    for y in range(crown_center_y - crown_radius//2, crown_center_y + crown_radius + 1):
        for z in range(base_z - crown_radius, base_z + crown_radius + 1):
            dist = ((x-base_x)**2 + (y-crown_center_y)**2 + (z-base_z)**2)**0.5
            # Irregular edge with randomness
            threshold = crown_radius * (0.7 + random.random() * 0.3)
            if dist <= threshold:
                commands.append(f'/setblock {x} {y} {z} oak_leaves[persistent=true]')
""", description="Procedural oak tree")
```

### Boulder (Irregular Rock)

```python
build(code="""
commands = []
import random
random.seed(123)

cx, cy, cz = 105, 65, 205
base_radius = 5

for x in range(cx - base_radius - 2, cx + base_radius + 3):
    for y in range(cy - base_radius, cy + base_radius + 3):
        for z in range(cz - base_radius - 2, cz + base_radius + 3):
            # Slightly squashed sphere with noise
            dist = ((x-cx)**2 / 1.3 + (y-cy)**2 * 1.5 + (z-cz)**2 / 1.2)**0.5
            threshold = base_radius + (random.random() - 0.5) * 2
            
            if dist <= threshold:
                # Mix of stone types for texture
                r = random.random()
                if r < 0.6:
                    block = 'stone'
                elif r < 0.85:
                    block = 'cobblestone'
                else:
                    block = 'mossy_cobblestone'
                commands.append(f'/setblock {x} {y} {z} {block}')
""", description="Natural boulder")
```

### Vine/Tendril

```python
build(code="""
commands = []
import random
import math
random.seed(456)

start_x, start_y, start_z = 100, 70, 200
length = 20

# Random walk in 3D space
x, y, z = start_x, start_y, start_z
for i in range(length):
    commands.append(f'/setblock {int(x)} {int(y)} {int(z)} oak_log')
    
    # Random direction with downward bias
    x += random.uniform(-0.8, 0.8)
    y -= random.uniform(0.3, 0.8)  # Mostly down
    z += random.uniform(-0.8, 0.8)
""", description="Hanging vine")
```

---

## Terrain Generation

### Simple Noise (No Imports)

```python
# Pseudo-random noise function (no imports needed)
def noise(x, z, seed=42):
    n = x * 374761393 + z * 668265263 + seed
    n = (n ^ (n >> 13)) * 1274126177
    return ((n ^ (n >> 16)) & 255) / 255.0
```

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
        # Multi-octave noise for smooth terrain
        height = 0
        height += noise(x, z, 1) * amplitude
        height += noise(x * 2, z * 2, 2) * amplitude * 0.5
        height += noise(x * 4, z * 4, 3) * amplitude * 0.25
        
        y = int(base_y + height)
        
        # Top layer grass, below dirt/stone
        commands.append(f'/setblock {x} {y} {z} grass_block')
        for below in range(base_y - 5, y):
            if y - below <= 3:
                commands.append(f'/setblock {x} {below} {z} dirt')
            else:
                commands.append(f'/setblock {x} {below} {z} stone')
""", description="Rolling hills terrain")
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
        # Ridged noise for mountain peaks
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
""", description="Mountain range")
```

### Valley/River Bed

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
    
    # Carve valley
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
""", description="River valley")
```

---

## Architectural Algorithms

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
    y = base_y + step // 3  # Rise every 3 steps
    
    x = int(cx + math.cos(angle) * radius)
    z = int(cz + math.sin(angle) * radius)
    
    # Determine stair facing based on angle
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
width = 7  # Odd number for center
height = 10

half_w = width // 2

# Pointed arch using two circles
for y in range(height):
    if y < height - 3:
        # Vertical sides
        commands.append(f'/setblock {base_x} {base_y + y} {base_z} stone_bricks')
        commands.append(f'/setblock {base_x + width - 1} {base_y + y} {base_z} stone_bricks')
    else:
        # Curved top (two arcs meeting at point)
        progress = (y - (height - 3)) / 3
        left_inset = int(half_w * progress)
        right_inset = int(half_w * progress)
        
        for x in range(left_inset, width - right_inset):
            commands.append(f'/setblock {base_x + x} {base_y + y} {base_z} stone_bricks')
""", description="Gothic pointed arch")
```

### Rose Window

```python
build(code="""
commands = []
import math

cx, cy, cz = 105, 75, 200
radius = 6
petals = 8

# Outer ring
for angle_deg in range(360):
    angle = math.radians(angle_deg)
    x = int(cx + math.cos(angle) * radius)
    y = int(cy + math.sin(angle) * radius)
    commands.append(f'/setblock {x} {y} {cz} stone_bricks')

# Petal dividers
for i in range(petals):
    angle = math.radians(i * 360 / petals)
    for r in range(1, radius):
        x = int(cx + math.cos(angle) * r)
        y = int(cy + math.sin(angle) * r)
        commands.append(f'/setblock {x} {y} {cz} stone')

# Fill petals with colored glass
colors = ['red_stained_glass', 'orange_stained_glass', 'yellow_stained_glass', 
          'lime_stained_glass', 'blue_stained_glass', 'purple_stained_glass',
          'magenta_stained_glass', 'cyan_stained_glass']

for i in range(petals):
    start_angle = math.radians(i * 360 / petals + 360 / petals / 4)
    end_angle = math.radians((i + 1) * 360 / petals - 360 / petals / 4)
    
    for r in range(2, radius - 1):
        for angle_offset in range(-15, 16, 5):
            angle = start_angle + math.radians(angle_offset)
            x = int(cx + math.cos(angle) * r)
            y = int(cy + math.sin(angle) * r)
            commands.append(f'/setblock {x} {y} {cz} {colors[i % len(colors)]}')
""", description="Gothic rose window")
```

### Crenellations (Battlements)

```python
build(code="""
commands = []

base_x, base_y, base_z = 100, 70, 200
length = 20
merlon_width = 2  # Raised parts
crenel_width = 1  # Gaps
height = 3        # Height of merlons

x = base_x
while x < base_x + length:
    # Merlon (raised part)
    for dx in range(merlon_width):
        if x + dx < base_x + length:
            for dy in range(height):
                commands.append(f'/setblock {x + dx} {base_y + dy} {base_z} stone_bricks')
    x += merlon_width
    
    # Crenel (gap) - just skip
    x += crenel_width
""", description="Wall battlements")
```

---

## Pattern Generation

### Checkerboard

```python
build(code="""
commands = []
base_x, base_y, base_z = 100, 64, 200
size = 16

for x in range(size):
    for z in range(size):
        if (x + z) % 2 == 0:
            block = 'white_concrete'
        else:
            block = 'black_concrete'
        commands.append(f'/setblock {base_x + x} {base_y} {base_z + z} {block}')
""", description="Checkerboard floor")
```

### Gradient

```python
build(code="""
commands = []
base_x, base_y, base_z = 100, 64, 200
length = 20

# Gradient from white to black
palette = ['white_concrete', 'light_gray_concrete', 'gray_concrete', 'black_concrete']

for x in range(length):
    progress = x / (length - 1)
    index = int(progress * (len(palette) - 1))
    commands.append(f'/setblock {base_x + x} {base_y} {base_z} {palette[index]}')
""", description="Horizontal gradient")
```

### Radial Pattern

```python
build(code="""
commands = []
cx, cy, cz = 110, 64, 210
radius = 15

# Concentric rings
palette = ['white_wool', 'orange_wool', 'magenta_wool', 'light_blue_wool', 
           'yellow_wool', 'lime_wool', 'pink_wool', 'gray_wool']

for x in range(cx - radius, cx + radius + 1):
    for z in range(cz - radius, cz + radius + 1):
        dist = int(((x-cx)**2 + (z-cz)**2)**0.5)
        if dist <= radius:
            index = dist % len(palette)
            commands.append(f'/setblock {x} {cy} {z} {palette[index]}')
""", description="Radial floor pattern")
```

### Brick Pattern

```python
build(code="""
commands = []
base_x, base_y, base_z = 100, 64, 200
width = 20
height = 10
brick_width = 4
brick_height = 2

for y in range(height):
    offset = (y // brick_height * 2) % brick_width  # Stagger every row
    for x in range(width):
        # Vertical mortar line
        if (x + offset) % brick_width == 0:
            block = 'gray_concrete'
        # Horizontal mortar line
        elif y % brick_height == 0:
            block = 'gray_concrete'
        else:
            block = 'red_terracotta'
        commands.append(f'/setblock {base_x + x} {base_y + y} {base_z} {block}')
""", description="Brick wall pattern")
```

---

## Complex Structures

### Tower with Windows

```python
build(code="""
commands = []
import math

cx, cz = 105, 205
base_y = 64
radius = 8
height = 25
wall_thickness = 1
window_interval = 5  # Height between windows
windows_per_level = 4

# Build cylindrical wall
for y in range(base_y, base_y + height):
    for angle_deg in range(360):
        angle = math.radians(angle_deg)
        
        # Outer wall
        x = int(cx + math.cos(angle) * radius)
        z = int(cz + math.sin(angle) * radius)
        
        # Check if this is a window position
        is_window = False
        if (y - base_y) % window_interval == 3:  # Window row
            window_angle = ((y - base_y) // window_interval * 45) % 360
            for w in range(windows_per_level):
                w_angle = (window_angle + w * 90) % 360
                if abs(angle_deg - w_angle) < 10 or abs(angle_deg - w_angle) > 350:
                    is_window = True
        
        if is_window:
            block = 'glass_pane'
        else:
            block = 'stone_bricks'
        
        commands.append(f'/setblock {x} {y} {z} {block}')

# Cone roof
for y in range(height, height + 8):
    layer = y - height
    roof_radius = radius - layer
    if roof_radius < 1:
        break
    for angle_deg in range(360):
        angle = math.radians(angle_deg)
        x = int(cx + math.cos(angle) * roof_radius)
        z = int(cz + math.sin(angle) * roof_radius)
        commands.append(f'/setblock {x} {base_y + y} {z} dark_oak_planks')
""", description="Tower with windows and roof")
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
    # Parabolic arc
    progress = (x - start_x) / length
    arc = math.sin(progress * math.pi) * arc_height
    y = int(base_y + arc)
    
    # Bridge surface
    for dz in range(-2, 3):
        commands.append(f'/setblock {x} {y} {z + dz} stone_brick_slab[type=top]')
    
    # Railings
    commands.append(f'/setblock {x} {y + 1} {z - 2} stone_brick_wall')
    commands.append(f'/setblock {x} {y + 1} {z + 2} stone_brick_wall')
    
    # Support columns at intervals
    if (x - start_x) % 5 == 0:
        for support_y in range(base_y - 5, y):
            commands.append(f'/setblock {x} {support_y} {z} stone_bricks')
""", description="Arched bridge")
```

### Spiral Tower

```python
build(code="""
commands = []
import math

cx, cz = 105, 205
base_y = 64
height = 40
base_radius = 10
top_radius = 5

for y in range(base_y, base_y + height):
    progress = (y - base_y) / height
    # Radius decreases as we go up
    radius = base_radius - (base_radius - top_radius) * progress
    # Spiral offset
    spiral_offset = progress * 4 * math.pi  # 2 full rotations
    
    for angle_deg in range(360):
        angle = math.radians(angle_deg) + spiral_offset
        x = int(cx + math.cos(angle) * radius)
        z = int(cz + math.sin(angle) * radius)
        
        # Only outer shell
        inner_x = int(cx + math.cos(angle) * (radius - 1))
        inner_z = int(cz + math.sin(angle) * (radius - 1))
        
        if (x, z) != (inner_x, inner_z):
            commands.append(f'/setblock {x} {y} {z} prismarine')
""", description="Spiral tower")
```

---

## Performance Tips

### Batching Commands

```python
# GOOD: Use /fill for rectangular regions
build(commands=[
    "/fill 100 64 200 120 64 220 oak_planks"  # 1 command for 420 blocks
])

# AVOID: Individual setblock for large regions
# This would be 420 commands instead of 1
```

### Chunking Large Builds

```python
# For very large builds, split into sections
def build_section(section_id, total_sections):
    commands = []
    # Calculate which portion of the build this section handles
    # Only generate commands for this section
    return commands

# Execute each section separately
for i in range(total_sections):
    section_cmds = build_section(i, total_sections)
    build(commands=section_cmds, description=f"Section {i+1}")
```

### Hollow vs Solid

```python
# For large shapes, prefer hollow
# Hollow sphere: ~1,200 blocks (shell only)
# Solid sphere: ~4,200 blocks (filled)

# Only place blocks on the surface:
if radius - 1 <= dist <= radius:  # Shell only
    commands.append(...)
```

---

## Algorithm Reference

### Common Formulas

```python
# Sphere: x² + y² + z² ≤ r²
if (x-cx)**2 + (y-cy)**2 + (z-cz)**2 <= radius**2:

# Ellipsoid: (x/a)² + (y/b)² + (z/c)² ≤ 1
if (x-cx)**2/a**2 + (y-cy)**2/b**2 + (z-cz)**2/c**2 <= 1:

# Cylinder: x² + z² ≤ r² (for all y)
if (x-cx)**2 + (z-cz)**2 <= radius**2:

# Torus: (√(x²+z²) - R)² + y² ≤ r²
dist_xz = ((x-cx)**2 + (z-cz)**2)**0.5
if (dist_xz - major_radius)**2 + (y-cy)**2 <= minor_radius**2:

# Sine wave terrain: y = base + amplitude * sin(x * frequency)
y = base_y + int(amplitude * sin(x * 0.1))

# Exponential decay (for trees, mountains):
value = amplitude * math.exp(-distance / falloff)
```

### Randomization Seeds

```python
# For reproducible "random" builds:
import random
random.seed(42)  # Same seed = same result

# For unique builds each time:
import random
random.seed()  # Uses current time
```

---

## Integration with WorldEdit

For very large or performance-critical builds, combine procedural generation with WorldEdit:

```python
# Generate shape, then use WorldEdit for bulk operations
build(code="""
commands = []

# First, generate the hollow sphere with WorldEdit
commands.append('//pos1 95,60,195')
commands.append('//pos2 115,80,215')
commands.append('//sphere stone 10')

# Then add procedural details with setblock
import random
random.seed(42)
for i in range(50):  # Random crystals
    angle = random.uniform(0, 6.28)
    y = random.randint(65, 75)
    x = int(105 + random.uniform(8, 12) * math.cos(angle))
    z = int(205 + random.uniform(8, 12) * math.sin(angle))
    commands.append(f'/setblock {x} {y} {z} amethyst_block')
""", description="Geode with crystals")
```

---

**Combine with WorldEdit expressions for maximum power!**
