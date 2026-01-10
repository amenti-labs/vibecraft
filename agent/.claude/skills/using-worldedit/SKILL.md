---
name: using-worldedit
description: PRIMARY BUILDING SKILL - Use for ANY building, construction, or creation task. WorldEdit is the default tool for walls, floors, structures, shapes, terrain, and regions. Provides //set, //walls, //replace, //hollow, selections, patterns, masks, expressions, and batch operations via build(). Load this skill FIRST for any non-trivial building request.
---

# Using WorldEdit

## 🚨 CRITICAL: WorldEdit Requires Player Context!

**WorldEdit commands CANNOT run directly via RCON - they SILENTLY FAIL!**

You MUST wrap ALL WorldEdit commands with `execute as <player> at @s run`:

### Step 1: Get Player Name & Set World Context (ONCE)
```
player = get_player_position()  # Get player name from response
rcon_command("execute as {player} at @s run /world world")
```

### Step 2: Run WorldEdit Commands (SINGLE slash!)
```
rcon_command("execute as {player} at @s run /pos1 100,64,200")
rcon_command("execute as {player} at @s run /pos2 120,80,220")
rcon_command("execute as {player} at @s run /set stone_bricks")
```

### Key Rules:
- ✅ Always use `execute as <player> at @s run /command`
- ✅ Use **SINGLE slash** `/` (NOT `//`)
- ✅ Set `/world world` FIRST (once per session)
- ❌ NEVER send WorldEdit commands directly via RCON
- ⛔ NEVER teleport the player! Use pos1/pos2 with coordinates instead

### CRITICAL: NO TELEPORTING!
Commands like `/sphere` and `/cyl` create at player position. **DO NOT teleport the player to build!**

**WRONG:**
```
tp player 100 64 200              # BAD - annoying to player!
execute as player at @s run /sphere stone 10
```

**RIGHT:**
```
execute as player at @s run /pos1 90,54,190
execute as player at @s run /pos2 110,74,210
execute as player at @s run /sphere stone 10   # Uses selection center
```

**BEST (vanilla, no wrapper):**
```
/fill 90 54 190 110 74 210 stone   # Works directly!
```

## ⚡ RECOMMENDED: Use build() for Batch WorldEdit

The `build()` tool **automatically handles** player context for WorldEdit commands!

```python
# No manual wrapping needed - build() does it automatically!
build(commands=[
    "//pos1 100,64,200",
    "//pos2 120,80,220",
    "//set stone_bricks",
    "//walls oak_planks",
    "//hollow"
], description="Castle structure")
```

**How it works:**
- Commands starting with `//` are auto-detected
- Player name is fetched automatically
- World context is set once at start
- Each `//cmd` → `execute as <player> at @s run /cmd`

**Use build() for:**
- Multiple WorldEdit commands in one call
- Procedural generation with code mode
- Mixing vanilla + WorldEdit commands

**Use individual tools for:**
- Single WorldEdit operations
- Interactive/exploratory building

## MCP Tools
- `worldedit_selection` - pos1, pos2, expand, contract, shift, sel
- `worldedit_region` - set, replace, walls, faces, hollow, line, curve
- `worldedit_generation` - sphere, cylinder, pyramid, cone
- `worldedit_clipboard` - copy, cut, paste, rotate, flip
- `worldedit_deform` - Math expressions
- `worldedit_terrain_advanced` - smooth, naturalize, caves
- `rcon_command(command="...")` - Must wrap with execute!

## Syntax
**Commands need execute wrapper!** See above.
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

## ⛔ Commands That DO NOT Work via RCON

These commands require direct player interaction and **CANNOT be executed via RCON/build()**:

### Brushes (ALL brush commands)
```
/br sphere stone 5    # ❌ Requires player to hold item + right-click
/br cyl stone 3 1     # ❌ Brushes bind to items in player's hand
/br smooth 3          # ❌ Error: "must be used with a player"
/br forest oak 5      # ❌ All /brush and /br commands fail
```

### Tool Bindings
```
/tool tree            # ❌ Binds to held item
/tool info            # ❌ Requires player session
/tool deltree         # ❌ All /tool commands fail
```

### Navigation (player-position dependent)
```
/thru                 # ❌ Moves player through walls
/jumpto               # ❌ Teleports to click location
/up 10                # ❌ Creates platform under player
/ascend               # ❌ Player movement commands
```

### Why These Fail
- **Brushes** bind to the player's currently held item and activate via right-click
- **Tools** require a player session with inventory context
- **Navigation** commands operate on player position/view direction
- Even with `execute as <player>` wrapper, these need **actual player input**

### Alternatives for Trees
Instead of `/br forest`, use:
```
# Selection-based forest generation (WORKS!)
execute as {player} at @s run /pos1 100,64,200
execute as {player} at @s run /pos2 150,64,250
execute as {player} at @s run /forest oak 5

# Or standalone forestgen command
execute as {player} at @s run /forestgen 50 oak 5

# Or procedural with build():
build(code="""
commands = []
# Generate trunk
for y in range(64, 72):
    commands.append(f'/setblock 100 {y} 200 oak_log')
# Generate leaves sphere
# ... procedural code
""")
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
Variables: x, y, z (relative to center)
Operators: + - * / ^ < > == != && || !
Functions: sqrt() sin() cos() abs() floor() perlin() voronoi()

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

**REMEMBER: All commands need `execute as <player> at @s run` wrapper!**

**Foundation** (via execute wrapper):
```
execute as {player} at @s run /pos1 100,64,200
execute as {player} at @s run /pos2 120,64,220
execute as {player} at @s run /set oak_planks
```

**Walls**:
```
execute as {player} at @s run /pos1 100,64,200
execute as {player} at @s run /pos2 120,70,220
execute as {player} at @s run /walls cobblestone
```

**Alternative: Use Vanilla /fill (no wrapper needed, simpler):**
```
/fill 100 64 200 120 64 220 oak_planks
/fill 100 64 200 120 70 220 cobblestone hollow
```

**When to use WorldEdit vs Vanilla:**
- Vanilla `/fill`: Simple rectangular regions, <100 blocks, precise control
- WorldEdit: Complex shapes (spheres, cylinders), large regions, patterns
