// lib/actions.ts
// Action registry type definitions for the command palette.

export interface PaletteAction {
  id: string;
  label: string;
  icon?: string;
  shortcut?: string;         // tinykeys format: '$mod+n'
  execute: () => void;
  keywords?: string[];       // Additional search terms
  group: 'navigation' | 'action' | 'settings';
  when?: () => boolean;      // Conditional availability
}

export function createActionRegistry(actions: PaletteAction[]): PaletteAction[] {
  return actions.filter(action => !action.when || action.when());
}
