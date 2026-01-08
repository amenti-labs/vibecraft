# WorldEdit Expression Guide

Complete reference for WorldEdit's expression parser used in `//generate`, `//deform`, and expression masks.

## Overview

WorldEdit expressions are mathematical formulas that evaluate to determine block placement or transformation. They're incredibly powerful for creating organic shapes, terrain, and complex geometric forms.

**Commands that use expressions:**
- `//generate <block> <expression>` - Generate shapes based on formula
- `//deform <expression>` - Transform existing blocks mathematically  
- `//gmask =<expression>` - Expression-based global masks
- Brush expressions

## Basic Syntax

### Variables

| Variable | Description |
|----------|-------------|
| `x` | X coordinate (relative to selection center) |
| `y` | Y coordinate (relative to selection center) |
| `z` | Z coordinate (relative to selection center) |

**Coordinate modes:**
- Default: Normalized to -1 to 1 range across selection
- `-r` flag: Raw block coordinates
- `-o` flag: Offset from selection origin
- `-c` flag: Chunk-relative coordinates

### Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `+` | Addition | `x + 1` |
| `-` | Subtraction | `y - 0.5` |
| `*` | Multiplication | `x * 2` |
| `/` | Division | `y / 3` |
| `^` | Exponentiation | `x^2` |
| `%` | Modulo | `x % 5` |
| `<` | Less than | `y < 0` |
| `>` | Greater than | `x > 0.5` |
| `<=` | Less or equal | `y <= 1` |
| `>=` | Greater or equal | `x >= -1` |
| `==` | Equal | `y == 0` |
| `!=` | Not equal | `x != 0` |
| `&&` | Logical AND | `x > 0 && y > 0` |
| `\|\|` | Logical OR | `x < -1 \|\| x > 1` |
| `!` | Logical NOT | `!(x > 0)` |
| `? :` | Ternary | `y > 0 ? 1 : 0` |

### Mathematical Functions

| Function | Description | Example |
|----------|-------------|---------|
| `abs(x)` | Absolute value | `abs(x)` |
| `sqrt(x)` | Square root | `sqrt(x^2+y^2)` |
| `sin(x)` | Sine (radians) | `sin(x*pi)` |
| `cos(x)` | Cosine | `cos(y*pi)` |
| `tan(x)` | Tangent | `tan(x)` |
| `asin(x)` | Arc sine | `asin(y)` |
| `acos(x)` | Arc cosine | `acos(x)` |
| `atan(x)` | Arc tangent | `atan(y/x)` |
| `atan2(y,x)` | Two-arg arctan | `atan2(z,x)` |
| `floor(x)` | Round down | `floor(y)` |
| `ceil(x)` | Round up | `ceil(y)` |
| `round(x)` | Round nearest | `round(x)` |
| `min(a,b)` | Minimum | `min(x,y)` |
| `max(a,b)` | Maximum | `max(x,y)` |
| `ln(x)` | Natural log | `ln(x+1)` |
| `log(x)` | Base-10 log | `log(y)` |
| `log(x,b)` | Log base b | `log(x,2)` |
| `exp(x)` | e^x | `exp(-x^2)` |

### Constants

| Constant | Value |
|----------|-------|
| `pi` | 3.14159... |
| `e` | 2.71828... |
| `true` | 1 |
| `false` | 0 |

### Noise Functions (Advanced)

| Function | Description |
|----------|-------------|
| `perlin(seed,x,y,z,freq,octaves,persist)` | Perlin noise |
| `voronoi(seed,x,y,z,freq)` | Voronoi/cell noise |
| `ridgedmulti(seed,x,y,z,freq,octaves)` | Ridged multifractal |
| `simplex(seed,x,y,z)` | Simplex noise (faster than perlin) |

---

## Shape Formulas

### Basic 3D Shapes

**Solid Sphere:**
```
//generate stone x^2+y^2+z^2 < 1
```
Explanation: Points where distance from center < radius are filled.

**Hollow Sphere:**
```
//generate -h stone x^2+y^2+z^2 < 1
```
The `-h` flag generates only the shell.

**Ellipsoid:**
```
//generate stone (x/a)^2 + (y/b)^2 + (z/c)^2 < 1
```
Where a, b, c are the radii along each axis. Example for tall ellipsoid:
```
//generate stone (x/10)^2 + (y/20)^2 + (z/10)^2 < 1
```

**Cylinder (vertical):**
```
//generate stone x^2 + z^2 < 1
```
No y constraint = infinite height (bounded by selection).

**Cylinder (horizontal, along X axis):**
```
//generate stone y^2 + z^2 < 1
```

