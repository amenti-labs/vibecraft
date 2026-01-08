---
name: using-worldedit
description: Executes WorldEdit commands in Minecraft using VibeCraft MCP tools. Use when running WorldEdit commands like //set, //replace, //copy, //paste, selections, brushes, or any WorldEdit operation. Provides command syntax, patterns, masks, and expressions.
---

# Using WorldEdit

Execute WorldEdit commands via VibeCraft MCP tools.

## MCP Tools

### Selection
- `worldedit_selection` - pos1, pos2, expand, contract, shift, sel

### Region
- `worldedit_region` - set, replace, walls, faces, hollow, line, curve

### Generation
- `worldedit_generation` - sphere, cylinder, pyramid, cone

### Clipboard
- `worldedit_clipboard` - copy, cut, paste, rotate, flip

### Advanced
- `worldedit_deform` - Math expressions for deformation
- `worldedit_vegetation` - Trees, flora, forests
- `worldedit_terrain_advanced` - Smooth, naturalize, caves

### Direct Execution
- `rcon_command(command="...")` - Any WorldEdit command

## Command Syntax

**From RCON, use SINGLE slash `/`, not double `//`!**

```python
# Correct
rcon_command(command="/pos1 100,64,200")
rcon_command(command="/set stone")

# Or use MCP tools
worldedit_selection(command="pos1 100,64,200")
worldedit_region(command="set stone")
```

**Coordinates are comma-separated:**
```
/pos1 100,64,200  ✓ Correct
/pos1 100 64 200  ✗ Wrong
```

## Selection Commands

### Set Positions
```
/pos1 100,64,200      # First corner
/pos2 120,80,220      # Second corner
/pos1                 # Use player position
/hpos1                # Position at crosshair
```

### Modify Selection
```
/expand 5 up          # Expand up
/expand 5 down        # Expand down
/expand vert          # Full height
/contract 3 north     # Shrink from north
/shift 10 east        # Move selection
/inset 2              # Shrink all sides
/outset 2             # Expand all sides
```

### Selection Modes
```
/sel cuboid           # Default rectangular
/sel extend           # Extends existing
/sel poly             # Polygon (2D)
/sel sphere           # Spherical
/sel cyl              # Cylindrical
```

### Info
```
/size                 # Show selection size
/count stone          # Count specific block
```

## Region Commands

### Fill
```
/set stone                      # Fill with stone
/set air                        # Clear
/set 50%stone,50%cobblestone    # Random mix
```

### Replace
```
/replace dirt grass_block       # Dirt → Grass
/replace stone,cobble air       # Multiple → Air
/replacenear 20 stone cobble    # Near player
```

### Structure
```
/walls stone          # Only walls
/faces stone          # All 6 faces
/outline stone        # 3D outline
/hollow               # Remove interior
/center stone         # Single center block
```

### Transform
```
/move 10 up           # Move selection
/stack 5 north        # Stack copies
/copy                 # To clipboard
/cut                  # Copy + clear
/paste                # From clipboard
/rotate 90            # Rotate clipboard
/flip north           # Mirror clipboard
```

## Patterns

### Simple
```
stone                 # Single block
oak_planks
```

### Random
```
50%stone,50%cobblestone         # Equal chance
80%stone,15%cobble,5%gravel     # Weighted
```

### Block States
```
oak_stairs[facing=north,half=bottom]
oak_log[axis=y]
```

### Pattern Types
```
#clipboard            # From clipboard
#existing             # Keep existing block type
#solid                # Only solid blocks
```

## Masks

### Block Masks
```
-m stone              # Only affect stone
-m !air               # Exclude air
-m stone,cobble       # Multiple blocks
```

### Region Masks
```
-m #region            # Only in selection
-m #existing          # Only existing blocks
```

### Combined
```
-m "stone,cobble !air"   # Stone/cobble but not air
```

## Generation Commands

### Shapes
```
/sphere stone 10              # Solid sphere r=10
/hsphere stone 10             # Hollow sphere
/cyl stone 5 10               # Cylinder r=5 h=10
/hcyl glass 5 10              # Hollow cylinder
/pyramid sandstone 15         # Pyramid base=15
```

### Expressions
```
/generate stone (x*x+y*y+z*z)<100     # Sphere equation
/generate -h stone ...                 # Hollow variant
```

## Brush Commands

### Setup Brush
```
/br sphere stone 5            # Sphere brush r=5
/br cyl stone 3 1             # Cylinder brush
/br smooth 3                  # Smooth brush
/br gravity                   # Gravity brush
```

### Brush Settings
```
/mask stone                   # Only affect stone
/material cobble              # Set material
/range 100                    # Max range
/size 5                       # Brush size
```

## Utility Commands

### Fix
```
/drain 10                     # Remove water/lava
/fixwater 10                  # Fix water flow
/fixlava 10                   # Fix lava flow
```

### Clear
```
/removeabove 10               # Clear above
/removebelow 10               # Clear below
/removenear stone 10          # Remove nearby
```

### Nature
```
/flora 10                     # Add flowers/grass
/forest 20 oak                # Generate forest
/tree oak                     # Single tree
/pumpkins 5                   # Pumpkin patch
```

## Terrain Commands

```
/smooth 3                     # Smooth terrain
/naturalize                   # Add dirt/stone layers
/regen                        # Regenerate chunks
```

## Expression Syntax

### Variables
```
x, y, z       # Coordinates relative to center
```

### Operators
```
+ - * / ^     # Math
< > == !=     # Comparison
&& || !       # Logic
```

### Functions
```
sqrt(), sin(), cos(), tan()
abs(), floor(), ceil()
perlin(), voronoi()
```

### Shape Formulas
```
# Sphere
(x*x+y*y+z*z)<r^2

# Ellipsoid
(x/a)^2+(y/b)^2+(z/c)^2<1

# Torus
(sqrt(x*x+z*z)-R)^2+y*y<r^2

# Sine wave
y<sin(x/5)*3+sin(z/5)*3
```

For detailed expressions, see [expressions.md](expressions.md).

## History

```
/undo                 # Undo last action
/redo                 # Redo
/undo 5               # Undo 5 actions
/clearhistory         # Clear undo history
```

## Quick Reference

| Task | Command |
|------|---------|
| Fill region | `/set block` |
| Replace | `/replace old new` |
| Walls only | `/walls block` |
| Hollow out | `/hollow` |
| Copy | `/copy` then `/paste` |
| Rotate | `/rotate 90` |
| Sphere | `/sphere block radius` |
| Smooth | `/smooth iterations` |
| Undo | `/undo` |

## Common Workflows

### Build Foundation
```
/pos1 100,64,200
/pos2 120,64,220
/set oak_planks
```

### Build Walls
```
/pos1 100,64,200
/pos2 120,70,220
/walls cobblestone
```

### Smooth Terrain
```
/pos1 ...
/pos2 ...
/smooth 3
```
