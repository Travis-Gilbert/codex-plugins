# Accessibility

## WCAG 2.2 Framework

WCAG 2.2 organizes requirements under four principles: **Perceivable, Operable, Understandable, Robust** (POUR).

| Level | Description | Requirement |
|-------|-------------|-------------|
| A | Minimum | Must not prevent access |
| AA | Standard | Target for most products |
| AAA | Enhanced | Achievable for specific contexts |

Most products target **AA**. AAA is aspirational and not required for full conformance.

---

## Perceivable

### Text Alternatives (1.1)

Every non-text content element needs a text alternative.

```tsx
// Images
<img src="chart.png" alt="Monthly revenue increased 23% from $41k to $50k in Q3" />

// Decorative images (no alt text, but alt attribute present)
<img src="divider.svg" alt="" role="presentation" />

// Icon buttons
<button aria-label="Close dialog">
  <XIcon aria-hidden="true" />
</button>

// Meaningful icons inline with text (hide from AT)
<span>
  <CheckIcon aria-hidden="true" className="text-success" />
  File saved
</span>
```

**Rule:** If an image conveys information, describe that information. If it's decorative, use `alt=""`. Never omit the `alt` attribute entirely.

### Color Contrast (1.4.3 / 1.4.11)

- Normal text: **4.5:1** minimum against background (WCAG AA)
- Large text (≥18pt regular / ≥14pt bold): **3:1** minimum
- UI components (buttons, inputs, focus rings): **3:1** minimum
- Incidental text (disabled states): no requirement

```css
/* Test your colors at: https://webaim.org/resources/contrastchecker/ */

/* Example: verify this passes */
.button-primary {
  background: var(--color-brand);    /* oklch(0.50 0.21 245) */
  color: white;                       /* oklch(1 0 0) */
  /* Contrast ratio: verify ≥ 4.5:1 with the above values */
}
```

### Non-Text Contrast (1.4.11)

Input borders, button outlines, and focus rings need 3:1 contrast against their surroundings.

```css
.input {
  border: 1.5px solid var(--color-border);
  /* --color-border must achieve 3:1 against the input background */
}
```

### Resize Text (1.4.4)

Text must be resizable to 200% without loss of content or functionality. Use `rem` units, not `px`, for font sizes. Test by setting browser font size to 32px (200% of 16px default).

### Content on Hover (1.4.13)

Tooltips and other hover-triggered content must:
- Be dismissable without moving focus (press Escape)
- Be hoverable (mouse can move onto the tooltip without it disappearing)
- Persistent (stays visible until dismissed or focus moves away)

```tsx
// Use a library that handles this (Radix Tooltip does it correctly)
import * as Tooltip from '@radix-ui/react-tooltip'
```

---

## Operable

### Keyboard Navigation (2.1.1)

All interactive elements must be keyboard accessible. This means:
- Buttons: activatable with Enter and Space
- Links: activatable with Enter
- Dropdowns: navigable with arrow keys
- Dialogs: focus trapped inside while open, Escape closes
- Tabs: arrow keys move between tabs, Enter/Space selects

**Test by:** Disconnect your mouse. Navigate the entire UI with Tab, Shift+Tab, Enter, Space, Escape, and arrow keys. Every feature must work.

### Visible Focus (2.4.11 — WCAG 2.2)

Every interactive element must have a visible focus indicator. The focus ring must achieve 3:1 contrast against adjacent colors.

```css
/* Custom focus ring — do NOT use outline: none without a replacement */
:focus-visible {
  outline: 2px solid var(--color-brand);
  outline-offset: 2px;
}

/* Suppress focus ring for mouse users only (keyboard users always see it) */
:focus:not(:focus-visible) {
  outline: none;
}
```

**Never use `outline: 0` or `outline: none` without providing an equally visible replacement.** This is the single most common accessibility violation in modern UIs.

### Target Size (2.5.8 — WCAG 2.2)

Interactive targets must be at least 24×24 CSS pixels, with exceptions for inline links.

Recommended minimum for touch: **44×44px** (Apple HIG / Android guidelines).

### Timing (2.2.1)

If content has a time limit, users must be able to:
- Turn off the time limit, or
- Adjust it, or
- Extend it with at least 20 seconds warning

Exception: Real-time events (auction timers, live broadcasts).

---

## Understandable

### Language (3.1.1)

Set the language on the `<html>` element:

```html
<html lang="en">
```

For content in a different language:
```html
<p>The French phrase <span lang="fr">déjà vu</span> means already seen.</p>
```

### Error Identification (3.3.1)

When a form error is detected, identify the error in text. Don't rely on color alone.

