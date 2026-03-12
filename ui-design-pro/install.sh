#!/bin/bash
# install.sh
# Sets up ui-design-pro as a Claude Code plugin
#
# What this does:
#   1. Verifies directory structure
#   2. Clones reference source repos into refs/
#   3. Creates slash command symlinks
#
# Usage:
#   ./install.sh              # Local install
#   ./install.sh --global     # Global install

set -e

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo "${BOLD}UI-Design-Pro Plugin Installer${NC}"
echo "================================"
echo "Directory: ${CYAN}$PLUGIN_DIR${NC}"
echo ""

# 1. Ensure directory structure
echo "${BOLD}1. Directory structure${NC}"
for dir in agents refs examples commands scripts \
           skills/design-theory/references \
           skills/ui-engineering/references \
           examples/polymorphic-renderer \
           examples/design-token-scales \
           examples/state-matrices; do
  if [ ! -d "$PLUGIN_DIR/$dir" ]; then
    mkdir -p "$PLUGIN_DIR/$dir"
    echo "   ${GREEN}Created${NC} $dir/"
  else
    echo "   ${GREEN}OK${NC}      $dir/"
  fi
done
echo ""

# 2. Clone reference repos
echo "${BOLD}2. Cloning reference source repos${NC}"

clone_ref() {
  local repo="$1"
  local target="$2"
  local depth="${3:-1}"

  if [ -d "$PLUGIN_DIR/refs/$target" ] && [ -n "$(ls -A "$PLUGIN_DIR/refs/$target" 2>/dev/null)" ]; then
    echo "   ${GREEN}OK${NC}      refs/$target/"
  else
    echo "   ${YELLOW}Cloning${NC} $repo -> refs/$target/"
    git clone --depth "$depth" --single-branch \
      "https://github.com/$repo.git" "$PLUGIN_DIR/refs/$target" 2>/dev/null || {
      echo "   ${RED}Failed${NC}  $repo"
      return 1
    }
    # Remove .git to save space (we only need source, not history)
    rm -rf "$PLUGIN_DIR/refs/$target/.git"
    echo "   ${GREEN}Cloned${NC}  refs/$target/"
  fi
}

clone_ref "shadcn-ui/ui"                    "shadcn-ui"
clone_ref "radix-ui/primitives"             "radix-primitives"
clone_ref "radix-ui/colors"                 "radix-colors"
clone_ref "radix-ui/themes"                 "radix-ui-themes"
clone_ref "emilkowalski/vaul"               "vaul"
clone_ref "emilkowalski/sonner"             "sonner"
clone_ref "pacocoursey/cmdk"                "cmdk"
clone_ref "saadeghi/daisyui"                "daisyui"
clone_ref "motiondivision/motion"           "motion"
clone_ref "tailwindlabs/tailwindcss"        "tailwindcss"
clone_ref "argyleink/open-props"            "open-props"

echo ""

# 3. Create slash command symlinks
echo "${BOLD}3. Registering commands${NC}"
GLOBAL=""
if [[ "$1" == "--global" ]]; then
  GLOBAL="--global"
  CMD_DIR="$HOME/.claude/commands"
else
  CMD_DIR="$PLUGIN_DIR/.claude/commands"
fi

mkdir -p "$CMD_DIR"
for cmd in "$PLUGIN_DIR/commands/"*.md; do
  [ -f "$cmd" ] || continue
  name=$(basename "$cmd" .md)
  ln -sf "$cmd" "$CMD_DIR/$name.md"
  echo "   ${GREEN}Registered${NC} /$name"
done
echo ""

# 4. Summary
echo "${BOLD}Summary${NC}"
echo "   Agents:     $(ls "$PLUGIN_DIR/agents/"*.md 2>/dev/null | wc -l | tr -d ' ')"
echo "   Commands:   $(ls "$PLUGIN_DIR/commands/"*.md 2>/dev/null | wc -l | tr -d ' ')"
echo "   Refs:       $(ls -d "$PLUGIN_DIR/refs/"*/ 2>/dev/null | wc -l | tr -d ' ')"
echo "   Skills:     2 (design-theory, ui-engineering)"
echo ""
echo "${GREEN}UI-Design-Pro plugin installed.${NC}"
echo "Launch Claude Code from ${CYAN}$PLUGIN_DIR${NC} to use."
