#!/bin/bash
# sync-plugins.sh — Sync local plugins from codex-plugins to Claude Code
#
# How Claude Code plugin install works:
#   1. Plugins must exist at ~/.claude/plugins/marketplaces/local-desktop-app-uploads/<name>/
#   2. They must be registered in ~/.claude/plugins/installed_plugins.json
#   3. Claude Code reads ONLY from that path — not from your dev directory
#
# This script creates symlinks from the marketplace path to your dev directory,
# so changes you make in codex-plugins/ are instantly available to Claude Code.
# It also registers new plugins in installed_plugins.json.
#
# Usage:
#   ./sync-plugins.sh              # sync all plugins
#   ./sync-plugins.sh d3-pro       # sync one plugin
#   ./sync-plugins.sh --status     # show sync status
#   ./sync-plugins.sh --uninstall d3-pro  # remove a plugin

set -euo pipefail

DEV_DIR="$(cd "$(dirname "$0")" && pwd)"
MARKETPLACE="$HOME/.claude/plugins/marketplaces/local-desktop-app-uploads"
REGISTRY="$HOME/.claude/plugins/installed_plugins.json"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# ─────────────────────────────────────────────
# Find all plugins in the dev directory
# A plugin is any directory with .claude-plugin/plugin.json
# ─────────────────────────────────────────────
find_plugins() {
    local search_dir="${1:-$DEV_DIR}"
    find "$search_dir" -maxdepth 4 -path "*/.claude-plugin/plugin.json" \
        -not -path "*/worktrees/*" \
        -not -path "*/.claude/worktrees/*" \
        -not -path "*/node_modules/*" \
        -exec dirname {} \; \
        | xargs -I{} dirname {} \
        | sort
}

# ─────────────────────────────────────────────
# Read plugin name from plugin.json
# ─────────────────────────────────────────────
get_plugin_name() {
    local plugin_dir="$1"
    python3 -c "import json; print(json.load(open('$plugin_dir/.claude-plugin/plugin.json'))['name'])" 2>/dev/null
}

# ─────────────────────────────────────────────
# Read plugin version from plugin.json
# ─────────────────────────────────────────────
get_plugin_version() {
    local plugin_dir="$1"
    python3 -c "
import json
d = json.load(open('$plugin_dir/.claude-plugin/plugin.json'))
print(d.get('version', '0.0.0'))
" 2>/dev/null
}

# ─────────────────────────────────────────────
# Check if plugin is registered in installed_plugins.json
# ─────────────────────────────────────────────
is_registered() {
    local name="$1"
    python3 -c "
import json
data = json.load(open('$REGISTRY'))
key = '${name}@local-desktop-app-uploads'
exit(0 if key in data.get('plugins', {}) else 1)
" 2>/dev/null
}

# ─────────────────────────────────────────────
# Register a plugin in installed_plugins.json
# ─────────────────────────────────────────────
register_plugin() {
    local name="$1"
    local version="$2"
    local install_path="$MARKETPLACE/$name"

    python3 -c "
import json
from datetime import datetime, timezone

registry_path = '$REGISTRY'
data = json.load(open(registry_path))

key = '${name}@local-desktop-app-uploads'
now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')

data['plugins'][key] = [{
    'scope': 'user',
    'installPath': '$install_path',
    'version': '$version',
    'installedAt': now,
    'lastUpdated': now
}]

with open(registry_path, 'w') as f:
    json.dump(data, f, indent=2)
"
}

# ─────────────────────────────────────────────
# Update the lastUpdated timestamp for existing plugin
# ─────────────────────────────────────────────
update_timestamp() {
    local name="$1"
    local version="$2"

    python3 -c "
import json
from datetime import datetime, timezone

registry_path = '$REGISTRY'
data = json.load(open(registry_path))

key = '${name}@local-desktop-app-uploads'
now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')

if key in data['plugins'] and len(data['plugins'][key]) > 0:
    data['plugins'][key][0]['lastUpdated'] = now
    data['plugins'][key][0]['version'] = '$version'

with open(registry_path, 'w') as f:
    json.dump(data, f, indent=2)
"
}

# ─────────────────────────────────────────────
# Unregister a plugin from installed_plugins.json
# ─────────────────────────────────────────────
unregister_plugin() {
    local name="$1"

    python3 -c "
import json

registry_path = '$REGISTRY'
data = json.load(open(registry_path))

key = '${name}@local-desktop-app-uploads'
if key in data['plugins']:
    del data['plugins'][key]

with open(registry_path, 'w') as f:
    json.dump(data, f, indent=2)
"
}

