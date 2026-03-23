# App-Pro Agent Registry

> Agent routing rules for the App-Pro plugin. Claude Code reads this
> to determine which specialist to load for a given task.

## Agent Selection

Agents are composable context, not exclusive. A single task may load
multiple agents. Read the relevant agent .md file(s) before starting work.

### By Task Type

| Task | Primary Agent | Also Load | Key Refs |
|------|--------------|-----------|----------|
| PWA manifest setup | `pwa-engineer` | -- | `refs/serwist/` |
| Service worker caching | `pwa-engineer` | -- | `refs/workbox/packages/workbox-strategies/`, `refs/serwist/packages/next/` |
| Web Share Target | `pwa-engineer` | -- | `references/quick-capture-patterns.md` |
| Install prompt | `pwa-engineer` | -- | `references/pwa-caching-strategies.md` |
| Push notifications (web) | `pwa-engineer` | `mobile-api` | `refs/workbox/packages/workbox-background-sync/` |
| RN app scaffold | `rn-architect` | -- | `refs/expo-router/`, `references/rn-architecture-patterns.md` |
| Navigation structure | `rn-architect` | -- | `refs/react-navigation/`, `refs/expo-router/` |
| RN state management | `rn-architect` | `offline-engineer` | `refs/tanstack-query/`, `refs/mmkv/` |
| Platform-specific UI | `rn-architect` | `mobile-optimizer` | `refs/react-native/Libraries/Components/` |
| Shared logic extraction | `rn-architect` | -- | -- |
| Expo EAS build/submit | `rn-architect` | -- | `refs/expo-router/docs/` |
| Touch target audit | `mobile-optimizer` | -- | `references/touch-interaction-patterns.md` |
| Viewport/responsive fix | `mobile-optimizer` | -- | `references/touch-interaction-patterns.md` |
| Performance optimization | `mobile-optimizer` | -- | `references/mobile-performance-budgets.md` |
| Gesture implementation | `mobile-optimizer` | -- | `refs/react-native-gesture-handler/`, `refs/react-native-reanimated/` |
| Safe area handling | `mobile-optimizer` | -- | `refs/react-native/Libraries/Components/SafeAreaView/` |
| Offline read cache | `offline-engineer` | -- | `refs/watermelondb/`, `refs/tanstack-query/` |
| Offline write queue | `offline-engineer` | `mobile-api` | `refs/watermelondb/src/sync/`, `refs/workbox/packages/workbox-background-sync/` |
| Sync protocol design | `offline-engineer` | `mobile-api` | `references/offline-sync-protocol.md` |
| Conflict resolution | `offline-engineer` | -- | `references/offline-sync-protocol.md` |
| Token auth setup | `mobile-api` | -- | `refs/simplejwt/`, `refs/expo-secure-store/` |
| Mobile API endpoints | `mobile-api` | -- | `references/mobile-api-shape.md` |
| Push notification backend | `mobile-api` | -- | `references/push-notification-architecture.md` |
| Reminder system | `mobile-api` | -- | `references/push-notification-architecture.md` |
| Quick Capture flow | `mobile-api` | `offline-engineer` | `references/quick-capture-patterns.md`, `templates/quick-capture/` |
| Composite endpoints | `mobile-api` | -- | `references/mobile-api-shape.md` |
| D3 viz mobile adaptation | `viz-adapter` | -- | `references/mobile-viz-adaptation.md` |
| Force graph on mobile | `viz-adapter` | -- | `references/mobile-viz-adaptation.md` |
| RN chart implementation | `viz-adapter` | -- | `refs/victory-native/`, `refs/react-native-skia/` |
| Canvas/WebGL on mobile | `viz-adapter` | `mobile-optimizer` | `refs/react-native-skia/` |
| Capacitor setup | `pwa-engineer` | `rn-architect` | `refs/capacitor/`, `references/capacitor-bridge-patterns.md` |

### Composition Rules

- When implementing Quick Capture, load BOTH mobile-api AND offline-engineer.
  The capture endpoint design and the offline queue must agree on the mutation
  format, conflict strategy, and sync protocol.
- When building offline-capable screens with visualizations, load BOTH
  offline-engineer AND viz-adapter. The cached data shape affects which
  visualization adaptation is viable.
- When setting up push notifications end-to-end, load BOTH mobile-api
  (backend) AND pwa-engineer or rn-architect (frontend, depending on
  target). The device registration flow spans both sides.
- When adapting a D3 visualization for React Native, load BOTH viz-adapter
  AND D3-Pro (if available). viz-adapter selects the adaptation level;
  D3-Pro knows the D3 API internals.
- When building Capacitor bridge, load BOTH pwa-engineer (web layer) AND
  rn-architect (native layer patterns). The Capacitor bridge sits between
  the two.
