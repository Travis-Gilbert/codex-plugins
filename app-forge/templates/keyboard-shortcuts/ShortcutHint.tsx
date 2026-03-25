// components/ShortcutHint.tsx
// Platform-aware keyboard shortcut display component.
'use client';

export function ShortcutHint({ keys }: { keys: string }) {
  const isMac =
    typeof navigator !== 'undefined' && navigator.platform.includes('Mac');

  const display = keys
    .split('+')
    .map((key) => {
      if (key === '$mod') return isMac ? '\u2318' : 'Ctrl';
      if (key === 'Shift') return isMac ? '\u21E7' : 'Shift';
      if (key === 'Alt') return isMac ? '\u2325' : 'Alt';
      if (key === 'Control') return isMac ? '\u2303' : 'Ctrl';
      if (key === 'Backspace') return isMac ? '\u232B' : 'Backspace';
      if (key === 'Enter') return isMac ? '\u21A9' : 'Enter';
      if (key === 'Escape') return 'Esc';
      return key.toUpperCase();
    })
    .join(isMac ? '' : '+');

  return (
    <kbd className="ml-auto text-xs text-muted-foreground font-mono bg-muted px-1.5 py-0.5 rounded">
      {display}
    </kbd>
  );
}
