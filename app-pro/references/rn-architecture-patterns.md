# React Native Architecture Patterns

> Navigation, state, data fetching, and platform adaptation.

## Navigation Architecture

### Expo Router (File-Based)

```
app/
├── _layout.tsx          # Root layout (providers, auth guard)
├── (tabs)/
│   ├── _layout.tsx      # Tab navigator
│   ├── index.tsx         # Home tab
│   ├── explore.tsx       # Explore tab
│   └── profile.tsx       # Profile tab
├── (auth)/
│   ├── _layout.tsx       # Auth stack (no tabs)
│   ├── login.tsx
│   └── register.tsx
├── object/
│   └── [slug].tsx        # Dynamic route
└── +not-found.tsx        # 404 fallback
```

### Authentication Flow

```
App Launch
  └─ Check SecureStore for refresh token
      ├─ Token exists → Validate → Main app (tabs)
      │                    └─ Invalid → Auth screens
      └─ No token → Auth screens
```

### Deep Linking

Expo Router: automatic from file structure. URL `/object/my-slug` maps
to `app/object/[slug].tsx` with `useLocalSearchParams()`.

React Navigation: manual `linking` config on NavigationContainer.

## State Architecture

```
┌─────────────────────────────────────┐
│  TanStack Query (server state)      │  API data, cached, auto-refetch
│  ├─ useQuery for reads              │
│  ├─ useMutation for writes          │
│  └─ persistQueryClient for offline  │
├─────────────────────────────────────┤
│  Zustand (client state)             │  UI prefs, feature flags
│  └─ persisted to MMKV              │
├─────────────────────────────────────┤
│  Expo SecureStore (secure state)    │  Auth tokens only
│  └─ Encrypted, biometric-gated     │
└─────────────────────────────────────┘
```

## Shared Logic Extraction

### What to Share (web + native)

- `packages/shared/src/api/` — API client, endpoint types, response types
- `packages/shared/src/validation/` — Zod schemas
- `packages/shared/src/transforms/` — Data normalization
- `packages/shared/src/types/` — All shared interfaces

### What NOT to Share

- Components (different component primitives)
- Navigation (different paradigms)
- Storage (different APIs per platform)
- Animation (Reanimated vs CSS/Motion)

## Platform Adaptation Patterns

### Small Differences: Platform.select()

```typescript
const styles = StyleSheet.create({
  shadow: Platform.select({
    ios: { shadowColor: '#000', shadowOffset: { width: 0, height: 2 } },
    android: { elevation: 4 },
  }),
});
```

### Large Differences: Platform Files

```
components/
├── ObjectCard.tsx           # Shared interface
├── ObjectCard.ios.tsx       # iOS-specific rendering
└── ObjectCard.android.tsx   # Android-specific rendering
```

## Expo Config Plugins

For native configuration without ejecting:

```typescript
// app.config.ts
export default {
  plugins: [
    ["expo-camera", { cameraPermission: "Used for document scanning" }],
    ["expo-notifications", { icon: "./assets/notification-icon.png" }],
  ],
};
```
