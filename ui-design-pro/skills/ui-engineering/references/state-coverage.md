# State Coverage

Every interactive UI element exists in some combination of states. If your implementation does not handle a state, that state is a bug that users will encounter.

---

## The Full State Matrix

### Interaction States
- **Default**: the resting state with no user interaction
- **Hover**: pointer over the element (desktop)
- **Focus-visible**: keyboard focus (visible ring, not on mouse click)
- **Pressed/Active**: during click or tap
- **Disabled**: interaction is not available
- **Loading**: action is in progress, outcome unknown
- **Dragging**: element is being repositioned

### Data States
- **Empty**: no data to display (distinct from loading)
- **Error**: data fetch or action failed
- **Success**: action completed successfully
- **Partial**: some data loaded, more available (pagination, infinite scroll)
- **Stale**: data is present but may be outdated

### Content States
- **Skeleton**: placeholder while content loads
- **Truncated**: content exceeds available space
- **Overflow**: content exceeds container (scroll, ellipsis, expand)
- **Collapsed**: content hidden behind disclosure

### Responsive States
- **Mobile collapsed**: content reorganized for small viewport
- **Touch mode**: larger targets, different interaction patterns
- **Reduced motion**: animations minimized or removed

---

## Implementation Checklist

For each component, verify:
- [ ] Default state renders correctly with real content
- [ ] Hover state has visible feedback (not just cursor change)
- [ ] Focus-visible state has a clear ring/outline
- [ ] Disabled state is visually distinct AND not interactive
- [ ] Loading state shows progress or indeterminate indicator
- [ ] Empty state explains what should be here and how to add it
- [ ] Error state is actionable (retry, fix, contact support)
- [ ] Success state matches the weight of the action
- [ ] Skeleton matches the shape of the content it replaces
- [ ] Mobile layout is usable at 320px width
- [ ] Keyboard-only navigation works for all interactive elements
- [ ] Screen reader announces state changes via aria-live

---

## State Transitions

- Loading → success: show result, toast confirmation for async
- Loading → error: show error with retry action
- Empty → populated: no jarring layout shift
- Expanded → collapsed: animate with purpose, instant for dense UIs
- Enabled → disabled: explain why (tooltip or inline text)

---

## Button: Full State Coverage

The complete interactive state set for a button:

```tsx
// All states handled in one utility string
<button
  disabled={isPending}
  className="
    inline-flex items-center gap-2 rounded-button px-4 py-2 text-sm font-medium
    bg-brand text-white
    hover:bg-brand-hover
    active:scale-[0.98]
    focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2
    disabled:opacity-50 disabled:pointer-events-none
    transition-colors
  "
>
  {isPending ? (
    <>
      <Spinner className="h-4 w-4 animate-spin" aria-hidden="true" />
      <span>Saving…</span>
    </>
  ) : (
    'Save changes'
  )}
</button>
```

**States covered:** default, hover, pressed, focus-visible, disabled, loading.

---

## Input: Full State Coverage

```tsx
function FormField({
  label, id, error, required, ...inputProps
}: {
  label: string
  id: string
  error?: string
  required?: boolean
} & React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <div>
      <label htmlFor={id} className="block text-sm font-medium text-content-1 mb-1">
        {label}
        {required && <span aria-hidden="true" className="text-destructive ml-0.5">*</span>}
      </label>
      <input
        id={id}
        aria-required={required}
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-error` : undefined}
        className={cn(
          // Default
          'w-full rounded-input border bg-surface-3 px-3 py-2 text-sm text-content-1 placeholder:text-content-3',
          // Focus-visible
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-0',
          // Disabled
          'disabled:bg-surface-2 disabled:text-content-3 disabled:pointer-events-none',
          // Error
          error ? 'border-destructive' : 'border-border',
        )}
        {...inputProps}
      />
      {error && (
        <p id={`${id}-error`} role="alert" className="mt-1 text-xs text-destructive">
          {error}
        </p>
      )}
    </div>
  )
}
```

**States covered:** default, focus-visible, disabled, error.

---

## List / Collection: Empty, Loading, Error, Populated

This is the most common state coverage failure — only the populated state is built.

```tsx
type AsyncState<T> =
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'empty' }
  | { status: 'success'; data: T[] }

