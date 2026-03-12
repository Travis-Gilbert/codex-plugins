# Responsive Strategy

## Mobile-First vs. Desktop-First

**Mobile-first** means writing base styles for the smallest viewport, then adding complexity with `min-width` media queries.

**Desktop-first** means writing base styles for large viewports, then removing complexity with `max-width` media queries.

**Use mobile-first.** Removing complexity is harder than adding it. Mobile-first keeps base styles lean and avoids override cascades.

```css
/* Mobile-first ✓ */
.sidebar {
  display: none;           /* hidden on mobile */
}

@media (min-width: 768px) {
  .sidebar {
    display: block;        /* visible at tablet+ */
  }
}

/* Desktop-first ✗ */
.sidebar {
  display: block;          /* visible by default */
}

@media (max-width: 767px) {
  .sidebar {
    display: none;         /* hidden on mobile — harder to maintain */
  }
}
```

---

## Breakpoint Strategy

### Standard Breakpoints

| Name | Value | Context |
|------|-------|---------|
| `sm` | 640px | Large mobile, small tablet |
| `md` | 768px | Tablet portrait |
| `lg` | 1024px | Tablet landscape, small desktop |
| `xl` | 1280px | Desktop |
| `2xl` | 1536px | Large desktop, wide monitors |

These match Tailwind's defaults. Don't invent custom breakpoints unless required by a specific design constraint.

### Breakpoint Philosophy

**Breakpoints should be content-driven, not device-driven.** Add a breakpoint when the content requires it, not because a specific device exists.

A card grid should add a column when there's enough space for another column — not at a specific breakpoint. Use intrinsic sizing:

```css
/* Content-driven: columns appear when there's room */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
```

Use named breakpoints only for major layout shifts: navigation collapse, sidebar appearance, column count decisions.

---

## Layout Adaptation Patterns

### Single-Column Collapse

The most common mobile adaptation. At mobile widths, stack columns vertically.

```css
.two-column {
  display: grid;
  grid-template-columns: 1fr;          /* Mobile: single column */
  gap: 24px;
}

@media (min-width: 768px) {
  .two-column {
    grid-template-columns: 2fr 1fr;    /* Tablet: main + sidebar */
  }
}
```

### Navigation Collapse

Desktop: horizontal nav bar. Mobile: hidden nav behind hamburger menu or bottom tab bar.

```tsx
// Two distinct implementations — not one overloaded component
function Navigation() {
  return (
    <>
      {/* Desktop nav */}
      <nav className="hidden md:flex items-center gap-6">
        {navItems.map(item => <NavLink key={item.href} {...item} />)}
      </nav>

      {/* Mobile nav — different interaction model */}
      <MobileNav className="flex md:hidden" items={navItems} />
    </>
  )
}
```

**Decision:** Bottom tab bar vs. hamburger drawer depends on item count.
- ≤5 items: Bottom tab bar (immediate access)
- 6–12 items: Hamburger drawer
- 12+ items: Hierarchical navigation with search

### Sidebar Behavior

| Viewport | Behavior |
|----------|---------|
| Mobile | Hidden; opens as bottom sheet or overlay drawer |
| Tablet | May be collapsible to icon strip |
| Desktop | Always visible; full labels |

### Tables on Mobile

Tables with many columns break on mobile. Options:

1. **Horizontal scroll**: Wrap table in `overflow-x: auto` container. Good for data-dense tables.
2. **Card transform**: Convert each row to a card at mobile. Each cell becomes a label-value pair. Good for ≤ 5 columns.
3. **Priority columns**: Hide non-essential columns at mobile, show on desktop with `hidden md:table-cell`.

```css
/* Horizontal scroll — simplest */
.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

/* Priority columns */
.col-secondary {
  display: none;
}

@media (min-width: 768px) {
  .col-secondary {
    display: table-cell;
  }
}
```

---

## Container Queries

Container queries let components respond to their container's size rather than the viewport. This enables truly reusable components.

