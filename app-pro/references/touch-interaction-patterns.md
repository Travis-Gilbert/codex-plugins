# Touch Interaction Patterns

> Touch targets, thumb zone, gestures, safe areas.

## Touch Target Requirements

| Platform | Minimum Size | Source |
|----------|-------------|--------|
| Google (Material) | 48x48 dp | Material Design guidelines |
| Apple (HIG) | 44x44 pt | Human Interface Guidelines |
| WCAG 2.2 | 24x24 CSS px (minimum), 44x44 (enhanced) | AAA target size |

**Use 48x48 as the minimum.** It satisfies all three.

### Spacing

Minimum 8px between adjacent interactive elements. Without this,
users consistently hit the wrong target.

### iOS Auto-Zoom Prevention

```css
input, select, textarea {
  font-size: 16px; /* Prevents iOS auto-zoom on focus */
}
```

Anything below 16px triggers viewport zoom when the input receives focus.

## Thumb Zone Analysis

```
┌─────────────────────────┐
│                         │
│  HARD   HARD    HARD    │  ← Requires repositioning hand
│                         │
│  OK     OK      OK      │  ← Reachable but uncomfortable
│                         │
│  EASY   EASY    EASY    │  ← Natural thumb resting zone
│          [●]            │  ← Primary action here
└─────────────────────────┘
```

### Placement Rules

- **Navigation**: Bottom tab bar (always visible, always reachable)
- **Primary actions**: Bottom-center or bottom-right
- **Secondary actions**: Middle of screen
- **Destructive/infrequent actions**: Top of screen (hard to reach = hard to accidentally tap)
- **FAB (Floating Action Button)**: Bottom-right, 56x56 dp minimum

## Pointer and Hover Media Queries

```css
/* Enlarge targets on touch devices */
@media (pointer: coarse) {
  .btn { min-height: 48px; min-width: 48px; }
}

/* Replace hover interactions on non-hover devices */
@media (hover: none) {
  .tooltip-trigger:hover .tooltip { display: none; }
  /* Use tap/long-press instead */
}
```

## Safe Areas

### CSS (Web)

```css
.bottom-nav {
  padding-bottom: env(safe-area-inset-bottom);
}

.header {
  padding-top: env(safe-area-inset-top);
}
```

### React Native

```tsx
import { useSafeAreaInsets } from 'react-native-safe-area-context';

function BottomNav() {
  const insets = useSafeAreaInsets();
  return (
    <View style={{ paddingBottom: insets.bottom }}>
      {/* Nav items */}
    </View>
  );
}
```

## Gesture Vocabulary

| Gesture | Convention | Example |
|---------|-----------|---------|
| Tap | Select, toggle, navigate | Tap a list item to open |
| Long-press | Context menu, multi-select | Long-press for options |
| Swipe horizontal | Dismiss, reveal actions | Swipe to delete/archive |
| Swipe vertical | Pull to refresh, dismiss sheet | Pull down to refresh feed |
| Pinch | Zoom in/out | Pinch to zoom on image/map |
| Double-tap | Quick action (like, zoom) | Double-tap to zoom to fit |

### Gesture/Scroll Coexistence

1. Contain pannable areas in fixed-height viewports
2. Use `simultaneousHandlers` for coexisting gestures
3. Provide visual boundaries for interactive areas
4. Double-tap to reset pan/zoom state

## Keyboard Avoidance

### React Native

```tsx
import { KeyboardAvoidingView, Platform } from 'react-native';

<KeyboardAvoidingView
  behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
  keyboardVerticalOffset={headerHeight}
>
  {/* Content with inputs */}
</KeyboardAvoidingView>
```

### Web

Use `visualViewport` API to detect keyboard presence and adjust layout.
Do not rely on `window.innerHeight` changes alone (unreliable on iOS).
