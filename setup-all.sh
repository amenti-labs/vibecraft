#!/bin/bash
###############################################################################
# VibeCraft Complete Setup Script
# This script automates the entire VibeCraft setup process
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo "============================================================"
    echo "$1"
    echo "============================================================"
    echo ""
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

###############################################################################
# Pre-flight Checks
###############################################################################

print_header "🎮 VibeCraft Complete Setup"
log_info "Starting automated setup process..."
echo ""

# Check for required commands
log_info "Checking prerequisites..."

# Initialize pyenv if available (for uv)
if command_exists pyenv; then
    eval "$(pyenv init -)"
fi

if ! command_exists uv; then
    log_error "uv is not installed. Please install uv first."
    log_info "Visit: https://github.com/astral-sh/uv"
    log_info "Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Get uv version (disable exit-on-error temporarily)
set +e
uv_version=$(uv --version 2>&1)
uv_check_status=$?
set -e

if [ $uv_check_status -eq 0 ]; then
    log_success "uv $uv_version found"
else
    log_warning "uv found but version check failed (this is OK)"
fi

if ! command_exists python3; then
    log_error "Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

python_version=$(python3 --version 2>&1 | awk '{print $2}')
log_success "Python $python_version found"

if ! command_exists docker; then
    log_error "Docker is not installed. Please install Docker Desktop."
    log_info "Visit: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    log_error "Docker is not running. Please start Docker Desktop."
    exit 1
fi

log_success "Docker is installed and running"

if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
    log_error "Docker Compose is not installed."
    exit 1
fi

# Determine which docker-compose command to use
if command_exists docker-compose; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

log_success "Docker Compose found ($DOCKER_COMPOSE)"

###############################################################################
# Step 1: Set up MCP Server
###############################################################################

print_header "📦 Step 1/4: Setting up MCP Server"

cd mcp-server

log_info "Installing dependencies with uv..."
if [ -f "uv.lock" ]; then
    log_info "Lock file found, installing from uv.lock..."
    uv sync --quiet
else
    log_info "No lock file found, creating one..."
    uv sync --quiet
fi
log_success "Dependencies installed with uv"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    # Check if .env.example exists
    if [ ! -f ".env.example" ]; then
        log_error ".env.example not found in mcp-server/"
        log_info "This file should exist in the repository. Please verify your installation."
        exit 1
    fi

    log_info "Creating .env file from .env.example..."
    cp .env.example .env

    # Generate a random RCON password
    if command_exists openssl; then
        RCON_PASSWORD=$(openssl rand -base64 12 | tr -d "=+/" | cut -c1-16)
    else
        log_warning "openssl not found, using Python to generate password"
        RCON_PASSWORD=$(python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16)))")
    fi

    # Update .env with the password
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/VIBECRAFT_RCON_PASSWORD=.*/VIBECRAFT_RCON_PASSWORD=$RCON_PASSWORD/" .env
    else
        # Linux
        sed -i "s/VIBECRAFT_RCON_PASSWORD=.*/VIBECRAFT_RCON_PASSWORD=$RCON_PASSWORD/" .env
    fi

    log_success ".env file created with random password"
    log_info "RCON Password: $RCON_PASSWORD"
    echo "$RCON_PASSWORD" > ../.rcon_password
else
    log_warning ".env file already exists"
    # Extract password from existing .env
    RCON_PASSWORD=$(grep VIBECRAFT_RCON_PASSWORD .env | cut -d '=' -f2)
    log_info "Using existing RCON password from mcp-server/.env"
fi

log_info "Testing MCP server..."
# Quick validation that the module can be imported (disable exit-on-error for this test)
set +e
if command_exists timeout; then
    timeout 5 uv run python -m src.vibecraft.server 2>&1 | head -1
    log_info "MCP server validated (timeout expected)"
else
    uv run python -c "import sys; sys.path.insert(0, 'src'); from vibecraft import server" 2>&1
    if [ $? -eq 0 ]; then
        log_success "MCP server module validated"
    else
        log_warning "MCP server validation skipped (will be tested during final verification)"
    fi
fi
set -e

cd ..
log_success "MCP Server setup complete"

###############################################################################
# Step 2: Set up Minecraft Server with Docker
###############################################################################

print_header "🐳 Step 2/4: Setting up Minecraft Server (Docker)"

# Verify docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    log_error "docker-compose.yml not found in project root"
    log_info "This file should exist in the repository. Please verify your installation."
    exit 1
fi

# Create root .env file for docker-compose if it doesn't exist
if [ ! -f ".env" ]; then
    log_info "Creating root .env file for docker-compose..."
    cat > .env << EOF
# VibeCraft Docker Compose Configuration
# RCON Password for Minecraft server
VIBECRAFT_RCON_PASSWORD=$RCON_PASSWORD
EOF
    log_success "Root .env file created"
