<p align="center">
  <img src="assets/vibecraft_logo.png" alt="VibeCraft logo" width="420" />
</p>

# VibeCraft

**AI-Powered Minecraft Building** — Build structures through natural-language conversations with Claude.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Minecraft 1.21+](https://img.shields.io/badge/minecraft-1.21+-green.svg)](https://www.minecraft.net/)

## How It Works

```
┌─────────────┐     MCP      ┌─────────────┐   WebSocket   ┌─────────────┐
│   Claude    │◄────────────►│  VibeCraft  │◄─────────────►│  Minecraft  │
│  (AI Chat)  │   Protocol   │ MCP Server  │    Bridge     │ Client Mod  │
└─────────────┘              └─────────────┘               └─────────────┘
                                                                  │
                                                                  ▼
                                                           ┌─────────────┐
                                                           │  Minecraft  │
                                                           │   Server    │
                                                           └─────────────┘
```

1. You chat with Claude asking it to build something
2. Claude sends commands to the VibeCraft MCP server
3. The server forwards commands to the Fabric client mod via WebSocket
4. The client mod executes commands in Minecraft as your player

**Works with any Minecraft server** — vanilla, Paper, Spigot, or modded. WorldEdit optional.

---

## Quick Start

### Prerequisites

- **Python 3.10+** with [uv](https://github.com/astral-sh/uv) package manager
- **Java 21** (for Minecraft 1.21.x) or **Java 17** (for 1.20.x)
- **jq** for build script: `brew install jq`
- **Minecraft Java Edition** with a launcher like [Prism](https://prismlauncher.org/)

### 1. Build the Client Mod

```bash
cd client-mod
./build.sh 1.21.1    # Replace with your Minecraft version
```

Output: `build/release/vibecraft-client-0.1.0-mc1.21.1.jar`

<details>
<summary>Supported versions</summary>

| Minecraft | Java |
|-----------|------|
| 1.21.4    | 21   |
| 1.21.3    | 21   |
| 1.21.1    | 21   |
| 1.21      | 21   |
| 1.20.6    | 21   |
| 1.20.4    | 17   |
| 1.20.1    | 17   |

Run `./build.sh --list` to see all versions.
</details>

### 2. Install with Prism Launcher

1. **Create instance:** Add Instance → Select Minecraft version → OK
2. **Add Fabric:** Edit → Version → Install Loader → Fabric → OK
3. **Add Fabric API:** Mods → Download mods → Search "Fabric API" → Select → OK
4. **Add VibeCraft:** Mods → Add file → Select `vibecraft-client-*.jar`
5. **Launch** and join a world/server

### 3. Enable AI Control

In Minecraft chat:
```
/vibecraft allow
```

### 4. Install Python Dependencies

```bash
cd mcp-server
uv sync
```

### 5. Configure Claude Code

Add to `~/.claude.json`:

```json
{
  "projects": {
    "/path/to/vibecraft/agent": {
      "mcpServers": {
        "vibecraft": {
          "type": "sse",
          "url": "http://127.0.0.1:8765/sse"
        }
      }
    }
  }
}
```

### 6. Start MCP Server

```bash
cd mcp-server
./start-vibecraft.sh
```

### 7. Start Claude Code

```bash
cd agent
claude
```

You're ready! Ask Claude to build something:
> "Build me a small stone cottage"

---

## Detailed Setup

See [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for:
- Alternative launcher instructions
- Stdio mode configuration
- Troubleshooting
- WorldEdit configuration

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VIBECRAFT_CLIENT_HOST` | `127.0.0.1` | Client mod WebSocket host |
| `VIBECRAFT_CLIENT_PORT` | `8766` | Client mod WebSocket port |
| `VIBECRAFT_CLIENT_PATH` | `/vibecraft` | WebSocket path |
| `VIBECRAFT_WORLDEDIT_MODE` | `auto` | `auto`, `force`, or `off` |

### WorldEdit Mode

- **`off`** — Use vanilla `/fill` and `/setblock` commands only
- **`auto`** — Detect WorldEdit availability, fall back to vanilla
- **`force`** — Require WorldEdit, fail if not available

Set `VIBECRAFT_WORLDEDIT_MODE=off` if you don't have WorldEdit installed.

### Client Mod Commands

Run these in Minecraft:

| Command | Description |
|---------|-------------|
| `/vibecraft status` | Show bridge status |
| `/vibecraft allow` | Enable AI control |
| `/vibecraft deny` | Disable AI control |
| `/vibecraft token <value>` | Set authentication token |
| `/vibecraft port <number>` | Change WebSocket port |
| `/vibecraft restart` | Restart the bridge |

---

## Usage

Once connected, ask Claude to build things:

```
User: "Build me a small cottage near my position"
Claude: "I see these players online: Steve, Alex. Which player should I build near?"
User: "Steve"
Claude: *builds cottage using /fill and /setblock commands*
```

### Run from the Agent Folder

For the best building experience, run Claude from the `agent/` folder:

```bash
cd agent
claude
```

This folder has:
- Pre-configured `.mcp.json`
- Building skills and workflows
- Material guides and templates

---

## Troubleshooting

### "Player not found"

Make sure you're using the exact player name (case-sensitive).

### "Command dispatched" but nothing happens

The client mod might not be capturing command output. Update to the latest mod version.

### "Unknown block type"

The block doesn't exist in your Minecraft version. Use blocks from your version.

### WorldEdit commands fail

Set `VIBECRAFT_WORLDEDIT_MODE=off` if you don't have WorldEdit installed.

### Connection failed

1. Make sure Minecraft is running with the mod
2. Run `/vibecraft status` to check the bridge
3. Run `/vibecraft allow` to enable AI control
4. Check that ports match (default: 8766)

---

## Legacy Alternative: Server-Only Mode (RCON)

The client mod approach above works with any server. For **headless environments** or **server-side automation** without a Minecraft client, you can use direct RCON:

```bash
./setup-all.sh  # Starts Minecraft server in Docker with RCON
```

This is useful for CI/testing but has limitations (no multiplayer, requires server access). See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for details.

---

## Project Structure

```
vibecraft/
├── agent/                    # Run Claude here to BUILD in Minecraft
│   ├── .claude/skills/       # Building skills and workflows
│   ├── context/              # Material guides, templates
│   ├── .mcp.json             # MCP server config
│   └── CLAUDE.md             # Agent system prompt
│
├── client-mod/               # Fabric client mod (Java)
│   ├── src/                  # Mod source code
│   ├── build.gradle          # Gradle build config
│   └── README.md             # Mod-specific docs
│
├── mcp-server/               # MCP server (Python)
│   ├── src/vibecraft/        # Server source code
│   ├── server_http.py        # SSE mode entry point
│   ├── start-vibecraft.sh    # SSE mode launcher
│   └── pyproject.toml        # Python dependencies
│
└── README.md                 # This file
```

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT License - see [LICENSE](LICENSE).

## Support

- 📧 Email: [evan@amentilabs.com](mailto:evan@amentilabs.com)
- 🐛 Issues: [GitHub Issues](https://github.com/amenti-labs/vibecraft/issues)

---

**Happy building!** 🧱
