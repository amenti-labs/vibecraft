---
name: using-worldedit
description: WorldEdit commands for BULK operations - terrain modification, large fills, copy/paste, spheres/cylinders. For detailed structures with oriented blocks (doors, stairs), use build_schematic instead. WorldEdit is best for terrain, large regions, and geometric shapes.
---

# Using WorldEdit

## When to Use WorldEdit vs Schematics

| Task | Use WorldEdit | Use build_schematic |
|------|---------------|---------------------|
| Flatten terrain | ✅ `//set grass` | |
| Fill large area | ✅ `//set stone` | |
| Spheres, cylinders | ✅ `//sphere`, `//cyl` | |
| Copy/paste | ✅ `//copy`, `//paste` | |
| Terrain smoothing | ✅ `//smooth` | |
| Pattern fills | ✅ `50%stone,50%cobble` | |
| Structures with doors | | ✅ |
| Stairs, oriented blocks | | ✅ |
| Fine detail work | | ✅ |
| Precise block states | | ✅ |

**Rule of thumb**: WorldEdit for bulk/terrain, Schematics for detailed structures.

## WorldEdit via Client Bridge

Commands execute **as the local player** through the Fabric client bridge.

### Key Rules:
- ✅ Use `//` prefix for WorldEdit commands
- ✅ Comma-separated coordinates: `//pos1 100,64,200`
- ❌ Never use `execute as` wrappers
- ⛔ NEVER teleport the player

## Selection Commands

```
//pos1 100,64,200      # First corner
//pos2 120,80,220      # Second corner
//expand 5 up          # Expand up
//expand vert          # Full height
//contract 3 north     # Shrink from north
//shift 10 east        # Move selection
//inset 2              # Shrink all sides
//outset 3             # Expand all sides
//sel cuboid|sphere|cyl|poly  # Selection mode
//size                 # Show size
```

## Region Commands

```
//set stone                       # Fill selection
//set 50%stone,50%cobblestone     # Random mix
//replace dirt grass_block        # Replace blocks
//walls stone                     # Only walls
//faces stone                     # All 6 faces
//hollow                          # Remove interior
//move 10 up                      # Move selection
//stack 5 north                   # Stack copies
```

## Generation Commands

```
//sphere stone 10      # Solid sphere r=10
//hsphere stone 10     # Hollow sphere
//cyl stone 5 10       # Cylinder r=5 h=10
//hcyl stone 5 10      # Hollow cylinder
//pyramid stone 15     # Pyramid
//generate stone (x*x+y*y+z*z)<100  # Expression
```

## Terrain Commands

```
//smooth 3             # Smooth terrain
//naturalize           # Add dirt/stone layers
//flora 10             # Add flowers/grass
//forest 20 oak        # Generate forest
//drain 10             # Remove water/lava
//fixwater 10          # Fix water flow
```

## Clipboard Commands

```
//copy                 # Copy selection
//cut                  # Copy + clear
//paste                # Paste at player
//paste -a             # Paste, skip air
//rotate 90            # Rotate clipboard
//flip north           # Mirror clipboard
```

## Patterns

```
stone                             # Single block
50%stone,50%cobblestone           # Random percentage
oak_stairs[facing=north]          # With block state
```

## Masks

```
-m stone              # Only affect stone
-m !air               # Exclude air
-m stone,cobble       # Multiple blocks
```

## Common Workflows

### Terrain Prep for Building
```python
build(commands=[
    "//pos1 100,60,200",
    "//pos2 150,70,250",
    "//set grass_block",
    "//smooth 2"
], description="Flatten area")
```

### Create Platform
```python
build(commands=[
    "//pos1 100,64,200",
    "//pos2 120,64,220",
    "//set stone_bricks"
], description="Stone platform")
```

### Forest Generation
```
//pos1 100,64,200
//pos2 200,64,300
//forest oak 5
```

### Large Sphere
```
//pos1 95,70,195      # Center - radius
//pos2 115,90,215     # Center + radius
//sphere stone 10
```

## Using build() for WorldEdit

```python
build(commands=[
    "//pos1 100,64,200",
    "//pos2 120,80,220",
    "//set stone_bricks",
    "//walls oak_planks",
    "//hollow"
], description="Basic shell")
```

## ⛔ Commands That DON'T Work via RCON

**Brushes** (require player click):
```
❌ //br sphere stone 5
❌ //br cyl stone 3 1
❌ //brush smooth 3
```

**Tool bindings** (require held item):
```
❌ //tool tree
❌ //tool info
```

**Alternatives for trees:**
```
✅ //forest oak 5        # Selection-based
✅ //forestgen 50 oak 5  # Standalone
```

## History

```
//undo                 # Undo last
//redo                 # Redo
//undo 5               # Undo 5 actions
```

## After WorldEdit: Add Details with Schematics

Typical workflow:
1. Use WorldEdit to prepare terrain and create bulk structure
2. Use `build_schematic()` to add doors, stairs, furniture, details

```python
# Step 1: WorldEdit for bulk
build(commands=[
    "//pos1 100,64,200",
    "//pos2 120,68,220",
    "//set oak_planks",
    "//hollow"
], description="House shell")

# Step 2: Schematic for details
build_schematic(
  schematic={
    "anchor": [100, 64, 220],  # South wall
    "palette": {
      "Dl": "oak_door[facing=south,half=lower]",
      "Du": "oak_door[facing=south,half=upper]",
      "W": "oak_planks"
    },
    "layers": [
      {"y": 1, "grid": [["W", "Dl", "W"]]},
      {"y": 2, "grid": [["W", "Du", "W"]]}
    ]
  },
  description="Add door"
)
```
