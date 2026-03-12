# Design Systems and Token Hierarchies

## The Three Layers of a Token System

A well-structured token system has three layers. Violating this hierarchy produces brittle systems where changing the brand color requires editing 40 files.

```
Layer 1: Primitive tokens     (raw values — never used in components)
           ↓
Layer 2: Semantic tokens      (purpose-named — used in components)
           ↓
Layer 3: Component tokens     (component-specific overrides — used sparingly)
```

### Layer 1: Primitive Tokens

Raw values with no semantic meaning:

```css
/* Primitives: what EXISTS in the system */
--color-blue-500: oklch(0.56 0.19 245);
--color-blue-600: oklch(0.50 0.21 245);
--color-gray-100: oklch(0.97 0.01 265);
--color-gray-900: oklch(0.13 0.02 265);

--space-1: 4px;
--space-2: 8px;
--space-4: 16px;
--space-8: 32px;

--font-size-sm: 0.875rem;
--font-size-base: 1rem;
--font-size-lg: 1.125rem;
```

Primitive tokens are never used in component CSS. They exist only to be consumed by semantic tokens.

### Layer 2: Semantic Tokens

Purpose-named tokens that reference primitives:

```css
/* Semantics: what MEANS something in the system */
:root {
  --color-brand: var(--color-blue-600);
  --color-surface-1: var(--color-gray-100);
  --color-surface-2: white;
  --color-content-1: var(--color-gray-900);
  --color-content-2: var(--color-gray-700);
  --color-content-3: var(--color-gray-500);
  --color-border: var(--color-gray-200);
  --color-destructive: var(--color-red-600);
  --color-success: var(--color-green-600);

  --space-component-padding: var(--space-4);
  --space-section-gap: var(--space-8);
}

/* Dark mode: change semantics, not components */
[data-theme="dark"] {
  --color-surface-1: var(--color-gray-950);
  --color-surface-2: var(--color-gray-900);
  --color-content-1: var(--color-gray-50);
  --color-content-2: var(--color-gray-300);
  --color-content-3: var(--color-gray-500);
  --color-border: var(--color-gray-800);
}
```

**Components reference semantic tokens only.** Switching from light to dark mode means changing 10–15 semantic tokens; all components update automatically.

### Layer 3: Component Tokens

Used only when a specific component needs customization outside the standard semantic system:

```css
/* Rare: component-specific token */
.data-table {
  --table-row-hover: rgba(0, 0, 0, 0.04);
  --table-header-bg: var(--color-surface-2);
}
```

Component tokens should be rare. If many components need overrides, the semantic layer is wrong.

---

## Semantic Color Roles

| Token | Purpose |
|-------|---------|
| `--color-surface-1` | Page background |
| `--color-surface-2` | Card/panel background |
| `--color-surface-3` | Input background, elevated surface |
| `--color-surface-4` | Tooltip, popover background |
| `--color-content-1` | Primary text and icons |
| `--color-content-2` | Secondary/body text |
| `--color-content-3` | Muted/placeholder text |
| `--color-brand` | Primary interactive color (buttons, links) |
| `--color-brand-hover` | Hover state of brand |
| `--color-accent` | Secondary emphasis, highlights |
| `--color-destructive` | Danger, delete, irreversible actions |
| `--color-success` | Positive confirmation |
| `--color-warning` | Caution state |
| `--color-info` | Informational (non-warning, non-error) |
| `--color-border` | Dividers, input borders |
| `--color-border-focus` | Focus ring color |

---

## Spacing Scale

Use a base-4 scale. Every spacing value is a multiple of 4:

```css
:root {
  --space-0: 0px;
  --space-1: 4px;    /* micro gaps, icon padding */
  --space-2: 8px;    /* inner padding, tight spacing */
  --space-3: 12px;   /* compact component padding */
  --space-4: 16px;   /* standard content padding */
  --space-5: 20px;   /* medium padding */
  --space-6: 24px;   /* section breathing room */
  --space-8: 32px;   /* large section gaps */
  --space-10: 40px;  /* major content spacing */
  --space-12: 48px;  /* major section separation */
  --space-16: 64px;  /* page-level white space */
  --space-20: 80px;  /* hero-level breathing */
  --space-24: 96px;  /* maximum whitespace */
}
```

---

## Typography Scale

### Scale Configuration

