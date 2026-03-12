# Tailwind Patterns

## v4 Setup

Tailwind v4 changed the configuration model significantly. Know which version is in the project before writing any config.

**Source:** `refs/tailwindcss/`

### v4 Setup (current)

```css
/* globals.css */
@import "tailwindcss";

@theme {
  /* Custom tokens become utilities automatically */
  --color-brand: oklch(0.50 0.21 245);
  --color-brand-hover: oklch(0.44 0.21 245);
  --color-surface-1: oklch(0.97 0.01 265);
  --color-surface-2: oklch(1 0 0);
  --color-surface-3: oklch(0.94 0.01 265);
  --color-content-1: oklch(0.13 0.02 265);
  --color-content-2: oklch(0.35 0.02 265);
  --color-content-3: oklch(0.60 0.01 265);
  --color-border: oklch(0.88 0.01 265);
  --color-destructive: oklch(0.53 0.24 27);
  --color-success: oklch(0.53 0.17 145);
  --color-warning: oklch(0.72 0.18 80);

  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-button: var(--radius-md);
  --radius-input: var(--radius-md);
  --radius-card: var(--radius-lg);

  --font-family-sans: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  --font-family-mono: ui-monospace, "Cascadia Code", monospace;
}
```

In v4, `@theme` variables become Tailwind utilities automatically. `--color-brand` becomes `bg-brand`, `text-brand`, `border-brand`. No `tailwind.config.js` needed.

### v3 Setup (legacy projects)

```js
// tailwind.config.js — v3 only
module.exports = {
  content: ['./src/**/*.{tsx,ts,jsx,js}'],
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
    },
  },
}
```

---

## Dark Mode

### v4 dark mode

```css
@theme {
  /* Light mode defaults */
  --color-surface-1: oklch(0.97 0.01 265);
}

/* Dark mode override */
@layer base {
  [data-theme="dark"] {
    --color-surface-1: oklch(0.10 0.02 265);
    --color-surface-2: oklch(0.15 0.02 265);
    --color-content-1: oklch(0.95 0.01 265);
    --color-content-2: oklch(0.75 0.01 265);
    --color-content-3: oklch(0.55 0.01 265);
    --color-border: oklch(0.25 0.02 265);
  }
}
```

### v3 dark mode

```js
// tailwind.config.js
module.exports = {
  darkMode: ['class', '[data-theme="dark"]'],
}
```

```tsx
// Using dark: prefix
<div className="bg-surface-1 dark:bg-gray-900">
```

**Recommendation:** Use CSS variable override (`[data-theme="dark"]`) rather than Tailwind's `dark:` prefix. It keeps dark mode logic in CSS where it belongs, works the same in v3 and v4, and avoids doubling every color utility.

---

## Semantic Color in Components

Always use semantic tokens, never primitives directly:

```tsx
// WRONG: hardcoded primitive
<div className="bg-gray-100 text-gray-900 border-gray-200">

// CORRECT: semantic token
<div className="bg-surface-1 text-content-1 border-border">
```

The semantic pattern means dark mode is free — change the CSS variable, every component updates.

---

## Responsive Utilities

Tailwind's mobile-first breakpoint prefixes:

```tsx
// Stack on mobile, side-by-side on tablet+
<div className="flex flex-col md:flex-row gap-4">

// Hidden on mobile, visible at desktop
<nav className="hidden lg:flex items-center gap-6">

// Full width on mobile, constrained on desktop
<main className="w-full max-w-4xl mx-auto px-4 md:px-6">
```

### Container pattern

```tsx
// Consistent page container
function Container({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn('mx-auto w-full max-w-screen-xl px-4 md:px-6 lg:px-8', className)}>
      {children}
    </div>
  )
}
```

---

## Typography Utilities

### Prose (for user-generated content)

```tsx
// @tailwindcss/typography plugin
<article className="prose prose-sm md:prose-base prose-neutral max-w-none">
  {/* Markdown-rendered HTML gets automatic typographic styling */}
</article>
```

Install: `@tailwindcss/typography`

### Custom type scale

```tsx
// Use semantic size names, not size numbers
<h1 className="text-3xl font-bold tracking-tight text-content-1">Page Title</h1>
<h2 className="text-xl font-semibold text-content-1">Section</h2>
<p className="text-base text-content-2 leading-relaxed">Body text</p>
<span className="text-sm text-content-3">Caption / metadata</span>
<code className="text-sm font-mono bg-surface-2 px-1 py-0.5 rounded">code</code>
```

### Truncation patterns

```tsx
// Single-line truncate
<p className="truncate">Long text that gets cut off...</p>

// Multi-line clamp (2-line limit)
<p className="line-clamp-2">Text that wraps to two lines then gets an ellipsis...</p>

// Explicit: don't truncate (useful for overriding inherited truncate)
<p className="whitespace-normal overflow-visible text-clip">...</p>
```