function ItemList({ state, onRetry }: {
  state: AsyncState<Item>
  onRetry: () => void
}) {
  if (state.status === 'loading') {
    return <ListSkeleton count={5} />
  }

  if (state.status === 'error') {
    return (
      <div role="alert" className="rounded-card border border-destructive/30 bg-destructive/5 px-6 py-8 text-center">
        <p className="text-sm font-medium text-destructive">{state.message}</p>
        <button
          onClick={onRetry}
          className="mt-3 text-sm text-brand hover:underline"
        >
          Try again
        </button>
      </div>
    )
  }

  if (state.status === 'empty') {
    return (
      <div className="rounded-card border border-border border-dashed px-6 py-12 text-center">
        <p className="text-sm font-medium text-content-1">No items yet</p>
        <p className="mt-1 text-sm text-content-3">Items you create will appear here.</p>
      </div>
    )
  }

  return (
    <ul className="space-y-2">
      {state.data.map(item => <ItemRow key={item.id} item={item} />)}
    </ul>
  )
}
```

**States covered:** loading, error (with retry), empty (with explanation), populated.

**Rule:** Empty and error states must explain the situation and offer a next action. "No data" alone is insufficient. "Error" alone is insufficient.

---

## Skeleton: Shape-Matching Placeholders

Skeletons must match the shape of the content they replace. Mismatched skeletons cause layout shift.

```tsx
// Skeleton that matches a user card
function UserCardSkeleton() {
  return (
    <div
      className="flex items-center gap-3 rounded-card border border-border bg-surface-2 px-4 py-3"
      aria-hidden="true"   // Skeleton is decorative; screen reader doesn't need it
    >
      {/* Avatar placeholder */}
      <div className="h-10 w-10 rounded-full bg-surface-3 animate-pulse flex-shrink-0" />
      <div className="flex-1 space-y-1.5">
        {/* Name line */}
        <div className="h-3.5 w-32 rounded bg-surface-3 animate-pulse" />
        {/* Email line */}
        <div className="h-3 w-48 rounded bg-surface-3 animate-pulse" />
      </div>
    </div>
  )
}

// Repeat N times
function ListSkeleton({ count = 5 }: { count?: number }) {
  return (
    <div className="space-y-2" aria-busy="true" aria-label="Loading items">
      {Array.from({ length: count }).map((_, i) => (
        <UserCardSkeleton key={i} />
      ))}
    </div>
  )
}
```

**Skeleton rules:**
- `aria-hidden="true"` on each skeleton element — pure visual
- `aria-busy="true"` on the container — screen reader knows content is loading
- Match height, width proportions, and layout of real content
- Use `animate-pulse` or `animate-shimmer` — not blinking
- Never use a single full-width skeleton for a list of cards

---

## Success State: Appropriate Weight

Success feedback should match the weight of the action:

```tsx
// Lightweight: inline confirmation (for small, frequent actions like "copied")
function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <button
      onClick={handleCopy}
      className="inline-flex items-center gap-1.5 text-sm text-content-3 hover:text-content-1 transition-colors"
      aria-label={copied ? 'Copied!' : 'Copy to clipboard'}
    >
      {copied ? (
        <Check className="h-3.5 w-3.5 text-success" aria-hidden="true" />
      ) : (
        <Copy className="h-3.5 w-3.5" aria-hidden="true" />
      )}
      {copied ? 'Copied!' : 'Copy'}
    </button>
  )
}

// Heavyweight: toast notification (for destructive or significant actions)
// Use sonner:
import { toast } from 'sonner'

const handleDelete = async () => {
  await deleteItem(id)
  toast.success('Item deleted', {
    description: 'The item has been permanently removed.',
  })
}
```

**Weight matching guide:**
| Action | Success feedback |
|--------|-----------------|
| Copy text | Inline icon swap + label change |
| Save draft | Subtle "Saved" badge near save button |
| Submit form | Navigate to confirmation page or toast |
| Delete item | Toast with undo action |
| Send message | Navigate to sent confirmation |

---

## Disabled vs. Unavailable

These are different states:

```tsx
// Disabled: temporarily unavailable, user knows it exists
<button
  disabled
  title="You need editor permissions to do this"
  className="... disabled:opacity-50 disabled:cursor-not-allowed"