# ─────────────────────────────────────────────
# Sync a single plugin
# ─────────────────────────────────────────────
sync_plugin() {
    local plugin_dir="$1"
    local name
    name=$(get_plugin_name "$plugin_dir")
    local version
    version=$(get_plugin_version "$plugin_dir")

    if [[ -z "$name" ]]; then
        echo -e "  ${RED}✗${NC} Could not read plugin name from $plugin_dir"
        return 1
    fi

    local target="$MARKETPLACE/$name"

    # Check current state
    if [[ -L "$target" ]]; then
        local current_link
        current_link=$(readlink "$target")
        if [[ "$current_link" == "$plugin_dir" ]]; then
            # Already symlinked correctly — just update timestamp
            update_timestamp "$name" "$version"
            echo -e "  ${GREEN}✓${NC} $name ($version) — already linked"
            return 0
        else
            # Symlink points elsewhere — update it
            rm "$target"
            echo -e "  ${YELLOW}↻${NC} $name — updating symlink (was: $current_link)"
        fi
    elif [[ -d "$target" ]]; then
        # Physical directory exists — back it up and replace with symlink
        local backup="$target.backup.$(date +%Y%m%d%H%M%S)"
        mv "$target" "$backup"
        echo -e "  ${YELLOW}↻${NC} $name — replacing copy with symlink (backup: $(basename "$backup"))"
    fi

    # Create symlink
    ln -s "$plugin_dir" "$target"

    # Register if not already in installed_plugins.json
    if is_registered "$name"; then
        update_timestamp "$name" "$version"
        echo -e "  ${GREEN}✓${NC} $name ($version) — synced (symlink + registry updated)"
    else
        register_plugin "$name" "$version"
        echo -e "  ${GREEN}✓${NC} $name ($version) — installed (new symlink + registered)"
    fi
}

# ─────────────────────────────────────────────
# Show status of all plugins
# ─────────────────────────────────────────────
show_status() {
    echo -e "${CYAN}Plugin Sync Status${NC}"
    echo "Dev directory: $DEV_DIR"
    echo "Marketplace:   $MARKETPLACE"
    echo ""

    local plugins
    plugins=$(find_plugins)

    if [[ -z "$plugins" ]]; then
        echo "No plugins found in $DEV_DIR"
        return
    fi

    printf "%-20s %-8s %-12s %s\n" "PLUGIN" "VERSION" "STATUS" "DETAILS"
    printf "%-20s %-8s %-12s %s\n" "──────" "───────" "──────" "───────"

    while IFS= read -r plugin_dir; do
        local name version status details
        name=$(get_plugin_name "$plugin_dir")
        version=$(get_plugin_version "$plugin_dir")
        local target="$MARKETPLACE/$name"

        if [[ -L "$target" ]]; then
            local link_target
            link_target=$(readlink "$target")
            if [[ "$link_target" == "$plugin_dir" ]]; then
                status="${GREEN}linked${NC}"
                details="→ $plugin_dir"
            else
                status="${YELLOW}stale link${NC}"
                details="→ $link_target (expected: $plugin_dir)"
            fi
        elif [[ -d "$target" ]]; then
            status="${RED}copy${NC}"
            details="Physical copy (may be stale)"
        else
            status="${RED}not installed${NC}"
            details="Run ./sync-plugins.sh $name"
        fi

        printf "%-20s %-8s " "$name" "$version"
        echo -e "$status  $details"
    done <<< "$plugins"
}

# ─────────────────────────────────────────────
# Uninstall a plugin
# ─────────────────────────────────────────────
uninstall_plugin() {
    local name="$1"
    local target="$MARKETPLACE/$name"

    if [[ -L "$target" ]]; then
        rm "$target"
        echo -e "  ${GREEN}✓${NC} Removed symlink: $target"
    elif [[ -d "$target" ]]; then
        echo -e "  ${YELLOW}!${NC} $target is a physical directory, not a symlink."
        echo "  Remove manually if you're sure: rm -rf \"$target\""
        return 1
    else
        echo -e "  ${YELLOW}!${NC} $name not found in marketplace"
    fi

    if is_registered "$name"; then
        unregister_plugin "$name"
        echo -e "  ${GREEN}✓${NC} Removed from installed_plugins.json"
    fi
}

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
main() {
    mkdir -p "$MARKETPLACE"

    if [[ "${1:-}" == "--status" ]]; then
        show_status
        return
    fi

    if [[ "${1:-}" == "--uninstall" ]]; then
        if [[ -z "${2:-}" ]]; then
            echo "Usage: $0 --uninstall <plugin-name>"
            exit 1
        fi
        uninstall_plugin "$2"
        return
    fi

    echo -e "${CYAN}Syncing plugins to Claude Code${NC}"
    echo ""

    if [[ -n "${1:-}" ]]; then
        # Sync specific plugin
        local found=false
        while IFS= read -r plugin_dir; do
            local name
            name=$(get_plugin_name "$plugin_dir")
            if [[ "$name" == "$1" ]] || [[ "$(basename "$plugin_dir")" == "$1" ]]; then
                sync_plugin "$plugin_dir"
                found=true
                break
            fi
        done <<< "$(find_plugins)"

        if [[ "$found" == false ]]; then
            echo -e "  ${RED}✗${NC} Plugin '$1' not found in $DEV_DIR"
            echo "  Available plugins:"
            find_plugins | while read -r p; do
                echo "    - $(get_plugin_name "$p") ($(basename "$p")/)"
            done
            exit 1
        fi
    else
        # Sync all plugins
        while IFS= read -r plugin_dir; do
            sync_plugin "$plugin_dir"
        done <<< "$(find_plugins)"
    fi

    echo ""
    echo -e "${GREEN}Done.${NC} Restart Claude Code to pick up changes."
}

main "$@"