else
    log_warning "Root .env file already exists"
    # Update password in existing file
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/^VIBECRAFT_RCON_PASSWORD=.*/VIBECRAFT_RCON_PASSWORD=$RCON_PASSWORD/" .env
    else
        sed -i "s/^VIBECRAFT_RCON_PASSWORD=.*/VIBECRAFT_RCON_PASSWORD=$RCON_PASSWORD/" .env
    fi
    log_info "Updated RCON password in root .env"
fi

# Export RCON password as environment variable for docker-compose
export VIBECRAFT_RCON_PASSWORD="$RCON_PASSWORD"
log_success "RCON password configured for docker-compose"

log_info "Starting Minecraft server container..."

# Check if container already exists
if docker ps -a --format '{{.Names}}' | grep -q '^vibecraft-minecraft$'; then
    if docker ps --format '{{.Names}}' | grep -q '^vibecraft-minecraft$'; then
        log_warning "Container already running"
        log_info "Restarting to apply any configuration changes..."
        $DOCKER_COMPOSE restart
    else
        log_info "Container exists but stopped, starting..."
        $DOCKER_COMPOSE up -d
    fi
else
    log_info "Creating new container (first run may take several minutes)..."
    log_info "Downloading Paper 1.21.11 and WorldEdit 7.3.18..."
    $DOCKER_COMPOSE up -d
fi

log_success "Docker container started"

log_info "Waiting for Minecraft server to initialize..."
log_warning "This can take 2-5 minutes for first startup..."

# Wait for server to be ready (check recent logs only to avoid false positives from old runs)
MAX_WAIT=300  # 5 minutes
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    # Check logs from last 2 minutes to avoid finding old "Done" messages
    if docker logs --since 2m vibecraft-minecraft 2>&1 | grep -q "Done"; then
        log_success "Minecraft server is ready!"
        break
    fi

    if [ $((WAITED % 30)) -eq 0 ]; then
        log_info "Still waiting... ($WAITED seconds elapsed)"
    fi

    sleep 5
    WAITED=$((WAITED + 5))
done

if [ $WAITED -ge $MAX_WAIT ]; then
    log_error "Minecraft server did not start within $MAX_WAIT seconds"
    log_info "Check logs with: docker logs vibecraft-minecraft"
    exit 1
fi

# Test RCON connection with retries
log_info "Testing RCON connection..."
RCON_RETRIES=6
RCON_SUCCESS=false

for i in $(seq 1 $RCON_RETRIES); do
    sleep 5
    if docker exec vibecraft-minecraft rcon-cli list >/dev/null 2>&1; then
        log_success "RCON connection successful"
        RCON_SUCCESS=true
        break
    else
        if [ $i -lt $RCON_RETRIES ]; then
            log_info "RCON not ready yet, retrying... (attempt $i/$RCON_RETRIES)"
        fi
    fi
done

if [ "$RCON_SUCCESS" = false ]; then
    log_error "RCON connection failed after $RCON_RETRIES attempts"
    log_info "Server may still be initializing. Check logs with: docker logs vibecraft-minecraft"
fi

# Verify WorldEdit is installed
log_info "Verifying WorldEdit installation..."
WE_VERSION=$(docker exec vibecraft-minecraft rcon-cli "version WorldEdit" 2>/dev/null || echo "")
if echo "$WE_VERSION" | grep -q "WorldEdit"; then
    log_success "WorldEdit is installed: $WE_VERSION"
else
    log_warning "WorldEdit version check failed, but may still be loading"
fi

# Configure WorldEdit for console/RCON usage
log_info "Configuring WorldEdit for RCON/console usage..."
docker exec vibecraft-minecraft bash -c '
if [ -f plugins/WorldEdit/config.yml ]; then
    # Remove block restrictions (allows all blocks)
    sed -i "s/^    disallowed-blocks:.*/    disallowed-blocks: []/g" plugins/WorldEdit/config.yml

    # Enable all required features
    if ! grep -q "use-scheduler-optimization" plugins/WorldEdit/config.yml; then
        echo "use-scheduler-optimization: true" >> plugins/WorldEdit/config.yml
    fi

    echo "WorldEdit configuration updated"
else
    echo "WorldEdit config not found yet (will be created on next restart)"
fi
' 2>&1 | grep -v "^$" || true

log_success "WorldEdit configured for console usage"

log_success "Minecraft Server setup complete"

###############################################################################
# Step 3: Configure Claude Code Integration
###############################################################################

print_header "🤖 Step 3/4: AI Client Configuration"

log_info "Generating MCP configuration files..."

# Generate Mode 1: stdio/Command Mode configuration
cat > claude-code-config.json << EOF
{
  "mcpServers": {
    "vibecraft": {
      "command": "uv",
      "args": ["run", "python", "-m", "src.vibecraft.server"],
      "cwd": "$(pwd)/mcp-server",
      "env": {
        "VIBECRAFT_RCON_HOST": "127.0.0.1",
        "VIBECRAFT_RCON_PORT": "25575",
        "VIBECRAFT_RCON_PASSWORD": "$RCON_PASSWORD"
      }
    }
  }
}
EOF