>
  Edit

// Unavailable: feature doesn't apply — just don't render it
{canEdit && <button>Edit</button>}

// Hidden with explanation: feature exists but user lacks access
{!canEdit && (
  <Tooltip content="Upgrade to Pro to edit items">
    <button disabled aria-describedby="upgrade-tip" className="... disabled:opacity-40 disabled:cursor-not-allowed">
      Edit
    </button>
  </Tooltip>
)}
```

**Rule:** Disabled elements without explanation cause confusion. Add a `title` attribute or tooltip explaining why.

---

## Loading States: Spinner vs. Skeleton vs. Progress

| Pattern | When to use |
|---------|-------------|
| Skeleton | First load of a list or page section — matches content shape |
| Spinner (inline) | Button action in progress — small, inside the button |
| Spinner (overlay) | Full-page or panel loading — blocks interaction |
| Progress bar | Upload, download, multi-step process with known progress |
| Indeterminate progress | Background processing, unknown duration |

```tsx
// Inline spinner — for button loading state
<button disabled className="...">
  <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
  </svg>
  Saving…
</button>

// Progress bar — for known-duration operations
<div role="progressbar" aria-valuenow={progress} aria-valuemin={0} aria-valuemax={100} className="h-1.5 w-full rounded-full bg-surface-3">
  <div
    className="h-full rounded-full bg-brand transition-all duration-300"
    style={{ width: `${progress}%` }}
  />
</div>
```

---

## Mobile Collapse Pattern

Navigation and sidebar content that needs to collapse on mobile:

```tsx
function Sidebar({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false)

  return (
    <>
      {/* Mobile: hamburger trigger */}
      <button
        className="lg:hidden p-2 rounded hover:bg-surface-2"
        aria-label="Open navigation"
        aria-expanded={open}
        onClick={() => setOpen(true)}
      >
        <Menu className="h-5 w-5" aria-hidden="true" />
      </button>

      {/* Sidebar: hidden on mobile, always visible on desktop */}
      <aside
        className={cn(
          // Desktop: always shown as left sidebar
          'lg:flex lg:flex-col lg:w-64 lg:relative lg:translate-x-0',
          // Mobile: overlay drawer
          'fixed inset-y-0 left-0 z-40 w-64 flex flex-col bg-surface-1 border-r border-border transition-transform duration-300',
          open ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {children}
      </aside>

      {/* Mobile overlay backdrop */}
      {open && (
        <div
          className="fixed inset-0 z-30 bg-black/40 lg:hidden"
          aria-hidden="true"
          onClick={() => setOpen(false)}
        />
      )}
    </>
  )
}
```

---

## Reduced Motion

Always wrap animations with a reduced motion check:

```tsx
import { useReducedMotion } from 'motion/react'

function FadeIn({ children }: { children: React.ReactNode }) {
  const reduce = useReducedMotion()
  return (
    <motion.div
      initial={{ opacity: 0, y: reduce ? 0 : 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={reduce ? { duration: 0.01 } : { type: 'spring', stiffness: 400, damping: 30 }}
    >
      {children}
    </motion.div>
  )
}
```

For CSS-only animations, use the media query:

```css
@media (prefers-reduced-motion: reduce) {
  .animate-pulse {
    animation: none;
  }
  .transition-all,
  .transition-colors {
    transition: none;
  }
}
```

**Rule:** Keep opacity transitions even when reducing motion — they communicate state changes without spatial movement.

---

## Screen Reader State Announcements

State changes that are not visually obvious must be announced via `aria-live`:

```tsx
// Announce async results
<div aria-live="polite" aria-atomic="true" className="sr-only">
  {status === 'success' && 'Changes saved successfully'}
  {status === 'error' && `Error: ${errorMessage}`}
</div>

// Announce loading state on a region
<section aria-busy={isLoading} aria-label="Search results">
  {isLoading ? <ListSkeleton /> : <ResultList items={results} />}
</section>
```

**`aria-live` values:**
- `polite` — announces when user is idle (most cases)
- `assertive` — interrupts immediately (only for critical errors)
- `aria-atomic="true"` — announces the whole region, not just the changed part

**`aria-busy`:** Use on containers that are loading content. Screen readers wait before reading the content.
