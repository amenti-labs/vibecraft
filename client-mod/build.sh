#!/bin/bash
# VibeCraft Client Mod Build Script
# Usage: ./build.sh [version]
# Examples:
#   ./build.sh           # Build for default version (1.21.11)
#   ./build.sh 1.21.4    # Build for Minecraft 1.21.4
#   ./build.sh 1.20.1    # Build for Minecraft 1.20.1
#   ./build.sh --list    # List available versions

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check for jq
if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq is required but not installed.${NC}"
    echo "Install with: brew install jq"
    exit 1
fi

VERSIONS_FILE="versions.json"

# List available versions
if [[ "$1" == "--list" ]] || [[ "$1" == "-l" ]]; then
    echo -e "${BLUE}Available Minecraft versions:${NC}"
    jq -r '.versions | keys[]' "$VERSIONS_FILE" | sort -rV
    echo ""
    echo -e "Default: ${GREEN}$(jq -r '.default' "$VERSIONS_FILE")${NC}"
    exit 0
fi

# Get version from argument or default
VERSION="${1:-$(jq -r '.default' "$VERSIONS_FILE")}"

# Check if version exists
if ! jq -e ".versions[\"$VERSION\"]" "$VERSIONS_FILE" > /dev/null 2>&1; then
    echo -e "${RED}Error: Version '$VERSION' not found in versions.json${NC}"
    echo ""
    echo "Available versions:"
    jq -r '.versions | keys[]' "$VERSIONS_FILE" | sort -rV
    exit 1
fi

# Extract version info
MC_VERSION=$(jq -r ".versions[\"$VERSION\"].minecraft_version" "$VERSIONS_FILE")
YARN_MAPPINGS=$(jq -r ".versions[\"$VERSION\"].yarn_mappings" "$VERSIONS_FILE")
LOADER_VERSION=$(jq -r ".versions[\"$VERSION\"].loader_version" "$VERSIONS_FILE")
FABRIC_VERSION=$(jq -r ".versions[\"$VERSION\"].fabric_version" "$VERSIONS_FILE")
JAVA_VERSION=$(jq -r ".versions[\"$VERSION\"].java_version" "$VERSIONS_FILE")

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  VibeCraft Client Mod Builder${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Minecraft:    ${GREEN}$MC_VERSION${NC}"
echo -e "Yarn:         $YARN_MAPPINGS"
echo -e "Fabric Loader: $LOADER_VERSION"
echo -e "Fabric API:   $FABRIC_VERSION"
echo -e "Java:         $JAVA_VERSION"
echo ""

# Update gradle.properties
echo -e "${YELLOW}Updating gradle.properties...${NC}"
cat > gradle.properties << EOF
org.gradle.jvmargs=-Xmx1G

minecraft_version=$MC_VERSION
yarn_mappings=$YARN_MAPPINGS
loader_version=$LOADER_VERSION
fabric_version=$FABRIC_VERSION
java_websocket_version=1.5.7

mod_version=0.1.0
maven_group=com.vibecraft
archives_base_name=vibecraft-client
EOF

# Clean previous build
echo -e "${YELLOW}Cleaning previous build...${NC}"
./gradlew clean --quiet

# Build
echo -e "${YELLOW}Building mod...${NC}"
./gradlew build

# Check if build succeeded
JAR_FILE="build/libs/vibecraft-client-0.1.0.jar"
if [[ -f "$JAR_FILE" ]]; then
    # Create versioned output directory
    OUTPUT_DIR="build/release"
    mkdir -p "$OUTPUT_DIR"

    # Copy with version in filename
    OUTPUT_FILE="$OUTPUT_DIR/vibecraft-client-0.1.0-mc$MC_VERSION.jar"
    cp "$JAR_FILE" "$OUTPUT_FILE"

    JAR_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Build Successful!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "Output: ${BLUE}$OUTPUT_FILE${NC}"
    echo -e "Size:   $JAR_SIZE"
    echo ""
    echo -e "Install: Copy to your Minecraft mods folder"
else
    echo -e "${RED}Build failed! JAR not found.${NC}"
    exit 1
fi
