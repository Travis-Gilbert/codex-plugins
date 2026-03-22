# Codex Plugins

Multi-plugin repository. Each subdirectory is a standalone Claude Code plugin.

## Plugin Install Model

Three gates must all be satisfied for a plugin to load:

| Step | What | Where | How |
|------|------|-------|-----|
| 1. Symlink | Plugin files accessible | `~/.claude/plugins/marketplaces/local-desktop-app-uploads/<name>/` | `./sync-plugins.sh` |
| 2. Registry | Plugin registered | `~/.claude/plugins/installed_plugins.json` | `./sync-plugins.sh` |
| 3. Enablement | Plugin enabled | `~/.claude/settings.json` → `enabledPlugins` | Manual: add `"<name>@local-desktop-app-uploads": true` |

`sync-plugins.sh` now handles all three steps automatically. If step 3 fails, manually add `"<name>@local-desktop-app-uploads": true` to `enabledPlugins` in `~/.claude/settings.json`.

`~/.claude/plugins/<name>/` (without marketplace namespace) is NOT read by Claude Code.

## Active Plugins

| Plugin | Version | Path |
|--------|---------|------|
| ui-design-pro | 1.1.0 | `ui-design-pro/` |
| scipy-pro | 4.0.0 | `scipy-pro/` |
| django-design | 4.0.0 | `django-design/` |
| d3-pro | 1.0.0 | `d3-pro/` |
| three-pro | 1.0.0 | `three-pro/` |
| shipit | 1.0.0 | `shipit/` |
| ml-pro | 1.0.0 | `ml-pro/` |
| django-engine-pro | 1.0.0 | `django-engine-pro/` |

## Sync

Run `./sync-plugins.sh` to symlink all plugins to the Claude Code install path.
Run `./sync-plugins.sh --status` to check which plugins are linked.

## Remote

Remote: `https://github.com/Travis-Gilbert/Plugins-building.git`
