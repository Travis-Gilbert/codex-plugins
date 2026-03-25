// components/CommandPalette.tsx
// Command palette with cmdk: navigation, content search, actions, recent items.
'use client';

import { Command } from 'cmdk';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ShortcutHint } from './ShortcutHint';

interface PaletteAction {
  id: string;
  label: string;
  group: 'navigation' | 'action' | 'settings';
  shortcut?: string;
  keywords?: string[];
  execute: () => void;
}

interface RecentItem {
  id: string;
  title: string;
  type: string;
  url: string;
  timestamp: number;
}

const RECENT_KEY = 'app:recent-items';
const MAX_RECENT = 10;

function getRecentItems(): RecentItem[] {
  if (typeof window === 'undefined') return [];
  return JSON.parse(localStorage.getItem(RECENT_KEY) || '[]');
}

export function addRecentItem(item: Omit<RecentItem, 'timestamp'>) {
  const stored = getRecentItems();
  const filtered = stored.filter(r => r.id !== item.id);
  const updated = [{ ...item, timestamp: Date.now() }, ...filtered].slice(0, MAX_RECENT);
  localStorage.setItem(RECENT_KEY, JSON.stringify(updated));
}

export function CommandPalette({ actions }: { actions: PaletteAction[] }) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const router = useRouter();
  const recentItems = getRecentItems();

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen(prev => !prev);
      }
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, []);

  const navigate = (url: string, title: string, type: string) => {
    setOpen(false);
    setQuery('');
    addRecentItem({ id: url, title, type, url });
    router.push(url);
  };

  return (
    <Command.Dialog
      open={open}
      onOpenChange={setOpen}
      label="Command palette"
      className="fixed inset-0 z-50"
    >
      <div className="fixed inset-0 bg-black/50" onClick={() => setOpen(false)} />
      <div className="fixed top-[20%] left-1/2 -translate-x-1/2 w-full max-w-lg bg-background border rounded-xl shadow-2xl overflow-hidden">
        <Command.Input
          value={query}
          onValueChange={setQuery}
          placeholder="Type a command or search..."
          className="w-full px-4 py-3 text-sm border-b outline-none bg-transparent"
        />
        <Command.List className="max-h-80 overflow-auto p-2">
          <Command.Empty className="py-6 text-center text-sm text-muted-foreground">
            No results found.
          </Command.Empty>

          {!query && recentItems.length > 0 && (
            <Command.Group heading="Recent" className="text-xs text-muted-foreground px-2 py-1.5">
              {recentItems.map(item => (
                <Command.Item
                  key={item.id}
                  onSelect={() => navigate(item.url, item.title, item.type)}
                  className="flex items-center gap-2 px-3 py-2 text-sm rounded cursor-pointer aria-selected:bg-accent"
                >
                  <span className="text-xs text-muted-foreground">{item.type}</span>
                  {item.title}
                </Command.Item>
              ))}
            </Command.Group>
          )}

          <Command.Group heading="Actions" className="text-xs text-muted-foreground px-2 py-1.5">
            {actions.map(action => (
              <Command.Item
                key={action.id}
                onSelect={() => { setOpen(false); action.execute(); }}
                keywords={action.keywords}
                className="flex items-center gap-2 px-3 py-2 text-sm rounded cursor-pointer aria-selected:bg-accent"
              >
                <span className="flex-1">{action.label}</span>
                {action.shortcut && <ShortcutHint keys={action.shortcut} />}
              </Command.Item>
            ))}
          </Command.Group>
        </Command.List>
      </div>
    </Command.Dialog>
  );
}
