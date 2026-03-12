# Stack Detection

## Why Detect Before Building

Adding a library that duplicates existing functionality is one of the most common mistakes. Before writing a single component:

1. Find what CSS framework is installed and at what version
2. Find what component library (if any) is already in use
3. Find what animation library (if any) is installed
4. Find whether there is an existing design token system
5. Find whether there are existing base components to build on

Running the `detect-stack` command or `stack-detector` agent automates this. The output shapes every downstream library decision.

---

## Quick Detection Commands

Run these in the project root:

```bash
# Check package.json for UI dependencies
cat package.json | grep -E '"(tailwindcss|@radix-ui|shadcn|framer-motion|motion|daisyui|@headlessui|chakra|mui|antd|@mantine|styled-components|emotion)"'

# Find Tailwind config — indicates v3 vs v4
ls tailwind.config.{js,ts,cjs,mjs} 2>/dev/null
grep -r '@import "tailwindcss"' src/ 2>/dev/null | head -5

# Find existing component directory
ls src/components/ui/ 2>/dev/null
ls components/ui/ 2>/dev/null

# Find shadcn config
cat components.json 2>/dev/null

# Find existing CSS variables / token system
grep -r "@theme\|--color-brand\|--color-primary" src/ --include="*.css" 2>/dev/null | head -10
```

---

## Reading package.json

The `dependencies` and `devDependencies` keys tell you what is installed. Key signals:

### Tailwind Version

```json
// v4 — no tailwind.config.js needed
"tailwindcss": "^4.x.x"

// v3 — requires tailwind.config.js
"tailwindcss": "^3.x.x"
```

If `tailwindcss` is in devDependencies but no `tailwind.config.js` exists, it's likely v4.

### Component Library

| Package | Library |
|---------|---------|
| `@radix-ui/react-*` | Radix Primitives (headless) |
| `shadcn` or presence of `components.json` | shadcn/ui (styled Radix) |
| `daisyui` | DaisyUI (Tailwind plugin) |
| `@radix-ui/themes` | Radix Themes (pre-designed) |
| `@headlessui/react` | Headless UI (Tailwind Labs) |
| `@chakra-ui/react` | Chakra UI |
| `@mui/material` | Material UI |
| `antd` | Ant Design |

### Animation Library

| Package | Library |
|---------|---------|
| `motion` | Motion (formerly Framer Motion) — use `motion/react` |
| `framer-motion` | Same package, older import — check version |
| `@formkit/motion` | FormKit Motion |
| `react-spring` | React Spring |

**Note:** `motion` and `framer-motion` are the same package. If you see `framer-motion`, `import from 'motion/react'` still works in v11+.

### Form Library

| Package | Library |
|---------|---------|
| `react-hook-form` | React Hook Form |
| `formik` | Formik |
| `@tanstack/react-form` | TanStack Form |

### Table Library

| Package | Library |
|---------|---------|
| `@tanstack/react-table` | TanStack Table |
| `react-table` | TanStack Table (legacy import) |
| `ag-grid-react` | AG Grid |

---

## Detecting Tailwind Version and Configuration

### v4 Indicators

```bash
# CSS file imports tailwindcss directly (v4)
grep -r '@import "tailwindcss"' . --include="*.css" 2>/dev/null

# @theme block exists (v4)
grep -r '@theme' . --include="*.css" 2>/dev/null

# No tailwind.config file (v4 doesn't need one)
ls tailwind.config.* 2>/dev/null || echo "No config file — likely v4"
```

### v3 Indicators

```bash
# tailwind.config.js exists
ls tailwind.config.{js,ts,cjs,mjs} 2>/dev/null

# CSS uses @tailwind directives (v3)
grep -r '@tailwind base' . --include="*.css" 2>/dev/null
```

### What Version Changes

| Feature | v3 | v4 |
|---------|----|----|
| Config | `tailwind.config.js` | `@theme {}` in CSS |
| Import | `@tailwind base/components/utilities` | `@import "tailwindcss"` |
| Dark mode | `dark:` prefix + config | CSS variable override recommended |
| Tokens | Via `theme.extend` in config | Via `@theme` CSS custom properties |
| Custom utilities | `plugin()` API | `@utility` in CSS |

