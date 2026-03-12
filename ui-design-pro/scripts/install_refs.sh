#!/usr/bin/env bash
# install_refs.sh
# Clones all reference source repos into refs/
# Can be run independently of install.sh to update or re-clone refs.
#
# Usage:
#   ./scripts/install_refs.sh           # Clone all missing refs
#   ./scripts/install_refs.sh --update  # Re-clone even if already present

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REFS_DIR="$PLUGIN_DIR/refs"
UPDATE="${1:-}"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

mkdir -p "$REFS_DIR"

clone_ref() {
  local repo="$1"
  local target="$2"
  local target_dir="$REFS_DIR/$target"

  if [[ -d "$target_dir" ]] && [[ -n "$(ls -A "$target_dir" 2>/dev/null)" ]] && [[ "$UPDATE" != "--update" ]]; then
    echo "   ${GREEN}OK${NC}      refs/$target/"
    return 0
  fi

  if [[ -d "$target_dir" ]] && [[ "$UPDATE" == "--update" ]]; then
    echo "   ${YELLOW}Removing${NC} refs/$target/ (updating)"
    rm -rf "$target_dir"
  fi

  echo "   ${YELLOW}Cloning${NC} https://github.com/$repo -> refs/$target/"
  if git clone --depth 1 --single-branch \
      "https://github.com/$repo.git" "$target_dir" 2>/dev/null; then
    rm -rf "$target_dir/.git"
    echo "   ${GREEN}Cloned${NC}  refs/$target/"
  else
    echo "   ${RED}Failed${NC}  $repo (check network connection)"
    return 1
  fi
}

echo ""
echo "${BOLD}Reference Repo Installer${NC}"
echo "========================"
echo "Target: ${CYAN}$REFS_DIR${NC}"
if [[ "$UPDATE" == "--update" ]]; then
  echo "Mode:   ${YELLOW}Update (re-cloning all)${NC}"
else
  echo "Mode:   Skip existing"
fi
echo ""

failed=0

clone_ref "shadcn-ui/ui"             "shadcn-ui"       || ((failed++))
clone_ref "radix-ui/primitives"      "radix-primitives" || ((failed++))
clone_ref "radix-ui/colors"          "radix-colors"    || ((failed++))
clone_ref "radix-ui/themes"          "radix-ui-themes" || ((failed++))
clone_ref "emilkowalski/vaul"        "vaul"            || ((failed++))
clone_ref "emilkowalski/sonner"      "sonner"          || ((failed++))
clone_ref "pacocoursey/cmdk"         "cmdk"            || ((failed++))
clone_ref "saadeghi/daisyui"         "daisyui"         || ((failed++))
clone_ref "motiondivision/motion"    "motion"          || ((failed++))
clone_ref "tailwindlabs/tailwindcss" "tailwindcss"     || ((failed++))
clone_ref "argyleink/open-props"     "open-props"      || ((failed++))

echo ""
total=$(ls -d "$REFS_DIR"/*/ 2>/dev/null | wc -l | tr -d ' ')
echo "${BOLD}Done.${NC} $total refs cloned."
if [[ $failed -gt 0 ]]; then
  echo "${RED}$failed repos failed to clone.${NC} Check your network connection and retry."
  exit 1
fi
