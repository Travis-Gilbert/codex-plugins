# App-Forge Plugin

You have access to cmdk source code (command palette), tinykeys source
(keyboard shortcuts), Tauri 2 core and plugin source, service worker
tooling (Serwist + Workbox), Framer Motion animation internals, and
selective Next.js App Router source for layout and parallel route
rendering. Use them.

## When You Start a Web-to-App Task

1. Determine the track. Read the relevant agent in agents/.
2. Check refs/ for the libraries you will use. Grep the source to verify
   API signatures and internal behavior rather than relying on memory.
3. If the task involves app shell architecture, read references/app-shell-patterns.md
   to understand the page-to-panel transformation before modifying any layout code.
4. If the task involves the command palette, read references/command-palette-design.md
   to understand the search and action architecture before integrating cmdk.
5. If the task involves Tauri, read references/tauri-nextjs-integration.md
   to understand the static export constraint before scaffolding anything.
6. If the task involves background sync, read references/background-sync-architecture.md
   to understand the coordination between service workers, Web Workers, and SSE.

## Source References

Library source is in refs/. Use it to verify API details:
- Command palette internals: refs/cmdk/src/
- Keyboard shortcut handling: refs/tinykeys/src/
- Tauri core bridge and invoke: refs/tauri-v2/core/
- Tauri JavaScript APIs: refs/tauri-api-js/src/
- Tauri official plugins: refs/tauri-v2/plugins/
- Service worker strategies: refs/workbox/packages/workbox-strategies/src/
- Next.js SW integration: refs/serwist/packages/next/src/
- Animation / transitions: refs/framer-motion/src/animation/
- Next.js parallel routes: refs/next-app-router/

## Reference Library

Curated knowledge docs in references/. Read the relevant one before starting:
- app-shell-patterns.md: Page-to-panel, persistent layouts, route groups
- command-palette-design.md: cmdk integration, search, actions, recent items
- keyboard-shortcuts-catalog.md: Standard shortcuts, conflicts, hint display
- view-transition-patterns.md: Directional transitions, View Transitions API
- background-sync-architecture.md: SW + Web Worker + SSE coordination
- pwa-setup-nextjs.md: Manifest, install prompt, offline fallback
- tauri-nextjs-integration.md: Static export, monorepo, server.url
- tauri-native-features.md: Menus, tray, notifications, file system, auto-update
- monorepo-dual-target.md: Turborepo workspace for web + desktop
- swift-handoff-template.md: Planning document template for Swift/AppKit

## Agent Loading

Agents are composable. A single task may load multiple agents. Read the
relevant agent .md file(s) before starting work. See AGENTS.md for routing.

## Rules

1. NEVER build a "page" when you should be building a "panel." If the
   content renders inside a persistent shell (sidebar visible, toolbar
   present, status bar showing), it is a panel. Panels swap within the
   shell. Pages replace the shell. In an app, almost everything is a panel.
   Full-page routes are reserved for auth screens, onboarding, and print views.

2. NEVER register keyboard shortcuts without checking for conflicts with
   browser defaults and input element focus. Cmd+C in a text input means
   "copy," not your custom action. Use tinykeys with a guard that checks
   `document.activeElement` before firing custom handlers.

3. NEVER implement background sync without a user-visible indicator of
   sync status. The user must know: (a) whether they are online or offline,
   (b) whether there are pending changes queued for sync, and (c) when
   the last successful sync occurred. A silent sync that fails silently
   is worse than no sync at all.

4. NEVER try to use Next.js Server Components, Server Actions, or API
   routes inside a Tauri WebView. Tauri has no Node.js runtime. If you
   need server features in the desktop app, either use Tauri's server.url
   mode (loads the hosted web app) or refactor the server-dependent code
   into client-side API calls that hit the deployed backend.

5. NEVER wrap a website in Tauri without adding at least one native
   desktop feature (native menu, system tray, global shortcut, or
   system notification). A bare WebView wrapper provides no value over
   the browser. If the user gains nothing from the desktop shell, they
   should stay in the browser.

6. NEVER add transitions to every navigation. Transitions communicate
   spatial relationships: moving deeper (left), moving back (right),
   opening an overlay (up), closing an overlay (down). If a transition
   does not communicate direction, it is decoration. Navigation between
   sibling panels in a tab bar should cross-fade, not slide.

7. NEVER implement a command palette without fuzzy search. Exact-match
   search in a command palette is nearly useless. Users type fragments,
   misspell, and abbreviate. cmdk has built-in fuzzy matching; use it.
   Weight recent items higher than alphabetical results.

8. When producing a Swift/AppKit handoff document, NEVER include
   implementation details (SwiftUI view code, Core Data schema DDL,
   Xcode project settings). The handoff is an architecture plan, not
   a code scaffold. A future Swift-Pro plugin owns implementation.

## Knowledge Layer

This plugin has a self-improving knowledge layer in `knowledge/`.

### At Session Start
1. Read `knowledge/manifest.json` for stats and last update time
2. Read `knowledge/claims.jsonl` for active claims relevant to this task
   (filter by tags matching the agents you are loading)
3. When a claim's confidence > 0.8 and it conflicts with static
   instructions, follow the claim. It represents learned behavior.
4. When a claim's confidence < 0.5 and it conflicts with static
   instructions, follow the static instructions.

### During the Session
- When you consult a claim, note which claim and why
- When you make a suggestion based on a claim, note the link
- When the user corrects you, note what they said and which claim
  was involved (this is a tension signal)
- When you notice a pattern not in the knowledge base, note it
  as a candidate claim

### At Session End
Run `/learn` to save and update knowledge. This is the ONLY
knowledge command you need.

## Cross-Reference with Other Plugins

If the project also uses other plugins:

- For React Native mobile: defer to app-pro. App-Forge does not touch
  mobile at all.
- For D3 visualizations: defer to D3-Pro. App-Forge specifies the panel
  that contains the visualization; D3-Pro builds the visualization itself.
- For Django backend API: defer to Django-Engine-Pro. App-Forge specifies
  which endpoints are needed; Django-Engine-Pro implements them.
- For general React/JS patterns: defer to JS-Pro. App-Forge owns the
  app-specific patterns (shell, palette, shortcuts, sync).
- For Next.js route architecture: defer to Next-Pro / next-design for
  general routing. App-Forge owns the specific patterns that enable
  app behavior (parallel routes for panels, route groups for shell zones,
  intercepting routes for overlays).
- For UI component design: defer to ui-design-pro. App-Forge owns the
  structural patterns (where components go in the shell); ui-design-pro
  designs how the components look.
- For motion and animation: defer to Animation-Pro / animation-design for
  complex choreography. App-Forge owns the navigation transition layer
  (which direction, what triggers) and delegates the animation
  implementation details.
- This plugin owns: app shell architecture, panel-based navigation,
  command palette integration, keyboard shortcut management, View
  Transitions, background sync coordination, PWA setup, Tauri desktop
  integration, monorepo structure for dual-target builds, and Swift/AppKit
  planning handoff documents.
