// hooks/useShortcuts.ts
// React hook for registering component-scoped keyboard shortcuts.
'use client';

import { useEffect } from 'react';
import { shortcutManager, type ShortcutRegistration } from '../lib/shortcuts';

export function useShortcuts(shortcuts: Omit<ShortcutRegistration, 'id'>[]) {
  useEffect(() => {
    const ids: string[] = [];

    for (const shortcut of shortcuts) {
      const id = `${shortcut.keys}:${shortcut.label}`;
      shortcutManager.register({ ...shortcut, id });
      ids.push(id);
    }

    return () => {
      for (const id of ids) {
        shortcutManager.unregister(id);
      }
    };
  }, [shortcuts]);
}
