---
name: using-worldedit
description: Executes WorldEdit commands in Minecraft using VibeCraft MCP tools. Use when running WorldEdit commands like //set, //replace, //copy, //paste, selections, brushes, or any WorldEdit operation. Provides command syntax, patterns, masks, and expressions.
---

# Using WorldEdit

## MCP Tools
- `worldedit_selection` - pos1, pos2, expand, contract, shift, sel
- `worldedit_region` - set, replace, walls, faces, hollow, line, curve
- `worldedit_generation` - sphere, cylinder, pyramid, cone
- `worldedit_clipboard` - copy, cut, paste, rotate, flip
- `worldedit_deform` - Math expressions
- `worldedit_terrain_advanced` - smooth, naturalize, caves
- `rcon_command(command="...")` - Any WorldEdit command

## Syntax
**From RCON: SINGLE slash `/`, not double `//`!**
**Coordinates: comma-separated** `/pos1 100,64,200` ✓

## Selection Commands
```
/pos1 100,64,200      # First corner
/pos2 120,80,220      # Second corner
/expand 5 up          # Expand up
/expand vert          # Full height
/contract 3 north     # Shrink from north
/shift 10 east        # Move selection
/inset 2              # Shrink all sides
/sel cuboid|sphere|cyl|poly  # Selection mode
/size                 # Show size
```

## Region Commands
```
/set stone                       # Fill
/set 50%stone,50%cobblestone     # Random mix
/replace dirt grass_block        # Dirt → Grass
/replacenear 20 stone cobble     # Near player
/walls stone                     # Only walls
/faces stone                     # All 6 faces
/hollow                          # Remove interior
/move 10 up                      # Move selection
/stack 5 north                   # Stack copies
```

## Clipboard
```
/copy                 # To clipboard
/cut                  # Copy + clear
/paste                # From clipboard
/rotate 90            # Rotate clipboard
/flip north           # Mirror clipboard
```

## Patterns
```
stone                             # Single
50%stone,50%cobblestone           # Random
oak_stairs[facing=north,half=bottom]  # Block states
#clipboard                        # From clipboard
```

## Masks
```
-m stone              # Only affect stone
-m !air               # Exclude air
-m stone,cobble       # Multiple blocks
```

## Generation
```
/sphere stone 10      # Solid sphere r=10
/hsphere stone 10     # Hollow sphere
/cyl stone 5 10       # Cylinder r=5 h=10
/pyramid sandstone 15 # Pyramid
/generate stone (x*x+y*y+z*z)<100  # Expression
```

## Brushes
```
/br sphere stone 5    # Sphere brush
/br cyl stone 3 1     # Cylinder brush
/br smooth 3          # Smooth brush
/mask stone           # Only affect stone
/size 5               # Brush size
```

## Utility
```
/drain 10             # Remove water/lava
/fixwater 10          # Fix water flow
/removeabove 10       # Clear above
/flora 10             # Add flowers/grass
/forest 20 oak        # Generate forest
/smooth 3             # Smooth terrain
/naturalize           # Add dirt/stone layers
```

## Expressions
Variables: `x, y, z` (relative to center)
Operators: `+ - * / ^` `< > == !=` `&& || !`
Functions: `sqrt() sin() cos() abs() floor() perlin() voronoi()`

**Formulas**:
- Sphere: `(x*x+y*y+z*z)<r^2`
- Ellipsoid: `(x/a)^2+(y/b)^2+(z/c)^2<1`
- Torus: `(sqrt(x*x+z*z)-R)^2+y*y<r^2`
- Sine wave: `y<sin(x/5)*3+sin(z/5)*3`

## History
```
/undo                 # Undo last
/redo                 # Redo
/undo 5               # Undo 5 actions
```

## Quick Reference

| Task | Command |
|------|---------|
| Fill region | `/set block` |
| Replace | `/replace old new` |
| Walls only | `/walls block` |
| Hollow out | `/hollow` |
| Copy/Paste | `/copy` → `/paste` |
| Sphere | `/sphere block radius` |
| Smooth | `/smooth iterations` |

## Common Workflows

**Foundation**: `/pos1 100,64,200` → `/pos2 120,64,220` → `/set oak_planks`
**Walls**: `/pos1 100,64,200` → `/pos2 120,70,220` → `/walls cobblestone`
**Smooth terrain**: Select area → `/smooth 3`
