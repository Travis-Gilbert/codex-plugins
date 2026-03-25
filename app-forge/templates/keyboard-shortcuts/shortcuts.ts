// lib/shortcuts.ts
// Keyboard shortcut registration with tinykeys, focus guards, and central registry.

import { tinykeys } from 'tinykeys';

export interface ShortcutRegistration {
  id: string;
  keys: string;             // tinykeys format: '$mod+k'
  label: string;            // Human-readable: 'Open Command Palette'
  handler: (e: KeyboardEvent) => void;
  requiresFocusGuard: boolean;
  scope: 'global' | 'panel' | 'dialog';
}

function isInputFocused(): boolean {
  const active = document.activeElement;
  if (!active) return false;
  const tag = active.tagName.toLowerCase();
  if (tag === 'input' || tag === 'textarea' || tag === 'select') return true;
  if (active.getAttribute('contenteditable') === 'true') return true;
  if (active.getAttribute('cmdk-input') !== null) return true;
  return false;
}

export class ShortcutManager {
  private shortcuts: Map<string, ShortcutRegistration> = new Map();
  private unsubscribe: (() => void) | null = null;

  register(shortcut: ShortcutRegistration): void {
    this.shortcuts.set(shortcut.id, shortcut);
    this.rebind();
  }

  unregister(id: string): void {
    this.shortcuts.delete(id);
    this.rebind();
  }

  getAll(): ShortcutRegistration[] {
    return Array.from(this.shortcuts.values());
  }

  destroy(): void {
    this.unsubscribe?.();
    this.shortcuts.clear();
  }

  private rebind(): void {
    this.unsubscribe?.();
    const bindings: Record<string, (e: KeyboardEvent) => void> = {};
    for (const s of this.shortcuts.values()) {
      bindings[s.keys] = (e: KeyboardEvent) => {
        if (s.requiresFocusGuard && isInputFocused()) return;
        s.handler(e);
      };
    }
    this.unsubscribe = tinykeys(window, bindings);
  }
}

// Singleton instance
export const shortcutManager = new ShortcutManager();
