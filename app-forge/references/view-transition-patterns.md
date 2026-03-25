# View Transition Patterns

## View Transitions API

The View Transitions API provides native browser support for animated transitions between DOM states. It captures a screenshot of the old state, applies the DOM change, then animates between the old and new states.

### Basic Usage

```tsx
function navigateWithTransition(url: string) {
  if (!document.startViewTransition) {
    router.push(url);
    return;
  }

  document.startViewTransition(() => {
    router.push(url);
  });
}
```

### Per-Element Transitions

Assign `view-transition-name` to elements that should animate independently:

```css
.main-content {
  view-transition-name: main-content;
}

.sidebar {
  view-transition-name: sidebar;
  /* Sidebar should NOT transition — it persists */
}
```

Elements with `view-transition-name` get their own transition pair (old + new). Elements without it are grouped into the root transition.

### Opting Elements Out of Transitions

The shell (sidebar, toolbar, status bar) should NOT transition:

```css
.app-shell-sidebar,
.app-shell-toolbar,
.app-shell-statusbar {
  view-transition-name: none;
}
```

## Directional Transition Model

Every transition should communicate spatial direction:

### Direction Data Attribute Pattern

```tsx
type TransitionDirection = 'push' | 'pop' | 'fade' | 'cover' | 'reveal';

function navigateWithDirection(url: string, direction: TransitionDirection) {
  if (!document.startViewTransition) {
    router.push(url);
    return;
  }

  document.documentElement.dataset.transitionDirection = direction;
  const transition = document.startViewTransition(() => {
    router.push(url);
  });

  transition.finished.then(() => {
    delete document.documentElement.dataset.transitionDirection;
  });
}
```

### CSS Keyframes

```css
@keyframes slide-in-right {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}
@keyframes slide-out-left {
  from { transform: translateX(0); }
  to { transform: translateX(-100%); }
}
@keyframes slide-in-left {
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
}
@keyframes slide-out-right {
  from { transform: translateX(0); }
  to { transform: translateX(100%); }
}
@keyframes slide-in-up {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}
@keyframes slide-out-down {
  from { transform: translateY(0); }
  to { transform: translateY(100%); }
}
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes fade-out {
  from { opacity: 1; }
  to { opacity: 0; }
}

/* Push: deeper into hierarchy */
[data-transition-direction="push"]::view-transition-old(main-content) {
  animation: slide-out-left 250ms ease-in-out;
}
[data-transition-direction="push"]::view-transition-new(main-content) {
  animation: slide-in-right 250ms ease-in-out;
}

/* Pop: back up hierarchy */
[data-transition-direction="pop"]::view-transition-old(main-content) {
  animation: slide-out-right 250ms ease-in-out;
}
[data-transition-direction="pop"]::view-transition-new(main-content) {
  animation: slide-in-left 250ms ease-in-out;
}

/* Fade: sibling switch (tabs) */
[data-transition-direction="fade"]::view-transition-old(main-content) {
  animation: fade-out 200ms ease-in-out;
}
[data-transition-direction="fade"]::view-transition-new(main-content) {
  animation: fade-in 200ms ease-in-out;
}

/* Cover: open overlay */
[data-transition-direction="cover"]::view-transition-old(main-content) {
  animation: none;
}
[data-transition-direction="cover"]::view-transition-new(main-content) {
  animation: slide-in-up 300ms ease-out;
}

/* Reveal: close overlay */
[data-transition-direction="reveal"]::view-transition-old(main-content) {
  animation: slide-out-down 300ms ease-in;
}
[data-transition-direction="reveal"]::view-transition-new(main-content) {
  animation: none;
}
```

## Browser Support Fallback

View Transitions API is not supported in all browsers. Always provide a fallback:

```tsx
function navigateWithTransition(url: string, direction: TransitionDirection) {
  if (!document.startViewTransition) {
    // No API support: navigate immediately, no animation
    router.push(url);
    return;
  }
  // API supported: animate
  document.documentElement.dataset.transitionDirection = direction;
  document.startViewTransition(() => router.push(url));
}
```

## Framer Motion as Alternative

When View Transitions API is insufficient (complex enter/exit choreography, gesture-driven transitions):

```tsx
import { AnimatePresence, motion } from 'framer-motion';

const slideVariants = {
  push: {
    initial: { x: '100%', opacity: 0 },
    animate: { x: 0, opacity: 1 },
    exit: { x: '-30%', opacity: 0 },
  },
  pop: {
    initial: { x: '-100%', opacity: 0 },
    animate: { x: 0, opacity: 1 },
    exit: { x: '30%', opacity: 0 },
  },
};

function PanelContent({ children, direction, routeKey }: Props) {
  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.div
        key={routeKey}
        variants={slideVariants[direction]}
        initial="initial"
        animate="animate"
        exit="exit"
        transition={{ duration: 0.25, ease: [0.32, 0.72, 0, 1] }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
```

## Performance Considerations

1. ONLY animate `transform` and `opacity` — these are GPU-composited
2. Keep duration under 300ms for navigation transitions
3. Use `ease-out` for enters, `ease-in` for exits
4. Disable transitions for `prefers-reduced-motion: reduce`:

```css
@media (prefers-reduced-motion: reduce) {
  ::view-transition-old(*),
  ::view-transition-new(*) {
    animation: none !important;
  }
}
```

5. Avoid transitioning large DOM trees — use `view-transition-name` to target specific elements