```css
:root {
  --font-size-xs:   0.75rem;    /* 12px */
  --font-size-sm:   0.875rem;   /* 14px */
  --font-size-base: 1rem;       /* 16px */
  --font-size-md:   1.125rem;   /* 18px */
  --font-size-lg:   1.25rem;    /* 20px */
  --font-size-xl:   1.5rem;     /* 24px */
  --font-size-2xl:  1.875rem;   /* 30px */
  --font-size-3xl:  2.25rem;    /* 36px */
  --font-size-4xl:  3rem;       /* 48px */

  --font-weight-normal:   400;
  --font-weight-medium:   500;
  --font-weight-semibold: 600;
  --font-weight-bold:     700;

  --line-height-tight:    1.25;
  --line-height-snug:     1.375;
  --line-height-normal:   1.5;
  --line-height-relaxed:  1.625;

  --font-family-sans: system-ui, -apple-system, sans-serif;
  --font-family-mono: ui-monospace, "Cascadia Code", monospace;
}
```

### Semantic Typography Tokens

```css
:root {
  /* Semantic: what the type is FOR */
  --text-heading-xl:    var(--font-size-3xl);
  --text-heading-lg:    var(--font-size-2xl);
  --text-heading-md:    var(--font-size-xl);
  --text-heading-sm:    var(--font-size-lg);
  --text-body:          var(--font-size-base);
  --text-body-sm:       var(--font-size-sm);
  --text-caption:       var(--font-size-xs);
  --text-code:          var(--font-size-sm);
}
```

---

## Border Radius Scale

Consistent rounding creates visual cohesion. Inconsistent rounding (some 4px, some 8px, some 16px) makes a system look arbitrary.

```css
:root {
  --radius-none:   0px;
  --radius-sm:     4px;    /* small elements: badges, chips */
  --radius-md:     8px;    /* standard elements: inputs, buttons */
  --radius-lg:     12px;   /* cards, panels */
  --radius-xl:     16px;   /* sheets, large containers */
  --radius-2xl:    24px;   /* featured content areas */
  --radius-full:   9999px; /* pills, avatars */
}

/* Semantic radius */
:root {
  --radius-button:  var(--radius-md);
  --radius-input:   var(--radius-md);
  --radius-card:    var(--radius-lg);
  --radius-dialog:  var(--radius-xl);
  --radius-avatar:  var(--radius-full);
  --radius-badge:   var(--radius-sm);
}
```

---

## Shadow Scale

Shadows communicate elevation. Use them to separate overlaid layers, not for decoration.

```css
:root {
  --shadow-sm:   0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md:   0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg:   0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl:   0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
}

/* Semantic shadow — by elevation level */
:root {
  --shadow-card:    var(--shadow-sm);
  --shadow-dropdown: var(--shadow-lg);
  --shadow-dialog:  var(--shadow-xl);
  --shadow-toast:   var(--shadow-lg);
}
```

---

## Easing and Duration

Animation should use a consistent easing vocabulary.

```css
:root {
  /* Duration */
  --duration-instant: 0ms;
  --duration-fast:    100ms;
  --duration-normal:  200ms;
  --duration-slow:    300ms;
  --duration-slower:  500ms;

  /* Easing */
  --ease-default:    cubic-bezier(0.16, 1, 0.3, 1);  /* Expo out: fast start, gentle stop */
  --ease-in:         cubic-bezier(0.4, 0, 1, 1);
  --ease-out:        cubic-bezier(0, 0, 0.2, 1);
  --ease-in-out:     cubic-bezier(0.4, 0, 0.2, 1);
  --ease-spring:     cubic-bezier(0.34, 1.56, 0.64, 1); /* Slight overshoot */
}
```

---

## Tailwind Integration

When using Tailwind, map design system tokens to the theme config:

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: 'var(--color-brand)',
        surface: {
          1: 'var(--color-surface-1)',
          2: 'var(--color-surface-2)',
        },
        content: {
          1: 'var(--color-content-1)',
          2: 'var(--color-content-2)',
          3: 'var(--color-content-3)',
        },
        border: 'var(--color-border)',
        destructive: 'var(--color-destructive)',
      },
      borderRadius: {
        DEFAULT: 'var(--radius-md)',
        sm: 'var(--radius-sm)',
        lg: 'var(--radius-lg)',
        card: 'var(--radius-card)',
        full: 'var(--radius-full)',
      },
    },
  },
}
```

This way, `bg-surface-2`, `text-content-1`, and `border-border` automatically pick up theme values and respond to dark mode.

---

## Common Token System Errors

| Error | Consequence | Fix |
|-------|-------------|-----|
| Using raw hex values in components | Dark mode requires manual editing of every component | Always use semantic tokens |
| Skipping the primitive layer | Tokens reference tokens reference tokens — cycle risk | Primitives → Semantics → Components |
| Too many semantic tokens | Developers can't remember which to use | 15–20 semantic color tokens max |
| Inconsistent naming | `--btn-primary` vs `--primary-btn` | Establish pattern: `--[category]-[variant]` |
| One shadow for everything | No sense of elevation | Use shadows by layer, not by aesthetic preference |
| Hardcoded z-index values | Stacking order conflicts | Define z-index as tokens: `--z-modal: 200` |
