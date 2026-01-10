# VibeCraft MCP Server

**AI-Powered WorldEdit for Minecraft**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

VibeCraft is a Model Context Protocol (MCP) server that exposes ALL WorldEdit commands to AI assistants like Claude, enabling AI-powered building in Minecraft.

## Features

- 🎯 **Complete WorldEdit Coverage** - All 200+ WorldEdit commands accessible
- 🔒 **Safety First** - Command validation, sanitization, and coordinate bounds checking
- 🛠️ **Hybrid Tool Approach** - Generic RCON + Categorized WorldEdit + Helper utilities
- 📚 **Comprehensive Documentation** - Built-in guides for patterns, masks, expressions
- 🔌 **Easy Integration** - Works with Claude Code, Claude Desktop, Cursor, and other MCP clients
- ⚡ **RCON-Based** - Simple setup, no custom Minecraft plugins required

## Quick Start

### Prerequisites

- uv - Fast Python package manager ([install](https://github.com/astral-sh/uv))
- Python 3.10 or higher
- Minecraft server with WorldEdit and RCON enabled
- Claude Code, Claude Desktop, or another MCP-compatible client

### Installation

```bash
# Clone the repository and navigate to mcp-server directory
cd <VIBECRAFT_ROOT>/mcp-server

# Install dependencies with uv (automatically manages Python environment)
uv sync
```

### Configuration

Create a `.env` file in the `mcp-server` directory:

```bash
# RCON Connection
VIBECRAFT_RCON_HOST=127.0.0.1
VIBECRAFT_RCON_PORT=25575
VIBECRAFT_RCON_PASSWORD=your_rcon_password_here
VIBECRAFT_RCON_TIMEOUT=10

# Safety Settings
VIBECRAFT_ENABLE_SAFETY_CHECKS=true
VIBECRAFT_ALLOW_DANGEROUS_COMMANDS=true
VIBECRAFT_MAX_COMMAND_LENGTH=1000

# Optional: Build Area Constraints
# VIBECRAFT_BUILD_MIN_X=0
# VIBECRAFT_BUILD_MAX_X=1000
# VIBECRAFT_BUILD_MIN_Y=-64
# VIBECRAFT_BUILD_MAX_Y=319
# VIBECRAFT_BUILD_MIN_Z=0
# VIBECRAFT_BUILD_MAX_Z=1000

# Feature Flags
VIBECRAFT_ENABLE_VERSION_DETECTION=true
VIBECRAFT_ENABLE_COMMAND_LOGGING=true
```

### Test the Server

```bash
# Run the server directly (for testing)
# uv automatically manages the Python environment
uv run python -m src.vibecraft.server
```

The server will connect to your Minecraft server and verify WorldEdit is installed.

## Integrating with AI Clients

### Claude Code

Add to your Claude Code MCP configuration:

```json
{
  "mcpServers": {
    "vibecraft": {
      "command": "uv",
      "args": ["run", "python", "-m", "src.vibecraft.server"],
      "cwd": "<VIBECRAFT_ROOT>/mcp-server",
      "env": {
        "VIBECRAFT_RCON_HOST": "127.0.0.1",
        "VIBECRAFT_RCON_PORT": "25575",
        "VIBECRAFT_RCON_PASSWORD": "your_password_here"
      }
    }
  }
}
```

Restart Claude Code. You should now see VibeCraft tools available!

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "vibecraft": {
      "command": "uv",
      "args": ["run", "python", "-m", "src.vibecraft.server"],
      "cwd": "<VIBECRAFT_ROOT>/mcp-server",
      "env": {
        "VIBECRAFT_RCON_HOST": "127.0.0.1",
        "VIBECRAFT_RCON_PORT": "25575",
        "VIBECRAFT_RCON_PASSWORD": "your_password_here"
      }
    }
  }
}
```

Restart Claude Desktop.

### Cursor

Edit `.cursor/mcp.json` in your project:

```json
{
  "mcpServers": {
    "vibecraft": {
      "command": "uv",
      "args": ["run", "python", "-m", "src.vibecraft.server"],
      "cwd": "<VIBECRAFT_ROOT>/mcp-server",
      "env": {
        "VIBECRAFT_RCON_HOST": "127.0.0.1",
        "VIBECRAFT_RCON_PORT": "25575",
        "VIBECRAFT_RCON_PASSWORD": "your_password_here"
      }
    }
  }
}
```

## Available Tools

VibeCraft provides three tiers of tools:

### Tier 1: Generic RCON
- `rcon_command` - Execute any Minecraft/WorldEdit command

### Tier 2: Categorized WorldEdit Commands
- `worldedit_selection` - Define and manipulate regions
- `worldedit_region` - Modify selected regions (set, replace, walls, etc.)
- `worldedit_generation` - Generate shapes (spheres, cylinders, pyramids)
- `worldedit_clipboard` - Copy, cut, paste operations
- `worldedit_schematic` - Save/load structures
- `worldedit_history` - Undo/redo changes
- `worldedit_utility` - Fill, drain, remove, environment commands
- `worldedit_biome` - View and modify biomes
- `worldedit_brush` - Brush-based editing (requires player)
- `worldedit_general` - Session options, limits, side-effects, and overrides
- `worldedit_navigation` - Movement commands that usually need player context
- `worldedit_chunk` - Chunk diagnostics and deletion commands
- `worldedit_snapshot` - Snapshot selection and restoration
- `worldedit_scripting` - CraftScript execution helpers
- `worldedit_reference` - Search and help index commands
- `worldedit_tools` - Tool binding, super pickaxe, and brush configuration
- `worldedit_deform` - Mathematical terrain deformations (//deform expressions)
- `worldedit_vegetation` - Flora and forest generation (//flora, //forest, /tool tree)
- `worldedit_terrain_advanced` - Advanced terrain (//caves, //ore, //regen)
- `worldedit_analysis` - Block distribution and calculations (//distr, //calc)

### Tier 3: Helper Utilities
- `validate_pattern` - Validate WorldEdit patterns
- `validate_mask` - Validate WorldEdit masks
- `get_server_info` - Get server status and info
- `calculate_region_size` - Calculate region dimensions and block count
- `search_minecraft_item` - Find blocks by name (2,565 items from Minecraft 1.21.11)
- `get_player_position` - Get player coordinates, rotation, target block, ground level
- `get_surface_level` - Find ground Y-coordinate at X,Z position

## Example Usage with AI

Once configured, you can ask Claude (or your AI assistant):

```
"Build a stone castle at coordinates 100, 64, 100. Make it 30x20x30 blocks."