---

## Detecting Existing Token System

Look for CSS custom properties that follow a semantic naming pattern:

```bash
# Search for token definitions in CSS files
grep -r "^  --color-\|^  --radius-\|^  --font-" . --include="*.css" 2>/dev/null | head -20
```

### Interpreting Results

**Semantic tokens found (`--color-brand`, `--color-surface-1`):**
→ A design system is in place. Add new components using these tokens. Do NOT introduce new raw color values.

**Radix Colors found (`--blue-9`, `--gray-1`):**
→ Radix color scale is in use. Map semantic meaning to scale steps (step 9 = brand, step 11 = text).

**No tokens found, raw Tailwind only:**
→ No token system. Introduce one in `globals.css` using `@theme` (v4) or CSS custom properties + Tailwind config (v3).

---

## Detecting Existing Components

Before building any component, check if one already exists:

```bash
# Check for UI component directory
ls src/components/ui/ 2>/dev/null
ls components/ui/ 2>/dev/null
ls src/ui/ 2>/dev/null

# Search for existing button component
find . -name "button.tsx" -o -name "Button.tsx" 2>/dev/null | grep -v node_modules

# Search for existing dialog component
find . -name "dialog.tsx" -o -name "Dialog.tsx" 2>/dev/null | grep -v node_modules
```

### shadcn Detection

```bash
# components.json indicates shadcn is configured
cat components.json 2>/dev/null
```

If `components.json` exists, shadcn is installed. The components live in `src/components/ui/` (or the configured path). **Do not recreate components that already exist** — extend them using the `className` prop.

---

## Detection Output Structure

The `stack-detector` agent produces a structured output. Example:

```json
{
  "framework": "react",
  "tailwind": {
    "installed": true,
    "version": "4.x",
    "config": "css-only",
    "tokenSystem": "custom"
  },
  "componentLibrary": {
    "name": "shadcn",
    "version": "v4",
    "configFile": "components.json",
    "componentsDir": "src/components/ui"
  },
  "animation": {
    "name": "motion",
    "importPath": "motion/react"
  },
  "formLibrary": "react-hook-form",
  "tableLibrary": "@tanstack/react-table",
  "existingComponents": [
    "button", "dialog", "input", "select", "tabs", "accordion"
  ],
  "notes": [
    "Dark mode uses [data-theme='dark'] CSS variable override",
    "Token system is semantic: --color-surface-1, --color-content-1 etc."
  ]
}
```

See `examples/stack-detection-output.json` for the full format.

---

## Decision Rules After Detection

### Tailwind v4 detected

- Write all new tokens in `globals.css` using `@theme {}`
- Do NOT create a `tailwind.config.js`
- Use `@utility` for custom utilities (not `plugin()`)

### shadcn detected with existing component

- Use the existing component
- Extend via `className` prop (tailwind-merge handles conflict resolution)
- Do NOT create a parallel component — ask stack-detector what exists first

### Motion detected

- Import from `motion/react` regardless of whether package name is `motion` or `framer-motion`
- Do not add `framer-motion` if `motion` is already installed — same package

### No component library detected

- Reach for Radix Primitives for any interactive component
- Add CVA for variant management if building more than one variant
- Set up shadcn if the project will need many components

### Radix Colors detected

- Use scale variables directly: `var(--blue-9)` for brand, `var(--blue-11)` for readable text
- Step mapping: 1–4 backgrounds, 5–8 interactive, 9–10 solid, 11–12 text
- Dark mode is automatic — import `blue-dark.css` alongside `blue.css`

---

## The `detect_ui_stack.sh` Script

The `scripts/detect_ui_stack.sh` script runs all of the above checks automatically and outputs a detection summary. Run it from the project root:

```bash
# From project root
bash /path/to/ui-design-pro/scripts/detect_ui_stack.sh
```

The output includes:
- Framework detection (React, Vue, Svelte, plain HTML)
- Tailwind version and configuration style
- Component library name and version hint
- Animation library
- Existing component directories
- Token system status
