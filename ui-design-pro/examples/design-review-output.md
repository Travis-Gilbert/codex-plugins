# Design Review: Dashboard Activity Feed

**Component:** `src/components/dashboard/activity-feed.tsx`
**Reviewed by:** design-critic agent
**Stack context:** Next.js 15 App Router, Tailwind v4, shadcn/ui v4, Motion 12

---

## Executive Summary

The activity feed violates the plugin's core principle: **Polymorphic Object Rendering**. Three fundamentally different content types — project invites, code commits, and system alerts — are rendered through a single `<ActivityCard>` wrapper, producing a visually uniform list that obscures meaning and buries actionable items.

Secondary issues: missing ARIA on interactive elements, no empty/error state handling, and no motion on list updates.

**Priority fixes: 3 critical, 2 moderate, 2 minor.**

---

## Critical Issues

### 1. Uniform Rendering of Heterogeneous Items

**Location:** `activity-feed.tsx:42–58`

**Current pattern:**
```tsx
{items.map(item => (
  <ActivityCard key={item.id} item={item} />
))}
```

`ActivityCard` renders every item with the same layout: avatar circle, title text, timestamp. An invitation requiring user action looks identical to a commit notification. This violates Gestalt's **Law of Similarity** — visually similar elements imply equal importance and identical function.

**Impact:** Users cannot triage at a glance. Invitations requiring action are buried in noise. This is a discoverability failure, not a style preference.

**Fix:** Implement a polymorphic renderer with a discriminated union:

```tsx
type ActivityItem =
  | { kind: "invite";  id: string; from: string; project: string; sentAt: string }
  | { kind: "commit";  id: string; sha: string; message: string; repo: string; pushedAt: string }
  | { kind: "alert";   id: string; level: "warning" | "error"; body: string; createdAt: string };

const renderers: Record<ActivityItem["kind"], (item: any) => React.ReactNode> = {
  invite:  (item) => <InviteRow  item={item} />,
  commit:  (item) => <CommitRow  item={item} />,
  alert:   (item) => <AlertBanner item={item} />,
};

{items.map(item => (
  <React.Fragment key={item.id}>
    {renderers[item.kind]?.(item)}
  </React.Fragment>
))}
```

**Visual differentiation guidelines:**
- `InviteRow`: highlighted border (`border-brand/30 bg-brand-subtle`), accept/decline buttons visible
- `CommitRow`: monospace SHA chip, repo badge, no action buttons
- `AlertBanner`: full-width, destructive or warning colors, icon at left, dismiss button

---

### 2. No Loading / Empty / Error State Coverage

**Location:** `activity-feed.tsx` — no state handling present

**Current pattern:** The component renders nothing when `items` is an empty array. No loading skeleton, no empty state explanation, no error boundary.

**Impact:**
- Empty state renders as blank space — users cannot tell if content is loading, empty, or broken
- Violates the mental model of "I should see something here"

**Fix:** Adopt `AsyncState<T>` pattern (see `examples/polymorphic-list.tsx`):

```tsx
type AsyncState<T> =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "empty" }
  | { status: "success"; data: T[]; hasMore?: boolean };
```

Empty state must include:
1. An explanation ("No activity yet")
2. A contextual CTA ("Invite a teammate" or "Start a project")

Loading state must use a shape-matching skeleton with `aria-busy="true"` on the container.

---

### 3. Interactive Invite Items Not Keyboard Accessible

**Location:** `activity-feed.tsx:61–72` — `InviteAcceptButton` uses `onClick` directly on a `<div>`

**Current pattern:**
```tsx
<div onClick={() => onAccept(item.id)} className="...">
  Accept
</div>
```

**Impact:** Keyboard-only users and screen reader users cannot activate the accept action. This is a WCAG 2.2 Level A failure (Success Criterion 4.1.2: Name, Role, Value).

