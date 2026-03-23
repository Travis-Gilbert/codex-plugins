#!/bin/bash
# install.sh — App-Pro plugin installer
# Sparse-clones library source into refs/ for grep-based verification

set -e

APP_PRO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REFS_DIR="$APP_PRO_DIR/refs"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo "${BOLD}App-Pro Plugin Installer${NC}"
echo "========================"
echo "Directory: $APP_PRO_DIR"
echo ""

# Helper: sparse clone a repo, keeping only specified paths
sparse_clone() {
  local name="$1"
  local repo="$2"
  shift 2
  local paths=("$@")

  local target="$REFS_DIR/$name"

  if [ -d "$target" ] && [ "$(ls -A "$target" 2>/dev/null)" ]; then
    echo "  ${GREEN}OK${NC}      refs/$name/ (already populated)"
    return
  fi

  echo "  ${YELLOW}Cloning${NC} $repo -> refs/$name/"

  local tmp_dir
  tmp_dir=$(mktemp -d)
  trap "rm -rf $tmp_dir" RETURN

  git clone --depth 1 --filter=blob:none --sparse "$repo" "$tmp_dir" 2>/dev/null

  cd "$tmp_dir"
  git sparse-checkout set --no-cone "${paths[@]}" 2>/dev/null

  mkdir -p "$target"
  for p in "${paths[@]}"; do
    if [ -e "$tmp_dir/$p" ]; then
      local parent
      parent=$(dirname "$p")
      mkdir -p "$target/$parent"
      cp -r "$tmp_dir/$p" "$target/$parent/" 2>/dev/null || true
    fi
  done

  cd "$APP_PRO_DIR"
  rm -rf "$tmp_dir"
  trap - RETURN

  local count
  count=$(find "$target" -type f | wc -l | tr -d ' ')
  echo "  ${GREEN}Done${NC}    refs/$name/ ($count files)"
}

# ── Phase 1: Core Infrastructure ──────────────────────────────────────

echo "${BOLD}Phase 1: Core refs (PWA + API)${NC}"

sparse_clone "workbox" "https://github.com/GoogleChrome/workbox.git" \
  "packages/workbox-strategies/src" \
  "packages/workbox-routing/src" \
  "packages/workbox-precaching/src" \
  "packages/workbox-background-sync/src"

sparse_clone "serwist" "https://github.com/serwist/serwist.git" \
  "packages/next/src" \
  "packages/sw/src"

sparse_clone "simplejwt" "https://github.com/jazzband/djangorestframework-simplejwt.git" \
  "rest_framework_simplejwt"

sparse_clone "capacitor" "https://github.com/ionic-team/capacitor.git" \
  "core/src" \
  "ios" \
  "android"

echo ""

# ── Phase 2: Mobile Optimization ──────────────────────────────────────

echo "${BOLD}Phase 2: Mobile optimization refs${NC}"

sparse_clone "react-native-gesture-handler" "https://github.com/software-mansion/react-native-gesture-handler.git" \
  "src"

sparse_clone "react-native-reanimated" "https://github.com/software-mansion/react-native-reanimated.git" \
  "src"

sparse_clone "tanstack-query" "https://github.com/TanStack/query.git" \
  "packages/query-core/src" \
  "packages/react-query/src"

echo ""

# ── Phase 3: Offline + Data ──────────────────────────────────────────

echo "${BOLD}Phase 3: Offline + data refs${NC}"

sparse_clone "watermelondb" "https://github.com/Nozbe/WatermelonDB.git" \
  "src"

sparse_clone "mmkv" "https://github.com/mrousavy/react-native-mmkv.git" \
  "src"

echo ""

# ── Phase 4: React Native + Visualization ────────────────────────────

echo "${BOLD}Phase 4: React Native + visualization refs${NC}"

sparse_clone "react-native" "https://github.com/facebook/react-native.git" \
  "Libraries/Components" \
  "Libraries/Lists" \
  "Libraries/Animated" \
  "Libraries/StyleSheet"

sparse_clone "expo-router" "https://github.com/expo/expo.git" \
  "packages/expo-router/src" \
  "packages/expo-secure-store" \
  "packages/expo-notifications"

sparse_clone "react-navigation" "https://github.com/react-navigation/react-navigation.git" \
  "packages/native/src" \
  "packages/stack/src" \
  "packages/bottom-tabs/src" \
  "packages/drawer/src"

sparse_clone "react-native-skia" "https://github.com/Shopify/react-native-skia.git" \
  "packages/skia/src"

sparse_clone "victory-native" "https://github.com/FormidableLabs/victory.git" \
  "packages/victory-native/src"

echo ""

# ── Knowledge Layer ──────────────────────────────────────────────────

echo "${BOLD}Knowledge Layer${NC}"
mkdir -p "$APP_PRO_DIR/knowledge/session_log"
for f in claims.jsonl tensions.jsonl questions.jsonl methods.jsonl preferences.jsonl; do
  touch "$APP_PRO_DIR/knowledge/$f"
done
echo "  ${GREEN}OK${NC}      knowledge/ directory ready"
echo ""

# ── Summary ──────────────────────────────────────────────────────────

echo "${BOLD}Summary${NC}"
echo "  Agents:     $(ls "$APP_PRO_DIR/agents/"*.md 2>/dev/null | wc -l | tr -d ' ')"
echo "  Skills:     $(find "$APP_PRO_DIR/skills" -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')"
echo "  Commands:   $(ls "$APP_PRO_DIR/commands/"*.md 2>/dev/null | wc -l | tr -d ' ')"
echo "  Refs:       $(ls -d "$REFS_DIR"/*/ 2>/dev/null | wc -l | tr -d ' ') libraries"
echo "  References: $(ls "$APP_PRO_DIR/references/"*.md 2>/dev/null | wc -l | tr -d ' ')"
echo ""
echo "${GREEN}App-Pro installed.${NC}"
echo "Run sync-plugins.sh to register with Claude Code."