**Cone (point up):**
```
//generate stone x^2 + z^2 < (1-y)^2 && y > 0 && y < 1
```

**Cone (point down):**
```
//generate stone x^2 + z^2 < y^2 && y > 0 && y < 1
```

**Cube (not very useful, but possible):**
```
//generate stone abs(x) < 1 && abs(y) < 1 && abs(z) < 1
```

### Advanced Shapes

**Torus (Donut):**
```
//generate stone (sqrt(x^2+z^2)-R)^2 + y^2 < r^2
```
Where R = major radius (ring), r = minor radius (tube thickness).
Example: R=0.7, r=0.3
```
//generate stone (sqrt(x^2+z^2)-0.7)^2 + y^2 < 0.09
```

**Vertical Torus (standing donut):**
```
//generate stone (sqrt(x^2+y^2)-0.7)^2 + z^2 < 0.09
```

**Heart Shape (2D extruded):**
```
//generate stone (x^2+y^2-1)^3 - x^2*y^3 < 0
```
3D heart requires more complex formula.

**Star (2D, 5-pointed, extruded vertically):**
```
//generate stone cos(5*atan2(z,x))*sqrt(x^2+z^2) < 0.5+0.3*cos(5*atan2(z,x))
```

**Helix/Spiral:**
```
//generate stone (x-0.5*cos(y*2*pi))^2 + (z-0.5*sin(y*2*pi))^2 < 0.04
```
This creates a spiral staircase-like shape.

**Hyperboloid (cooling tower shape):**
```
//generate stone x^2 + z^2 - y^2 < 0.1 && y > -1 && y < 1
```

**Paraboloid (satellite dish):**
```
//generate stone y > x^2 + z^2 && y < 1
```

**Saddle (Pringle shape):**
```
//generate stone abs(x^2 - z^2 - y) < 0.1
```

### Wave and Terrain Shapes

**Sine Wave Surface:**
```
//generate stone y < 0.3*sin(x*3) + 0.3*cos(z*3)
```

**Ripple Effect (concentric waves):**
```
//generate stone y < 0.2*sin(sqrt(x^2+z^2)*5)
```

**Egg/Ovoid:**
```
//generate stone x^2 + z^2 + (y*1.3)^2 < 1 && y > -0.5
```

**Capsule (pill shape):**
```
//generate stone x^2+z^2 < 0.25 && y > -0.5 && y < 0.5 || x^2+z^2+(y-0.5)^2 < 0.25 || x^2+z^2+(y+0.5)^2 < 0.25
```

### Compound Shapes

**Sphere with hole (bead):**
```
//generate stone x^2+y^2+z^2 < 1 && !(x^2+z^2 < 0.1)
```

**Box with rounded edges:**
```
//generate stone max(abs(x),max(abs(y),abs(z))) < 0.8 || x^2+y^2+z^2 < 1
```

**Difference (subtraction) - Sphere minus Cube:**
```
//generate stone x^2+y^2+z^2 < 1 && !(abs(x) < 0.5 && abs(y) < 0.5 && abs(z) < 0.5)
```

---

## Deform Expressions

The `//deform` command transforms existing blocks using expressions that modify coordinates.

### Syntax
```
//deform <expression>
```

The expression modifies `x`, `y`, `z` to move blocks. Use `x+=`, `y-=`, etc.

### Examples

**Twist around Y axis:**
```
//deform swap(x,z,sin(y)*x+cos(y)*z,cos(y)*x-sin(y)*z)
```
Simpler approximation:
```
//deform x+=sin(y*0.1)*2;z+=cos(y*0.1)*2
```

**Bulge outward:**
```
//deform x*=1+0.2*sin(y*pi);z*=1+0.2*sin(y*pi)
```

**Wave distortion:**
```
//deform y+=0.3*sin(x*3);y+=0.2*cos(z*3)
```

**Pinch at center:**
```
//deform x*=y^2;z*=y^2
```

**Spherical bulge:**
```
//deform r=sqrt(x^2+z^2);f=1+0.3*sin(r*5);x*=f;z*=f
```

**Shear:**
```
//deform x+=y*0.5
```

**Scale non-uniformly:**
```
//deform x*=2;y*=0.5
```

---

## Noise-Based Generation

### Perlin Noise Terrain

**Basic terrain:**
```
//generate stone y < perlin(1,x,0,z,1,4,0.5)*0.5
```

Parameters: `perlin(seed, x, y, z, frequency, octaves, persistence)`
- `seed` - Random seed
- `frequency` - Scale of noise (higher = more detail)
- `octaves` - Layers of detail (4-8 typical)
- `persistence` - How much each octave contributes

**Mountainous terrain:**
```
//generate stone y < perlin(1,x,0,z,0.5,6,0.6)*0.8
```

