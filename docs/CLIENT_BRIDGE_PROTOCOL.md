# VibeCraft Client Bridge Protocol (Draft)

Local WebSocket protocol between the MCP server and the Fabric client mod.

## Transport

- WebSocket over localhost (default `ws://127.0.0.1:8766/vibecraft`)
- UTF-8 JSON messages
- Request/response with `id` correlation

## Common Envelope

```json
{
  "id": "uuid-or-random",
  "type": "command.execute",
  "token": "optional-shared-secret",
  "payload": {}
}
```

Response:

```json
{
  "id": "same-id",
  "ok": true,
  "result": "free-form string or object"
}
```

Errors:

```json
{
  "id": "same-id",
  "ok": false,
  "error": "human readable error"
}
```

## Required Message Types (MVP)

### `hello`
Handshake + capabilities.

Response `result`:
```json
{
  "client": "fabric",
  "version": "0.1.0",
  "capabilities": {
    "worldedit": {
      "available": true,
      "mode": "auto",
      "fallback": "warn",
      "reason": "command_tree"
    },
    "vision": false,
    "region_snapshot": false
  }
}
```

### `command.execute`
Execute a command as the local player.

Request `payload`:
```json
{ "command": "//set stone" }
```

Response `result`:
```json
"Command dispatched"
```

Note: Commands may include a leading slash; the client should accept both `set stone` and `/set stone`.

### `server.info`
Optional. Best-effort server info (player list, time, difficulty).

Response `result`:
```json
{
  "players": "There are 1 of a max of 20 players online: player1",
  "time": "The time is 12345",
  "difficulty": "easy"
}
```

## Planned Message Types (Phase 2+)

- `player.get_state` → position, rotation, target block, biome, surface
- `world.get_region` → sparse voxel snapshot for analysis
- `vision.capture` → screenshot + depth map (binary or base64)
- `inventory.get` → player inventory + nearby containers

## Security

- Localhost bind only (no remote access)
- Shared token required (user-visible in mod UI)
- Mod UI toggle: "Allow AI Control"
