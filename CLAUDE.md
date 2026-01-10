# VibeCraft Development Guide

You are working on the **VibeCraft codebase** - an AI-powered Minecraft WorldEdit MCP server.

> **Note:** This CLAUDE.md is for **developing** VibeCraft. To **use** VibeCraft as a building agent, run Claude Code from the `/agent` folder instead.

## Repository Structure

```
vibecraft/
├── agent/                    # VibeCraft AGENT files (run Claude from here to BUILD in Minecraft)
│   ├── .claude/skills/       # 7 building skills (worldedit, structures, terrain, etc.)
│   ├── context/              # AI reference guides (MD files agent reads)
│   ├── CLAUDE.md             # Agent system prompt
│   └── SYSTEM_PROMPT.md      # Source for agent prompt
│
├── mcp-server/               # MCP SERVER CODE (Python)
│   ├── src/vibecraft/
│   │   ├── server.py         # Main MCP server entry point
│   │   ├── tools/            # Tool handlers (modular)
│   │   ├── rcon_manager.py   # RCON protocol handler
│   │   ├── code_sandbox.py   # Safe code execution for build()
│   │   ├── sanitizer.py      # Command validation
│   │   └── ...
│   ├── data/                 # Server data files (JSON loaded by tools)
│   ├── pyproject.toml        # Dependencies
│   └── start-vibecraft.sh    # Server launcher
│
├── dev_docs/                 # Development documentation
├── docs/                     # User documentation
├── docker-compose.yml        # Minecraft server setup
└── setup-all.sh              # One-command setup
```

## Key Development Areas

### MCP Server (`mcp-server/src/vibecraft/`)

The core Python server that provides MCP tools to AI clients.

| File | Purpose |
|------|---------|
| `server.py` | Main entry, tool registration, MCP protocol |
| `tools/__init__.py` | Tool registry, handler dispatch |
| `tools/build_tools.py` | `build()` tool - batch command execution |
| `tools/core_tools.py` | RCON, WorldEdit generic handlers |
| `tools/worldedit_*.py` | WorldEdit-specific tools |
| `rcon_manager.py` | Minecraft RCON connection |
| `code_sandbox.py` | Safe Python execution for procedural builds |
| `tool_schemas.py` | MCP tool definitions and schemas |

### Agent Files (`agent/`)

Files consumed by the VibeCraft building agent.

| File | Purpose |
|------|---------|
| `.claude/skills/` | Building skills with detailed workflows |
| `context/` | JSON catalogs (items, patterns, templates) |
| `SYSTEM_PROMPT.md` | Master agent instructions |

## Development Commands

```bash
# Start Minecraft server
docker compose up -d

# Run MCP server (stdio mode)
cd mcp-server && uv run python -m src.vibecraft.server

# Run MCP server (HTTP/SSE mode for debugging)
cd mcp-server && ./start-vibecraft.sh

# Run tests
cd mcp-server && uv run pytest

# Type checking
cd mcp-server && uv run mypy src/

# Linting
cd mcp-server && uv run ruff check src/
```

## Common Development Tasks

### Adding a New MCP Tool

1. Define schema in `tool_schemas.py`
2. Create handler in `tools/` (or add to existing module)
3. Register in `tools/__init__.py` TOOL_REGISTRY
4. Update agent docs if user-facing

### Modifying WorldEdit Behavior

- `build_tools.py` handles `//` command auto-wrapping
- `core_tools.py` has `prepare_worldedit_command()` for single commands
- WorldEdit commands need `execute as <player> at @s run` wrapper

### Updating Agent Skills

Skills are in `agent/.claude/skills/`. Each skill has:
- `SKILL.md` - Main skill content (required)
- Optional supporting `.md` files

The skill description in YAML frontmatter controls when it triggers.

## Testing with Minecraft

1. Ensure Docker is running: `docker compose up -d`
2. Connect to server: `localhost:25565`
3. Player must be online for WorldEdit commands
4. Check logs: `docker compose logs -f minecraft`

## Code Style

- Python 3.10+ with type hints
- Ruff for linting
- Async handlers for MCP tools
- Descriptive error messages for AI consumption

## Important Notes

- WorldEdit commands via RCON need player context (`execute as <player>`)
- Brush/tool commands don't work via RCON (require player interaction)
- The `build()` tool auto-wraps `//` commands with player context
- Always test changes with an actual Minecraft client connected
