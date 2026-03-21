# Codex Plugins

Multi-plugin repository. Each subdirectory is a standalone Claude Code plugin.

## Plugin Install Model

Local plugins register under `~/.claude/plugins/marketplaces/local-desktop-app-uploads/<name>/`.
The canonical path is in `~/.claude/plugins/installed_plugins.json` — only that path is loaded.
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

## Sync

Run `./sync-plugins.sh` to symlink all plugins to the Claude Code install path.
Run `./sync-plugins.sh --status` to check which plugins are linked.

## Remote

Remote: `https://github.com/Travis-Gilbert/Plugins-building.git`