```css
/* Define a containment context */
.card-container {
  container-type: inline-size;
  container-name: card;
}

/* Card responds to container, not viewport */
@container card (min-width: 400px) {
  .card-content {
    display: grid;
    grid-template-columns: auto 1fr;
  }
}

@container card (max-width: 399px) {
  .card-content {
    display: flex;
    flex-direction: column;
  }
}
```

Use container queries for:
- Components that appear in both narrow sidebars and wide content areas
- Cards that adapt to both grid and list views
- Any component placed in contexts of varying width

Use viewport queries for:
- Overall page layout changes
- Navigation changes (desktop vs. mobile nav)
- Global content density changes

---

## Touch Target Sizing

Mobile requires larger touch targets than desktop hover targets.

- **Minimum:** 44×44px (Apple HIG) / 48×48dp (Android Material)
- **Comfortable:** 44–56px tall for primary actions
- **WCAG 2.5.8 minimum:** 24×24px

```css
/* Ensure minimum touch target with invisible padding */
.nav-icon-button {
  padding: 12px;                /* 16px icon + 24px invisible padding = 40px */
  min-width: 44px;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
```

---

## Fluid Typography

Use `clamp()` to scale type fluidly between breakpoints without media queries.

```css
/* Fluid heading: 24px at 320px viewport, 48px at 1280px viewport */
h1 {
  font-size: clamp(1.5rem, 2.5vw + 1rem, 3rem);
}

/* Tailwind equivalent using built-in clamp utilities */
/* <h1 className="text-3xl md:text-5xl lg:text-6xl"> */
```

For body text, avoid fluid sizing — stick to a fixed comfortable size (14–16px). Body text scaling creates jarring reading experience.

---

## Image Responsiveness

```html
<!-- Responsive images with srcset -->
<img
  src="hero-800.jpg"
  srcset="hero-400.jpg 400w, hero-800.jpg 800w, hero-1200.jpg 1200w"
  sizes="(max-width: 768px) 100vw, (max-width: 1280px) 50vw, 600px"
  alt="Hero image"
  width="1200"
  height="600"
/>
```

Always set `width` and `height` attributes on images to prevent layout shift (CLS). The browser can calculate the aspect ratio before the image loads.

In Next.js, use the `<Image>` component — it handles srcset, lazy loading, and format conversion automatically.

---

## Common Responsive Errors

| Error | Symptom | Fix |
|-------|---------|-----|
| Fixed widths on containers | Horizontal scroll on mobile | Use `max-width` + `width: 100%` |
| No padding on mobile | Content touches screen edge | Add `padding-inline: 16px` to all full-bleed containers |
| Hover-only interactions | Mobile users can't access | Add tap trigger for hover-only states |
| Desktop-only modals | Modal wider than screen | Set `max-width: min(90vw, 600px)` |
| Fixed navigation height | Content hidden behind nav on mobile | Use `padding-top: var(--nav-height)` on main, set `--nav-height` as a token |
| SVG without viewBox | SVG ignores responsive sizing | Always include `viewBox` attribute |
| Tables without overflow | Table overflows container on mobile | Wrap in `overflow-x: auto` |
| Mouse-only drag interactions | No keyboard/touch alternative | Add touch event handlers or gesture library |

---

## Testing Responsive Layouts

1. **Browser DevTools:** Toggle device toolbar; test at 320px (minimum), 375px (iPhone SE), 768px (tablet), 1280px (desktop)
2. **Real devices:** Test on actual iOS and Android — DevTools emulation is not identical
3. **Text resize:** Set browser font size to 200%; all layouts must still work
4. **Zoom to 400%:** WCAG 1.4.10 (Reflow) — content must be readable with only vertical scrolling at 400% zoom

Standard viewport test points:
- 320px: smallest modern phone
- 375px: iPhone SE / standard small phone
- 390px: iPhone 14
- 768px: iPad portrait
- 1024px: iPad landscape / small laptop
- 1280px: standard desktop
- 1440px: wide desktop