```tsx
function FormField({ label, error, ...props }) {
  return (
    <div>
      <label htmlFor={props.id}>{label}</label>
      <input
        {...props}
        aria-invalid={!!error}
        aria-describedby={error ? `${props.id}-error` : undefined}
        className={error ? 'border-destructive' : 'border-border'}
      />
      {error && (
        <p id={`${props.id}-error`} role="alert" className="text-destructive text-sm mt-1">
          {error}
        </p>
      )}
    </div>
  )
}
```

### Labels (3.3.2)

Every input must have a visible label. Never use placeholder text as the only label. Placeholder disappears when the user starts typing.

```tsx
// WRONG: placeholder only
<input placeholder="Email address" />

// CORRECT: visible label
<label htmlFor="email">Email address</label>
<input id="email" placeholder="you@example.com" />

// ALSO CORRECT: visually hidden label (for search, etc.)
<label htmlFor="search" className="sr-only">Search</label>
<input id="search" type="search" placeholder="Search..." />
```

---

## Robust

### Valid HTML (4.1.1)

Screen readers depend on correctly nested HTML. Test with an HTML validator. Common problems:
- `<button>` inside `<button>`
- Missing `<tbody>` in `<table>`
- Duplicate `id` attributes
- Interactive elements inside interactive elements

### Name, Role, Value (4.1.2)

Every interactive element must have:
- **Name**: What it is (via `aria-label`, `aria-labelledby`, or visible text)
- **Role**: What type of control it is (button, checkbox, dialog, etc.)
- **Value**: Current state if applicable (checked, expanded, selected)

```tsx
// Accordion example
<button
  aria-expanded={isOpen}
  aria-controls="panel-1"
>
  Section Title
</button>
<div id="panel-1" role="region" aria-labelledby="button-1" hidden={!isOpen}>
  Panel content
</div>

// Custom toggle
<button
  role="switch"
  aria-checked={isEnabled}
  onClick={toggle}
>
  {isEnabled ? 'On' : 'Off'}
</button>
```

### Status Messages (4.1.3)

Messages that appear without focus change must be programmatically determinable. Use `role="status"` for non-urgent messages and `role="alert"` for errors.

```tsx
// Toast notification — user doesn't focus it
<div role="status" aria-live="polite">
  Profile updated successfully
</div>

// Error that requires immediate attention
<div role="alert" aria-live="assertive">
  Submission failed. Please try again.
</div>
```

---

## ARIA Patterns for Common Components

### Dialog / Modal

```tsx
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="dialog-title"
  aria-describedby="dialog-description"
>
  <h2 id="dialog-title">Confirm deletion</h2>
  <p id="dialog-description">This action cannot be undone.</p>
  <button onClick={onConfirm}>Delete</button>
  <button onClick={onCancel}>Cancel</button>
</div>
```

Requirements: focus trapped inside, Escape closes, returns focus to trigger on close.

### Menu / Dropdown

```tsx
<button
  aria-haspopup="menu"
  aria-expanded={isOpen}
  aria-controls="dropdown-menu"
>
  Options
</button>
<ul
  id="dropdown-menu"
  role="menu"
  aria-label="Options menu"
>
  <li role="menuitem" tabIndex={-1}>Edit</li>
  <li role="menuitem" tabIndex={-1}>Delete</li>
</ul>
```

Requirements: arrow keys navigate items, Enter/Space activates, Escape closes, Tab closes and moves to next focusable element.

### Combobox / Select

Use Radix `@radix-ui/react-select` or `cmdk` — don't build this from scratch. The ARIA pattern for a combobox is significantly complex. Radix and cmdk implement it correctly.

---

## Screen Reader Testing

Test with:
- **macOS**: VoiceOver (`Cmd+F5` to start)
- **Windows**: NVDA (free) or JAWS
- **iOS**: VoiceOver (triple-press Home/Side button)
- **Android**: TalkBack

Minimum test checklist:
- [ ] All images have meaningful alt text (or empty alt for decorative)
- [ ] All form fields have visible labels
- [ ] All interactive elements are reachable by keyboard
- [ ] All dialogs trap focus and return focus on close
- [ ] Error messages are announced to screen readers
- [ ] Dynamic content changes are announced via live regions
- [ ] Page title is set and meaningful

---

## Automated Testing Tools

| Tool | Use |
|------|-----|
| `axe-core` / `@axe-core/react` | Runtime violations in development |
| `eslint-plugin-jsx-a11y` | Static analysis for JSX |
| Lighthouse | Overall accessibility score |
| Chrome DevTools Accessibility panel | Inspect computed ARIA tree |
| WAVE browser extension | Visual overlay of accessibility issues |

Automated tools catch ~30–40% of accessibility issues. Manual testing with keyboard and screen reader is required for the rest.