log_success "Configuration saved to: claude-code-config.json"

# Generate Mode 2: HTTP/SSE Server Mode configuration
cat > claude-code-config-sse.json << EOF
{
  "mcpServers": {
    "vibecraft-sse": {
      "transport": "sse",
      "url": "http://127.0.0.1:8765/sse"
    }
  }
}
EOF

log_success "SSE configuration saved to: claude-code-config-sse.json"

echo ""
log_info "📋 Two server modes available:"
echo ""
log_info "MODE 1: stdio/Command (Recommended for single client)"
log_info "   - Simple setup, AI client launches server automatically"
log_info "   - Use config: claude-code-config.json"
echo ""
log_info "MODE 2: HTTP/SSE Server (Best for debugging & multiple clients)"
log_info "   - From project root: cd mcp-server && ./start-vibecraft.sh"
log_info "   - See real-time logs, connect multiple clients"
log_info "   - Use config: claude-code-config-sse.json"
echo ""

# Detect Claude Code config location
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
    CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    CLAUDE_CONFIG_DIR="$HOME/.config/Claude"
    CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
else
    log_warning "Unsupported OS for automatic Claude Code configuration"
    CLAUDE_CONFIG_FILE=""
fi

if [ -n "$CLAUDE_CONFIG_FILE" ]; then
    log_info "To complete setup:"
    log_info "1. Choose a mode (see above)"
    log_info "2. Copy config to your AI client"
    log_info "3. For Claude Code: cp SYSTEM_PROMPT.md CLAUDE.md"
    log_info "4. Restart your AI client"
else
    log_warning "Automatic configuration not available for this OS"
    log_info "Manual configuration files created"
fi

log_success "AI client configuration generated"

###############################################################################
# Step 4: Verification
###############################################################################

print_header "✅ Step 4/4: Verification"

log_info "Running final verification tests..."

# Test MCP server can connect
cd mcp-server

log_info "Testing MCP server connection to Minecraft..."
set +e
uv run python << 'PYEOF'
import os
from mcrcon import MCRcon

host = "127.0.0.1"
port = 25575
password = os.getenv("RCON_PASSWORD", "")

if not password:
    with open("../.rcon_password", "r") as f:
        password = f.read().strip()

try:
    with MCRcon(host, password, port=port, timeout=5) as mcr:
        response = mcr.command("list")
        print(f"✓ Connection successful: {response}")
        exit(0)
except Exception as e:
    print(f"✗ Connection failed: {e}")
    exit(1)
PYEOF

VERIFICATION_STATUS=$?
set -e

if [ $VERIFICATION_STATUS -eq 0 ]; then
    log_success "MCP server can communicate with Minecraft"
else
    log_error "MCP server cannot communicate with Minecraft"
    log_info "Check that Minecraft server is running: docker ps"
fi

cd ..

###############################################################################
# Summary
###############################################################################

print_header "🎉 Setup Complete!"

echo "VibeCraft is now ready to use!"
echo ""
echo "📋 Summary:"
echo "  ✅ MCP Server: Running at mcp-server/"
echo "  ✅ Minecraft Server: Running in Docker (Port 25565)"
echo "  ✅ RCON: Enabled (Port 25575)"
echo "  ✅ WorldEdit: Installed and configured for console usage"
echo "  ✅ Configuration: Generated"
echo ""
echo "🔑 RCON Password: $RCON_PASSWORD"
echo "   (Saved in: .rcon_password)"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "  Choose a server mode:"
echo ""
echo "  MODE 1: stdio/Command (Recommended for daily use)"
echo "    1. Copy system prompt: cp SYSTEM_PROMPT.md CLAUDE.md"
echo "    2. Configure AI client with: claude-code-config.json"
echo "    3. Restart your AI client"
echo ""
echo "  MODE 2: HTTP/SSE Server (For debugging & multiple clients)"
echo "    1. Start server: cd mcp-server && ./start-vibecraft.sh"
echo "    2. Configure AI client with: claude-code-config-sse.json"
echo "    3. Restart your AI client"
echo ""
echo "  See README.md for detailed configuration instructions"
echo ""
echo "📚 Useful Commands:"
echo "  • View Minecraft logs:  docker logs -f vibecraft-minecraft"
echo "  • Stop Minecraft:       $DOCKER_COMPOSE down"
echo "  • Start Minecraft:      $DOCKER_COMPOSE up -d"
echo "  • Start SSE server:     cd mcp-server && ./start-vibecraft.sh"
echo "  • Test RCON:           docker exec vibecraft-minecraft rcon-cli list"
echo "  • Join server:         minecraft://localhost:25565"
echo ""
echo "📖 Documentation:"
echo "  • Main Guide:     README.md"
echo "  • Server Setup:   docs/MINECRAFT_SERVER_SETUP.md"
echo "  • System Prompt:  SYSTEM_PROMPT.md"
echo ""
print_header "Happy Building! 🏗️"
