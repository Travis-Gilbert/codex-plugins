# App Shell Patterns: Page-to-Panel Transformation

## Mental Model Shift

A website is a collection of pages. An app is a persistent shell with swappable content panels.

The browser provides the frame for websites (address bar, tabs, back button). An app provides its own frame (sidebar, toolbar, status bar). The URL still changes, but the user perceives a view switch within the app, not a page load.

## Next.js App Router Layout Persistence

Layouts in the App Router persist across navigations within their subtree. A layout component renders once and survives route changes to its children. This is the mechanism that enables the app shell pattern.

Key insight: `layout.tsx` does NOT re-render when you navigate between its child routes. The layout mounts once and the router swaps only the `children` (or parallel route slots) inside it.

### How Layout Persistence Works

```
app/
├── layout.tsx         # Root layout - renders ONCE, never re-renders on navigation
└── (app)/
    ├── layout.tsx     # App shell layout - persists across all (app) routes
    ├── objects/
    │   └── page.tsx   # Swapped INTO the shell
    └── graph/
        └── page.tsx   # Swapped INTO the shell
```

When navigating from `/objects` to `/graph`, ONLY the page component changes. The `(app)/layout.tsx` stays mounted with its state intact. The sidebar selection updates, but the sidebar component itself does not unmount/remount.

## Route Group Strategy

Route groups `(name)` organize routes without affecting the URL structure. Use them to separate the app shell from non-shell routes:

```
app/
├── (app)/              # Routes WITH the app shell
│   ├── layout.tsx      # Shell: sidebar + toolbar + content zone
│   ├── objects/page.tsx
│   ├── graph/page.tsx
│   └── settings/page.tsx
├── (auth)/             # Routes WITHOUT the shell
│   ├── layout.tsx      # Minimal: centered card, no sidebar
│   ├── login/page.tsx
│   └── register/page.tsx
└── (print)/            # Routes for print views
    ├── layout.tsx      # Clean: no navigation, print-optimized
    └── report/[id]/page.tsx
```

The `(app)` group gets the full shell. The `(auth)` group gets a minimal layout. The `(print)` group gets a clean layout. Same Next.js app, three different frames.

## Parallel Route Composition

Parallel routes render multiple panel slots simultaneously. Each slot routes independently.

```
app/(app)/
├── layout.tsx          # Renders ALL parallel slots
├── @sidebar/           # Slot 1: sidebar navigation
│   ├── default.tsx     # Default when no specific match
│   └── objects/page.tsx  # Sidebar state when viewing objects
├── @main/              # Slot 2: main content
│   ├── default.tsx
│   ├── objects/page.tsx
│   └── graph/page.tsx
├── @inspector/         # Slot 3: detail inspector
│   ├── default.tsx     # Empty state or collapsed
│   └── objects/[slug]/page.tsx  # Shows when object selected
└── @modal/             # Slot 4: modal overlay
    ├── default.tsx     # null (no modal)
    └── (.)objects/[slug]/page.tsx  # Intercepting route
```

### Layout with Parallel Slots

```tsx
// app/(app)/layout.tsx
export default function AppShell({
  sidebar,
  main,
  inspector,
  modal,
}: {
  sidebar: React.ReactNode;
  main: React.ReactNode;
  inspector: React.ReactNode;
  modal: React.ReactNode;
}) {
  return (
    <div className="flex h-screen">
      <aside className="w-64 shrink-0 border-r overflow-auto">
        {sidebar}
      </aside>
      <div className="flex-1 flex min-w-0">
        <main className="flex-1 overflow-auto min-w-0">
          {main}
        </main>
        <aside className="w-80 shrink-0 border-l overflow-auto">
          {inspector}
        </aside>
      </div>
      {modal}
    </div>
  );
}
```

### Default Files Are Required

Every parallel route slot MUST have a `default.tsx`. Without it, direct URL access returns 404. The default file defines what renders when no specific route matches for that slot.

```tsx
// app/(app)/@inspector/default.tsx
export default function InspectorDefault() {
  return (
    <div className="p-4 text-muted-foreground">
      <p>Select an item to inspect</p>
    </div>
  );
}
```

## Intercepting Routes for Overlays

Intercepting routes catch navigation and render content in an overlay (modal, sheet, drawer) while preserving the shell underneath.

Convention: `(.)` intercepts same-level routes, `(..)` intercepts parent-level routes.

```
@modal/
└── (.)objects/[slug]/page.tsx  # Intercepts /objects/[slug]
```

When clicking an object link from within the app, the intercepting route catches it and renders in the `@modal` slot. The main content behind the modal stays visible. Refreshing the page or navigating directly loads the full page version.

## Loading Boundaries

Place loading boundaries PER PANEL, not at the shell level:

```
@main/
├── loading.tsx         # Shows spinner ONLY in main panel
├── objects/
│   ├── loading.tsx     # Shows spinner for object list
│   └── page.tsx
```

This ensures the shell (sidebar, toolbar) never shows a loading state. Only the panel that is fetching data shows loading UI.

## Scroll Position Restoration

Parallel route panels maintain independent scroll positions. But you need to handle this explicitly for the main content panel when navigating back:

```tsx
// Store scroll position before navigating away
useEffect(() => {
  const main = document.querySelector('[data-panel="main"]');
  if (!main) return;

  return () => {
    sessionStorage.setItem(`scroll:${pathname}`, String(main.scrollTop));
  };
}, [pathname]);

// Restore on mount
useEffect(() => {
  const main = document.querySelector('[data-panel="main"]');
  const saved = sessionStorage.getItem(`scroll:${pathname}`);
  if (main && saved) {
    main.scrollTop = Number(saved);
  }
}, [pathname]);
```

## Resizable Panels

For a professional app feel, panels should be resizable:

```tsx
// Use a resize handle between panels
function ResizeHandle({ onResize }: { onResize: (delta: number) => void }) {
  const handleMouseDown = (e: React.MouseEvent) => {
    const startX = e.clientX;
    const handleMouseMove = (e: MouseEvent) => {
      onResize(e.clientX - startX);
    };
    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  return (
    <div
      className="w-1 cursor-col-resize hover:bg-blue-500/50 transition-colors"
      onMouseDown={handleMouseDown}
    />
  );
}
```

Persist panel widths in localStorage so they survive page reloads.