**Fix:**
```tsx
<button
  type="button"
  onClick={() => onAccept(item.id)}
  className="rounded-button bg-brand text-white px-2.5 py-1 text-xs hover:bg-brand-hover transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand"
>
  Accept
</button>
```

---

## Moderate Issues

### 4. List Container Has No Accessible Label

**Location:** `activity-feed.tsx:38` — `<div className="space-y-2">`

Screen readers announce this as an unlabeled region. With a `<section>` and `aria-label`, AT users can navigate directly to the feed.

**Fix:**
```tsx
<section aria-label="Recent activity" aria-busy={isLoading}>
  ...
</section>
```

---

### 5. Timestamps Not Machine-Readable

**Location:** `activity-feed.tsx` — timestamps rendered as "2 hours ago" strings

Relative timestamps are user-friendly but inaccessible to screen readers and broken for browser translation.

**Fix:** Use a `<time>` element with `dateTime` attribute:
```tsx
<time dateTime={item.createdAt} title={formatAbsolute(item.createdAt)}>
  {formatRelative(item.createdAt)}
</time>
```

---

## Minor Issues

### 6. No Motion on List Updates

When items are added or removed (e.g., after accepting an invite), the list reorders without animation. This causes a jarring visual jump and violates the **Change Visibility** principle — users lose track of what changed.

**Recommendation:** Wrap with `AnimatePresence` and add `motion.div` per item with `layout` prop for positional animation on reorder:

```tsx
<AnimatePresence initial={false}>
  {items.map(item => (
    <motion.div
      key={item.id}
      layout
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: "auto" }}
      exit={{ opacity: 0, height: 0 }}
      transition={spring.gentle}
    >
      {renderers[item.kind]?.(item)}
    </motion.div>
  ))}
</AnimatePresence>
```

Check `useReducedMotion()` before applying.

---

### 7. `ActivityCard` Accepts `any` Type

**Location:** `activity-feed.tsx:8` — `item: any`

The `any` type disables type checking on item properties and prevents TypeScript from catching missing kind-specific fields. This allows runtime errors to slip through undetected.

**Fix:** Replace with the `ActivityItem` discriminated union above. The TypeScript `never` exhaustive check pattern (see `examples/polymorphic-list.tsx:242`) will catch any newly added kinds that lack a renderer.

---

## Design Principles Checklist

| Principle | Status | Notes |
|-----------|--------|-------|
| Polymorphic Object Rendering | ❌ Fails | Single template for 3 item types |
| Gestalt: Similarity | ❌ Fails | Identical visual = implies identical function |
| AsyncState<T> coverage | ❌ Fails | No loading/empty/error states |
| WCAG 4.1.2 (Name, Role, Value) | ❌ Fails | `<div onClick>` not keyboard-accessible |
| Fitts's Law (target size) | ✅ Passes | Buttons ≥ 32px touch target |
| Color contrast (text) | ✅ Passes | All text tokens pass 4.5:1 on surface-1 |
| Focus visibility | ⚠️ Partial | Focus ring on some elements, missing on `<div onClick>` |
| Change visibility (motion) | ⚠️ Partial | No list-update animation |
| Timestamps machine-readable | ⚠️ Partial | Relative strings only; no `<time dateTime>` |
| `useReducedMotion()` | ✅ N/A | No motion present yet |

---

## Recommended Implementation Order

1. **Define `ActivityItem` discriminated union** — establishes the type contract everything else builds on
2. **Implement `InviteRow`** — highest visual differentiation, has interactive elements
3. **Implement `CommitRow`** — simpler, informational only
4. **Implement `AlertBanner`** — destructive/warning treatment
5. **Wire polymorphic renderer** — replace `ActivityCard` usage
6. **Add `AsyncState<T>` wrapper** — loading skeleton, empty state, error state
7. **Add AnimatePresence** — animate item additions/removals
8. **ARIA audit** — `<section aria-label>`, `<time dateTime>`, focus rings

Estimated effort: **4–6 hours** for a developer familiar with the stack.