"Create a hollow sphere of glass with a 15 block radius at 200, 80, 200."

"Replace all dirt in the region from (0,60,0) to (50,70,50) with grass blocks."

"Copy the structure at (100,64,100) to (100,64,110) and paste it at (300,64,300)."
```

The AI will use VibeCraft tools to execute appropriate WorldEdit commands!

## Documentation Resources

VibeCraft provides built-in documentation resources that AI can access:

- `vibecraft://guide/patterns` - WorldEdit pattern syntax
- `vibecraft://guide/masks` - WorldEdit mask syntax
- `vibecraft://guide/expressions` - WorldEdit expression syntax
- `vibecraft://guide/coordinates` - Coordinate system guide
- `vibecraft://guide/workflows` - Common building workflows
- `vibecraft://guide/player-context` - Player context commands info

## Safety Features

- **Command Sanitization** - Blocks command injection, control characters
- **Dangerous Command Controls** - Optional restrictions via config (default allows all)
- **Coordinate Bounds** - Optional restrictions on build area
- **Player Context Warnings** - Warns about commands that need player interaction
- **Command Logging** - Track all executed commands

## Troubleshooting

### RCON Connection Failed

**Problem:** "Failed to connect to Minecraft server"

**Solutions:**
1. Verify Minecraft server is running
2. Check `server.properties` has `enable-rcon=true`
3. Verify RCON password matches
4. Ensure no firewall blocking port 25575
5. Test with `mcrcon` CLI tool

### WorldEdit Commands Not Working

**Problem:** Commands execute but nothing happens

**Solutions:**
1. Verify WorldEdit is installed: `/version WorldEdit`
2. Check you have operator permissions
3. Use comma-separated coordinates from console: `//pos1 X,Y,Z`
4. Some commands require player context - use alternatives

### Commands Blocked by Safety

