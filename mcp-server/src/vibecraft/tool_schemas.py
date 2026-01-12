"""
MCP Tool Schema Definitions

All tool schemas for the VibeCraft MCP server.
Extracted from server.py for better maintainability.
"""

from mcp.types import Tool


def get_tool_schemas() -> list[Tool]:
    """
    Return all tool schemas for VibeCraft MCP server.

    Returns:
        List of Tool objects with name, description, and inputSchema
    """
    schemas = [
        # TIER 1: Categorized WorldEdit Tools
        Tool(
            name="worldedit_selection",
            description="""WorldEdit Selection Commands - Define and manipulate the selected region.

Before performing operations on a region, you must define it by setting positions.
World context is provided by the client player.

Key Commands:
- /pos1 X,Y,Z - Set first corner (comma-separated!)
- /pos2 X,Y,Z - Set second corner (comma-separated!)
- /sel [mode] - Change selection mode (cuboid, extend, poly, ellipsoid, sphere, cyl, convex)
- /expand <amount> [direction] - Expand selection
- /expand vert - Expand selection vertically to world limits (Y=-64 to Y=319)
- /contract <amount> [direction] - Contract selection
- /inset <amount> - Inset selection (contract all faces equally)
- /outset <amount> - Outset selection (expand all faces equally)
- /shift <amount> [direction] - Shift selection
- /size - Get selection information
- /count <mask> - Count blocks matching mask

Example Workflow:
1. /pos1 100,64,100
2. /pos2 120,80,120
3. /size
4. Now you can use region commands like /set

Selection Modes:
- cuboid (default) - Standard box selection
- extend - Extend selection with each click
- poly - 2D polygon selection
- ellipsoid - Ellipsoid selection
- sphere - Spherical selection
- cyl - Cylindrical selection
- convex - Convex hull selection

Special:
- //expand vert - Extends selection from bedrock to build limit (full height)
- //inset 2 - Shrinks selection by 2 blocks on all sides
- //outset 3 - Expands selection by 3 blocks on all sides

Note: Always use comma-separated coordinates from console!
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Selection command (e.g., 'pos1 100,64,100' or 'size' or 'sel sphere')",
                    }
                },
                "required": ["command"],
            },
        ),
        Tool(
            name="worldedit_region",
            description="""WorldEdit Region Commands - Modify the selected region.

These commands operate on your current selection (set with //pos1 and //pos2).

Most Common Commands:
- //set <pattern> - Fill region with pattern
- //replace [from] <to> - Replace blocks in selection
- //replacenear <size> <from> <to> - Replace blocks in sphere around you (no selection needed!)
- //walls <pattern> - Build walls (sides only)
- //faces <pattern> - Build all 6 faces
- //overlay <pattern> - Overlay pattern on top surface
- //center <pattern> - Set center blocks
- //hollow [thickness] - Hollow out the region
- //line <pattern> [thickness] [-h] - Draw line (use -h for hollow)
- //curve <pattern> [thickness] [-h] - Draw curve (use -h for hollow)
- //smooth [iterations] - Smooth terrain elevation
- //naturalize - Create natural dirt/stone layers

Advanced Movement:
- //move [count] [direction] [replace] [-s] [-a] [-b] [-e] [-m <mask>]
  -s: Move without copying (cut)
  -a: Skip air blocks
  -b: Copy biomes
  -e: Copy entities
  -m: Source mask

- //stack [count] [direction] [-s] [-a] [-b] [-e] [-r] [-m <mask>]
  -s: Stack without original
  -a: Skip air blocks
  -b: Copy biomes
  -e: Copy entities
  -r: Move in reverse
  -m: Source mask

Pattern Examples:
- stone
- 50%stone,30%cobblestone,20%andesite
- ##wool (random wool colors)

Example Usage:
//set stone_bricks - Fill region with stone bricks
//walls oak_planks - Create wooden walls
//replace stone air - Remove all stone in selection
//replacenear 20 stone cobblestone - Replace stone with cobblestone within 20 blocks
//move 10 north -s - Cut and move 10 blocks north
//stack 5 up -a - Stack 5 times upward, skip air

Note: //replacenear is more intuitive for quick edits - no selection needed!
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Region command (e.g., 'set stone' or 'replacenear 10 dirt grass_block')",
                    }
                },
                "required": ["command"],
            },
        ),
        Tool(
            name="worldedit_generation",
            description="""WorldEdit Generation Commands - Generate shapes and structures.

⚠️ CRITICAL: NEVER teleport the player! Always use selection commands instead.

✅ World context is provided by the client player.

MANDATORY Workflow (NO teleportation):
1. Calculate target coordinates where you want to build
2. Calculate the selection region needed (see formulas below)
3. Set selection using worldedit_selection (pos1, pos2)
4. Run generation command

Selection Formulas:
- Sphere radius R at center (X,Y,Z):
  pos1: X-R, Y-R, Z-R
  pos2: X+R, Y+R, Z+R

- Cylinder radius R, height H at base (X,Y,Z):
  pos1: X-R, Y, Z-R
  pos2: X+R, Y+H-1, Z+R

- Pyramid size S at base (X,Y,Z):
  pos1: X-S, Y, Z-S
  pos2: X+S, Y+S, Z+S

Available Commands:
- sphere <pattern> <radius> [raised?] - Create filled sphere
- hsphere <pattern> <radius> [raised?] - Create hollow sphere
- pyramid <pattern> <size> - Create filled pyramid
- hpyramid <pattern> <size> - Create hollow pyramid
- cyl <pattern> <radius> [height] - Create cylinder
- hcyl <pattern> <radius> [height] - Create hollow cylinder

Example: Build 15-block pyramid at X=1242, Y=-60, Z=43
1. Calculate: pyramid size 15 needs region from -15 to +15 in X/Z
2. pos1 = (1242-15, -60, 43-15) = (1227, -60, 28)
3. pos2 = (1242+15, -60+15, 43+15) = (1257, -45, 58)
4. Commands:
   worldedit_selection(command="pos1 1227,-60,28")
   worldedit_selection(command="pos2 1257,-45,58")
   worldedit_generation(command="pyramid sandstone 15")

❌ WRONG: tp @p X Y Z → worldedit_generation(...)
✅ CORRECT: Calculate region → pos1 → pos2 → worldedit_generation(...)

Note: Patterns can be block names (stone, oak_wood) or complex patterns (50%stone,50%cobblestone).
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Generation command (e.g., 'sphere stone 10')",
                    }
                },
                "required": ["command"],
            },
        ),
        Tool(
            name="worldedit_clipboard",
            description="""WorldEdit Clipboard Commands - Copy, cut, and paste structures.

Workflow:
1. Select region with //pos1 and //pos2
2. Copy or cut to clipboard
3. Move to new location
4. Paste

Copy/Cut Commands:
- //copy [-b] [-e] [-m <mask>] - Copy selection to clipboard
  -b: Copy biomes
  -e: Copy entities
  -m: Source mask

- //cut [pattern] [-b] [-e] [-m <mask>] - Cut selection (fill with pattern)
  -b: Copy biomes
  -e: Copy entities
  -m: Source mask

Paste Commands:
- //paste [-a] [-b] [-e] [-n] [-o] [-s] [-v] [-m <sourceMask>]
  -a: Skip air blocks
  -b: Paste biomes
  -e: Paste entities
  -n: No biomes
  -o: Paste at original position
  -s: Select pasted region
  -v: Include structure void
  -m: Source mask

Transform Commands:
- //rotate <y> [x] [z] - Rotate clipboard
- //flip [direction] - Flip clipboard

Clear:
- /clearclipboard - Clear clipboard

Example Workflow:
1. //pos1 100,64,100
2. //pos2 110,70,110
3. //copy -e - Copy with entities
4. //pos1 200,64,200
5. //paste -a - Paste, skip air
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Clipboard command (e.g., 'copy' or 'paste -a')",
                    }
                },
                "required": ["command"],
            },
        ),
        Tool(
            name="worldedit_schematic",
            description="""WorldEdit Schematic Commands - Save and load structures from files.

Schematics let you save structures to files and load them later.

Commands:
- /schem list [-p page] - List available schematics
- /schem load <filename> - Load schematic to clipboard
- /schem save <filename> - Save clipboard to schematic file
- /schem delete <filename> - Delete a schematic file

Workflow:
1. Build or copy a structure to clipboard
2. //schem save my_house
3. Later: //schem load my_house
4. //paste

Note: Schematic operations may be read-only depending on server configuration.
File access requires proper permissions on the server.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Schematic command (e.g., 'list' or 'load my_house')",
                    }
                },
                "required": ["command"],
            },
        ),
        Tool(
            name="worldedit_history",
            description="""WorldEdit History Commands - Undo and redo changes.

Manage edit history to undo mistakes or redo undone changes.

Commands:
- //undo [times] - Undo last edit(s)
- //redo [times] - Redo undone edit(s)
- //clearhistory - Clear edit history

Examples:
- //undo - Undo last edit
- //undo 5 - Undo last 5 edits
- //redo - Redo last undone edit
- //clearhistory - Clear all history (free memory)

Note: History is per-session and limited by server configuration.
Large edits consume more history memory.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "History command (e.g., 'undo' or 'redo 3')",
                    }
                },
                "required": ["command"],
            },
        ),
        Tool(
            name="worldedit_utility",
            description="""WorldEdit Utility Commands - Various useful operations.

Fill & Drain:
- //fill <pattern> <radius> [depth] - Fill holes
- //fillr <pattern> <radius> [depth] - Recursive fill
- //drain <radius> - Drain water/lava pools

Block Removal:
- /removeabove [size] [height] - Remove blocks above
- /removebelow [size] [height] - Remove blocks below
- /removenear <mask> [radius] - Remove nearby blocks

Environment:
- /fixwater <radius> - Fix water flow
- /fixlava <radius> - Fix lava flow
- /snow [size] - Simulate snowfall
- /thaw [size] - Melt snow/ice
- /green [size] - Convert dirt to grass
- /extinguish [radius] - Remove fire

Entity Management:
- /butcher [radius] - Remove mobs
- /remove <type> <radius> - Remove entities

Math:
- //calc <expression> - Evaluate math expression

Examples:
//drain 10 - Drain water within 10 blocks
/removeabove 20 5 - Remove 20 blocks up to 5 blocks high
/extinguish 30 - Put out fires within 30 blocks
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Utility command (e.g., 'drain 10' or 'green 20')",
                    }
                },
                "required": ["command"],
            },
        ),
        Tool(
            name="worldedit_biome",
            description="""WorldEdit Biome Commands - View and modify biomes.

Biomes affect terrain generation, mob spawning, weather, and more.

Commands:
- /biomelist [-p page] - List all biomes
- /biomeinfo [-t] - Get biome at location
  -t: Use target block instead of feet
- //setbiome <biome> - Set biome in selection

Example Usage:
1. //pos1 100,64,100
2. //pos2 150,100,150
3. //setbiome minecraft:plains

Common Biomes:
- minecraft:plains
- minecraft:forest
- minecraft:desert
- minecraft:taiga
- minecraft:savanna
- minecraft:jungle
- minecraft:swamp

Note: Biome changes affect new chunks and may require relogging to see effects.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Biome command (e.g., 'biomelist' or 'setbiome minecraft:plains')",
                    }
                },
                "required": ["command"],
            },
        ),
        Tool(
            name="worldedit_brush",
            description="""WorldEdit Brush Commands - Create brushes for click-based editing.

⚠️ IMPORTANT: Brushes require player interaction (clicking). Most won't work from server console.
However, you CAN configure brushes from console using the configuration commands below.

BRUSH CONFIGURATION (works from console):
- /mask <mask> - Set brush mask (which blocks to affect)
- /material <pattern> - Set brush material/pattern
- /size <size> - Set brush size/radius
- /range <range> - Set brush range (reach distance)
- /tracemask [mask] - Set trace mask (what stops ray-trace)
- // or /, - Toggle super pickaxe

BASIC BRUSHES (require player interaction):
- /br sphere <pattern> [radius] [-h] - Sphere brush (-h for hollow)
- /br cylinder <pattern> [radius] [height] [-h] - Cylinder brush
- /br smooth [radius] [iterations] [mask] - Terrain smoother
- /br gravity [radius] [-h <height>] - Gravity simulator
- /br clipboard [-a] [-v] [-o] [-e] [-b] [-m <mask>] - Clipboard brush
- /br snowsmooth [radius] [iterations] - Snow terrain smoother
- /br extinguish [radius] - Fire extinguisher
- /br butcher [radius] [-p] [-n] [-g] [-a] [-b] - Kill mobs brush
- /br splatter <pattern> [radius] [decay] - Splatter brush

ADVANCED BRUSH SYSTEMS (require player interaction):

/brush apply <shape> [radius] <type> <params>
  Applies operations in specific shapes (sphere, cylinder, cuboid)
  Types:
  - forest <tree_type> - Plant trees in shape
  - item <item> [direction] - Use item in shape
  - set <pattern> - Place blocks in shape

  Examples:
  /br apply sphere 10 forest oak
  /br apply cylinder 15 set stone_bricks
  /br apply cuboid 20 item bone_meal up

/brush paint <shape> [radius] [density] <type> <params>
  Paints operations with density control (0-100% coverage)
  Types:
  - forest <tree_type> - Paint trees with density
  - item <item> [direction] - Paint with item at density
  - set <pattern> - Paint blocks at density

  Examples:
  /br paint sphere 15 30 forest oak  (30% tree coverage)
  /br paint cylinder 12 50 set grass_block  (50% grass coverage)

BRUSH WORKFLOW EXAMPLE:
1. /br sphere stone 5 - Create stone sphere brush
2. /mask dirt,grass_block - Only affect dirt/grass
3. /size 10 - Change size to 10
4. Player right-clicks to use brush

For AI/programmatic building, use region or generation commands instead of brushes.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Brush command (e.g., 'sphere stone 5')",
                    }
                },
                "required": ["command"],
            },
        ),
        Tool(
            name="worldedit_general",
            description="""WorldEdit Session & Global Commands - Manage limits, masks, and global options.

Includes history, side-effect, and mask controls:
- //undo, //redo, //clearhistory
- //limit, //timeout, //perf, //update, //reorder, //drawsel
- //gmask <mask>, //world <world>, //watchdog <mode>
- /worldedit help|version|reload

Include the proper leading / or // in the command string.

Examples:
//limit 500000
//gmask !air
/worldedit version
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "General WorldEdit command (include leading / or //)",
                    }
                },
                "required": ["command"],
            },
        ),
        Tool(
            name="worldedit_navigation",
            description="""WorldEdit Navigation Commands - Move the player or adjust position quickly.

Commands:
- /ascend [levels], /descend [levels]
- /ceil [-fg] [clearance], /thru, /up <distance>
- /unstuck, /jumpto

Most navigation commands require player context and direct player input.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Navigation command (e.g., '/ascend 1')",
                    }
                },
                "required": ["command"],
            },
        ),
        Tool(
            name="worldedit_chunk",
            description="""WorldEdit Chunk Commands - Inspect or delete chunks in the world.

Commands:
- /chunkinfo - Show information about the chunk you target
- /listchunks [-p <page>] - List chunks in the current selection
- /delchunks [-o <age>] - Delete chunks (dangerous, now allowed by default)

Use with extreme caution—deleting chunks cannot be undone.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Chunk command (e.g., '/delchunks -o 30d')",
                    }
                },
                "required": ["command"],
            },
        ),
        Tool(
            name="worldedit_snapshot",
            description="""WorldEdit Snapshot Commands - Manage snapshot selection and restoration.

Commands:
- /snap list [-p <page>]
- /snap use <name>, /snap sel <index>
- /snap before <date>, /snap after <date>
- /restore [snapshot]

Ensure snapshots are configured on the server before using these commands.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Snapshot command (e.g., '/snap list')",
                    }
                },
                "required": ["command"],
            },
        ),
        Tool(
            name="worldedit_scripting",
            description="""WorldEdit Scripting Commands - Execute CraftScripts on the server.

Commands:
- /cs <filename> [args...] - Run a CraftScript in the scripts directory
- /.s [args...] - Re-run the previous script with optional arguments

Scripts must exist on the server filesystem. Include any required arguments.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Scripting command (e.g., '/cs terraform.js 10')",
                    }
                },
                "required": ["command"],
            },
        ),
        Tool(
            name="worldedit_reference",
            description="""WorldEdit Reference Commands - Search blocks/items or read help.

Commands:
- /searchitem [-bi] [-p <page>] <query>
- //help [-s] [-p <page>] [command]
- /schem formats, /we report

Use this tool to surface documentation directly inside the client.
Include the leading slash in each command.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Reference command (e.g., '/searchitem oak')",
                    }
                },
                "required": ["command"],
            },
        ),
        Tool(
            name="worldedit_tools",
            description="""WorldEdit Tool Binding Commands - Configure tool and brush options.

Tool Modes:
- /tool selwand - Selection wand (left click = pos1, right click = pos2)
- /tool tree [type] - Tree placer (right click to place trees)
- /tool repl <pattern> - Replacer tool (left click = source, right click = replace with pattern)
- /tool cycler - Block data cycler (cycle through block states)
- /tool stacker [range] [mask] - Block stacker
- /tool info - Block information tool
- /tool farwand - Long-range position setting (extends selection range)
- /none - Unbind current tool

Tool Configuration:
- /mask <mask> - Set which blocks the tool affects
- /material <pattern> - Set material for tool
- /range <distance> - Set tool reach distance
- /size <radius> - Set tool size/radius
- /tracemask [mask] - Set trace mask (what stops ray-trace)

Super Pickaxe:
- // or /, - Toggle super pickaxe on/off
- /sp single - Single block mode
- /sp area <radius> - Area destruction mode
- /sp recursive <radius> - Recursive destruction mode

Other:
- /toggleeditwand - Toggle edit wand on/off
- //wand - Get selection wand item

Tool Usage Examples:
- /tool repl stone_bricks - Left-click source block, right-click to paste stone bricks
- /tool tree oak - Right-click to place oak trees
- /tool farwand - Extend selection range for distant positioning

Note: Most commands require the player to hold an item; configure from console, then
have the player interact in-game with left/right clicks.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Tool binding command (include leading / or //)",
                    }
                },
                "required": ["command"],
            },
        ),
        # TIER 3: Helper Utilities
        Tool(
            name="validate_mask",
            description="""Validate a WorldEdit mask before using it in commands.

Masks determine which blocks are affected by operations.

Mask types supported:
- Block: stone, !air
- Categories: ##wool
- Special: #existing, #solid, #surface
- Expressions: =y<64, =x^2+z^2<100
- Random: %50

Returns: Validation result and explanation of the mask.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "mask": {
                        "type": "string",
                        "description": "The mask to validate",
                    }
                },
                "required": ["mask"],
            },
        ),
        Tool(
            name="get_server_info",
            description="""Get information about the Minecraft server.

Returns:
- Connected players
- Current time
- Server difficulty
- WorldEdit version (if detected)

Useful for checking server status before executing commands.
""",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="search_minecraft_item",
            description="""Search for Minecraft blocks/items by name.

Find blocks and items from Minecraft 1.21.3 to use in your builds.
Returns item ID, name, display name, and stack size.

Search examples:
- "stone" - finds stone, stone_bricks, stone_stairs, etc.
- "concrete" - finds all concrete colors
- "oak" - finds oak_planks, oak_log, oak_stairs, etc.
- "red" - finds red_wool, red_concrete, red_terracotta, etc.

Use this before building to:
- Check exact block names for WorldEdit commands
- Find color variants (e.g., all wool colors)
- Discover building material options
- Verify block exists in Minecraft 1.21.3

Returns: Up to 20 matching items with details.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term (partial name match, case-insensitive)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results to return (default: 20, max: 50)",
                        "default": 20,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_player_position",
            description="""Get comprehensive position data for a player in the Minecraft world.

Returns:
- Player X, Y, Z coordinates (feet position)
- Player rotation (yaw, pitch - which direction they're facing)
- Target block (the block the player is looking at, if within 5 blocks)
- Surface level at player's position (for building context)

Useful for:
- Building at the player's current location
- Building where the player is looking (target block)
- Determining ground level for structures
- Understanding player orientation for directional builds

If no player_name is provided, gets the position of the first online player.

Returns: Comprehensive position context including coordinates, rotation, look target, and surface level.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "player_name": {
                        "type": "string",
                        "description": "Name of the player (optional - uses first online player if not specified)",
                    }
                },
                "required": [],
            },
        ),
        Tool(
            name="get_surface_level",
            description="""Find the surface (top solid block) Y-coordinate at given X, Z coordinates.

Useful for:
- Determining where to place building foundations
- Finding ground level before terraforming
- Calculating structure height above terrain
- Smart building placement on uneven terrain

Uses raycast from Y=320 (build limit) down to bedrock to find first solid block.

Returns: Surface Y-coordinate and block type at that location.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate",
                    },
                    "z": {
                        "type": "integer",
                        "description": "Z coordinate",
                    },
                },
                "required": ["x", "z"],
            },
        ),
        Tool(
            name="furniture_lookup",
            description="""Search and retrieve Minecraft furniture layouts for automated building.

This tool provides access to pre-designed furniture blueprints that can be automatically
placed in the world using WorldEdit commands.

Two operations:
1. **search** - Find furniture by name, category, or tags
2. **get** - Retrieve complete layout data for a specific furniture piece by ID

Each layout includes:
- Precise block placements with coordinates
- Material requirements and counts
- Bounding box dimensions
- Clearance requirements
- Design notes and variants

Use this to:
- Browse available furniture options
- Get exact specifications for furniture building
- Check material requirements before building
- Find furniture that matches a specific style or category

Examples:
- search: {"action": "search", "query": "table"} - Find all table designs
- search: {"action": "search", "category": "bedroom"} - Find bedroom furniture
- search: {"action": "search", "tags": ["compact", "modern"]} - Find compact modern furniture
- get: {"action": "get", "furniture_id": "simple_dining_table"} - Get full layout for dining table

After retrieving a layout, use the placement helper tool to build it in the world.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["search", "get"],
                        "description": "Operation to perform: 'search' for finding furniture, 'get' for retrieving specific layout",
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query (for action='search') - matches name, category, or tags",
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by category (for action='search'): bedroom, kitchen, living_room, etc.",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by tags (for action='search'): compact, modern, wood, stone, etc.",
                    },
                    "furniture_id": {
                        "type": "string",
                        "description": "Furniture ID to retrieve (for action='get')",
                    },
                },
                "required": ["action"],
            },
        ),
        Tool(
            name="place_furniture",
            description="""Place a furniture layout from the library at a world location.

This tool executes the exact WorldEdit and vanilla commands needed to instantiate a
layout. Use `preview_only=true` to review the commands before running them.

Inputs:
- `furniture_id` from furniture_lookup (must be a layout with automated coordinates)
- `origin_x`, `origin_y`, `origin_z` for the layout origin
- Optional `facing` override (north/east/south/west)
- `place_on_surface` (default: true) - If true, origin_y is treated as the FLOOR LEVEL
  and furniture is placed ON TOP (at origin_y + 1). If false, furniture is placed
  exactly at origin_y (may replace floor blocks).

IMPORTANT: When using get_surface_level, pass the returned Y directly as origin_y.
The furniture will automatically be placed on top of the surface. Example:
  surface_y = 64 (the floor block)
  place_furniture(origin_y=64, place_on_surface=true)  # Places furniture at Y=65 (on floor)

The tool reports a placement summary and highlights any command failures so you can
//undo if necessary.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "furniture_id": {
                        "type": "string",
                        "description": "Layout ID returned by furniture_lookup",
                    },
                    "origin_x": {"type": "integer", "description": "World origin X"},
                    "origin_y": {
                        "type": "integer",
                        "description": "World origin Y (floor level when place_on_surface=true, exact Y when false)",
                    },
                    "origin_z": {"type": "integer", "description": "World origin Z"},
                    "facing": {
                        "type": "string",
                        "enum": ["north", "south", "east", "west"],
                        "description": "Optional facing override",
                    },
                    "place_on_surface": {
                        "type": "boolean",
                        "description": "If true (default), treat origin_y as floor level and place furniture on top. If false, place at exact origin_y.",
                        "default": True,
                    },
                    "preview_only": {
                        "type": "boolean",
                        "description": "Return commands without executing",
                        "default": False,
                    },
                },
                "required": ["furniture_id", "origin_x", "origin_y", "origin_z"],
            },
        ),
        Tool(
            name="spatial_awareness_scan",
            description="""⚡ ADVANCED SPATIAL AWARENESS V2 - Fast multi-strategy spatial analysis (10-20x faster than V1!)

**🎯 WHEN TO USE**: Use this tool BEFORE placing ANY blocks to understand the spatial context.

**⚠️ MANDATORY FOR**:
- ✅ ALL furniture placement → Scan at furniture center BEFORE placing
- ✅ ALL roof construction → Scan each layer BEFORE placing stairs
- ✅ ALL interior walls → Scan to ensure ceiling height clearance
- ✅ ALL window placement → Scan to detect wall thickness and frame depth
- ✅ ANY block placement requiring alignment with existing structure

**WHY V2 IS BETTER**:
- 🚀 10-20x faster (2-10 seconds vs 30-60 seconds)
- 📊 MORE information (clearance, materials, structure type)
- 🎯 Better recommendations (style matching, placement guidance)
- ⚡ Uses WorldEdit bulk operations (not per-block queries)

**DETAIL LEVELS** (choose speed vs. information tradeoff):

**LOW** (~50 commands, 2-3 seconds):
- Floor/ceiling detection (Y coordinates)
- 3D voxel density map
- Basic material summary
- USE FOR: Quick checks before simple placements

**MEDIUM** (~100 commands, 4-5 seconds) - ⭐ RECOMMENDED:
- Everything in LOW +
- Clearance in 6 directions (north/south/east/west/up/down)
- Blocked direction detection
- USE FOR: Most furniture, wall, and structural placements

**HIGH** (~200 commands, 8-10 seconds):
- Everything in MEDIUM +
- Material palette detection (style matching)
- Structure pattern detection (roof/building/wall classification)
- Architectural style inference (medieval/modern/rustic)
- USE FOR: Complex builds, style-matching requirements, quality builds

**RETURNS**:
```json
{
  "floor_y": 64,              // Y coordinate of floor block
  "ceiling_y": 69,            // Y coordinate of ceiling block
  "clearance": {              // Space in each direction
    "north": {"clearance": 5, "blocked_at": null},
    "south": {"clearance": 3, "blocked_at": 4, "blocking_block": "stone_bricks"},
    "up": {"clearance": 5},
    "down": {"clearance": 0, "blocked_at": 1}
  },
  "material_summary": {
    "dominant_material": "oak_planks",
    "all_materials": ["oak_planks", "stone_bricks", "glass"],
    "material_diversity": 0.65
  },
  "structure_patterns": {      // HIGH detail only
    "structure_type": "building",
    "has_stairs": true,
    "has_windows": true,
    "complexity": "high",
    "is_hollow": true
  },
  "material_palette": {         // HIGH detail only
    "primary_materials": ["oak_planks", "stone_bricks", "glass"],
    "wood_type": "oak",
    "stone_type": "stone_bricks",
    "style": "medieval"
  },
  "recommendations": {
    "floor_placement_y": 65,    // Place floor furniture HERE
    "ceiling_placement_y": 69,  // Hang ceiling items HERE
    "ceiling_height": 4,        // Blocks between floor and ceiling
    "clear_for_placement": true,
    "suggested_materials": ["oak_planks", "stone_bricks"],
    "detected_style": "medieval",
    "warnings": ["Low ceiling - may feel cramped"]
  },
  "summary": "Human-readable text summary..."
}
```

**EXAMPLE WORKFLOWS**:

**Furniture Placement (MEDIUM detail)**:
```
1. spatial_awareness_scan(center_x=100, center_y=65, center_z=200, radius=5, detail_level="medium")
   → Returns: floor_placement_y=65, ceiling_placement_y=69, clearance in all directions
2. Verify clearance: north=5 blocks, east=3 blocks → Table will fit!
3. place_furniture(furniture_id="table", origin_x=100, origin_y=65, origin_z=200)
   → Perfect placement on floor with confirmed clearance!
```

**Roof Construction (LOW detail - fast repeated scans)**:
```
1. spatial_awareness_scan(center_x=100, center_y=72, center_z=105, radius=8, detail_level="low")
   → Returns: Detects existing structures at Y=71
2. Place stairs at Y=72 (offset from Y=71 layer)
3. Repeat scan at Y=73 for next layer
   → Fast enough to scan before each layer!
```

**Style-Matching Build (HIGH detail)**:
```
1. spatial_awareness_scan(center_x=100, center_y=65, center_z=200, radius=10, detail_level="high")
   → Returns: style="medieval", wood_type="oak", stone_type="stone_bricks"
2. Build new structure using oak_planks and stone_bricks to match
   → Cohesive architectural style!
```

**Performance Tips**:
- Use LOW for quick/repeated scans (roof layers, simple checks)
- Use MEDIUM for most placements (furniture, walls, interiors) - ⭐ RECOMMENDED
- Use HIGH when you need style matching or detailed structure analysis
- Smaller radius = faster (radius 3-5 is usually sufficient)

**Performance Comparison by Detail Level**:
- LOW: ~50 commands, 2-3 seconds - Basic floor/ceiling detection
- MEDIUM: ~100 commands, 4-5 seconds - + clearance detection (⭐ RECOMMENDED)
- HIGH: ~200 commands, 8-10 seconds - + style matching & pattern recognition

**⚠️ CRITICAL REMINDER**: ALWAYS scan before placing blocks that need alignment!
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "center_x": {
                        "type": "integer",
                        "description": "Center X coordinate to analyze around",
                    },
                    "center_y": {
                        "type": "integer",
                        "description": "Center Y coordinate to analyze around",
                    },
                    "center_z": {
                        "type": "integer",
                        "description": "Center Z coordinate to analyze around",
                    },
                    "radius": {
                        "type": "integer",
                        "description": "Scan radius in blocks (default 5, recommended 3-8 for balance)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 15,
                    },
                    "detail_level": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Analysis detail level: 'low' (fast, 2-3s), 'medium' (balanced, 4-5s, RECOMMENDED), 'high' (comprehensive, 8-10s)",
                        "default": "medium",
                    },
                },
                "required": ["center_x", "center_y", "center_z"],
            },
        ),
        Tool(
            name="calculate_shape",
            description="""Calculate perfect circles, spheres, domes, ellipses, and arches for Minecraft building.

Uses Bresenham's algorithms for pixel-perfect mathematical accuracy. Returns coordinate lists and ASCII previews.

**Shape Types**:
- **circle**: 2D circle (for towers, ponds, circular rooms)
- **sphere**: 3D sphere (hollow or filled)
- **dome**: Hemisphere or partial sphere (for roofs, domes)
- **ellipse**: 2D ellipse (oval shapes)
- **arch**: Arch structure (for doorways, bridges, windows)

**Common Uses**:
- Tower foundations (circle)
- Dome roofs (dome, hemisphere style)
- Spherical structures (sphere, hollow)
- Arched doorways and bridges (arch)
- Oval rooms and ponds (ellipse)

**Output**: Returns coordinates list, block count, ASCII preview, and usage tips.

**Examples**:
- Circle tower base: calculate_shape(shape="circle", radius=10, filled=True)
- Hollow sphere: calculate_shape(shape="sphere", radius=8, hollow=True)
- Cathedral dome: calculate_shape(shape="dome", radius=15, style="hemisphere")
- Bridge arch: calculate_shape(shape="arch", width=10, height=8, depth=2)
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "shape": {
                        "type": "string",
                        "description": "Shape type: 'circle', 'sphere', 'dome', 'ellipse', or 'arch'",
                        "enum": ["circle", "sphere", "dome", "ellipse", "arch"],
                    },
                    "radius": {
                        "type": "integer",
                        "description": "Radius in blocks (for circle, sphere, dome)",
                        "minimum": 1,
                        "maximum": 100,
                    },
                    "width": {
                        "type": "integer",
                        "description": "Width in blocks (for ellipse, arch)",
                        "minimum": 1,
                        "maximum": 100,
                    },
                    "height": {
                        "type": "integer",
                        "description": "Height in blocks (for ellipse, arch)",
                        "minimum": 1,
                        "maximum": 100,
                    },
                    "depth": {
                        "type": "integer",
                        "description": "Depth/thickness in blocks (for arch). Default: 1",
                        "minimum": 1,
                        "maximum": 20,
                        "default": 1,
                    },
                    "filled": {
                        "type": "boolean",
                        "description": "Fill interior (for circle, ellipse). Default: false",
                        "default": False,
                    },
                    "hollow": {
                        "type": "boolean",
                        "description": "Hollow shell only (for sphere). Default: true",
                        "default": True,
                    },
                    "style": {
                        "type": "string",
                        "description": "Dome style: 'hemisphere', 'three_quarter', 'low'. Default: hemisphere",
                        "enum": ["hemisphere", "three_quarter", "low"],
                        "default": "hemisphere",
                    },
                },
                "required": ["shape"],
            },
        ),
        Tool(
            name="generate_terrain",
            description="""Generate realistic terrain features using WorldEdit noise functions.

Creates natural-looking landscapes with pre-tested recipes for hills, mountains, valleys, plateaus, and ranges.

**Terrain Types**:
- **rolling_hills**: Gentle undulating hills (Perlin noise)
- **rugged_mountains**: Sharp peaks and ridges (Ridged Multifractal)
- **valley_network**: Interconnected valleys for rivers (Inverted Perlin)
- **mountain_range**: Linear mountain chain in a direction (Oriented Ridged)
- **plateau**: Flat-topped elevation with rough edges

**Process**:
1. Sets WorldEdit selection
2. Applies noise-based deformation
3. Smooths terrain for natural appearance
4. Returns summary with parameters used

**Safety**: Amplitude capped at 50 blocks, region size limited

**Use Cases**:
- Create backdrop for castle/fortress
- Generate farmland with gentle slopes
- Add river valley systems
- Build continental divide features
- Make dramatic mesa formations

**Examples**:
- Gentle hills: generate_terrain(type="rolling_hills", x1=0, y1=64, z1=0, x2=100, y2=80, z2=100, scale=18, amplitude=6)
- Mountains: generate_terrain(type="rugged_mountains", x1=0, y1=64, z1=0, x2=100, y2=100, z2=100, scale=28, amplitude=18)
- Valleys: generate_terrain(type="valley_network", x1=0, y1=64, z1=0, x2=100, y2=80, z2=100, scale=22, depth=10)
- Range: generate_terrain(type="mountain_range", x1=0, y1=64, z1=0, x2=200, y2=100, z2=100, direction="north-south", amplitude=20)
- Plateau: generate_terrain(type="plateau", x1=0, y1=64, z1=0, x2=80, y2=85, z2=80, height=15)
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": [
                            "rolling_hills",
                            "rugged_mountains",
                            "valley_network",
                            "mountain_range",
                            "plateau",
                        ],
                        "description": "Terrain type to generate",
                    },
                    "x1": {"type": "integer", "description": "Region corner 1 X"},
                    "y1": {"type": "integer", "description": "Region corner 1 Y (base elevation)"},
                    "z1": {"type": "integer", "description": "Region corner 1 Z"},
                    "x2": {"type": "integer", "description": "Region corner 2 X"},
                    "y2": {"type": "integer", "description": "Region corner 2 Y (max elevation)"},
                    "z2": {"type": "integer", "description": "Region corner 2 Z"},
                    "scale": {
                        "type": "integer",
                        "description": "Feature scale/breadth (10-40, varies by type)",
                        "minimum": 10,
                        "maximum": 40,
                    },
                    "amplitude": {
                        "type": "integer",
                        "description": "Height variation for hills/mountains (3-30)",
                        "minimum": 3,
                        "maximum": 50,
                    },
                    "depth": {
                        "type": "integer",
                        "description": "Valley depth (5-20, for valley_network only)",
                        "minimum": 5,
                        "maximum": 20,
                    },
                    "height": {
                        "type": "integer",
                        "description": "Plateau height (10-25, for plateau only)",
                        "minimum": 10,
                        "maximum": 25,
                    },
                    "direction": {
                        "type": "string",
                        "enum": [
                            "north-south",
                            "east-west",
                            "northeast-southwest",
                            "northwest-southeast",
                        ],
                        "description": "Range direction (for mountain_range only)",
                    },
                    "octaves": {
                        "type": "integer",
                        "description": "Noise detail level (3-6, more = finer details)",
                        "minimum": 3,
                        "maximum": 6,
                    },
                    "smooth_iterations": {
                        "type": "integer",
                        "description": "Post-smoothing passes (1-4, more = smoother)",
                        "minimum": 1,
                        "maximum": 10,
                    },
                    "seed": {
                        "type": "integer",
                        "description": "Random seed (optional, auto-generated if omitted)",
                    },
                },
                "required": ["type", "x1", "y1", "z1", "x2", "y2", "z2"],
            },
        ),
        Tool(
            name="texture_terrain",
            description="""Apply natural surface texturing to terrain based on biome/style.

Replaces base blocks and overlays surface patterns to create realistic-looking landscapes.

**Texturing Styles**:
- **temperate**: Grass, moss, dirt (plains/forest biomes)
- **alpine**: Stone, snow, gravel (high altitude)
- **desert**: Sand, sandstone, terracotta (arid regions)
- **volcanic**: Basalt, magma, blackstone (lava zones)
- **jungle**: Rich soil, podzol, moss (tropical)
- **swamp**: Mud, clay, damp grass (wetlands)

**Process**:
1. Sets WorldEdit selection
2. Replaces bulk material (stone → style-appropriate base)
3. Overlays surface pattern (grass/snow/sand on top)
4. Returns confirmation

**When to Use**:
- AFTER terrain shaping (hills, mountains, etc.)
- To convert raw stone terrain to natural-looking landscape
- To theme an area for specific biome
- For visual cohesion across large regions

**Examples**:
- Grass hills: texture_terrain(style="temperate", x1=0, y1=64, z1=0, x2=100, y2=80, z2=100)
- Snowy peaks: texture_terrain(style="alpine", x1=0, y1=64, z1=0, x2=100, y2=100, z2=100)
- Desert mesa: texture_terrain(style="desert", x1=0, y1=64, z1=0, x2=100, y2=85, z2=100)
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "style": {
                        "type": "string",
                        "enum": ["temperate", "alpine", "desert", "volcanic", "jungle", "swamp"],
                        "description": "Texturing style/biome theme",
                    },
                    "x1": {"type": "integer", "description": "Region corner 1 X"},
                    "y1": {"type": "integer", "description": "Region corner 1 Y"},
                    "z1": {"type": "integer", "description": "Region corner 1 Z"},
                    "x2": {"type": "integer", "description": "Region corner 2 X"},
                    "y2": {"type": "integer", "description": "Region corner 2 Y"},
                    "z2": {"type": "integer", "description": "Region corner 2 Z"},
                },
                "required": ["style", "x1", "y1", "z1", "x2", "y2", "z2"],
            },
        ),
        Tool(
            name="smooth_terrain",
            description="""Smooth terrain to remove blocky/steppy appearance.

Applies WorldEdit smoothing algorithm to blend block heights naturally.

**Use Cases**:
- Post-processing after terrain generation
- Fixing blocky noise artifacts
- Creating gentle transitions between elevations
- Reducing harsh cliffs to natural slopes

**Parameters**:
- iterations: More passes = smoother (2-4 recommended)
- Less smoothing preserves sharp features (mountains)
- More smoothing creates gentler slopes (hills)

**Best Practices**:
- Always smooth after //deform operations
- Use 1-2 iterations for mountains (preserve peaks)
- Use 3-4 iterations for rolling hills (gentle)
- Can apply mask to smooth only certain blocks

**Examples**:
- Light smoothing: smooth_terrain(x1=0, y1=64, z1=0, x2=100, y2=80, z2=100, iterations=2)
- Heavy smoothing: smooth_terrain(x1=0, y1=64, z1=0, x2=100, y2=80, z2=100, iterations=4)
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "x1": {"type": "integer", "description": "Region corner 1 X"},
                    "y1": {"type": "integer", "description": "Region corner 1 Y"},
                    "z1": {"type": "integer", "description": "Region corner 1 Z"},
                    "x2": {"type": "integer", "description": "Region corner 2 X"},
                    "y2": {"type": "integer", "description": "Region corner 2 Y"},
                    "z2": {"type": "integer", "description": "Region corner 2 Z"},
                    "iterations": {
                        "type": "integer",
                        "description": "Number of smoothing passes (1-10)",
                        "minimum": 1,
                        "maximum": 10,
                        "default": 2,
                    },
                    "mask": {
                        "type": "string",
                        "description": "Optional mask to limit smoothing (e.g., 'grass_block,dirt')",
                    },
                },
                "required": ["x1", "y1", "z1", "x2", "y2", "z2"],
            },
        ),
        Tool(
            name="building_pattern_lookup",
            description="""Search and retrieve building patterns for architectural elements in Minecraft.

This tool provides access to a comprehensive library of building patterns including roofs,
windows, doors, corner pillars, chimneys, and other architectural elements with layer-by-layer
construction instructions.

**IMPORTANT - Discovery First**: If you don't know what's available, use discovery actions:
1. **browse** - List all available patterns (names and IDs only)
2. **categories** - List all categories with pattern counts
3. **subcategories** - List subcategories for a specific category
4. **tags** - List all available tags with usage counts
5. **search** - Find patterns by name, category, subcategory, or tags
6. **get** - Retrieve complete pattern data with full layer-by-layer instructions

**Discovery Workflow (RECOMMENDED)**:
1. Start with action="browse" or action="categories" to see what's available
2. Use action="subcategories" with category="roofing" to see roof types
3. Then search specifically: action="search" with appropriate filters
4. Finally get the pattern: action="get" with pattern_id

**Pattern Contents**:
- Layer-by-layer block placement instructions (3D blueprints)
- Material requirements and counts
- Dimensions (width, height, depth)
- Construction notes and best practices
- Related patterns and variants
- Difficulty level

**Examples**:
- browse: {"action": "browse"} - List all 29 patterns (quick overview)
- categories: {"action": "categories"} - See available categories and counts
- subcategories: {"action": "subcategories", "category": "roofing"} - List roof types
- tags: {"action": "tags"} - See all available tags
- search: {"action": "search", "query": "gable"} - Find all gable roof patterns
- search: {"action": "search", "category": "roofing"} - All roofing patterns
- get: {"action": "get", "pattern_id": "gable_oak_medium"} - Get full instructions

After retrieving a pattern, use the layer information to build with WorldEdit commands.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["browse", "categories", "subcategories", "tags", "search", "get"],
                        "description": "Operation: 'browse' (list all), 'categories' (list categories), 'subcategories' (list subcats), 'tags' (list tags), 'search' (find patterns), 'get' (retrieve pattern)",
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query (for action='search') - matches name, category, subcategory, or tags",
                    },
                    "category": {
                        "type": "string",
                        "description": "Category name (for action='search' or action='subcategories'): roofing, facades, corners, details",
                    },
                    "subcategory": {
                        "type": "string",
                        "description": "Filter by subcategory (for action='search'): gable, hip, slab_roof, etc.",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by tags (for action='search'): oak, stone, easy, medium, hard, etc.",
                    },
                    "pattern_id": {
                        "type": "string",
                        "description": "Pattern ID to retrieve (for action='get')",
                    },
                },
                "required": ["action"],
            },
        ),
        Tool(
            name="place_building_pattern",
            description="""Instantiate a structured building pattern at the desired coordinates.

Patterns with detailed layer data can be placed automatically. Use `preview_only=true`
to inspect the generated commands before modifying the world.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern_id": {
                        "type": "string",
                        "description": "Pattern identifier from building_pattern_lookup",
                    },
                    "origin_x": {"type": "integer", "description": "Placement origin X"},
                    "origin_y": {"type": "integer", "description": "Placement origin Y"},
                    "origin_z": {"type": "integer", "description": "Placement origin Z"},
                    "facing": {
                        "type": "string",
                        "enum": ["north", "south", "east", "west"],
                        "description": "Optional facing override",
                    },
                    "preview_only": {
                        "type": "boolean",
                        "description": "Return commands instead of executing",
                        "default": False,
                    },
                },
                "required": ["pattern_id", "origin_x", "origin_y", "origin_z"],
            },
        ),
        Tool(
            name="terrain_pattern_lookup",
            description="""Search and retrieve terrain patterns for natural elements in Minecraft.

This tool provides access to a comprehensive library of terrain patterns including trees,
bushes, rocks, ponds, paths, and decorative natural elements with layer-by-layer
construction instructions.

**IMPORTANT - Discovery First**: If you don't know what's available, use discovery actions:
1. **browse** - List all available patterns (names and IDs only)
2. **categories** - List all categories with pattern counts
3. **subcategories** - List subcategories for a specific category
4. **tags** - List all available tags with usage counts
5. **search** - Find patterns by name, category, subcategory, or tags
6. **get** - Retrieve complete pattern data with full layer-by-layer instructions

**Discovery Workflow (RECOMMENDED)**:
1. Start with action="browse" or action="categories" to see what's available
2. Use action="subcategories" with category="vegetation" to see tree/bush types
3. Then search specifically: action="search" with appropriate filters
4. Finally get the pattern: action="get" with pattern_id

**Pattern Contents**:
- Layer-by-layer block placement instructions (3D blueprints)
- Material requirements and counts
- Dimensions (width, height, depth)
- Construction notes and placement tips
- Related patterns and variants
- Difficulty level

**Examples**:
- browse: {"action": "browse"} - List all 41 patterns (quick overview)
- categories: {"action": "categories"} - See available categories and counts
- subcategories: {"action": "subcategories", "category": "vegetation"} - List tree/bush types
- tags: {"action": "tags"} - See all available tags
- search: {"action": "search", "query": "oak tree"} - Find oak tree patterns
- search: {"action": "search", "category": "vegetation"} - All vegetation patterns
- get: {"action": "get", "pattern_id": "oak_tree_medium"} - Get full instructions

After retrieving a pattern, use the layer information to build with WorldEdit commands.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["browse", "categories", "subcategories", "tags", "search", "get"],
                        "description": "Operation: 'browse' (list all), 'categories' (list categories), 'subcategories' (list subcats), 'tags' (list tags), 'search' (find patterns), 'get' (retrieve pattern)",
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query (for action='search') - matches name, category, subcategory, or tags",
                    },
                    "category": {
                        "type": "string",
                        "description": "Category name (for action='search' or action='subcategories'): vegetation, features, paths, details",
                    },
                    "subcategory": {
                        "type": "string",
                        "description": "Filter by subcategory (for action='search'): trees, bushes, rocks, ponds, etc.",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by tags (for action='search'): oak, small, medium, large, natural, etc.",
                    },
                    "pattern_id": {
                        "type": "string",
                        "description": "Pattern ID to retrieve (for action='get')",
                    },
                },
                "required": ["action"],
            },
        ),
        Tool(
            name="building_template",
            description="""Search and use parametric building templates for rapid, high-quality construction.

Building templates are reusable,  parametric designs for common structures (towers, houses, barns, etc.) that can be customized with user preferences.

**Available Templates** (5 templates):
1. **medieval_round_tower** (intermediate) - Circular stone tower with spiral stairs, arrow slits, crenellations
2. **simple_cottage** (beginner) - Cozy rectangular cottage with gabled roof, chimney
3. **guard_tower** (beginner) - Square defensive tower with observation platform
4. **wizard_tower** (intermediate) - Mystical tower with purple accents, glowing lights, cone roof
5. **simple_barn** (beginner) - Rustic wooden barn with large doors and hayloft

**Actions**:
- **list** - List all available templates with brief descriptions
- **search** - Find templates by category, difficulty, or style tags
- **get** - Retrieve full template with parameters and build instructions
- **customize** - Show customization options for a template

**Template Benefits**:
- ⚡ 10x faster than building from scratch
- ✅ Consistent, professional quality
- 🎨 Fully customizable (height, size, materials, style)
- 📐 Pre-calculated dimensions and proportions
- 🏗️ Step-by-step build sequence

**Usage Workflow**:
1. Search or list templates: `building_template(action="list")` or `building_template(action="search", category="towers")`
2. Get template details: `building_template(action="get", template_id="medieval_round_tower")`
3. Customize parameters (height, radius, materials, etc.) based on user preferences
4. Follow build_sequence to construct using WorldEdit commands
5. Each component provides specific commands with parameter substitution

**Example**:
building_template(action="get", template_id="simple_cottage")
→ Returns cottage template with parameters: width (7-15, default 9), depth (7-15, default 11), materials, etc.
→ User: "Make it 11×13 with stone walls"
→ Agent customizes: width=11, depth=13, wall_material="cobblestone"
→ Agent follows build_sequence: foundation → walls → floor → door → windows → roof → chimney
→ Result: Custom cottage in ~60 seconds

**Customization**:
Templates support parameters like:
- Dimensions: height, width, depth, radius (integer ranges with min/max)
- Materials: wall_material, roof_material, floor_material (enum with options)
- Features: has_windows, has_chimney, roof_style (boolean or enum)
- Complexity: num_floors, size (affects build scope)

**Categories**: towers, houses, agricultural, defensive, decorative, industrial, fantasy, religious
**Difficulty Levels**: beginner, intermediate, advanced
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "search", "get", "customize"],
                        "description": "Action to perform",
                    },
                    "template_id": {
                        "type": "string",
                        "description": "Template identifier (required for get and customize actions)",
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by category (for search action)",
                    },
                    "difficulty": {
                        "type": "string",
                        "enum": ["beginner", "intermediate", "advanced"],
                        "description": "Filter by difficulty (for search action)",
                    },
                    "style_tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by style tags (for search action)",
                    },
                },
                "required": ["action"],
            },
        ),
        Tool(
            name="worldedit_deform",
            description="""Apply mathematical deformations to terrain in WorldEdit.

**⚠️ POWERFUL COMMAND - Use with caution!**

The //deform command uses mathematical expressions to deform terrain in the current selection.
Variables available: x, y, z (current coordinates), and you reassign them to move blocks.

**Common Deformations**:

**Sine wave terrain**:
```
//deform y-=0.2*sin(x*5)
```
Creates wavy terrain with amplitude 0.2 and frequency 5.

**Radial stretch**:
```
//deform x*=1.5;z*=1.5
```
Stretches selection outward from center.

**Twist effect**:
```
//deform x-=0.3*sin(y*5);z-=0.3*cos(y*5)
```
Twists terrain vertically.

**Sphere/dome**:
```
//deform y+=sqrt(64-(x^2+z^2))
```
Creates domed/spherical deformation.

**Safety Notes**:
- Always test on small selections first
- Use //undo if result is unexpected
- Expressions execute per-block (expensive on large areas)
- Check coordinates carefully (x, y, z syntax)

**Examples**:
- deform: {"expression": "y-=0.2*sin(x*5)"} - Wavy terrain
- deform: {"expression": "x*=1.2;z*=1.2"} - Radial expansion
- deform: {"expression": "y+=0.5*cos(x)*sin(z)"} - Organic bumps
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression for deformation (e.g., 'y-=0.2*sin(x*5)')",
                    },
                },
                "required": ["expression"],
            },
        ),
        Tool(
            name="worldedit_vegetation",
            description="""Generate vegetation (flora, forests, trees) in WorldEdit.

Add natural vegetation to terrain quickly with density control.

**Commands**:

**//flora [density]** - Generate flora in selection
- Density: 0-100 (default 10)
- Places grass, flowers, mushrooms, dead bushes based on biome
- Respects existing terrain (only places on valid blocks)
- Example: flora(density=20) for moderate vegetation

**//forest [type] [density]** - Generate forest in selection
- Types: oak, birch, spruce, jungle, acacia, dark_oak, random
- Density: 0-100 (default 5)
- Automatically spaces trees naturally
- Respects terrain height
- Example: forest(type="oak", density=10) for oak forest

**/tool tree [type]** - Tree placer tool
- Bind to held item: right-click to place trees
- Types: oak, birch, spruce, jungle, acacia, dark_oak, random
- Size: small, medium, large (varies by tree type)
- Example: tool_tree(type="oak", size="medium")

**Best Practices**:
- Start with low density (5-10) and increase if needed
- Use //flora for undergrowth, //forest for trees
- Combine both for realistic forests
- Use selection to limit vegetation to specific areas

**Examples**:
- flora: {"density": 15} - Moderate flora coverage
- forest: {"type": "oak", "density": 7} - Oak forest
- forest: {"type": "random", "density": 10} - Mixed forest
- tool_tree: {"type": "spruce", "size": "large"} - Large spruce placer
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "enum": ["flora", "forest", "tool_tree"],
                        "description": "Vegetation command to execute",
                    },
                    "type": {
                        "type": "string",
                        "description": "Tree type (for forest/tool_tree): oak, birch, spruce, jungle, acacia, dark_oak, random",
                    },
                    "density": {
                        "type": "integer",
                        "description": "Density 0-100 (flora default 10, forest default 5)",
                        "minimum": 0,
                        "maximum": 100,
                    },
                    "size": {
                        "type": "string",
                        "enum": ["small", "medium", "large"],
                        "description": "Tree size (for tool_tree, default medium)",
                    },
                },
                "required": ["command"],
            },
        ),
        Tool(
            name="worldedit_terrain_advanced",
            description="""Advanced terrain generation (caves, ore, regeneration) in WorldEdit.

Generate natural terrain features or restore original terrain.

**Commands**:

**//caves [size] [freq] [rarity] [minY] [maxY]** - Generate cave systems
- Size: 1-100 (default 8) - Cave tunnel size
- Frequency: 1-100 (default 40) - How many cave branches
- Rarity: 1-100 (default 7) - How common caves are (higher = rarer)
- minY/maxY: Y-level range (default: minY=1, maxY=128)
- Creates natural cave networks with varying sizes
- Example: caves(size=10, freq=50, rarity=5) for extensive caves

**//ore <pattern> <size> <freq> <rarity> <minY> <maxY>** - Generate ore veins
- Pattern: Block type (e.g., "iron_ore", "diamond_ore")
- Size: Vein size 1-50 (default 8)
- Frequency: Attempts per chunk 1-100 (default 10)
- Rarity: 1-100 (default 100, lower = rarer)
- minY/maxY: Y-level range
- Example: ore(pattern="iron_ore", size=8, freq=20, rarity=50, minY=0, maxY=64)

**//regen** - Regenerate selection to original terrain
- Restores terrain to world seed generation
- Removes all player-made modifications
- Uses chunk-based regeneration
- ⚠️ DESTRUCTIVE - Cannot undo, backs up automatically
- Example: regen() to restore natural terrain

**Safety Notes**:
- Cave generation is expensive (limit selection size)
- Ore generation follows vanilla patterns
- //regen is irreversible (creates backup first)
- Test on small areas before large operations

**Examples**:
- caves: {"size": 8, "freq": 40, "rarity": 7} - Natural caves
- ore: {"pattern": "diamond_ore", "size": 5, "freq": 2, "rarity": 100, "minY": 0, "maxY": 16} - Diamond veins
- regen: {} - Regenerate to original terrain
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "enum": ["caves", "ore", "regen"],
                        "description": "Terrain generation command",
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Block pattern (for ore command, e.g., 'iron_ore')",
                    },
                    "size": {
                        "type": "integer",
                        "description": "Size parameter (caves: tunnel size, ore: vein size)",
                    },
                    "freq": {
                        "type": "integer",
                        "description": "Frequency parameter (how many/often)",
                        "minimum": 1,
                        "maximum": 100,
                    },
                    "rarity": {
                        "type": "integer",
                        "description": "Rarity parameter (higher = rarer)",
                        "minimum": 1,
                        "maximum": 100,
                    },
                    "minY": {
                        "type": "integer",
                        "description": "Minimum Y level",
                    },
                    "maxY": {
                        "type": "integer",
                        "description": "Maximum Y level",
                    },
                },
                "required": ["command"],
            },
        ),
        Tool(
            name="worldedit_analysis",
            description="""Analyze selections and perform calculations in WorldEdit.

Get information about selections or evaluate mathematical expressions.

**Commands**:

**//distr** - Block distribution in selection
- Shows count of each block type in current selection
- Displays percentages for each block
- Useful for analyzing terrain composition
- Helps plan material requirements
- Example: distr() to see what blocks are in selection

**//calc <expression>** - Mathematical calculator
- Evaluates math expressions
- Supports: +, -, *, /, ^, sqrt, sin, cos, tan, abs, floor, ceil
- Variables: pi, e
- Useful for coordinate calculations, scaling, planning
- Examples:
  - calc("100 * 1.5") = 150 (scale coordinates)
  - calc("sqrt(100^2 + 100^2)") = 141.42 (diagonal distance)
  - calc("64 / 8") = 8 (chunk calculations)
  - calc("pi * 10^2") = 314.16 (circle area)

**Use Cases**:
- Analyze block composition before modifications
- Calculate distances and dimensions
- Plan material requirements
- Verify selection contents
- Math for complex builds

**Examples**:
- distr: {} - Show block distribution in selection
- calc: {"expression": "150 * 2.5"} - Calculate scaled dimension
- calc: {"expression": "sqrt(50^2 + 50^2)"} - Diagonal distance
- calc: {"expression": "pi * 20"} - Circumference of radius 20
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "enum": ["distr", "calc"],
                        "description": "Analysis command to execute",
                    },
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression (for calc command)",
                    },
                },
                "required": ["command"],
            },
        ),
        # ===== BUILD TOOL =====
        Tool(
            name="build",
            description="""Execute Minecraft and WorldEdit commands for building structures.

This is the universal building tool - supports vanilla Minecraft commands AND all 130+ WorldEdit commands.

**Two modes available:**
1. **Direct commands** - Provide command strings (vanilla or WorldEdit)
2. **Code generation** - Write Python code that generates commands (RECOMMENDED for complex builds!)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODE 1: DIRECT COMMANDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Vanilla Minecraft Commands:**
- `/fill X1 Y1 Z1 X2 Y2 Z2 block [mode]` - Fill region
- `/setblock X Y Z block[states]` - Place single block
- `/summon entity X Y Z` - Spawn entity

**WorldEdit Commands (all 130+ commands supported!):**

**Selection & Region:**
- `//pos1 X,Y,Z` - Set first position
- `//pos2 X,Y,Z` - Set second position
- `//set <pattern>` - Fill selection
- `//replace <from> <to>` - Replace blocks
- `//walls <pattern>` - Build walls
- `//faces <pattern>` - Build all 6 faces
- `//move <count> [dir]` - Move selection
- `//stack <count> [dir]` - Stack/duplicate selection

**Shapes:**
- `//sphere <pattern> <radius>` - Create sphere
- `//hsphere <pattern> <radius>` - Hollow sphere
- `//cylinder <pattern> <radius> [height]` - Cylinder
- `//pyramid <pattern> <size>` - Pyramid

**Clipboard:**
- `//copy` - Copy selection
- `//cut` - Cut selection
- `//paste` - Paste
- `//rotate <angle>` - Rotate clipboard
- `//flip [direction]` - Flip clipboard

**Utility:**
- `//undo` - Undo last action
- `//redo` - Redo
- `//drain <radius>` - Remove water/lava
- `//smooth [iterations]` - Smooth terrain
- `//naturalize` - Add dirt/stone layers

**Advanced:**
- `//deform <expression>` - Math deformations
- `//generate <expression>` - Generate with formula
- `//forest <type> <density>` - Generate trees
- `//setbiome <biome>` - Change biome

Example:
```
build(commands=[
    "//pos1 100,64,200",
    "//pos2 110,70,210",
    "//set stone_bricks",
    "//walls oak_planks"
])
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODE 2: CODE GENERATION (RECOMMENDED for complex builds!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Write Python code that generates commands using loops, math, and logic.

Example - Procedural Sphere:
```
build(code=\"\"\"
commands = []
radius = 10
for x in range(-radius, radius+1):
    for y in range(-radius, radius+1):
        for z in range(-radius, radius+1):
            if x*x + y*y + z*z <= radius*radius:
                commands.append(f"/setblock {100+x} {70+y} {200+z} stone")
\"\"\")
```

Example - Mixing Vanilla + WorldEdit:
```
build(code=\"\"\"
commands = []
# Use WorldEdit for bulk
commands.append("//pos1 100,64,200")
commands.append("//pos2 120,64,220")
commands.append("//set grass_block")

# Use vanilla for precision details
for i in range(5):
    x = 110 + i*2
    commands.append(f"/setblock {x} 65 210 oak_fence")
\"\"\")
```

Example - Curved Structures with Math (NO import needed!):
```
build(code=\"\"\"
commands = []
# Create curved portico using trig functions
center_x, center_z = 100, 200
radius = 8

for angle in range(0, 181, 10):
    rad = radians(angle)  # radians() available without import!
    x = int(center_x + radius * cos(rad))
    z = int(center_z + radius * sin(rad))
    commands.append(f"/setblock {x} 64 {z} quartz_block")
\"\"\")
```

Example - Helper Functions with Efficient Commands:
```
build(code=\"\"\"
commands = []

# Define efficient helper functions using /fill
def column(x, z, base_y, height, material):
    # ✅ Use /fill for vertical column (1 command, not 'height' commands!)
    commands.append(f"/fill {x} {base_y} {z} {x} {base_y+height-1} {z} {material}")

def wall(x1, x2, y, z, material):
    # ✅ Use /fill for horizontal wall (1 command)
    commands.append(f"/fill {x1} {y} {z} {x2} {y} {z} {material}")

def floor(x1, z1, x2, z2, y, material):
    # ✅ Use /fill for floor area (1 command)
    commands.append(f"/fill {x1} {y} {z1} {x2} {y} {z2} {material}")

# Use helpers to build structure
base_x, base_y, base_z = 100, 64, 200

# Four corner columns (4 commands total, not 20!)
column(base_x, base_z, base_y, 5, "stone_bricks")
column(base_x + 10, base_z, base_y, 5, "stone_bricks")
column(base_x, base_z + 10, base_y, 5, "stone_bricks")
column(base_x + 10, base_z + 10, base_y, 5, "stone_bricks")

# Connecting walls (2 commands, not 20!)
wall(base_x, base_x + 10, base_y + 5, base_z, "oak_planks")
wall(base_x, base_x + 10, base_y + 5, base_z + 10, "oak_planks")

print(f"Generated {len(commands)} commands (efficient!)")  # Only 6 commands!
\"\"\")
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ CRITICAL: COMMAND EFFICIENCY - Use Bulk Operations!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**ALWAYS prefer bulk commands over individual block placement!**

**❌ INEFFICIENT (DON'T DO THIS):**
```python
# Placing 20 blocks individually - SLOW!
for y in range(64, 84):
    commands.append(f"/setblock 100 {y} 200 stone_bricks")
# Result: 20 commands for a simple column
```

**✅ EFFICIENT (DO THIS INSTEAD):**
```python
# One bulk command - FAST!
commands.append(f"/fill 100 64 200 100 83 200 stone_bricks")
# Result: 1 command for entire column (20x fewer commands!)
```

**Decision Tree for Command Selection:**

1. **Rectangular/cuboid region (ANY size)?**
   → Use `/fill X1 Y1 Z1 X2 Y2 Z2 block`
   - Works for: floors, walls, columns, beams, boxes
   - Even 1-block wide lines (vertical columns, horizontal beams)
   - Example: `/fill 100 64 200 100 80 200 stone` (vertical column)

2. **Large irregular shape (100+ blocks)?**
   → Use WorldEdit `//pos1`, `//pos2`, `//set pattern`
   - Best for: terrain, large structures, complex patterns

3. **Curved/organic shape?**
   → Generate coordinates mathematically, then:
   - If pattern repeats: Use `/fill` for repeated segments
   - If truly unique: Use `/setblock` per block

4. **Individual decorative block with specific state?**
   → Use `/setblock X Y Z block[states]`
   - Only for: buttons, levers, signs, item frames, unique blocks

**Examples of Efficient Code:**

**Building a pillar grid (4 pillars):**
```python
# ❌ WRONG - 80 commands
for x in [100, 110]:
    for z in [200, 210]:
        for y in range(64, 84):
            commands.append(f"/setblock {x} {y} {z} stone_bricks")

# ✅ CORRECT - 4 commands
for x in [100, 110]:
    for z in [200, 210]:
        commands.append(f"/fill {x} 64 {z} {x} 83 {z} stone_bricks")
```

**Building walls:**
```python
# ❌ WRONG - 400 commands
for x in range(100, 120):
    for y in range(64, 84):
        commands.append(f"/setblock {x} {y} 200 stone_bricks")

# ✅ CORRECT - 1 command
commands.append(f"/fill 100 64 200 119 83 200 stone_bricks")
```

**Building floor:**
```python
# ❌ WRONG - 400 commands
for x in range(100, 120):
    for z in range(200, 220):
        commands.append(f"/setblock {x} 64 {z} oak_planks")

# ✅ CORRECT - 1 command
commands.append(f"/fill 100 64 200 119 64 219 oak_planks")
```

**Hollow box:**
```python
# ✅ EFFICIENT - 6 commands (one per face)
x1, y1, z1 = 100, 64, 200
x2, y2, z2 = 119, 83, 219

commands.append(f"/fill {x1} {y1} {z1} {x2} {y1} {z2} stone")  # Floor
commands.append(f"/fill {x1} {y2} {z1} {x2} {y2} {z2} stone")  # Ceiling
commands.append(f"/fill {x1} {y1} {z1} {x2} {y2} {z1} stone")  # North wall
commands.append(f"/fill {x1} {y1} {z2} {x2} {y2} {z2} stone")  # South wall
commands.append(f"/fill {x1} {y1} {z1} {x1} {y2} {z2} stone")  # West wall
commands.append(f"/fill {x2} {y1} {z1} {x2} {y2} {z2} stone")  # East wall
```

**Rule of Thumb:**
- 1 rectangular region = 1 `/fill` command (not a loop of `/setblock`)
- Think "regions" not "individual blocks"
- If you're writing a loop that places blocks in a line/plane/box, use `/fill` instead
- Reserve `/setblock` for truly unique individual blocks

**Code Safety:**
- Runs in secure sandbox (Python built-in ast + exec)
- Allowed operations: loops, conditionals, functions (def), math, strings, lists
- Math functions available (NO import needed!):
  - Trigonometry: sin, cos, tan, asin, acos, atan, atan2
  - Conversions: radians, degrees
  - Constants: pi, e
  - Other: sqrt, floor, ceil, pow, abs, min, max
- Debugging: print() available for progress messages and debug output
- Blocked: imports, file access, network access, external execution
- Limits: Max 10,000 commands, 100,000 iterations

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHEN TO USE BUILD VS SPECIALIZED TOOLS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Use build() for:**
- ✅ Any sequence of commands (vanilla or WorldEdit)
- ✅ Complex procedural builds (code generation)
- ✅ Mixed vanilla + WorldEdit operations
- ✅ Quick one-off commands

**Use specialized tools for:**
- 📚 Pre-designed patterns (furniture_lookup, building_pattern_lookup)
- 🔍 Spatial analysis (spatial_awareness_scan, analyze_lighting)
- 🎯 Specific workflows (worldedit_* tools with detailed docs/examples)
- ✅ Parameter validation and error checking

**Performance:** Extremely fast - thousands of blocks in seconds via bulk commands.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "commands": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of Minecraft commands (Mode 1: Direct)",
                    },
                    "code": {
                        "type": "string",
                        "description": "Python code that generates commands (Mode 2: RECOMMENDED)",
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of what's being built",
                        "default": "Building structure",
                    },
                    "preview_only": {
                        "type": "boolean",
                        "description": "If True, return commands without executing",
                        "default": False,
                    },
                },
                "required": [],  # Either commands OR code required
            },
        ),
        # ===== CLIENT VISION/CONTEXT TOOLS =====
        Tool(
            name="capture_screenshot",
            description="""Capture a screenshot from the Minecraft client.

Returns the current game view as a base64-encoded PNG image with player context.

**Returns**:
- width, height: Actual image dimensions
- original_width, original_height: Screen resolution
- player_position: {x, y, z} of player when captured
- player_rotation: {yaw, pitch} of player when captured
- image: Base64-encoded PNG data (data:image/png;base64,...)

**Use Cases**:
- Visual verification of builds
- Understanding current scene context
- Orientation and direction checking
- Before/after comparisons

**Parameters**:
- max_width: Maximum image width (default 1920, scales down if larger)
- max_height: Maximum image height (default 1080, scales down if larger)
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_width": {
                        "type": "integer",
                        "description": "Maximum width in pixels (default 1920)",
                        "default": 1920,
                    },
                    "max_height": {
                        "type": "integer",
                        "description": "Maximum height in pixels (default 1080)",
                        "default": 1080,
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="get_heightmap",
            description="""Get a heightmap for a rectangular area.

Returns the Y-level of the highest non-air block for each X,Z coordinate.

**Returns**:
- origin: [minX, minZ]
- dimensions: [sizeX, sizeZ]
- heights: 2D array of Y values [row][column]
- surface_blocks: 2D array of block IDs at surface
- stats: {min_height, max_height, height_range}

**Use Cases**:
- Terrain analysis before building
- Finding flat areas for construction
- Understanding elevation changes
- Smart foundation placement

**Limits**:
- Max area: 256x256 (65,536 columns)
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "x1": {"type": "integer", "description": "First corner X"},
                    "z1": {"type": "integer", "description": "First corner Z"},
                    "x2": {"type": "integer", "description": "Second corner X"},
                    "z2": {"type": "integer", "description": "Second corner Z"},
                },
                "required": ["x1", "z1", "x2", "z2"],
            },
        ),
        Tool(
            name="get_player_context",
            description="""Get detailed player context including position, rotation, and raycast target.

Returns comprehensive information about the local player's current state.

**Returns**:
- position: {x, y, z, block_x, block_y, block_z}
- rotation: {yaw, pitch, head_yaw, facing}
- eye_position: {x, y, z} - exact eye location for raycast
- look_direction: {x, y, z} - normalized look vector
- target: Raycast result - what player is looking at
  - type: "block" or "miss"
  - block: Block ID (if type=block)
  - position: {x, y, z} of hit block
  - face: Which face was hit (north/south/east/west/up/down)
  - adjacent: {x, y, z} where a block would be placed
  - distance: Distance to target
- held_item: Currently held item
- game_mode: creative, survival, etc.
- is_flying: Boolean
- on_ground: Boolean
- dimension: Dimension ID

**Use Cases**:
- Build where player is looking
- Understand player orientation
- Get precise positioning for relative builds
- Check what player is interacting with
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "reach": {
                        "type": "number",
                        "description": "Raycast distance in blocks (default 128)",
                        "default": 128.0,
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="get_nearby_entities",
            description="""Get entities near the player.

Returns a list of entities within the specified radius.

**Returns**:
- entities: Array of entity data
  - type: Entity type ID
  - id: Entity numeric ID
  - distance: Distance from player
  - position: {x, y, z}
  - name: Custom name if present
- count: Total entities found
- radius: Search radius used
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "radius": {
                        "type": "number",
                        "description": "Search radius in blocks (default 32)",
                        "default": 32.0,
                    },
                },
                "required": [],
            },
        ),
        # ============================================================
        # SCHEMATIC BUILDING TOOL - Declarative JSON-based building
        # ============================================================
        Tool(
            name="build_schematic",
            description="""Build structures using declarative JSON schematics.

**THIS IS THE PREFERRED METHOD FOR ALL BUILDING!**

## COMPACT FORMAT (Recommended - 70% fewer tokens)

```json
{
  "a": [x, y, z],
  "p": {"S": "stone", "P": "oak_planks", "W": "oak_planks"},
  "l": [
    [0, "S*10|S P*8 S~8|S*10"],
    [1, "W*10|W .*8 W~3|W*10"]
  ]
}
```

**Compact Syntax:**
- Short keys: `"a"` (anchor), `"p"` (palette), `"l"` (layers), `"f"` (facing), `"s"` (shape)
- Layers: `[y_offset, "row|row|row"]` - pipe separates rows
- Run-length: `S*5` = 5 stone blocks
- Row repeat: `S P*3 S~8` = repeat this row 8 times

**Shape Primitives (even more compact):**
- 2D in layers: `fill:WxD:S`, `outline:WxD:S`, `frame:WxD:S:I`
- 3D shapes: `"s": "box:WxHxD:S"` or `"s": "room:WxHxD:W:F"`

**Examples:**
```json
{"a": [0,64,0], "p": {"S": "stone"}, "l": [[0, "outline:10x10:S"]]}
{"a": [0,64,0], "p": {"S": "stone_bricks"}, "s": "box:12x5x12:S"}
```

## Verbose Format (Backward Compatible)

```json
{
  "anchor": [x, y, z],
  "facing": "north",
  "mode": "replace",
  "palette": {"S": "stone_bricks", "Dl": "oak_door[facing=south,half=lower]"},
  "layers": [{"y": 0, "grid": [["S","S","S"],["S",".","S"]]}]
}
```

## Grid Convention
- `grid[row][col]` = `grid[z][x]`
- Row 0 = north edge, Col 0 = west edge
- Rows go North→South, Columns go West→East

## Palette
- Run-length in compact: `S*5` = 5 S blocks
- Block states: `"Sn": "oak_stairs[facing=north,half=bottom]"`
- NBT: `"C": "chest[facing=north]{Items:[...]}"`
- Air: `.`, `_`, or space (skipped)

## Benefits
- COMPACT format uses ~70% fewer tokens
- Validates before execution
- Automatically optimizes commands (combines into /fill)
- Handles rotation automatically
- Full Minecraft block state support
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "schematic": {
                        "type": "object",
                        "description": "Schematic object. Supports COMPACT format (recommended) or verbose format.",
                        "properties": {
                            # Compact format keys (recommended - uses ~70% fewer tokens)
                            "a": {
                                "oneOf": [
                                    {
                                        "type": "array",
                                        "items": {"type": "number"},
                                        "minItems": 3,
                                        "maxItems": 3,
                                    },
                                    {"type": "string", "enum": ["player"]},
                                ],
                                "description": "Anchor position [x, y, z] (compact key for 'anchor')",
                            },
                            "p": {
                                "type": "object",
                                "additionalProperties": {"type": "string"},
                                "description": "Palette map (compact key for 'palette')",
                            },
                            "l": {
                                "type": "array",
                                "description": "Layers in compact format: [[y, 'row|row'], ...] (compact key for 'layers')",
                            },
                            "s": {
                                "type": "string",
                                "description": "3D shape primitive: 'box:WxHxD:S' or 'room:WxHxD:W:F'",
                            },
                            # Verbose format keys (backward compatible)
                            "anchor": {
                                "oneOf": [
                                    {
                                        "type": "array",
                                        "items": {"type": "integer"},
                                        "minItems": 3,
                                        "maxItems": 3,
                                    },
                                    {"type": "string", "enum": ["player"]},
                                ],
                                "description": "World position [x, y, z] or 'player' for relative positioning",
                            },
                            "facing": {
                                "type": "string",
                                "enum": ["north", "south", "east", "west"],
                                "description": "Build orientation (rotates entire structure)",
                            },
                            "mode": {
                                "type": "string",
                                "enum": ["replace", "keep", "destroy"],
                                "description": "Block placement mode",
                            },
                            "palette": {
                                "type": "object",
                                "additionalProperties": {"type": "string"},
                                "description": "Map of symbols to block IDs with optional states/NBT",
                            },
                            "layers": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "y": {
                                            "type": "integer",
                                            "description": "Y offset from anchor",
                                        },
                                        "grid": {
                                            "type": "array",
                                            "items": {"type": "array", "items": {"type": "string"}},
                                            "description": "2D grid of palette symbols",
                                        },
                                    },
                                },
                                "description": "Array of layer definitions (verbose format)",
                            },
                            "shape": {
                                "type": "string",
                                "description": "3D shape primitive (verbose key for 's')",
                            },
                        },
                        # Note: No 'required' - accepts either compact (a,p,l) or verbose (anchor,palette,layers) format
                    },
                    "preview_only": {
                        "type": "boolean",
                        "description": "If true, show what would be built without executing",
                        "default": False,
                    },
                    "optimize": {
                        "type": "boolean",
                        "description": "If true, combine adjacent blocks into /fill commands",
                        "default": True,
                    },
                    "description": {
                        "type": "string",
                        "description": "Human-readable description of what's being built",
                    },
                },
                "required": ["schematic"],
            },
        ),
        # Client Bridge Tools - Efficient client-side data access
        Tool(
            name="scan_region",
            description="""Scan blocks in a rectangular region using the client's chunk cache.

This is an efficient way to read block data - it reads directly from the client's
loaded chunks rather than making individual server queries.

Returns:
- Block counts by type
- Palette of unique blocks found
- Compressed block data (RLE encoded)
- Region dimensions and statistics

Use Cases:
- Analyze existing structures before modification
- Count materials needed to replicate a build
- Verify build completion
- Map terrain composition

Limits:
- Max 64x64x64 blocks per scan (262,144 blocks)
- Region must be within client's render distance
- include_states=true increases data size significantly

Example: Scan a 20x10x20 area
{
  "x1": 100, "y1": 64, "z1": 100,
  "x2": 120, "y2": 74, "z2": 120
}
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "x1": {"type": "integer", "description": "First corner X coordinate"},
                    "y1": {"type": "integer", "description": "First corner Y coordinate"},
                    "z1": {"type": "integer", "description": "First corner Z coordinate"},
                    "x2": {"type": "integer", "description": "Second corner X coordinate"},
                    "y2": {"type": "integer", "description": "Second corner Y coordinate"},
                    "z2": {"type": "integer", "description": "Second corner Z coordinate"},
                    "include_states": {
                        "type": "boolean",
                        "description": "Include block states (facing, waterlogged, etc). Default false.",
                        "default": False,
                    },
                },
                "required": ["x1", "y1", "z1", "x2", "y2", "z2"],
            },
        ),
        Tool(
            name="analyze_palette",
            description="""Analyze block distribution in a spherical area around a point.

Reads from the client's chunk cache for efficient analysis.

Returns:
- Block counts sorted by frequency
- Total blocks analyzed
- Percentage breakdown
- Suggested complementary blocks

Use Cases:
- Understand existing build style/palette
- Find matching materials for additions
- Analyze terrain composition
- Plan material requirements

Example: Analyze blocks within 16 blocks of position
{
  "x": 100, "y": 64, "z": 100,
  "radius": 16
}
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "Center X coordinate"},
                    "y": {"type": "integer", "description": "Center Y coordinate"},
                    "z": {"type": "integer", "description": "Center Z coordinate"},
                    "radius": {
                        "type": "integer",
                        "description": "Radius in blocks (default 16, max 32)",
                        "default": 16,
                    },
                },
                "required": ["x", "y", "z"],
            },
        ),
        Tool(
            name="analyze_palette_region",
            description="""Analyze block distribution in a rectangular region.

Similar to analyze_palette but uses a box instead of sphere.

Returns:
- Block counts sorted by frequency
- Total blocks analyzed
- Percentage breakdown

Example: Analyze a building's materials
{
  "x1": 100, "y1": 64, "z1": 100,
  "x2": 120, "y2": 80, "z2": 120
}
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "x1": {"type": "integer", "description": "First corner X coordinate"},
                    "y1": {"type": "integer", "description": "First corner Y coordinate"},
                    "z1": {"type": "integer", "description": "First corner Z coordinate"},
                    "x2": {"type": "integer", "description": "Second corner X coordinate"},
                    "y2": {"type": "integer", "description": "Second corner Y coordinate"},
                    "z2": {"type": "integer", "description": "Second corner Z coordinate"},
                },
                "required": ["x1", "y1", "z1", "x2", "y2", "z2"],
            },
        ),
    ]

    return schemas
