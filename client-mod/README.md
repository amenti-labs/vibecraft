# VibeCraft Client Mod

Fabric client mod that bridges the VibeCraft MCP server to Minecraft. Commands from Claude are executed as your player.

## Quick Start

```bash
# Build for default version (1.21.11)
./build.sh

# Build for specific Minecraft version
./build.sh 1.21.4
./build.sh 1.20.1

# List available versions
./build.sh --list
```

Output: `build/release/vibecraft-client-0.1.0-mc<VERSION>.jar`

## Build Requirements

- **Java 21** (for Minecraft 1.21.x) or **Java 17** (for 1.20.x)
- **jq** for the build script: `brew install jq`
- Gradle (included via wrapper)

## Manual Build

If you prefer not to use the build script:

```bash
# Edit gradle.properties to set your Minecraft version
# Then run:
./gradlew clean build
```

Output: `build/libs/vibecraft-client-0.1.0.jar`

## Supported Versions

| Minecraft | Java | Status |
|-----------|------|--------|
| 1.21.11   | 21   | Default |
| 1.21.4    | 21   | Supported |
| 1.21.3    | 21   | Supported |
| 1.21.1    | 21   | Supported |
| 1.21      | 21   | Supported |
| 1.20.6    | 21   | Supported |
| 1.20.4    | 17   | Supported |
| 1.20.1    | 17   | Supported |

To add a new version, edit `versions.json`.

## Install

1. Install [Fabric Loader](https://fabricmc.net/) for your Minecraft version
2. Install [Fabric API](https://modrinth.com/mod/fabric-api) mod
3. Copy `vibecraft-client-*.jar` to your mods folder
4. Launch Minecraft

## Enable AI Control

In Minecraft, run:
```
/vibecraft allow
```

This is required before the MCP server can send commands.

## Commands

| Command | Description |
|---------|-------------|
| `/vibecraft status` | Show bridge status and settings |
| `/vibecraft allow` | Enable AI control |
| `/vibecraft deny` | Disable AI control |
| `/vibecraft toggle` | Toggle AI control on/off |
| `/vibecraft token <value>` | Set authentication token |
| `/vibecraft port <number>` | Change WebSocket port |
| `/vibecraft start` | Start the bridge |
| `/vibecraft stop` | Stop the bridge |
| `/vibecraft restart` | Restart the bridge |

## Configuration

Config file: `config/vibecraft-client.json`

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

| Setting | Default | Description |
|---------|---------|-------------|
| `enabled` | `true` | Start bridge on game launch |
| `host` | `127.0.0.1` | WebSocket bind address |
| `port` | `8766` | WebSocket port |
| `path` | `/vibecraft` | WebSocket path |
| `allowAiControl` | `false` | Allow commands from MCP server |
| `token` | `""` | Authentication token (optional) |
| `logCommands` | `false` | Log executed commands |

## How It Works

1. Mod starts a WebSocket server on `ws://127.0.0.1:8766/vibecraft`
2. MCP server connects and sends commands
3. Mod executes commands as your player using `sendChatCommand()`
4. Command output is captured and returned to the MCP server

## Notes

- **Local only** — The bridge only accepts connections from localhost
- **Player permissions** — Your player must have permission to run commands
- **WorldEdit** — Works if the server has WorldEdit installed (optional)
- **Any server** — Works on vanilla, Paper, Spigot, or modded servers

## Troubleshooting

### "AI control is disabled"

Run `/vibecraft allow` in Minecraft.

### Bridge not starting

Check the game log for errors. Try `/vibecraft restart`.

### Commands not working

1. Check `/vibecraft status`
2. Ensure you have operator permissions on the server
3. Check if the command is valid for your Minecraft version

### Build errors

1. Make sure you have the correct Java version installed
2. Run `./gradlew clean` then try again
3. Check `versions.json` for correct dependency versions
