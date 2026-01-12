# VibeCraft Setup Guide

Complete guide to getting VibeCraft running with Claude Code or any MCP-compatible AI client.

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10+ | With [uv](https://github.com/astral-sh/uv) package manager |
| Java | 21 (MC 1.21.x) or 17 (MC 1.20.x) | For building the mod |
| Minecraft | Java Edition 1.20.1+ | With Fabric Loader |
| jq | Any | For build script: `brew install jq` |

## Step 1: Build the Client Mod

The client mod connects Minecraft to the MCP server.

### Using the Build Script (Recommended)

```bash
cd client-mod

# Build for your Minecraft version
./build.sh 1.21.1      # For Minecraft 1.21.1
./build.sh 1.21.4      # For Minecraft 1.21.4
./build.sh 1.20.1      # For Minecraft 1.20.1

# List all supported versions
./build.sh --list
```

**Output:** `build/release/vibecraft-client-0.1.0-mc<VERSION>.jar`

### Supported Minecraft Versions

| Minecraft | Java | Fabric API |
|-----------|------|------------|
| 1.21.4    | 21   | 0.119.2+1.21.4 |
| 1.21.3    | 21   | 0.118.0+1.21.3 |
| 1.21.1    | 21   | 0.116.7+1.21.1 |
| 1.21      | 21   | 0.100.0+1.21 |
| 1.20.6    | 21   | 0.97.0+1.20.6 |
| 1.20.4    | 17   | 0.97.0+1.20.4 |
| 1.20.1    | 17   | 0.92.3+1.20.1 |

### Manual Build

If you prefer not to use the build script:

1. Edit `gradle.properties` to set your version:
   ```properties
   minecraft_version=1.21.1
   yarn_mappings=1.21.1+build.3
   loader_version=0.18.1
   fabric_version=0.116.7+1.21.1
   ```

2. Build:
   ```bash
   ./gradlew clean build
   ```

3. Find jar at `build/libs/vibecraft-client-0.1.0.jar`

## Step 2: Install the Mod

### Using Prism Launcher (Recommended)

1. **Create a new instance:**
   - Click "Add Instance"
   - Select your Minecraft version (e.g., 1.21.1)
   - Name it (e.g., "VibeCraft")
   - Click "OK"

2. **Install Fabric:**
   - Select your instance
   - Click "Edit" (right side)
   - Go to "Version" tab
   - Click "Install Loader" → "Fabric"
   - Select the latest Fabric Loader version
   - Click "OK"

3. **Install Fabric API:**
   - Go to "Mods" tab
   - Click "Download mods"
   - Search for "Fabric API"
   - Click "Select mod for download"
   - Click "Review and confirm" → "OK"

4. **Install VibeCraft:**
   - Still in "Mods" tab
   - Click "Add file"
   - Select `vibecraft-client-0.1.0-mc<VERSION>.jar`
   - Or drag-and-drop the jar into the mods list

5. **Launch:**
   - Close the edit dialog
   - Click "Launch"

### Using Other Launchers

1. Install Fabric Loader for your Minecraft version
2. Download [Fabric API](https://modrinth.com/mod/fabric-api) for your version
3. Copy both jars to your `mods` folder:
   - Windows: `%APPDATA%\.minecraft\mods\`
   - macOS: `~/Library/Application Support/minecraft/mods/`
   - Linux: `~/.minecraft/mods/`

## Step 3: Install Python Dependencies

```bash
cd mcp-server
uv sync
```

This installs all Python dependencies for the MCP server.

## Step 4: Configure Claude Code

### Option A: SSE Mode (Recommended for Development)

Run the server manually in a terminal:

```bash
cd mcp-server
./start-vibecraft.sh
```

You'll see:
```
VibeCraft MCP Server (HTTP/SSE Mode)
Configuration:
  - Client Bridge: ws://127.0.0.1:8766/vibecraft
  - WorldEdit Mode: off
```

Add to your Claude Code global config (`~/.claude.json`):

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

### Option B: Stdio Mode (Simpler)

Claude launches the server automatically. Create `.mcp.json` in your project:

```json
{
  "mcpServers": {
    "vibecraft": {
      "command": "/path/to/uv",
      "args": ["run", "python", "-m", "src.vibecraft.server"],
      "cwd": "/path/to/vibecraft/mcp-server",
      "env": {
        "VIBECRAFT_CLIENT_HOST": "127.0.0.1",
        "VIBECRAFT_CLIENT_PORT": "8766",
        "VIBECRAFT_WORLDEDIT_MODE": "off"
      }
    }
  }
}
```

**Tip:** Run `which uv` to get the full path to uv.

## Step 5: Enable AI Control in Minecraft

1. Launch Minecraft with the VibeCraft mod
2. Join a server or create a singleplayer world
3. Run this command in chat:
   ```
   /vibecraft allow
   ```

This allows the MCP server to send commands to your player.

## Step 6: Start Claude Code

For the best building experience, run Claude from the agent folder:

```bash
cd agent
claude
```

The agent folder has:
- Pre-configured `.mcp.json`
- Building skills and workflows
- Material guides and templates

## Verify Connection

1. Check mod status in Minecraft:
   ```
   /vibecraft status
   ```

   Should show: `Status: Connected` and `AI Control: Enabled`

2. In Claude Code, you should see VibeCraft tools available. Try:
   ```
   What tools do you have for Minecraft?
   ```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VIBECRAFT_CLIENT_HOST` | `127.0.0.1` | Client mod WebSocket host |
| `VIBECRAFT_CLIENT_PORT` | `8766` | Client mod WebSocket port |
| `VIBECRAFT_CLIENT_PATH` | `/vibecraft` | WebSocket path |
| `VIBECRAFT_WORLDEDIT_MODE` | `auto` | `auto`, `force`, or `off` |

### WorldEdit Mode

- **`off`** — Use vanilla `/fill` and `/setblock` only
- **`auto`** — Detect WorldEdit, fall back to vanilla if unavailable
- **`force`** — Require WorldEdit, fail if not available

Set `VIBECRAFT_WORLDEDIT_MODE=off` if your server doesn't have WorldEdit.

### Client Mod Config

Config file: `config/vibecraft-client.json` (in your Minecraft folder)

```json
{
  "enabled": true,
  "host": "127.0.0.1",
  "port": 8766,
  "path": "/vibecraft",
  "allowAiControl": false,
  "token": "",
  "logCommands": false
}
```

## Troubleshooting

### "Connection refused" or "Player not found"

1. Make sure Minecraft is running with the mod
2. Run `/vibecraft status` to check the bridge
3. Run `/vibecraft allow` to enable AI control
4. Check that ports match (default: 8766)

### "Unknown block type"

The block doesn't exist in your Minecraft version. Use `search_minecraft_item()` to find valid blocks.

### WorldEdit commands fail

Set `VIBECRAFT_WORLDEDIT_MODE=off` if your server doesn't have WorldEdit.

### Build script fails

1. Install jq: `brew install jq` (macOS) or `apt install jq` (Linux)
2. Make sure you have the correct Java version
3. Run `./gradlew clean` and try again

### Mod not loading

1. Make sure Fabric Loader is installed
2. Make sure Fabric API is installed
3. Check the mod jar is in the mods folder
4. Check the game log for errors
