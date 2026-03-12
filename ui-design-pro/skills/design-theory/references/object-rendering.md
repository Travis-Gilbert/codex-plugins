# Object Rendering

## The Core Problem: Uniform Rendering

The most common UI design error is applying a uniform visual treatment to heterogeneous data.

```tsx
// WRONG: Every item gets the same card
{items.map(item => (
  <Card key={item.id}>
    <img src={item.thumbnail} />
    <h3>{item.title}</h3>
    <p>{item.description}</p>
    <Button>View</Button>
  </Card>
))}
```

This fails when items are different types. A notification, a task, and a published article are not the same object. Rendering them identically communicates that they are identical — which is false.

---

## Object Classification

Before writing any rendering code, classify every object in the collection.

**Ask of each object:**
1. What is it? (type)
2. What does the user want to do with it? (interaction model)
3. What is its visual priority relative to other objects? (hierarchy)
4. What states can it be in? (state model)
5. What is its information density? (how many fields does it expose?)

### Example Classification Table

| Object | Type | Interaction | Priority | States | Density |
|--------|------|-------------|----------|--------|---------|
| Draft article | Editable content | Click to edit | High | draft, scheduled, published | Medium |
| Published article | Published content | Click to read | Medium | published, archived | Low |
| Notification | Alert | Click to acknowledge | Highest | unread, read, dismissed | Low |
| Task | Action item | Click to complete | High | pending, in-progress, done | Low |
| Media file | Asset | Click to preview | Low | processing, ready, error | High |

Once classified, each type gets its own renderer.

---

## The Render Map Pattern

A render map is a lookup table from object type to renderer function. It is the core implementation pattern for polymorphic rendering.

```tsx
// renderMap.tsx

// 1. Define discriminated union types
type DraftArticle   = { type: 'draft';     id: string; title: string; updatedAt: string; wordCount: number }
type PublishedPost  = { type: 'published'; id: string; title: string; publishedAt: string; views: number }
type Notification   = { type: 'notification'; id: string; message: string; unread: boolean; severity: 'info' | 'warn' | 'error' }
type Task           = { type: 'task';      id: string; title: string; done: boolean; dueDate?: string }

type FeedItem = DraftArticle | PublishedPost | Notification | Task

// 2. Each renderer is purpose-built for its type
function DraftArticleRow({ item }: { item: DraftArticle }) {
  return (
    <div className="flex items-center gap-3 py-3 px-4 hover:bg-surface-2 cursor-pointer group">
      <div className="w-2 h-2 rounded-full bg-amber-400 shrink-0" aria-label="Draft" />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-content-1 truncate">{item.title}</p>
        <p className="text-xs text-content-3">{item.wordCount} words · Edited {item.updatedAt}</p>
      </div>
      <span className="text-xs text-content-3 opacity-0 group-hover:opacity-100 transition-opacity">Edit</span>
    </div>
  )
}

function PublishedPostCard({ item }: { item: PublishedPost }) {
  return (
    <div className="rounded-card bg-surface-2 p-4 hover:shadow-md transition-shadow cursor-pointer">
      <h3 className="text-base font-semibold text-content-1 mb-1">{item.title}</h3>
      <div className="flex items-center gap-2 text-xs text-content-3">
        <span className="text-success font-medium">Published</span>
        <span>·</span>
        <span>{item.views.toLocaleString()} views</span>
        <span>·</span>
        <span>{item.publishedAt}</span>
      </div>
    </div>
  )
}

function NotificationBanner({ item }: { item: Notification }) {
  const colorMap = {
    info:  'bg-blue-50  border-blue-200  text-blue-800',
    warn:  'bg-amber-50 border-amber-200 text-amber-800',
    error: 'bg-red-50   border-red-200   text-red-800',
  }
  return (
    <div
      role="alert"
      className={`flex items-start gap-3 rounded-card border px-4 py-3 text-sm ${colorMap[item.severity]} ${item.unread ? 'font-medium' : 'opacity-75'}`}
    >
      {item.unread && <span className="mt-0.5 w-2 h-2 rounded-full bg-current shrink-0" />}
      <p>{item.message}</p>
    </div>
  )
}

function TaskCheckItem({ item }: { item: Task }) {
  return (
    <label className={`flex items-center gap-3 py-2 cursor-pointer group ${item.done ? 'opacity-50' : ''}`}>
      <input type="checkbox" checked={item.done} className="rounded border-border accent-brand" />
      <span className={`text-sm text-content-1 flex-1 ${item.done ? 'line-through text-content-3' : ''}`}>
        {item.title}
      </span>
      {item.dueDate && !item.done && (
        <span className="text-xs text-content-3 shrink-0">{item.dueDate}</span>
      )}
    </label>
  )
}

// 3. The render map — O(1) lookup, no conditionals in the render loop
const renderMap: Record<FeedItem['type'], (item: any) => JSX.Element> = {
  draft:        (item) => <DraftArticleRow   key={item.id} item={item} />,
  published:    (item) => <PublishedPostCard key={item.id} item={item} />,
  notification: (item) => <NotificationBanner key={item.id} item={item} />,
  task:         (item) => <TaskCheckItem     key={item.id} item={item} />,
}

// 4. The feed component stays simple
export function Feed({ items }: { items: FeedItem[] }) {
  return (
    <div className="space-y-2">
      {items.map(item => renderMap[item.type](item))}
    </div>
  )
}
```

