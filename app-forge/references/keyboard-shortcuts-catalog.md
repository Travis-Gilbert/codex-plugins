# Keyboard Shortcuts Catalog

## Standard App Keyboard Shortcuts

### Navigation
| Shortcut | Action | Notes |
|----------|--------|-------|
| `$mod+k` | Open command palette | Universal in modern apps |
| `$mod+/` | Toggle sidebar | VS Code convention |
| `$mod+\` | Toggle inspector/detail panel | Complement to sidebar |
| `$mod+1-9` | Switch to tab/panel N | Tab switching |
| `$mod+[` | Navigate back | Browser convention |
| `$mod+]` | Navigate forward | Browser convention |
| `Escape` | Close overlay/palette/inspector | Universal dismiss |

### Editing
| Shortcut | Action | Notes |
|----------|--------|-------|
| `$mod+n` | New item | With focus guard |
| `$mod+s` | Save | Override browser save-page |
| `$mod+d` | Duplicate | Must guard in text inputs |
| `$mod+Backspace` | Delete item | With confirmation |
| `$mod+z` | Undo | Browser handles in text inputs |
| `$mod+Shift+z` | Redo | Browser handles in text inputs |

### View
| Shortcut | Action | Notes |
|----------|--------|-------|
| `$mod+Shift+d` | Toggle dark/light mode | |
| `$mod+=` | Zoom in | Browser default, don't override |
| `$mod+-` | Zoom out | Browser default, don't override |
| `$mod+0` | Reset zoom | Browser default, don't override |
| `F11` | Fullscreen | Browser default, don't override |

### System (Desktop only — Tauri global shortcuts)
| Shortcut | Action | Notes |
|----------|--------|-------|
| `CmdOrCtrl+Shift+Space` | Quick capture | Works when app is in background |
| `CmdOrCtrl+Shift+F` | Global search | Works when app is in background |

## Conflict Detection

### Browser Defaults to NEVER Override
- `$mod+c` — Copy
- `$mod+v` — Paste
- `$mod+x` — Cut
- `$mod+a` — Select all
- `$mod+f` — Find (browser find bar)
- `$mod+l` — Focus address bar
- `$mod+t` — New tab
- `$mod+w` — Close tab
- `$mod+r` — Reload
- `$mod+p` — Print
- `$mod+q` — Quit (macOS)

### Shortcuts That Require Focus Guards
Any shortcut using a single letter key or `$mod+letter` that overlaps with text editing must check `isInputFocused()` before firing.

```tsx
function isInputFocused(): boolean {
  const active = document.activeElement;
  if (!active) return false;
  const tag = active.tagName.toLowerCase();
  if (tag === 'input' || tag === 'textarea' || tag === 'select') return true;
  if (active.getAttribute('contenteditable') === 'true') return true;
  // Also check for cmdk input
  if (active.getAttribute('cmdk-input') !== null) return true;
  return false;
}
```

## Platform-Aware Modifier Display

Users see different symbols on different platforms:

| Key | macOS | Windows/Linux |
|-----|-------|---------------|
| `$mod` | ⌘ | Ctrl |
| `Shift` | ⇧ | Shift |
| `Alt` | ⌥ | Alt |
| `Control` | ⌃ | Ctrl |

### Display Component

```tsx
function ShortcutHint({ keys }: { keys: string }) {
  const isMac = typeof navigator !== 'undefined' &&
    navigator.platform.includes('Mac');

  const display = keys
    .split('+')
    .map(key => {
      if (key === '$mod') return isMac ? '⌘' : 'Ctrl';
      if (key === 'Shift') return isMac ? '⇧' : 'Shift';
      if (key === 'Alt') return isMac ? '⌥' : 'Alt';
      if (key === 'Control') return isMac ? '⌃' : 'Ctrl';
      if (key === 'Backspace') return isMac ? '⌫' : 'Backspace';
      if (key === 'Enter') return isMac ? '↩' : 'Enter';
      if (key === 'Escape') return 'Esc';
      return key.toUpperCase();
    })
    .join(isMac ? '' : '+');

  return (
    <kbd className="ml-auto text-xs text-muted-foreground font-mono">
      {display}
    </kbd>
  );
}
```

## Registration System

Centralized registration makes shortcuts discoverable in the command palette:

```tsx
interface ShortcutRegistration {
  id: string;
  keys: string;           // tinykeys format: '$mod+k'
  label: string;          // Human-readable: 'Open Command Palette'
  handler: (e: KeyboardEvent) => void;
  requiresFocusGuard: boolean;
  scope: 'global' | 'panel' | 'dialog';
}

class ShortcutManager {
  private shortcuts: Map<string, ShortcutRegistration> = new Map();
  private unsubscribe: (() => void) | null = null;

  register(shortcut: ShortcutRegistration) {
    this.shortcuts.set(shortcut.id, shortcut);
    this.rebind();
  }

  unregister(id: string) {
    this.shortcuts.delete(id);
    this.rebind();
  }

  getAll(): ShortcutRegistration[] {
    return Array.from(this.shortcuts.values());
  }

  private rebind() {
    this.unsubscribe?.();
    const bindings: Record<string, (e: KeyboardEvent) => void> = {};
    for (const s of this.shortcuts.values()) {
      bindings[s.keys] = (e) => {
        if (s.requiresFocusGuard && isInputFocused()) return;
        s.handler(e);
      };
    }
    this.unsubscribe = tinykeys(window, bindings);
  }
}
```

## Shortcut Discovery

Make shortcuts discoverable through the command palette:

```tsx
// Populate palette with registered shortcuts
const shortcuts = shortcutManager.getAll();

<Command.Group heading="Keyboard Shortcuts">
  {shortcuts.map(s => (
    <Command.Item key={s.id} onSelect={() => s.handler(new KeyboardEvent('keydown'))}>
      {s.label}
      <ShortcutHint keys={s.keys} />
    </Command.Item>
  ))}
</Command.Group>
```
