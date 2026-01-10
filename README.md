<p align="center">
  <img src="assets/vibecraft_logo.png" alt="VibeCraft logo" width="420" />
</p>

# VibeCraft

**AI-Powered WorldEdit for Minecraft** — Build ambitious creations through natural-language conversations with your AI assistant.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Minecraft 1.21+](https://img.shields.io/badge/minecraft-1.21+-green.svg)](https://www.minecraft.net/)

## Features

- 🎯 **46 MCP Tools** – Complete WorldEdit coverage (130+ commands) with structured tools and safety guardrails
- ⚡ **Fast Execution** – Direct RCON connection with real-time command execution and feedback
- 🤖 **AI-Native Design** – Token-optimized context files, specialist agent prompts, and structured workflows
- 🏗️ **Smart Building Tools** – Furniture placement, building patterns, parametric templates, and terrain generation
- 🧠 **Spatial Awareness** – Advanced system prevents common placement errors with fast, accurate scanning
- 📚 **Knowledge Base** – 2,565 Minecraft items, 70+ patterns, 66 furniture designs, scale references
- 🧰 **Context-Aware Builds** – AI consumes curated docs so it can plan with block palettes, furniture layouts, and default `/fill` workflows when WorldEdit isn’t the right tool
- 🛠️ **Production Ready** – Docker-based setup, automated testing, comprehensive error handling
- 🔄 **Multi-Client Support** – Works with Claude Code, Claude Desktop, Cursor, and any MCP-compatible AI

### Context Library & Default Commands

VibeCraft isn’t just a WorldEdit wrapper. The repository ships a full AI-readable knowledge base in `context/`—block catalogs, building patterns, furniture layouts, scale references, terrain recipes, and more. Agents read these files before they build, so they understand materials, proportions, and style conventions. When a task calls for vanilla `/fill` or `/setblock` workflows (farm plots, redstone details, small interior tweaks), the extra context lets the AI combine standard commands with WorldEdit for precise results.

## Installation

### Prerequisites

- **uv** — Fast Python package manager — [Install](https://github.com/astral-sh/uv) with `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Python 3.10+** — [Download](https://www.python.org/downloads/)
- **Docker Desktop** with Docker Compose — [Download](https://www.docker.com/products/docker-desktop)
- **MCP-compatible AI client** — [Claude Code](https://claude.com/claude-code), [Claude Desktop](https://claude.ai/download), or [Cursor](https://cursor.sh/)

### Setup

1. **Clone and run setup script:**

```bash
git clone https://github.com/amenti-labs/vibecraft.git
cd vibecraft
./setup-all.sh
```

The script automatically:
- ✅ Installs dependencies with uv (fast, modern Python package manager)
- ✅ Downloads and starts PaperMC 1.21.11 + WorldEdit 7.3.18 in Docker
- ✅ Configures RCON with secure auto-generated password
- ✅ Creates AI client configuration file
- ✅ Tests all connections


2. **Choose your server mode:**

VibeCraft supports two ways to run:

### Mode 1: stdio/Command Mode (Recommended for Single Client)

**Best for:** Daily use, simple setup, single AI client

The AI client launches the MCP server as a subprocess when needed.

**Configuration:**

<details>
<summary><b>Claude Code (VSCode)</b></summary>

```bash
# Copy system prompt
cp SYSTEM_PROMPT.md CLAUDE.md
```

Add to VSCode settings (Settings > Search "MCP" > Add configuration):
```json
{
  "mcpServers": {
    "vibecraft": {
      "command": "uv",
      "args": ["run", "python", "-m", "src.vibecraft.server"],
      "cwd": "/absolute/path/to/vibecraft/mcp-server",
      "env": {
        "VIBECRAFT_RCON_HOST": "127.0.0.1",
        "VIBECRAFT_RCON_PORT": "25575",
        "VIBECRAFT_RCON_PASSWORD": "your_password_from_setup"
      }
    }
  }
}
```

</details>

<details>
<summary><b>Claude Desktop</b></summary>

```bash
# macOS
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux
nano ~/.config/Claude/claude_desktop_config.json
```

Add this configuration:
```json
{
  "mcpServers": {
    "vibecraft": {
      "command": "uv",
      "args": ["run", "python", "-m", "src.vibecraft.server"],
      "cwd": "/absolute/path/to/vibecraft/mcp-server",
      "env": {
        "VIBECRAFT_RCON_HOST": "127.0.0.1",
        "VIBECRAFT_RCON_PORT": "25575",
        "VIBECRAFT_RCON_PASSWORD": "your_password_from_setup"
      }
    }
  }
}
```

</details>

<details>
<summary><b>Cursor</b></summary>

Add to `.cursor/mcp.json` in your project:
```json
{
  "mcpServers": {
    "vibecraft": {
      "command": "uv",
      "args": ["run", "python", "-m", "src.vibecraft.server"],
      "cwd": "/absolute/path/to/vibecraft/mcp-server",
      "env": {
        "VIBECRAFT_RCON_HOST": "127.0.0.1",
        "VIBECRAFT_RCON_PORT": "25575",
        "VIBECRAFT_RCON_PASSWORD": "your_password_from_setup"
      }
    }
  }
}
```

</details>

---

### Mode 2: HTTP/SSE Server Mode (Best for Debugging & Multiple Clients)

**Best for:** Debugging, multiple AI clients, seeing real-time logs

Run VibeCraft as a standalone server that multiple clients can connect to.

**Start the server (from project root):**
```bash
# From the vibecraft root directory
cd mcp-server
./start-vibecraft.sh
```

You'll see:
```
🎮 VibeCraft MCP Server - HTTP/SSE Mode
   All 45 tools available
============================================================
📡 RCON Host: 127.0.0.1:25575
✅ RCON connected
✅ WorldEdit 7.3.18 detected
🚀 Server running at http://127.0.0.1:8765/sse
```

**Configuration:**

<details>
<summary><b>Claude Code (VSCode)</b></summary>

Add to VSCode settings:
```json
{
  "mcpServers": {
    "vibecraft-sse": {
      "transport": "sse",
      "url": "http://127.0.0.1:8765/sse"
    }
  }
}
```

</details>

<details>
<summary><b>Claude Desktop</b></summary>

```json
{
  "mcpServers": {
    "vibecraft-sse": {
      "url": "http://127.0.0.1:8765/sse"
    }
  }
}
```

</details>

<details>
<summary><b>Cursor</b></summary>

Add to `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "vibecraft-sse": {
      "transport": "sse",
      "url": "http://127.0.0.1:8765/sse"
    }
  }
}
```

</details>

**Benefits of SSE Mode:**
- ✅ See all RCON commands in real-time
- ✅ Debug issues with full logging
- ✅ Connect multiple AI clients simultaneously
- ✅ Restart clients without restarting server

---

3. **Get your RCON password:**

After setup completes, find your password:
```bash
cat .rcon_password
```

Replace `your_password_from_setup` in the configs above with this password.

4. **Restart your AI client completely**

5. **Verify setup:**
```
Ask your AI: "Can you connect to the Minecraft server?"
```

If your AI responds with server information, you're ready to build! 🎉

## Usage

### Building Structures

```
User: "Build a 15x20 medieval castle with towers at each corner"
AI: *analyzes terrain, creates foundation, builds walls with stone bricks,
     adds corner towers, creates battlements, installs oak doors*
```

### Interior Design

```
User: "Furnish the great hall with a dining area and throne"
AI: *scans room dimensions, places dining table with chairs,
     adds chandeliers, creates elevated throne platform*
```

### Terrain Shaping

```
User: "Create rolling hills with oak trees around the castle"
AI: *analyzes area, generates terrain with Perlin noise,
     textures with grass and dirt, plants trees strategically*
```

### Advanced Projects

```
User: "Build a village with 5 unique houses, a market, and a church"
AI: *uses building templates, customizes each structure,
     places roads, adds lighting, furnishes interiors*
```

## How It Works

### The MCP Architecture

VibeCraft implements the **Model Context Protocol (MCP)** to connect AI assistants to Minecraft:

1. **MCP Server** (Python) — Exposes WorldEdit commands as structured tools
2. **RCON Bridge** — Direct connection to Minecraft server (no mods required)
3. **AI Client** — Receives tool definitions and executes commands via natural language

### The Building Process

1. **User Request** — Natural language instruction to AI
2. **AI Planning** — Analyzes request, selects appropriate tools
3. **Spatial Awareness** — Scans environment to prevent placement errors
4. **Command Execution** — Executes WorldEdit commands via RCON
5. **Verification** — Checks results, adjusts if needed, reports completion

### Safety Features

- **Command Sanitization** — Validates all commands before execution
- **Coordinate Bounds** — Optional build area restrictions
- **Async Prevention** — Prevents race conditions in command execution
- **Undo Support** — Full WorldEdit history with `//undo` and `//redo`
- **Spatial Scanning** — Mandatory scans prevent furniture/roof placement errors

## Project Structure

```
vibecraft/
├── mcp-server/                # Core MCP server
│   ├── src/vibecraft/
│   │   ├── server.py          # Main MCP server
│   │   ├── rcon_manager.py    # RCON connection handler
│   │   ├── sanitizer.py       # Command validation
│   │   ├── tools/             # Tool handlers (47 tools)
│   │   └── minecraft_items_loader.py  # Item database
│   ├── tests/                 # Unit tests
│   ├── pyproject.toml         # Project metadata & dependencies
│   └── uv.lock                # Locked dependencies (managed by uv)
├── context/                   # AI knowledge base
│   ├── minecraft_items_filtered.json  # 2,565 items
│   ├── minecraft_furniture_catalog.json  # 66 designs
│   ├── building_patterns.json  # 29 building patterns
│   ├── terrain_patterns.json  # 41 terrain patterns
│   └── building_templates.json  # 5 parametric templates
├── AGENTS/                    # Specialist AI prompts
│   ├── minecraft-master-planner.md
│   ├── minecraft-shell-engineer.md
│   ├── minecraft-facade-architect.md
│   ├── minecraft-roofing-specialist.md
│   └── minecraft-interior-designer.md
├── SYSTEM_PROMPT.md           # Main AI instructions
├── docs/                      # Setup guides
├── scripts/                   # Helper scripts
├── setup-all.sh               # Automated setup
└── docker-compose.yml         # Minecraft server config

# Generated during use:
minecraft-data/                # Docker volume (world, logs)
.rcon_password                 # Auto-generated RCON password
claude-code-config.json        # AI client configuration
CLAUDE.md                      # System prompt (copy of SYSTEM_PROMPT.md)
mcp-server/.venv/              # Python virtual environment (managed by uv)
```

## Examples

### Example 1: Simple House
```bash
User: "Build a cozy cottage with stone walls and oak roof"
```
AI creates:
- 10×12 block foundation
- Cobblestone walls with corner pillars
- Oak stair roof with proper overhangs
- Windows with frames, oak door
- Interior floor and ceiling

### Example 2: Complex Castle
```bash
User: "Build a medieval fortress with main keep, four corner towers, and courtyard"
```
AI creates:
- Terrain analysis and foundation leveling
- 30×30 main keep with multiple floors
- Four 8×8 corner towers connected by walls
- Courtyard with entrance gate
- Interior rooms with furniture
- Lighting throughout

### Example 3: Landscape Design
```bash
User: "Create a Japanese garden with koi pond, stone paths, and cherry trees"
```
AI creates:
- Excavates pond with natural curves
- Places water and lily pads
- Creates gravel paths with stepping stones
- Plants cherry trees (pink concrete leaves)
- Adds stone lanterns and bamboo

### More Examples

For detailed conversation-style examples and workflows, see the `examples/` directory:

- **Basic Building** (`examples/basic_building_example.txt`) — Fundamentals: setting positions with `//pos1` and `//pos2`, creating walls/floors/roofs, using materials effectively

- **Furniture Placement** (`examples/furniture_example.txt`) — Interior design workflow: using `spatial_awareness_scan` to find floor/ceiling levels, browsing furniture catalog, placing furniture correctly ON floor (not embedded), creating complete room layouts

- **Terrain Generation** (`examples/terrain_example.txt`) — Natural landscape creation: generating hills/mountains/valleys, applying realistic texturing, smoothing for natural appearance

- **MCP Configurations** (`examples/configs/`) — Example configuration files for Claude Code, Claude Desktop, and other MCP clients

These are conversational examples showing typical AI-assisted building workflows that you can follow along with or adapt to your needs.

## Advanced Features

### Spatial Awareness

Advanced spatial analysis prevents common placement errors:

- 🏠 **Floor Detection** — Finds exact floor/ceiling Y coordinates
- 📏 **Clearance Analysis** — Checks space in all 6 directions
- 🧱 **Material Detection** — Identifies building materials for style matching
- 🏗️ **Structure Analysis** — Recognizes roofs, walls, buildings vs terrain

**Detail Levels:**
- `low` (2-3s) — Fast scans for quick checks
- `medium` (4-5s) — **Recommended** — Balanced speed and detail
- `high` (8-10s) — Comprehensive analysis with style detection

### Building Templates

**5 parametric templates** for instant structures:

- `medieval_round_tower` — Circular tower with spiral stairs
- `simple_cottage` — Customizable house with chimney
- `guard_tower` — Defensive watchtower
- `wizard_tower` — Fantasy tower with mystical elements
- `simple_barn` — Rustic wooden barn

**Customize:** height, width, materials, roof style, features

### Furniture System

**66 furniture designs** with automated placement:

- All 66 with exact block coordinates
- Automated placement via `place_furniture` tool
- Spatial awareness prevents placement errors
- Style-matched materials

### Pattern Library

**70+ patterns** for architectural elements:

- **Roofing** (29) — Gable, hip, slab, flat in multiple materials
- **Facades** (11) — Windows, doors, frames
- **Corners** (8) — Pillar styles and structural elements
- **Details** (22) — Chimneys, decorative elements

## Tips for Best Results

1. **Be Specific with Details**
   - Good: "Build a 20×30 Gothic cathedral with flying buttresses and rose window"
   - Less good: "Build a church"

2. **Let AI Scan Before Placing**
   - AI will automatically use spatial awareness for furniture and roofs
   - Trust the scanning process — it prevents 99% of placement errors

3. **Use Building Templates for Speed**
   - Templates are 10x faster than building from scratch
   - Fully customizable (height, materials, features)

4. **Leverage the Knowledge Base**
   - AI has access to 2,565 Minecraft items (blocks and items for Minecraft 1.21.11)
   - Ask: "What oak blocks are available?" for material suggestions

5. **Build in Phases**
   - Large projects work better in phases: shell → facade → roof → interior → landscape
   - AI can use specialist agents for each phase

6. **Check Progress**
   - Join server: `minecraft://localhost:25565`
   - Watch builds happen in real-time

## Troubleshooting

### "Minecraft server won't start"

```bash
# Check Docker status
docker ps

# View logs
docker logs -f vibecraft-minecraft

# Restart server
docker restart vibecraft-minecraft
```

### "RCON connection failed"

```bash
# Test connection
docker exec vibecraft-minecraft rcon-cli list

# Verify password
cat .rcon_password

# Check MCP server config
cat mcp-server/.env
```

### "AI can't connect to VibeCraft"

1. Verify Minecraft server is running: `docker ps`
2. Check MCP configuration matches `claude-code-config.json`
3. Restart AI client completely (not just reload)
4. Check system prompt is configured (`CLAUDE.md` for Claude Code)
5. Test RCON: `./scripts/test-connection.sh`

### "WorldEdit says 'You need to provide a world'"

This error occurs when WorldEdit can't determine world context from RCON/console.

**Fix (automatically done by setup script):**
```bash
# The setup script configures WorldEdit automatically
# If you need to fix manually:
docker exec vibecraft-minecraft bash -c "sed -i 's/^    disallowed-blocks:.*/    disallowed-blocks: []/g' plugins/WorldEdit/config.yml"
docker restart vibecraft-minecraft
```

**Alternative:** Ensure a player is online when running WorldEdit commands. WorldEdit works best when there's an active player to provide world context.

### "WorldEdit commands not working"

**Problem:** Commands execute but nothing happens in-game

**Solutions:**
- Verify WorldEdit plugin is loaded: Check server logs for "WorldEdit" on startup
- Ensure you have operator permissions: Run `op <username>` from server console
- Use comma-separated coordinates from RCON: `//pos1 100,64,100` (NOT `//pos1 100 64 100`)
- Some commands require player context - ensure a player is online

### "Server performance issues"

**Problem:** Server lag or slow WorldEdit operations

**Solutions:**
- Check Java version: `java --version` (must be 21+)
- Ensure adequate RAM: At least 2GB allocated
- Review server logs: `docker logs vibecraft-minecraft | grep ERROR`
- Increase WorldEdit limits in `plugins/WorldEdit/config.yml` if operations fail

## Technical Details

- **Package Manager**: uv (10-100x faster than pip)
- **MCP Server**: Python 3.10+ with MCP SDK
- **Minecraft Server**: PaperMC 1.21.11 (latest)
- **WorldEdit**: Version 7.3.18
- **RCON Protocol**: TCP connection to port 25575
- **Tools**: 46 MCP tools covering 130+ WorldEdit commands
- **Context Window**: Optimized for Claude models (200K tokens)
- **Response Time**: RCON commands execute in <100ms
- **Safety**: Command sanitization, bounds checking, async prevention
- **Docker**: Containerized Minecraft server with persistent volumes

### MCP Tools Breakdown

- **Core**: 2 tools (RCON command, server info)
- **WorldEdit**: 20 tool categories (selection, region, generation, etc.)
- **Advanced**: 13 tools (furniture, patterns, terrain, spatial analysis)
- **Validation**: 6 helper tools (pattern/mask validation, item search, etc.)
- **Templates**: 3 tools (building templates, schematics, terrain patterns)

## Manual Setup (Advanced)

The automated `setup-all.sh` script handles everything for you. If you prefer manual setup without Docker or need to customize the installation, archived manual setup instructions are available at `docs/archive/MANUAL_SETUP.md`:
- Manual Java and PaperMC installation
- WorldEdit plugin setup from source
- Manual RCON configuration
- Custom MCP server configuration

**Note:** Manual setup is not recommended for most users. The automated setup is faster, safer, and better tested.

## Contributing

We welcome contributions! Please review:
- [CONTRIBUTING.md](CONTRIBUTING.md) — Development workflow and standards
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — Community guidelines

**Areas for contribution:**
- Additional building templates
- More furniture designs
- Terrain generation recipes
- Pattern library expansions
- Bug fixes and optimizations

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support & Community

Need help or have questions? We're here to support you:

- 📧 **Email**: [evan@amentilabs.com](mailto:evan@amentilabs.com) — Questions, feedback, or to join the community
- 🐛 **Bug Reports**: [Open an issue](https://github.com/amenti-labs/vibecraft/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/amenti-labs/vibecraft/discussions)

We'd love to hear from you and help you build amazing creations!

## Credits

- **Created by**: [Amenti Labs](https://github.com/amenti-labs)
- **Powered by**: Anthropic's Claude AI via Model Context Protocol (MCP)
- **Built on**: Minecraft, PaperMC, WorldEdit, Docker
- **Repository**: https://github.com/amenti-labs/vibecraft

## Star History

<picture>
  <source
    media="(prefers-color-scheme: dark)"
    srcset="https://api.star-history.com/svg?repos=amenti-labs/vibecraft&type=Date&theme=dark"
  />
  <source
    media="(prefers-color-scheme: light)"
    srcset="https://api.star-history.com/svg?repos=amenti-labs/vibecraft&type=Date"
  />
  <img
    alt="Star History Chart"
    src="https://api.star-history.com/svg?repos=amenti-labs/vibecraft&type=Date"
  />
</picture>

---

**Happy building!** 🧱

Need help? Check the [Support & Community](#support--community) section above or email [evan@amentilabs.com](mailto:evan@amentilabs.com)
