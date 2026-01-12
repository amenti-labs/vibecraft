# VibeCraft MCP Server

Python MCP server that connects Claude to Minecraft via the VibeCraft client mod.

## Quick Start

```bash
# Install dependencies
uv sync

# Run in SSE mode (recommended for debugging)
./start-vibecraft.sh

# Or run in stdio mode (for MCP clients)
uv run python -m src.vibecraft.server
```

## Server Modes

### SSE Mode (Recommended)

Best for debugging and multiple clients.

```bash
./start-vibecraft.sh
```

Configure your AI client to connect to `http://127.0.0.1:8765/sse`

### Stdio Mode

For MCP clients that launch the server as a subprocess.

```bash
uv run python -m src.vibecraft.server
```

## Configuration

Set via environment variables or `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `VIBECRAFT_CLIENT_HOST` | `127.0.0.1` | Client mod WebSocket host |
| `VIBECRAFT_CLIENT_PORT` | `8766` | Client mod WebSocket port |
| `VIBECRAFT_CLIENT_PATH` | `/vibecraft` | WebSocket path |
| `VIBECRAFT_WORLDEDIT_MODE` | `auto` | `auto`, `force`, or `off` |

### WorldEdit Mode

- **`off`** — Vanilla commands only (`/fill`, `/setblock`)
- **`auto`** — Use WorldEdit if available, fall back to vanilla
- **`force`** — Require WorldEdit

## Available Tools

### Core Tools
- `rcon_command` — Execute any Minecraft command
- `get_server_info` — Get server status and player list
- `get_player_position` — Get player location and facing direction
- `get_surface_level` — Find ground level at coordinates
- `build` — Execute multiple commands with progress tracking

### WorldEdit Tools (when enabled)
- `worldedit_selection` — Define regions (`//pos1`, `//pos2`, `//sel`)
- `worldedit_region` — Modify regions (`//set`, `//replace`, `//walls`)
- `worldedit_generation` — Create shapes (`//sphere`, `//cyl`, `//pyramid`)
- `worldedit_clipboard` — Copy/paste operations
- `worldedit_history` — Undo/redo

### Helper Tools
- `search_minecraft_item` — Find blocks by name
- `validate_pattern` — Check WorldEdit pattern syntax
- `spatial_awareness_scan` — Analyze build area

## Development

```bash
# Run tests
uv run pytest

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/
```

## Architecture

```
src/vibecraft/
├── server.py          # Main MCP server
├── client_bridge.py   # WebSocket connection to client mod
├── config.py          # Configuration management
├── sanitizer.py       # Command validation
└── tools/             # Tool handlers
    ├── build_tools.py
    ├── core_tools.py
    └── worldedit_*.py
```

## Troubleshooting

### "Connection failed"

1. Check Minecraft is running with the mod installed
2. Run `/vibecraft status` in Minecraft
3. Run `/vibecraft allow` to enable AI control
4. Verify port matches (default: 8766)

### WorldEdit commands fail

Set `VIBECRAFT_WORLDEDIT_MODE=off` if you don't have WorldEdit installed.

### Commands return "Command dispatched" but nothing happens

Update the client mod to the latest version with output capture.
