# Layout Composition

## Grid Systems

### CSS Grid for Page Layout

CSS Grid is for two-dimensional layout. Use it for the page skeleton — the primary structure that doesn't change as content updates.

```css
/* Standard app shell */
.app-shell {
  display: grid;
  grid-template-columns: 240px 1fr;
  grid-template-rows: 56px 1fr;
  grid-template-areas:
    "sidebar header"
    "sidebar main";
  height: 100vh;
}

/* Dashboard with sidebar collapsing */
.app-shell[data-sidebar="collapsed"] {
  grid-template-columns: 56px 1fr;
}
```

### Flexbox for Component Layout

Flexbox is for one-dimensional layout — rows or columns within a component. Use it for navigation bars, button groups, card internals, form rows.

```css
/* Correct: toolbar is one-dimensional */
.toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Correct: card body is one-dimensional (stacked) */
.card-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
```

**Decision rule:** Page skeleton → Grid. Component internals → Flex. Content reflow → Grid. Linear alignment → Flex.

---

## Layout Patterns

### Hierarchy with Sidebar

The canonical app layout for deep information structures. Navigation persists; content area changes.

```
┌──────────┬─────────────────────────────┐
│          │  Header / Breadcrumb         │
│  Nav     ├─────────────────────────────┤
│  Sidebar │                             │
│          │  Content Area               │
│          │                             │
│          │                             │
└──────────┴─────────────────────────────┘
```

**Constraints:** Sidebar must be sticky or fixed on scroll. At mobile, sidebar becomes bottom sheet or hamburger overlay.

### Feed with Filters

For homogeneous browsable content. Filters live in a toolbar above or sidebar left; list/grid below.

```
┌──────────────────────────────────────────┐
│  Search ──────────  [ Filters ] [ Sort ] │
├──────────────────────────────────────────┤
│  Item 1                                  │
│  Item 2                                  │
│  Item 3                                  │
└──────────────────────────────────────────┘
```

**Key decision:** Filters in sidebar (for many filters) vs. toolbar chips (for few filters). Toolbar chips are more discoverable; sidebar filters handle 8+ options.

### Dashboard with Sections

Multiple independent monitoring widgets. Use CSS Grid with named areas for each widget. Never use a uniform card grid — widgets have different data densities and importance levels.

```
┌──────────────────┬──────────┬──────────┐
│                  │ Metric A │ Metric B │
│  Primary Chart   ├──────────┴──────────┤
│                  │   Secondary Chart   │
├──────────────────┴─────────────────────┤
│  Activity Feed (full width)            │
└────────────────────────────────────────┘
```

**Critical:** Asymmetry is intentional. The primary chart is larger because it communicates the most important signal.

### Detail View

Single object with related objects. Primary content left/center; metadata and related items right.

```
┌─────────────────────────┬──────────────┐
│  Primary Content        │  Metadata    │
│  (reading area)         │  Properties  │
│                         ├──────────────┤
│                         │  Related     │
│                         │  Items       │
└─────────────────────────┴──────────────┘
```

At narrow viewport, metadata moves below content.

### Form with Context

Input area left; live preview or guidance right. Reduces error by giving the user immediate feedback as they type.

### Command Interface

Full-width search input at top; results below. Used for search, command palette, and action-first flows.

---

## Whitespace and Breathing Room

### The Purpose of White Space

White space is not empty space — it is a communication tool. It separates unrelated elements, groups related elements, and creates visual priority for important content.

**Crowded layout:** Elements compete. User cannot determine what to focus on.
**Over-spaced layout:** Relationships between elements are lost. Form feels disconnected from its labels.

### Section Rhythm

Within a page, use consistent vertical rhythm. Three scales work well:

| Scale | Base unit | Section gap | Component gap | Element gap |
|-------|-----------|-------------|---------------|-------------|
| Tight | 4px | 24px | 12px | 4–8px |
| Standard | 4px | 48px | 24px | 8–16px |
| Comfortable | 4px | 80px | 40px | 16–24px |

Choose one scale per context. Mix scales only at deliberate boundaries (e.g., a tight data table inside a comfortable marketing page).

### Padding vs. Gap

- **Padding**: space inside a container, between its boundary and its children
- **Gap**: space between siblings in a flex or grid layout
- **Margin**: avoid using margin on components — it makes them non-reusable. Use gap on the parent container instead.

---

## Content Containers

### Max-Width for Readability

Long lines of text are harder to read. Constrain content containers:

```css
/* Prose / reading content */
.prose-container { max-width: 72ch; }  /* ~600px at 1rem */

/* Standard content area */
.content-area { max-width: 768px; }

/* Wide dashboard */
.dashboard { max-width: 1280px; }

/* Full-bleed (images, charts, hero) */
.full-bleed { max-width: 100%; }
```

### Centering Patterns

```css
/* Content column centering */
.content {
  max-width: 768px;
  margin-inline: auto;
  padding-inline: 16px; /* prevents edge-touching on mobile */
}
```

---

## Intrinsic Sizing and Min-Content

Use intrinsic sizing to make layouts naturally responsive without breakpoints:

```css
/* Sidebar that shrinks as content grows, but never below 200px */
.sidebar {
  width: clamp(200px, 25%, 320px);
}

/* Card grid that adds columns automatically */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
```

`auto-fill` creates as many columns as fit. `minmax(280px, 1fr)` ensures each column is at least 280px wide. The result is a responsive grid without any media queries.

---

## Overlay Layers

Overlays (dialogs, drawers, toasts, tooltips) exist in separate stacking layers. Manage them deliberately:

| Layer | z-index | Examples |
|-------|---------|---------|
| Base | 0 | Page content |
| Raised | 10 | Sticky headers, dropdowns |
| Floating | 100 | Tooltips, popovers |
| Overlay | 200 | Modals, dialogs, drawers |
| Toast | 300 | Notifications |
| Critical | 400 | Loading screens, forced errors |

Never use arbitrary z-index values like `z-index: 9999`. Name your layers and stay within the system.

---

## Common Layout Errors

| Error | Problem | Fix |
|-------|---------|-----|
| Content touching viewport edge | No padding on mobile | Add `padding-inline: 16px` to container |
| Sidebar and content misaligned | Grid rows don't span correctly | Use `grid-template-areas` explicitly |
| Form labels too far from inputs | Spacing hierarchy wrong | Label sits closer to its input than to the previous input |
| Wide table breaking layout | Table overflow hidden | Use horizontal scroll on table wrapper, not `overflow: hidden` |
| Modal not centered in viewport | Using margin instead of flexbox | Center with `display: grid; place-items: center` on the backdrop |