---

## Spacing Patterns

### Consistent padding

```tsx
// Page-level section padding
<section className="py-12 md:py-16 lg:py-20">

// Card component padding
<div className="p-4 md:p-6">

// List item padding
<li className="px-4 py-3">

// Form field spacing
<div className="space-y-4">
  <Input ... />
  <Input ... />
</div>
```

### Gap vs. space-y vs. margin

```tsx
// Flex/grid children: use gap
<div className="flex items-center gap-3">

// Stack of block elements: use space-y
<div className="space-y-4">

// Explicit margin: only for single elements needing specific offset
<p className="mt-1">Error message below field</p>
```

**Rule:** Prefer `gap` (flex/grid) and `space-y`/`space-x` over individual margin classes. Margin on the last child is a bug — `space-y` removes the trailing margin automatically.

---

## Focus and Interactive States

### Focus ring standard

```tsx
// Focus ring that works for keyboard users, hidden for mouse users
<button className="rounded-button focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2">
```

### Interactive state progression

```tsx
// Complete interactive state coverage
<button className="
  bg-brand text-white
  hover:bg-brand-hover
  active:scale-[0.98]
  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2
  disabled:opacity-50 disabled:pointer-events-none
  transition-colors
">
```

**States to include on every interactive element:**
1. `hover:` — pointer hover
2. `active:` — mouse press (scale or darker bg)
3. `focus-visible:` — keyboard focus ring
4. `disabled:` — disabled state (opacity + cursor)

---

## Group and Peer Modifiers

### `group` — parent controls child

```tsx
// Child visibility controlled by parent hover
<div className="group flex items-center gap-3 rounded-card px-4 py-3 hover:bg-surface-2">
  <span className="flex-1 text-sm text-content-1">{item.title}</span>
  <button className="opacity-0 group-hover:opacity-100 transition-opacity text-xs text-content-3 hover:text-brand">
    Edit
  </button>
</div>
```

### `peer` — sibling controls sibling

```tsx
// Checkbox state controls label style
<label className="flex items-center gap-2 cursor-pointer">
  <input
    type="checkbox"
    className="peer sr-only"   // Hidden checkbox, still in DOM for state
    checked={checked}
    onChange={onChange}
  />
  <div className="h-4 w-4 rounded border border-border peer-checked:bg-brand peer-checked:border-brand transition-colors" />
  <span className="text-sm text-content-1 peer-checked:line-through peer-checked:text-content-3 transition-colors">
    {label}
  </span>
</label>
```

`peer` is the element that holds state. `peer-[modifier]:` applies to the next sibling.

---

## Arbitrary Values

Use sparingly, only when the design system token doesn't have a suitable value:

```tsx
// Matching a specific design mockup
<div className="w-[340px]">         {/* Fixed width widget */}
<div className="top-[72px]">        {/* Exactly below 72px header */}
<div className="grid-cols-[1fr_2fr_1fr]">  {/* Asymmetric grid */}
```

**Anti-pattern:** Using arbitrary values to avoid extending the theme. If you need `w-[340px]` in multiple places, add `--spacing-widget: 340px` to `@theme` or `tailwind.config.js` instead.

---

## Animation Utilities

### CSS-only animations in Tailwind config

For simple animations that don't need Motion:

```css
/* v4 @theme */
@theme {
  --animate-accordion-down: accordion-down 0.2s ease-out;
  --animate-accordion-up: accordion-up 0.2s ease-out;
  --animate-fade-in: fade-in 0.15s ease-out;
}

@keyframes accordion-down {
  from { height: 0; opacity: 0; }
  to { height: var(--radix-accordion-content-height); opacity: 1; }
}

@keyframes accordion-up {
  from { height: var(--radix-accordion-content-height); opacity: 1; }
  to { height: 0; opacity: 0; }
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
```

Then: `data-[state=open]:animate-accordion-down`

Note: `var(--radix-accordion-content-height)` is set by Radix's JS — this is how the accordion height animation connects to the actual content height.

---

## Common Utility Combos

These combinations appear so frequently they are worth memorizing:

```tsx
// Full-bleed section with content max-width
'w-full px-4 md:px-6 lg:px-8 py-12'
// Container within
'mx-auto max-w-screen-lg'

// Centered flex
'flex items-center justify-center'

// Icon button
'inline-flex items-center justify-center rounded p-1.5 h-8 w-8 hover:bg-surface-2 transition-colors'

// Input base
'w-full rounded-input border border-border bg-surface-3 px-3 py-2 text-sm text-content-1 placeholder:text-content-3 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-0'

// Card
'rounded-card bg-surface-2 border border-border p-4 shadow-card'

// Badge
'inline-flex items-center rounded-badge px-2 py-0.5 text-xs font-medium'

// Divider
'border-t border-border my-4'

// Screen reader only (visible label)
'sr-only'
```
