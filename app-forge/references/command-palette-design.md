# Command Palette Design

## Architecture Overview

The command palette is the app's nervous system. It provides instant access to navigation, content search, and quick actions through a single keyboard-triggered interface.

## cmdk Component Tree

cmdk provides a composable command menu with built-in fuzzy search:

```
Command (root)
├── Command.Input        # Search input with built-in filtering
├── Command.List         # Scrollable results container
│   ├── Command.Empty    # Shown when no results match
│   ├── Command.Loading  # Shown during async search
│   ├── Command.Group    # Visual grouping with heading
│   │   └── Command.Item # Individual selectable result
│   └── Command.Separator # Visual divider
└── Command.Dialog       # Portal + overlay wrapper
```

## Custom Filter Functions

cmdk's default filter uses a simple string match. Override for weighted results:

```tsx
<Command
  filter={(value, search) => {
    // Weight recent items higher
    const isRecent = recentItems.includes(value);
    const matchScore = value.toLowerCase().includes(search.toLowerCase()) ? 1 : 0;
    return matchScore + (isRecent ? 0.5 : 0);
  }}
>
```

For full fuzzy matching with ranking, use a dedicated library:

```tsx
import Fuse from 'fuse.js';

const fuse = new Fuse(items, {
  keys: ['label', 'keywords'],
  threshold: 0.4,
  includeScore: true,
});
```

## Dynamic Group Population

Groups should be populated dynamically based on context:

```tsx
function AppPalette() {
  const [query, setQuery] = useState('');
  const recentItems = useRecentItems();
  const searchResults = useSearch(query);
  const actions = useActions();

  return (
    <Command.Dialog>
      <Command.Input value={query} onValueChange={setQuery} />
      <Command.List>
        <Command.Empty>No results found.</Command.Empty>

        {!query && (
          <Command.Group heading="Recent">
            {recentItems.map(item => (
              <Command.Item key={item.id} onSelect={() => navigate(item.url)}>
                <ItemIcon type={item.type} />
                {item.title}
              </Command.Item>
            ))}
          </Command.Group>
        )}

        {query && searchResults.length > 0 && (
          <Command.Group heading="Search Results">
            {searchResults.map(result => (
              <Command.Item key={result.id} onSelect={() => navigate(result.url)}>
                <TypeBadge type={result.type} />
                {result.title}
                <span className="text-muted text-xs ml-auto">
                  {result.type}
                </span>
              </Command.Item>
            ))}
          </Command.Group>
        )}

        <Command.Group heading="Actions">
          {actions.map(action => (
            <Command.Item key={action.id} onSelect={action.execute}>
              {action.icon}
              {action.label}
              {action.shortcut && <ShortcutHint keys={action.shortcut} />}
            </Command.Item>
          ))}
        </Command.Group>
      </Command.List>
    </Command.Dialog>
  );
}
```

## Action Registration System

Actions are the palette's verbs. Register them centrally:

```tsx
interface PaletteAction {
  id: string;
  label: string;
  icon?: React.ReactNode;
  shortcut?: string;
  execute: () => void;
  keywords?: string[];    // Additional search terms
  group: 'navigation' | 'action' | 'settings';
  when?: () => boolean;   // Conditional availability
}

const actionRegistry: PaletteAction[] = [
  {
    id: 'nav:objects',
    label: 'Go to Objects',
    group: 'navigation',
    execute: () => router.push('/objects'),
    keywords: ['items', 'content'],
  },
  {
    id: 'action:new-object',
    label: 'New Object',
    shortcut: '$mod+n',
    group: 'action',
    execute: () => openNewObjectDialog(),
  },
  {
    id: 'action:toggle-theme',
    label: 'Toggle Dark Mode',
    group: 'settings',
    execute: () => toggleTheme(),
  },
];
```

## Recent Items Tracking

Track and surface recently interacted items:

```tsx
const RECENT_KEY = 'app:recent-items';
const MAX_RECENT = 10;

interface RecentItem {
  id: string;
  title: string;
  type: string;
  url: string;
  timestamp: number;
}

function addRecentItem(item: Omit<RecentItem, 'timestamp'>) {
  const stored = JSON.parse(localStorage.getItem(RECENT_KEY) || '[]');
  const filtered = stored.filter((r: RecentItem) => r.id !== item.id);
  const updated = [{ ...item, timestamp: Date.now() }, ...filtered].slice(0, MAX_RECENT);
  localStorage.setItem(RECENT_KEY, JSON.stringify(updated));
}

function useRecentItems(): RecentItem[] {
  const [items, setItems] = useState<RecentItem[]>([]);
  useEffect(() => {
    setItems(JSON.parse(localStorage.getItem(RECENT_KEY) || '[]'));
  }, []);
  return items;
}
```

## Keyboard Navigation Within the Palette

cmdk handles keyboard navigation automatically:
- Arrow keys move between items
- Enter selects the highlighted item
- Escape closes the palette
- Type to filter

Additional patterns:
- Tab to cycle between groups
- Cmd+number for quick access to first N items
- Backspace on empty input goes back one group level

## Empty State Design

When no results match, show helpful guidance:

```tsx
<Command.Empty>
  <div className="py-6 text-center">
    <p className="text-muted-foreground">No results for "{query}"</p>
    <p className="text-xs text-muted-foreground mt-1">
      Try searching for objects, actions, or settings
    </p>
  </div>
</Command.Empty>
```

## Loading States for Async Search

When search results come from an API:

```tsx
const [loading, setLoading] = useState(false);

useEffect(() => {
  if (!query) return;
  setLoading(true);
  const timeout = setTimeout(async () => {
    const results = await searchAPI(query);
    setSearchResults(results);
    setLoading(false);
  }, 200); // Debounce
  return () => clearTimeout(timeout);
}, [query]);

// In the palette:
<Command.List>
  {loading && <Command.Loading>Searching...</Command.Loading>}
  {/* results */}
</Command.List>
```

## Integration with Routing

The palette should work with the app's router:

```tsx
function usePaletteNavigation() {
  const router = useRouter();
  const { setOpen } = useCommandPalette();

  const navigate = useCallback((url: string) => {
    setOpen(false);
    router.push(url);
    addRecentItem({ id: url, title: url, type: 'navigation', url });
  }, [router, setOpen]);

  return navigate;
}
```
