# App-Forge

A Claude Code plugin that transforms websites into applications: converting page-based Next.js sites into app-like experiences with persistent layouts, command palettes, and background sync; wrapping them in Tauri desktop shells with native OS integration; and producing architecture handoffs for native Swift/AppKit macOS apps.

## What This Is

A skill directory for Claude Code containing agent definitions, library source code, curated reference documents, and starter templates. Nothing here executes in production. It is all context and guidance for Claude Code.

## Agents

| Agent | Command | Model | Domain |
|-------|---------|-------|--------|
| app-shell | `/forge shell` | opus | Persistent layouts, panels, route groups, parallel routes |
| command-center | `/forge palette` | sonnet | Command palette (cmdk), keyboard shortcuts (tinykeys) |
| transition-engineer | `/forge transitions` | sonnet | View Transitions API, Framer Motion, directional animation |
| sync-engineer | `/forge sync` | opus | Service workers, PWA, background sync, SSE, Web Workers |
| tauri-builder | `/forge tauri` | opus | Tauri 2 desktop, native menus, tray, monorepo |
| swift-planner | `/forge swift-plan` | sonnet | Swift/AppKit architecture handoff documents |

Agents are composable. See `AGENTS.md` for the routing table and composition rules.

## Installation

1. Run `./sync-plugins.sh` from the codex-plugins root to symlink
2. Enable in `~/.claude/settings.json`: `"app-forge@local-desktop-app-uploads": true`

### Reference Libraries (Optional)

For full functionality, clone library source code into `refs/`:

```bash
cd refs/
git clone --depth 1 https://github.com/pacocoursey/cmdk.git
git clone --depth 1 https://github.com/jamiebuilds/tinykeys.git
git clone --depth 1 https://github.com/tauri-apps/tauri.git tauri-v2
git clone --depth 1 https://github.com/tauri-apps/plugins-workspace.git tauri-v2/plugins
git clone --depth 1 https://github.com/serwist/serwist.git
git clone --depth 1 https://github.com/GoogleChrome/workbox.git
git clone --depth 1 https://github.com/motiondivision/motion.git framer-motion
```

## Epistemic Knowledge Layer

App-Forge includes a self-improving knowledge base with 119 seeded claims across 12 domains. Claims track confidence via Bayesian updates from session evidence.

| Command | Purpose |
|---------|---------|
| `/knowledge-status` | Show claim counts, confidence distribution, tensions |
| `/knowledge-update` | Run between-session learning pipeline |
| `/knowledge-review` | Activate/retire draft claims, resolve tensions |
| `/session-save` | Flush session observations to knowledge log |

Run `/knowledge-review claims` after installation to activate the initial draft claims.

## Plugin Boundaries

- **App-Forge** owns: app shell, panels, command palette, shortcuts, transitions, background sync, PWA, Tauri desktop, monorepo, Swift handoff
- **JS-Pro** owns: general JavaScript/framework expertise
- **Next-Pro** owns: general Next.js architecture
- **ui-design-pro** owns: component implementation
- **app-pro** owns: React Native mobile
- **Django-Engine-Pro** owns: backend API implementation