**Islands with erosion effect:**
```
//generate stone y < perlin(1,x,0,z,1,4,0.5)*0.5 - sqrt(x^2+z^2)*0.3
```
The `-sqrt(x^2+z^2)*0.3` makes edges slope into water.

### Voronoi (Cell) Patterns

**Crystal/cell structures:**
```
//generate stone voronoi(1,x,y,z,2) > 0.3
```

**Cracked ground effect:**
```
//generate stone y < 0 || voronoi(1,x,0,z,4) > 0.2
```

### Ridged Multifractal

**Sharp mountain ridges:**
```
//generate stone y < ridgedmulti(1,x,0,z,1,4)*0.7
```

---

## Practical Examples

### Building Components

**Dome roof:**
```
//pos1 X,Y,Z  (corner 1)
//pos2 X2,Y2,Z2  (corner 2, Y2 should be Y + dome height)
//generate stone y > 0 && x^2+y^2+z^2 < 1 && y < sqrt(1-x^2-z^2)
```

**Arch (semicircular):**
```
//generate stone y > 0 && x^2+y^2 < 1 && abs(z) < 0.1
```

**Gothic pointed arch:**
```
//generate stone (x+0.3)^2+y^2 < 0.5 && (x-0.3)^2+y^2 < 0.5 && y > 0 && abs(z) < 0.1
```

**Spiral staircase column:**
```
//generate stone x^2+z^2 < 0.2 || ((x-0.5*cos(y*2))^2+(z-0.5*sin(y*2))^2 < 0.05)
```

**Buttress (angled support):**
```
//generate stone x > 0 && z < 0 && x+z+y < 1 && x+z > 0
```

### Decorative Elements

**Ornate pillar with bulges:**
```
//generate stone x^2+z^2 < (0.3+0.1*sin(y*5))^2
```

**Twisted pillar:**
```
//generate stone (x*cos(y*0.5)-z*sin(y*0.5))^2 + (x*sin(y*0.5)+z*cos(y*0.5))^2 < 0.25
```

**Fluted column (grooves):**
```
//generate stone x^2+z^2 < 0.3 - 0.05*cos(8*atan2(z,x))
```

### Organic Shapes

**Tree trunk with roots:**
```
//generate oak_log x^2+z^2 < (0.2 + max(0,-y)*0.3)^2
```
The roots flare out as y decreases.

**Boulder/rock:**
```
//generate stone x^2+y^2+z^2 < (0.8+0.2*perlin(1,x*3,y*3,z*3,1,2,0.5))^2
```

**Stalactite/Stalagmite:**
```
//generate stone x^2+z^2 < (1-y)^4*0.3 && y > 0
```

---

## Expression Masks

Use expressions in masks for complex filtering.

**Gradient mask (fade by height):**
```
//gmask =y>0.5
```

**Radial gradient:**
```
//gmask =sqrt(x^2+z^2)<0.7
```

**Noise-based mask:**
```
//gmask =perlin(1,x,y,z,2,2,0.5)>0.3
```

**Checkerboard:**
```
//gmask =(floor(x)+floor(y)+floor(z))%2==0
```

---

## Performance Tips

1. **Use `-h` flag** for hollow shapes - much faster than solid
2. **Simplify expressions** where possible - fewer operations = faster
3. **Limit selection size** - expressions evaluate per-block
4. **Use raw mode `-r`** when precision matters more than normalization
5. **Test on small selections first** before large operations

## Common Mistakes

1. **Forgetting coordinate normalization** - Default is -1 to 1, not block coords
2. **Missing logical operators** - Use `&&` not `and`, `||` not `or`
3. **Integer division issues** - Use `1.0` not `1` for decimals
4. **Selection orientation** - Y is always vertical in Minecraft

## Quick Reference Card

```
SHAPES:
  Sphere:     x^2+y^2+z^2 < r^2
  Cylinder:   x^2+z^2 < r^2
  Cone:       x^2+z^2 < (1-y)^2 && y>0
  Torus:      (sqrt(x^2+z^2)-R)^2 + y^2 < r^2
  Ellipsoid:  (x/a)^2+(y/b)^2+(z/c)^2 < 1

OPERATIONS:
  Union:      A || B
  Intersect:  A && B
  Subtract:   A && !B

NOISE:
  perlin(seed,x,y,z,freq,oct,persist)
  voronoi(seed,x,y,z,freq)
  ridgedmulti(seed,x,y,z,freq,oct)

USEFUL:
  Distance:   sqrt(x^2+y^2+z^2)
  Angle:      atan2(z,x)
  Normalize:  v/sqrt(v^2)
```