---

## Priority-Based Rendering for Same-Type Objects

When objects are the same type but have different priority, vary weight — not chrome.

```tsx
// Articles have same type but different priority
type Article = {
  id: string
  title: string
  excerpt: string
  priority: 'featured' | 'standard' | 'compact'
  publishedAt: string
  readTime: number
}

// Vary weight by priority, not wrapper:
function ArticleItem({ article }: { article: Article }) {
  if (article.priority === 'featured') {
    return (
      // Large format: title is the biggest element on the screen
      <article className="group cursor-pointer">
        <h2 className="text-2xl font-bold text-content-1 leading-tight group-hover:text-brand transition-colors">
          {article.title}
        </h2>
        <p className="mt-2 text-content-2 text-base leading-relaxed">{article.excerpt}</p>
        <div className="mt-3 flex gap-3 text-sm text-content-3">
          <span>{article.publishedAt}</span>
          <span>·</span>
          <span>{article.readTime} min read</span>
        </div>
      </article>
    )
  }

  if (article.priority === 'standard') {
    return (
      // Medium format: title prominent, excerpt present
      <article className="flex gap-4 cursor-pointer group py-3">
        <div className="flex-1 min-w-0">
          <h3 className="text-base font-semibold text-content-1 group-hover:text-brand truncate">{article.title}</h3>
          <p className="mt-1 text-sm text-content-2 line-clamp-2">{article.excerpt}</p>
        </div>
        <span className="text-xs text-content-3 shrink-0 mt-1">{article.readTime}m</span>
      </article>
    )
  }

  // compact: just title and meta
  return (
    <article className="flex items-center gap-3 py-2 cursor-pointer group">
      <p className="flex-1 text-sm text-content-1 group-hover:text-brand truncate">{article.title}</p>
      <span className="text-xs text-content-3 shrink-0">{article.readTime}m</span>
    </article>
  )
}
```

**Rule:** Same type, different priority → use the same component, vary weight inside it. Different types → use different components.

---

## Type Guards and TypeScript Safety

With discriminated unions, TypeScript provides compile-time guarantees:

```tsx
// Type guard for runtime narrowing
function isDraft(item: FeedItem): item is DraftArticle {
  return item.type === 'draft'
}

// Exhaustive check ensures new types are handled
function renderItem(item: FeedItem): JSX.Element {
  switch (item.type) {
    case 'draft':        return <DraftArticleRow item={item} />
    case 'published':    return <PublishedPostCard item={item} />
    case 'notification': return <NotificationBanner item={item} />
    case 'task':         return <TaskCheckItem item={item} />
    default:
      // TypeScript error if a new type is added and not handled
      const _exhaustive: never = item
      return <></>
  }
}
```

The `never` pattern on the default case means adding a new type to the union causes a TypeScript compile error until a renderer is added. This is the correct way to enforce exhaustive handling.

---

## State Model for Rendered Objects

Every object has multiple states. Design all of them before writing the first line of code.

```tsx
type DocumentState =
  | { status: 'loading' }
  | { status: 'empty' }
  | { status: 'error'; message: string }
  | { status: 'populated'; items: FeedItem[] }

function DocumentFeed({ state }: { state: DocumentState }) {
  if (state.status === 'loading') {
    return <FeedSkeleton count={5} />
  }

  if (state.status === 'empty') {
    return (
      <EmptyState
        title="No documents yet"
        description="Create your first document to see it here."
        action={<Button>New Document</Button>}
      />
    )
  }

  if (state.status === 'error') {
    return (
      <ErrorState
        message={state.message}
        action={<Button variant="ghost">Try again</Button>}
      />
    )
  }

  return <Feed items={state.items} />
}
```

**Rule:** A component that renders populated state but ignores empty and error states is incomplete. These are not edge cases — they are guaranteed states.

---

## Design Smells in Rendering Code

| Smell | Symptom | Fix |
|-------|---------|-----|
| Uniform card grid | `items.map(item => <Card>)` with identical structure | Classify items; build render map |
| Type-checking by field presence | `item.thumbnail ? <ImageCard> : <TextCard>` | Add explicit `type` field to data model |
| Style-by-index | `index === 0 ? 'featured' : 'standard'` | Priority belongs in data, not layout |
| Missing states | No `if (items.length === 0)` handler | Design empty state explicitly |
| Overloaded card | Card has 8+ variants via props | Split into separate type-specific components |
| Same wrapper, different content | All items wrapped in `<Card>` regardless of type | Remove wrapper; let type determine structure |

---

## When Uniform Rendering Is Correct

Uniform rendering is correct when objects are genuinely the same type with the same interaction model and the same information density.

**Correct use of uniform rendering:**
- A list of users with the same fields and the same interaction (click to view profile)
- A grid of thumbnails where every item is a media file
- A table of transactions where every row has the same structure

**Not correct for uniform rendering:**
- A feed mixing articles, events, and announcements
- A dashboard with metrics, charts, and action items
- A list where some items are editable and others are read-only
