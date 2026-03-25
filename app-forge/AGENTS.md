# App-Forge Agent Registry

> Agent routing rules for the App-Forge plugin. Claude Code reads this
> to determine which specialist to load for a given task.

## Agent Selection

Agents are composable context, not exclusive. A single task may load
multiple agents. Read the relevant agent .md file(s) before starting work.

### By Task Type

| Task | Primary Agent | Also Load | Key Refs |
|------|--------------|-----------|----------|
| App shell layout | `app-shell` | -- | `refs/next-app-router/`, `references/app-shell-patterns.md` |
| Persistent sidebar/toolbar | `app-shell` | -- | `references/app-shell-patterns.md` |
| Parallel routes for panels | `app-shell` | -- | `refs/next-app-router/` |
| Route groups for shell zones | `app-shell` | -- | `refs/next-app-router/` |
| Intercepting routes for overlays | `app-shell` | `transition-engineer` | `refs/next-app-router/` |
| Command palette setup | `command-center` | -- | `refs/cmdk/src/`, `references/command-palette-design.md` |
| Keyboard shortcut registration | `command-center` | -- | `refs/tinykeys/src/`, `references/keyboard-shortcuts-catalog.md` |
| Shortcut hint display | `command-center` | -- | `references/keyboard-shortcuts-catalog.md` |
| Navigation transitions | `transition-engineer` | -- | `refs/framer-motion/src/animation/`, `references/view-transition-patterns.md` |
| View Transitions API | `transition-engineer` | -- | `references/view-transition-patterns.md` |
| AnimatePresence on route change | `transition-engineer` | `app-shell` | `refs/framer-motion/src/animation/` |
| Service worker setup | `sync-engineer` | -- | `refs/serwist/`, `refs/workbox/`, `references/pwa-setup-nextjs.md` |
| PWA manifest and install | `sync-engineer` | -- | `references/pwa-setup-nextjs.md` |
| Background polling (Web Worker) | `sync-engineer` | -- | `references/background-sync-architecture.md` |
| SSE real-time updates | `sync-engineer` | -- | `references/background-sync-architecture.md` |
| Offline fallback page | `sync-engineer` | -- | `references/pwa-setup-nextjs.md` |
| Offline write queue | `sync-engineer` | -- | `refs/workbox/packages/workbox-background-sync/` |
| Tauri project scaffold | `tauri-builder` | -- | `refs/tauri-v2/`, `references/tauri-nextjs-integration.md` |
| Tauri + Next.js static export | `tauri-builder` | `app-shell` | `references/tauri-nextjs-integration.md` |
| Monorepo setup (web + desktop) | `tauri-builder` | -- | `references/monorepo-dual-target.md` |
| Native menus | `tauri-builder` | -- | `refs/tauri-api-js/src/`, `references/tauri-native-features.md` |
| System tray | `tauri-builder` | -- | `refs/tauri-v2/plugins/`, `references/tauri-native-features.md` |
| Global shortcuts (desktop) | `tauri-builder` | `command-center` | `refs/tauri-v2/plugins/global-shortcut/` |
| File system access | `tauri-builder` | -- | `refs/tauri-v2/plugins/fs/` |
| Auto-update | `tauri-builder` | -- | `refs/tauri-v2/plugins/updater/` |
| Deep linking | `tauri-builder` | -- | `refs/tauri-v2/plugins/deep-link/` |
| System notifications (desktop) | `tauri-builder` | -- | `refs/tauri-v2/plugins/notification/` |
| Swift/AppKit planning | `swift-planner` | -- | `references/swift-handoff-template.md` |
| macOS native app architecture | `swift-planner` | -- | `references/swift-handoff-template.md` |

### Composition Rules

- When building the app shell with transitions between panels, load BOTH
  app-shell AND transition-engineer. The shell defines where panels live;
  the transition engineer defines how they enter and exit.
- When adding a command palette with keyboard shortcuts, load BOTH agents
  from command-center (it covers both). But if the shortcuts need to work
  as global desktop shortcuts too, also load tauri-builder.
- When setting up PWA with background sync, sync-engineer covers both.
  But if the background processes also need to run when the desktop app
  is minimized, also load tauri-builder for the Rust-side background tasks.
- When building the Tauri desktop app, ALWAYS also load app-shell. The
  shell architecture must work in both the SSR web version and the static
  export desktop version.
- When producing a Swift/AppKit handoff, load swift-planner alone. It
  does not need other agents; its output is a planning document, not code.
