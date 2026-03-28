#!/bin/bash
# install.sh
# Sets up Swift-Pro as a Claude Code skill plugin

set -e

SWIFT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo "${BOLD}Swift-Pro Plugin Installer${NC}"
echo "--------------------------"
echo "Directory: $SWIFT_DIR"
echo ""

# 1. Verify directory structure
echo "${BOLD}1. Directory structure${NC}"
for dir in agents refs references templates commands hooks data; do
  if [ ! -d "$SWIFT_DIR/$dir" ]; then
    mkdir -p "$SWIFT_DIR/$dir"
    echo "   ${GREEN}Created${NC} $dir/"
  else
    echo "   ${GREEN}OK${NC}      $dir/"
  fi
done
echo ""

# 2. Check XcodeBuildMCP
echo "${BOLD}2. XcodeBuildMCP check${NC}"
if command -v npx &> /dev/null; then
  echo "   ${GREEN}OK${NC}      npx available (needed for XcodeBuildMCP)"
else
  echo "   ${YELLOW}WARN${NC}    npx not found. Install Node.js for XcodeBuildMCP support."
fi
echo ""

# 3. Install mode
INSTALL_MODE="local"
if [ "$1" = "--global" ]; then
  INSTALL_MODE="global"
fi

if [ "$INSTALL_MODE" = "global" ]; then
  echo "${BOLD}3. Global install${NC}"
  mkdir -p ~/.claude
  ln -sfn "$SWIFT_DIR" ~/.claude/swift-pro
  echo "   ${GREEN}Linked${NC} ~/.claude/swift-pro -> $SWIFT_DIR"

  mkdir -p ~/.claude/commands
  # Agent commands
  for agent in "$SWIFT_DIR"/agents/*.md; do
    name=$(basename "$agent" .md)
    case "$name" in
      swift-architect)         cmd="swift" ;;
      swiftui-builder)         cmd="view" ;;
      swiftdata-engineer)      cmd="model" ;;
      concurrency-specialist)  cmd="async" ;;
      platform-integrator)     cmd="integrate" ;;
      networking-engineer)     cmd="network" ;;
      appkit-specialist)       cmd="appkit" ;;
      webview-bridge)          cmd="bridge" ;;
      test-engineer)           cmd="test" ;;
      *)                       cmd="$name" ;;
    esac
    ln -sfn "$agent" ~/.claude/commands/"$cmd".md
    echo "   ${GREEN}Command${NC} /$cmd -> agents/$name.md"
  done
  # Workflow commands
  for cmdfile in "$SWIFT_DIR"/commands/*.md; do
    name=$(basename "$cmdfile" .md)
    ln -sfn "$cmdfile" ~/.claude/commands/"$name".md
    echo "   ${GREEN}Command${NC} /$name -> commands/$name.md"
  done
else
  echo "${BOLD}3. Local install${NC}"
  echo "   Run Claude Code from $SWIFT_DIR to use the plugin."
  echo "   Or use --global to install for all projects."
fi
echo ""

# 4. Summary
echo "${BOLD}4. Summary${NC}"
echo "   Agents:     $(ls "$SWIFT_DIR/agents/" 2>/dev/null | wc -l | tr -d ' ')"
echo "   Refs:       $(find "$SWIFT_DIR/refs/" -type f 2>/dev/null | wc -l | tr -d ' ')"
echo "   References: $(ls "$SWIFT_DIR/references/" 2>/dev/null | wc -l | tr -d ' ')"
echo "   Templates:  $(ls "$SWIFT_DIR/templates/" 2>/dev/null | wc -l | tr -d ' ')"
echo "   Commands:   $(ls "$SWIFT_DIR/commands/" 2>/dev/null | wc -l | tr -d ' ')"
echo ""
echo "Swift-Pro installed."
echo ""
echo "Next steps:"
echo "  1. Add XcodeBuildMCP if not already installed:"
echo "     claude mcp add --transport stdio XcodeBuildMCP -- npx -y xcodebuildmcp@latest"
echo "  2. Launch Claude Code from your iOS/macOS project directory"
echo "  3. Use /swift to get started"