**Problem:** "Potentially dangerous command blocked" (only when you've set `VIBECRAFT_ALLOW_DANGEROUS_COMMANDS=false`)

**Solutions:**
- Review command to ensure it's safe
- Re-enable dangerous commands with `VIBECRAFT_ALLOW_DANGEROUS_COMMANDS=true`
- Use coordinate bounds to limit build area

## Development

### Running Tests

```bash
# Install dev dependencies (includes test tools)
uv sync --all-extras

# Run tests with uv
uv run pytest

# Run with coverage
uv run pytest --cov=src/vibecraft --cov-report=html
```

### Code Quality

```bash
# Format code
uv run black src/

# Lint code
uv run ruff check src/

# Type checking
uv run mypy src/
```

## Architecture

```
VibeCraft MCP Server
├── Configuration Management (config.py)
├── RCON Connection Manager (rcon_manager.py)
├── Command Sanitization (sanitizer.py)
├── Documentation Resources (resources.py)
└── MCP Server Implementation (server.py)
    ├── Tier 1: Generic RCON Tool
    ├── Tier 2: Categorized WorldEdit Tools (16 tools)
    └── Tier 3: Helper Utilities (4 tools)
```

## Limitations

- **RCON-Based**: Some commands requiring player context won't work from console
- **No Schematic Browsing**: File system access depends on server permissions
- **Async Operations**: Large operations may timeout (increase `RCON_TIMEOUT`)
- **Version Detection**: Automatic but may fail on some server configurations

## Roadmap

Future enhancements planned:
- [ ] Custom Minecraft plugin for direct WorldEdit API access
- [ ] WebSocket support for real-time feedback
- [ ] Schematic preview and validation
- [ ] Build queue management for large operations
- [ ] Multi-server support
- [ ] Web UI for monitoring and management

## Recent Improvements

See `CLEANUP_COMPLETE.md` for details on recent cleanup work:
- ✅ **FIXED**: Updated system prompt with correct `spatial_awareness_scan` tool
- ✅ **FIXED**: Cleaned 15 dead imports from server.py (40% reduction in import section)

All documentation is now accurate and imports are clean. No known issues.

## Future Improvements

### ⚠️ HISTORICAL NOTE: Schematic Library System (REMOVED)

> **Status**: This feature was previously implemented but **REMOVED** to simplify the codebase.
> **Current Alternative**: Use `worldedit_schematic` tool for basic schematic operations.
> **This documentation is kept for historical reference and potential future re-implementation.**

A schematic library system was previously implemented but removed to simplify the codebase. This functionality can be re-added in the future with the following features:

#### Planned Features

**Schematic Management Tool** (`schematic_library`):
- **List** - Browse available `.schem` files in a repository directory
- **Info** - Inspect schematic metadata (dimensions, block count, offset)
- **Prepare** - Copy schematics to WorldEdit's schematics folder
- **Load** - Automatically load schematics into WorldEdit's clipboard

#### Implementation Details

The system would:
1. Store `.schem` files in a `schemas/` directory in the project root
2. Use `nbtlib` to read NBT metadata from schematic files
3. Copy files to the Minecraft server's WorldEdit schematics folder
4. Execute `//schem load` commands via RCON to load into clipboard
5. Integrate with WorldEdit's native clipboard commands for pasting

#### Example Workflow

```
1. schematic_library(action="list")
   → Shows available schematics with dimensions and status

2. schematic_library(action="load", name="modern_villa_1")
   → Copies to server, loads into clipboard

3. worldedit_clipboard(command="paste -a -o")
   → Pastes the loaded schematic at current location
```

#### Files Removed

- `schematic_manager.py` - NBT parsing and file management utilities
- Tool handler in `tools/core_tools.py` - Schematic library tool implementation
- Tool definition in `server.py` - MCP tool schema and description

#### Why Removed

- Added complexity with NBT file handling dependencies
- Limited use case (WorldEdit's native `/schem` commands work fine)
- File system access can be restricted on some servers
- Better as an optional plugin or separate utility

#### When to Re-Add

Consider re-implementing when:
- Users need managed schematic repositories with metadata
- Integration with schematic marketplaces/libraries is desired
- Preview functionality before placing is required
- Version control for schematics becomes necessary
- Team collaboration on schematic collections is needed

#### Alternative Approach

Instead of a custom library, users can:
- Use WorldEdit's native `/schem` commands via `worldedit_schematic` tool
- Manually copy `.schem` files to server's schematics folder
- Use file management tools to organize schematics
- Access schematics via server file system if available

#### Resources Available

The `schemas/` directory at project root contains example schematics:
- `modern_villa_1.schem` - Modern villa design
- `modern_villa_2.schem` - Alternative villa layout

These can serve as references for future implementation.

## Contributing

Contributions welcome! Please see our contributing guidelines.

## License

MIT License - see LICENSE file for details

## Credits

- WorldEdit by EngineHub
- MCP SDK by Anthropic
- mcrcon library by Tiiffi

## Support

- 📖 [Full Documentation](../docs/)
- 🐛 [Report Issues](https://github.com/amenti-labs/vibecraft/issues)
- 💬 [Discussions](https://github.com/amenti-labs/vibecraft/discussions)

---

**Built with ❤️ for the Minecraft and AI communities**
