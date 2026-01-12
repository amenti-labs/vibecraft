# VibeCraft Configuration Guide

Complete reference for configuring VibeCraft MCP server.

## Table of Contents

- [Operation Modes](#operation-modes)
- [Configuration File Location](#configuration-file-location)
- [Environment Variables Reference](#environment-variables-reference)
- [Configuration Categories](#configuration-categories)
  - [Client Bridge Connection](#client-bridge-connection)
  - [Safety Settings](#safety-settings)
  - [Build Area Constraints](#build-area-constraints)
  - [Feature Flags](#feature-flags)
- [MCP Client Configuration](#mcp-client-configuration)
- [Advanced Configuration](#advanced-configuration)
- [Troubleshooting](#troubleshooting)

---

## Operation Modes

VibeCraft supports two operation modes for communicating with Minecraft:

### Client Bridge Mode (Recommended)

The **Client Bridge** is the primary and recommended mode. It uses a local WebSocket
connection to a Fabric client mod running on your Minecraft client.

```
┌─────────────────┐     WebSocket      ┌──────────────────┐
│   MCP Server    │◄──────────────────►│  Fabric Mod      │
│   (Python)      │    localhost:8766  │  (Java Client)   │
└─────────────────┘                    └────────┬─────────┘
                                                │
                                       Minecraft Client
                                                │
                                       ┌────────▼─────────┐
                                       │  Minecraft       │
                                       │  Server          │
                                       │  (any server)    │
                                       └──────────────────┘
```

**Advantages:**
- Works with **any Minecraft server** (vanilla, Paper, Fabric, etc.)
- Works in **multiplayer** without server-side setup
- WorldEdit commands work when the **server** has WorldEdit installed
- User has explicit control via in-game `/vibecraft` commands
- No RCON password management

**Requirements:**
- VibeCraft Fabric client mod installed
- Player must enable "AI Control" in the mod

### RCON Mode (Legacy/Deprecated)

The **RCON Mode** connects directly to a Minecraft server's RCON port. This mode
is deprecated and kept for backwards compatibility with existing setups.

```
┌─────────────────┐       RCON         ┌──────────────────┐
│   MCP Server    │◄──────────────────►│  Minecraft       │
│   (Python)      │    localhost:25575 │  Server          │
└─────────────────┘                    └──────────────────┘
```

**When to use RCON:**
- Server-side automation without a player client
- Headless/CI environments
- Legacy deployments

**Limitations:**
- Requires server access to configure RCON
- WorldEdit commands need manual player context wrapping
- No multiplayer support without server modifications
- Security: RCON password must be managed

### Mode Selection

VibeCraft automatically uses Client Bridge mode when configured. To use RCON mode,
set `VIBECRAFT_CLIENT_HOST` to empty and configure `VIBECRAFT_RCON_*` variables.

| Configuration | Mode Used |
|---------------|-----------|
| `VIBECRAFT_CLIENT_HOST=127.0.0.1` | Client Bridge |
| `VIBECRAFT_CLIENT_HOST=` + `VIBECRAFT_RCON_HOST=...` | RCON (Legacy) |

**Recommendation:** Use Client Bridge mode for all new deployments.

---

## Configuration File Location

VibeCraft uses environment variables loaded from a `.env` file.

**Location**: `/path/to/vibecraft/mcp-server/.env`

Create this file if it doesn't exist:
```bash
cd mcp-server
cp .env.example .env  # If you have an example file
# OR create from scratch:
touch .env
```

---

## Environment Variables Reference

### Quick Reference Table

| Variable | Type | Default | Required | Description |
|----------|------|---------|----------|-------------|
| `VIBECRAFT_CLIENT_HOST` | string | `127.0.0.1` | Yes | Client bridge host |
| `VIBECRAFT_CLIENT_PORT` | integer | `8766` | Yes | Client bridge port |
| `VIBECRAFT_CLIENT_PATH` | string | `/vibecraft` | Yes | WebSocket path |
| `VIBECRAFT_CLIENT_TOKEN` | string | - | No | Client bridge auth token |
| `VIBECRAFT_CLIENT_TIMEOUT` | integer | `10` | No | Client bridge timeout (seconds) |
| `VIBECRAFT_CLIENT_USE_SSL` | boolean | `false` | No | Use TLS for the bridge |
| `VIBECRAFT_WORLDEDIT_MODE` | string | `auto` | No | WorldEdit mode: auto, force, off |
| `VIBECRAFT_WORLDEDIT_FALLBACK` | string | `warn` | No | When WE unavailable: warn, disable, auto |
| `VIBECRAFT_ENABLE_SAFETY_CHECKS` | boolean | `true` | No | Enable command validation |
| `VIBECRAFT_ALLOW_DANGEROUS_COMMANDS` | boolean | `true` | No | Allow potentially destructive commands |
| `VIBECRAFT_MAX_COMMAND_LENGTH` | integer | `1000` | No | Maximum command length |
| `VIBECRAFT_BUILD_MIN_X` | integer | - | No | Minimum X coordinate for builds |
| `VIBECRAFT_BUILD_MAX_X` | integer | - | No | Maximum X coordinate for builds |
| `VIBECRAFT_BUILD_MIN_Y` | integer | - | No | Minimum Y coordinate for builds |
| `VIBECRAFT_BUILD_MAX_Y` | integer | - | No | Maximum Y coordinate for builds |
| `VIBECRAFT_BUILD_MIN_Z` | integer | - | No | Minimum Z coordinate for builds |
| `VIBECRAFT_BUILD_MAX_Z` | integer | - | No | Maximum Z coordinate for builds |
| `VIBECRAFT_ENABLE_VERSION_DETECTION` | boolean | `true` | No | Auto-detect WorldEdit version |
| `VIBECRAFT_ENABLE_COMMAND_LOGGING` | boolean | `true` | No | Log all executed commands |

> **Note:** RCON-based configuration is deprecated. Some legacy examples below still mention
> `VIBECRAFT_RCON_*` values for the old server mode.

---

## Configuration Categories

### Client Bridge Connection

Configure the local WebSocket bridge provided by the Fabric client mod.

```bash
# Client Bridge
VIBECRAFT_CLIENT_HOST=127.0.0.1
VIBECRAFT_CLIENT_PORT=8766
VIBECRAFT_CLIENT_PATH=/vibecraft
VIBECRAFT_CLIENT_TOKEN=your_token_here
VIBECRAFT_CLIENT_TIMEOUT=10
VIBECRAFT_CLIENT_USE_SSL=false
VIBECRAFT_WORLDEDIT_MODE=auto
VIBECRAFT_WORLDEDIT_FALLBACK=warn
```

**Setup Checklist**:
1. ✅ Install and launch the VibeCraft Fabric client mod
2. ✅ Enable "AI Control" in the mod UI
3. ✅ Copy the bridge token into `.env`
4. ✅ Test connection: `uv run python -m src.vibecraft.server`

**Common Issues**:
- **Connection refused** → Client mod not running or wrong port
- **Authentication failed** → Token mismatch
- **Timeout** → Increase `VIBECRAFT_CLIENT_TIMEOUT`

---

### Safety Settings

Control command validation and safety checks.

```bash
# Safety Settings
VIBECRAFT_ENABLE_SAFETY_CHECKS=true      # Enable input validation
VIBECRAFT_ALLOW_DANGEROUS_COMMANDS=true  # Allow //regen, //delchunks, etc.
VIBECRAFT_MAX_COMMAND_LENGTH=1000        # Max characters per command
```

**Safety Levels**:

**Maximum Safety** (Recommended for public servers):
```bash
VIBECRAFT_ENABLE_SAFETY_CHECKS=true
VIBECRAFT_ALLOW_DANGEROUS_COMMANDS=false
VIBECRAFT_MAX_COMMAND_LENGTH=500
VIBECRAFT_BUILD_MIN_X=0
VIBECRAFT_BUILD_MAX_X=1000
VIBECRAFT_BUILD_MIN_Y=0
VIBECRAFT_BUILD_MAX_Y=256
VIBECRAFT_BUILD_MIN_Z=0
VIBECRAFT_BUILD_MAX_Z=1000
```

**Moderate Safety** (Default):
```bash
VIBECRAFT_ENABLE_SAFETY_CHECKS=true
VIBECRAFT_ALLOW_DANGEROUS_COMMANDS=true  # AI can use //regen, //delchunks
VIBECRAFT_MAX_COMMAND_LENGTH=1000
# No build area constraints
```

**No Safety** (Development/testing only):
```bash
VIBECRAFT_ENABLE_SAFETY_CHECKS=false
VIBECRAFT_ALLOW_DANGEROUS_COMMANDS=true
VIBECRAFT_MAX_COMMAND_LENGTH=10000
```

---

### Build Area Constraints

Optional: Restrict builds to a specific region.

```bash
# Optional: Build Area Constraints
VIBECRAFT_BUILD_MIN_X=0
VIBECRAFT_BUILD_MAX_X=1000
VIBECRAFT_BUILD_MIN_Y=-64    # Minecraft 1.18+ bedrock level
VIBECRAFT_BUILD_MAX_Y=319    # Minecraft 1.18+ build limit
VIBECRAFT_BUILD_MIN_Z=0
VIBECRAFT_BUILD_MAX_Z=1000
```

**When to Use**:
- ✅ Public servers (prevent builds in wrong area)
- ✅ Protected regions (keep AI builds in designated zone)
- ✅ Testing (limit scope of experiments)

**When NOT to Use**:
- ❌ Single-player worlds
- ❌ Private servers with trusted AI operators
- ❌ Creative mode testing

**Example Scenarios**:

**Spawn Protection**:
```bash
# Keep builds away from spawn (0,0)
VIBECRAFT_BUILD_MIN_X=500
VIBECRAFT_BUILD_MAX_X=2000
VIBECRAFT_BUILD_MIN_Z=500
VIBECRAFT_BUILD_MAX_Z=2000
```

**Creative Plot**:
```bash
# Restrict to a 256x256 plot
VIBECRAFT_BUILD_MIN_X=1000
VIBECRAFT_BUILD_MAX_X=1256
VIBECRAFT_BUILD_MIN_Y=64
VIBECRAFT_BUILD_MAX_Y=128
VIBECRAFT_BUILD_MIN_Z=1000
VIBECRAFT_BUILD_MAX_Z=1256
```

---

### Feature Flags

Enable/disable optional features.

```bash
# Feature Flags
VIBECRAFT_ENABLE_VERSION_DETECTION=true  # Auto-detect WorldEdit version
VIBECRAFT_ENABLE_COMMAND_LOGGING=true    # Log commands to file
```

**Version Detection**:
- Detects WorldEdit version on startup
- Helps diagnose compatibility issues
- Minimal performance impact

**Command Logging**:
- Logs all executed commands to `logs/vibecraft_*.log`
- Useful for debugging and auditing
- Slight performance overhead

---

## MCP Client Configuration

Configure VibeCraft in your MCP client (Claude Code, Claude Desktop, Cursor).

### Claude Code

**Location**: `.claude/mcp.json` in your project

```json
{
  "mcpServers": {
    "vibecraft": {
      "command": "uv",
      "args": ["run", "python", "-m", "src.vibecraft.server"],
      "cwd": "/absolute/path/to/vibecraft/mcp-server",
      "env": {
        "VIBECRAFT_CLIENT_HOST": "127.0.0.1",
        "VIBECRAFT_CLIENT_PORT": "8766",
        "VIBECRAFT_CLIENT_PATH": "/vibecraft",
        "VIBECRAFT_CLIENT_TOKEN": "your_token_here"
      }
    }
  }
}
```

**Important**:
- Use **absolute paths** for `cwd`
- Include client bridge settings in `env` (overrides .env file)
- Restart Claude Code after changes

### Claude Desktop

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "vibecraft": {
      "command": "uv",
      "args": ["run", "python", "-m", "src.vibecraft.server"],
      "cwd": "/absolute/path/to/vibecraft/mcp-server",
      "env": {
        "VIBECRAFT_CLIENT_HOST": "127.0.0.1",
        "VIBECRAFT_CLIENT_PORT": "8766",
        "VIBECRAFT_CLIENT_PATH": "/vibecraft",
        "VIBECRAFT_CLIENT_TOKEN": "your_token_here"
      }
    }
  }
}
```

Restart Claude Desktop after editing.

### Cursor

**Location**: `.cursor/mcp.json` in your project

```json
{
  "mcpServers": {
    "vibecraft": {
      "command": "uv",
      "args": ["run", "python", "-m", "src.vibecraft.server"],
      "cwd": "/absolute/path/to/vibecraft/mcp-server",
      "env": {
        "VIBECRAFT_CLIENT_HOST": "127.0.0.1",
        "VIBECRAFT_CLIENT_PORT": "8766",
        "VIBECRAFT_CLIENT_PATH": "/vibecraft",
        "VIBECRAFT_CLIENT_TOKEN": "your_token_here"
      }
    }
  }
}
```

---

## Advanced Configuration

### Multiple Clients

Connect to multiple Minecraft clients by running the Fabric mod with different ports:

```json
{
  "mcpServers": {
    "vibecraft-creative": {
      "command": "uv",
      "args": ["run", "python", "-m", "src.vibecraft.server"],
      "cwd": "/path/to/vibecraft/mcp-server",
      "env": {
        "VIBECRAFT_CLIENT_HOST": "127.0.0.1",
        "VIBECRAFT_CLIENT_PORT": "8766",
        "VIBECRAFT_CLIENT_PATH": "/vibecraft",
        "VIBECRAFT_CLIENT_TOKEN": "creative_token"
      }
    },
    "vibecraft-survival": {
      "command": "uv",
      "args": ["run", "python", "-m", "src.vibecraft.server"],
      "cwd": "/path/to/vibecraft/mcp-server",
      "env": {
        "VIBECRAFT_CLIENT_HOST": "127.0.0.1",
        "VIBECRAFT_CLIENT_PORT": "8767",
        "VIBECRAFT_CLIENT_PATH": "/vibecraft",
        "VIBECRAFT_CLIENT_TOKEN": "survival_token"
      }
    }
  }
}
```

### Remote Multiplayer Servers

Connect to a remote Minecraft server by joining it in the client. No extra MCP configuration
is required beyond the local client bridge.

**Security Considerations**:
- Keep the bridge bound to localhost
- Use a strong token and keep it private
- Disable "AI Control" when not in use

### Custom Python Environment

Use a specific Python version or virtualenv:

```json
{
  "mcpServers": {
    "vibecraft": {
      "command": "/usr/bin/python3.11",  // Specific Python
      "args": ["-m", "src.vibecraft.server"],
      "cwd": "/path/to/vibecraft/mcp-server",
      "env": {
        // ... client bridge config
      }
    }
  }
}
```

---

## Troubleshooting

### Configuration Not Loading

**Problem**: Changes to `.env` not taking effect

**Solutions**:
1. Restart MCP client (Claude Code/Desktop/Cursor)
2. Check `.env` file is in `mcp-server/` directory (not project root)
3. Verify no syntax errors in `.env` (no quotes, no spaces around `=`)
4. Check MCP client config overrides (client `env` takes precedence)

### RCON Connection Failed

**Problem**: "Failed to connect to Minecraft server"

**Debug Steps**:
```bash
# 1. Verify Minecraft server is running
# Check server logs

# 2. Test RCON with mcrcon tool
brew install mcrcon  # macOS
# or: apt-get install mcrcon  # Linux
mcrcon -H 127.0.0.1 -P 25575 -p your_password "list"

# 3. Check server.properties
grep rcon server.properties
# Should show:
# enable-rcon=true
# rcon.port=25575
# rcon.password=your_password

# 4. Check firewall
telnet 127.0.0.1 25575
# Should connect (Ctrl+C to exit)
```

### Commands Not Working

**Problem**: Commands execute but nothing happens in Minecraft

**Solutions**:
1. Verify WorldEdit is installed: `/version WorldEdit` in Minecraft
2. Check you have operator permissions: `/op YourUsername`
3. Use console-compatible syntax: `//pos1 X,Y,Z` (comma-separated!)
4. Some commands require player context (use alternatives from docs)

### Permission Errors

**Problem**: "You don't have permission to use this command"

**Solutions**:
1. Give yourself operator status: `/op YourUsername`
2. Check WorldEdit permissions in `plugins/WorldEdit/config.yml`
3. Verify the player running the client mod has admin privileges

---

## Configuration Best Practices

### Security

✅ **DO**:
- Use strong bridge tokens (16+ random characters)
- Keep `.env` out of version control (add to `.gitignore`)
- Use environment-specific `.env` files (.env.local, .env.production)
- Rotate bridge tokens periodically
- Use build area constraints on public servers

❌ **DON'T**:
- Commit `.env` to git
- Share tokens in screenshots/logs
- Use default tokens
- Disable safety checks on public servers

### Performance

✅ **DO**:
- Use local connections when possible (127.0.0.1)
- Set reasonable timeouts (10-30 seconds)
- Enable command logging for debugging

❌ **DON'T**:
- Use very short timeouts (< 5 seconds) for large builds
- Disable version detection (minimal overhead)

### Development vs Production

**Development**:
```bash
# Liberal settings for testing
VIBECRAFT_ENABLE_SAFETY_CHECKS=true
VIBECRAFT_ALLOW_DANGEROUS_COMMANDS=true
VIBECRAFT_ENABLE_COMMAND_LOGGING=true
# No build constraints
```

**Production**:
```bash
# Strict settings for public server
VIBECRAFT_ENABLE_SAFETY_CHECKS=true
VIBECRAFT_ALLOW_DANGEROUS_COMMANDS=false
VIBECRAFT_MAX_COMMAND_LENGTH=500
VIBECRAFT_BUILD_MIN_X=1000
VIBECRAFT_BUILD_MAX_X=2000
# ... full build area constraints
VIBECRAFT_ENABLE_COMMAND_LOGGING=true
```

---

## Example Configurations

### Single-Player Creative

```bash
# .env - Single-player creative (local)
VIBECRAFT_CLIENT_HOST=127.0.0.1
VIBECRAFT_CLIENT_PORT=8766
VIBECRAFT_CLIENT_PATH=/vibecraft
VIBECRAFT_CLIENT_TOKEN=creative_mode_token

VIBECRAFT_ENABLE_SAFETY_CHECKS=true
VIBECRAFT_ALLOW_DANGEROUS_COMMANDS=true  # Allow //regen, etc.
VIBECRAFT_MAX_COMMAND_LENGTH=1000

# No build constraints (entire world available)

VIBECRAFT_ENABLE_VERSION_DETECTION=true
VIBECRAFT_ENABLE_COMMAND_LOGGING=true
```

### Public Creative Server

```bash
# .env - Public server with build plots
VIBECRAFT_CLIENT_HOST=127.0.0.1
VIBECRAFT_CLIENT_PORT=8766
VIBECRAFT_CLIENT_PATH=/vibecraft
VIBECRAFT_CLIENT_TOKEN=super_secure_random_token_here

VIBECRAFT_ENABLE_SAFETY_CHECKS=true
VIBECRAFT_ALLOW_DANGEROUS_COMMANDS=false  # Block //regen, //delchunks
VIBECRAFT_MAX_COMMAND_LENGTH=500

# Restrict to creative build area (plot system)
VIBECRAFT_BUILD_MIN_X=5000
VIBECRAFT_BUILD_MAX_X=10000
VIBECRAFT_BUILD_MIN_Y=0
VIBECRAFT_BUILD_MAX_Y=256
VIBECRAFT_BUILD_MIN_Z=5000
VIBECRAFT_BUILD_MAX_Z=10000

VIBECRAFT_ENABLE_VERSION_DETECTION=true
VIBECRAFT_ENABLE_COMMAND_LOGGING=true
```

### Remote Development Server

```bash
# .env - Remote server joined from local client
VIBECRAFT_CLIENT_HOST=127.0.0.1
VIBECRAFT_CLIENT_PORT=8766
VIBECRAFT_CLIENT_PATH=/vibecraft
VIBECRAFT_CLIENT_TOKEN=remote_dev_token

VIBECRAFT_ENABLE_SAFETY_CHECKS=true
VIBECRAFT_ALLOW_DANGEROUS_COMMANDS=true
VIBECRAFT_MAX_COMMAND_LENGTH=1000

# No build constraints

VIBECRAFT_ENABLE_VERSION_DETECTION=true
VIBECRAFT_ENABLE_COMMAND_LOGGING=true
```

---

## Related Documentation

- [README.md](../README.md) - Quick start guide
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Development setup
- [RCON Password Setup](./RCON_PASSWORD_SETUP.md) - Secure password management

---

**Last Updated**: November 9, 2025
**Version**: 1.0.0
