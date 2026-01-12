#!/bin/bash
# Start VibeCraft MCP Server with HTTP/SSE Support (46 tools)

cd "$(dirname "$0")"

# Initialize pyenv if available
if command -v pyenv >/dev/null 2>&1; then
    eval "$(pyenv init -)"
fi

# Set defaults for client bridge
export VIBECRAFT_CLIENT_HOST="${VIBECRAFT_CLIENT_HOST:-127.0.0.1}"
export VIBECRAFT_CLIENT_PORT="${VIBECRAFT_CLIENT_PORT:-8766}"
export VIBECRAFT_CLIENT_PATH="${VIBECRAFT_CLIENT_PATH:-/vibecraft}"

# WorldEdit mode: auto, force, or off
# Default to "off" since most users don't have WorldEdit installed
export VIBECRAFT_WORLDEDIT_MODE="${VIBECRAFT_WORLDEDIT_MODE:-off}"

echo "Starting VibeCraft MCP Server (HTTP/SSE Mode)..."
echo "Server will run at http://127.0.0.1:8765/sse"
echo ""
echo "✨ Configuration:"
echo "  - Client Bridge: ws://${VIBECRAFT_CLIENT_HOST}:${VIBECRAFT_CLIENT_PORT}${VIBECRAFT_CLIENT_PATH}"
echo "  - WorldEdit Mode: ${VIBECRAFT_WORLDEDIT_MODE}"
echo ""
echo "✨ Features:"
echo "  - Building tools (vanilla /fill and /setblock)"
echo "  - Terrain analysis & generation"
echo "  - Furniture system with 66+ layouts"
echo "  - Multiple Claude instances can connect"
if [ "$VIBECRAFT_WORLDEDIT_MODE" != "off" ]; then
    echo "  - WorldEdit commands (if available)"
fi
echo ""
echo "Press Ctrl+C to stop"
echo ""

uv run python server_http.py --port 8765
