#!/bin/bash
# install.sh
# Sets up App-Forge as a Claude Code plugin

set -e

FORGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo "${BOLD}App-Forge Plugin Installer${NC}"
echo "--------------------------"
echo "Directory: $FORGE_DIR"
echo ""

# 1. Verify directory structure
echo "${BOLD}1. Directory structure${NC}"
for dir in agents refs references templates data commands; do
  if [ ! -d "$FORGE_DIR/$dir" ]; then
    mkdir -p "$FORGE_DIR/$dir"
    echo "   ${GREEN}Created${NC} $dir/"
  else
    echo "   ${GREEN}OK${NC}      $dir/"
  fi
done
echo ""

# 2. Verify plugin manifest
echo "${BOLD}2. Plugin manifest${NC}"
if [ -f "$FORGE_DIR/.claude-plugin/plugin.json" ]; then
  echo "   ${GREEN}OK${NC}      .claude-plugin/plugin.json"
else
  echo "   MISSING .claude-plugin/plugin.json"
  exit 1
fi
echo ""

# 3. Summary
echo "${BOLD}3. Summary${NC}"
echo "   Agents:     $(ls "$FORGE_DIR/agents/"*.md 2>/dev/null | wc -l | tr -d ' ')"
echo "   Commands:   $(ls "$FORGE_DIR/commands/"*.md 2>/dev/null | wc -l | tr -d ' ')"
echo "   References: $(ls "$FORGE_DIR/references/"*.md 2>/dev/null | wc -l | tr -d ' ')"
echo "   Templates:  $(ls -d "$FORGE_DIR/templates/"*/ 2>/dev/null | wc -l | tr -d ' ')"
echo "   Data:       $(ls "$FORGE_DIR/data/"*.json 2>/dev/null | wc -l | tr -d ' ')"
echo ""

# 4. Ref cloning instructions
echo "${BOLD}4. Reference libraries${NC}"
if [ -z "$(ls -A "$FORGE_DIR/refs/" 2>/dev/null)" ]; then
  echo "   refs/ is empty. Clone library sources for full functionality:"
  echo ""
  echo "   cd $FORGE_DIR/refs"
  echo "   git clone --depth 1 https://github.com/pacocoursey/cmdk.git"
  echo "   git clone --depth 1 https://github.com/jamiebuilds/tinykeys.git"
  echo "   git clone --depth 1 https://github.com/tauri-apps/tauri.git tauri-v2"
  echo "   git clone --depth 1 https://github.com/tauri-apps/plugins-workspace.git tauri-v2/plugins"
  echo "   git clone --depth 1 https://github.com/nicolo-ribaudo/tauri-docs.git tauri-api-js"
  echo "   git clone --depth 1 https://github.com/serwist/serwist.git"
  echo "   git clone --depth 1 https://github.com/nicolo-ribaudo/workbox.git"
  echo "   git clone --depth 1 https://github.com/motiondivision/motion.git framer-motion"
  echo ""
else
  echo "   ${GREEN}OK${NC}      refs/ has $(ls "$FORGE_DIR/refs/" | wc -l | tr -d ' ') libraries"
fi
echo ""

echo "${BOLD}App-Forge installed.${NC}"
echo "Enable in settings.json: \"app-forge@local-desktop-app-uploads\": true"
echo ""
