# Library Selection

## Decision Framework

Choose libraries in this priority order:

1. **What is already in the project?** Never add a library that duplicates existing functionality. Run stack-detector first.
2. **What does the project's framework support natively?** React 19 has native state and transitions; don't add a state library first.
3. **What is the simplest library that solves the problem?** Don't reach for a full component library if you need one primitive.
4. **Does it have source available in refs/?** If yes, you can verify the actual API.

---

## Component Library Tier

### Tier 1: Radix Primitives (Unstyled Headless)

**When to use:** Building a custom design system; need full styling control; accessibility cannot be compromised.

**What it provides:** Fully accessible, unstyled interactive components — Dialog, Dropdown, Select, Checkbox, Tabs, Accordion, Popover, Tooltip, and more.

**Source:** `refs/radix-primitives/packages/react/`

```tsx
import * as Dialog from '@radix-ui/react-dialog'

// Radix provides behavior + accessibility; you provide styling
<Dialog.Root>
  <Dialog.Trigger asChild>
    <Button>Open</Button>
  </Dialog.Trigger>
  <Dialog.Portal>
    <Dialog.Overlay className="fixed inset-0 bg-black/50" />
    <Dialog.Content className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 ...">
      <Dialog.Title>...</Dialog.Title>
      <Dialog.Close asChild>
        <Button variant="ghost">Close</Button>
      </Dialog.Close>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
```

### Tier 2: shadcn/ui (Styled Radix Wrappers)

**When to use:** Need styled components that match a Tailwind-based design system; want to own the code (components copied into the project, not a dependency).

**What it provides:** Radix primitives pre-styled with Tailwind. Configurable via `components.json`.

**Source:** `refs/shadcn-ui/apps/v4/registry/`

**Key difference from v3 to v4:** shadcn v4 restructured around composable primitives. Components like `Command` use `cmdk` under the hood. Check the actual registry files for current implementation.

```bash
# Detect if shadcn is in the project
ls components.json 2>/dev/null
ls src/components/ui/ 2>/dev/null
```

### Tier 3: DaisyUI (Tailwind CSS Plugin)

**When to use:** Rapid prototyping; Tailwind project that needs themed component classes without React component overhead; non-React frameworks.

**What it provides:** Semantic class names on top of Tailwind (`btn`, `card`, `modal`, etc.).

**Source:** `refs/daisyui/`

**Limitation:** Less flexible for custom polymorphic rendering — the component classes are opinionated. Better for conventional layouts.

### Tier 4: Radix Themes (Pre-designed System)

**When to use:** Internal tools where speed matters more than brand differentiation; admin dashboards; needs good defaults without design work.

**Source:** `refs/radix-ui-themes/`

---

## Overlay Library Tier

### Dialog / Modal: Radix Dialog

Built into Radix or shadcn. For standard modals and dialogs.

```tsx
import * as Dialog from '@radix-ui/react-dialog'
// or
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
```

**Source:** `refs/radix-primitives/packages/react/dialog/`

### Drawer / Sheet: Vaul

**When to use:** Mobile-first bottom sheets with snap points; drag-to-dismiss behavior; swipeable overlays.

**Source:** `refs/vaul/`

```tsx
import { Drawer } from 'vaul'

<Drawer.Root>
  <Drawer.Trigger asChild><Button>Open Drawer</Button></Drawer.Trigger>
  <Drawer.Portal>
    <Drawer.Overlay className="fixed inset-0 bg-black/40" />
    <Drawer.Content className="fixed bottom-0 left-0 right-0 mt-24 flex h-full max-h-[96%] flex-col rounded-t-[10px] bg-surface-2">
      <Drawer.Handle />
      {/* Content */}
    </Drawer.Content>
  </Drawer.Portal>
</Drawer.Root>
```

Key vaul features: `snapPoints`, `defaultSnap`, `fadeFromIndex` for multi-snap drawers.

### Toast / Notifications: Sonner

**When to use:** All toast/notification requirements. Sonner handles queue management, positioning, stacking, and animation correctly.

**Source:** `refs/sonner/`

```tsx
import { Toaster, toast } from 'sonner'

// In layout:
<Toaster position="bottom-right" richColors />

// In components:
toast.success('Profile updated')
toast.error('Failed to save', { description: 'Check your connection' })
toast.promise(saveProfile(), {
  loading: 'Saving...',
  success: 'Profile saved',
  error: 'Save failed',
})
```

### Command Palette: cmdk

**When to use:** Search-first navigation; global keyboard shortcut to find anything; power user feature.

**Source:** `refs/cmdk/`

```tsx
import { Command } from 'cmdk'

<Command.Dialog open={open} onOpenChange={setOpen}>
  <Command.Input placeholder="Type a command or search..." />
  <Command.List>
    <Command.Empty>No results found.</Command.Empty>
    <Command.Group heading="Pages">
      <Command.Item onSelect={() => router.push('/dashboard')}>
        Dashboard
      </Command.Item>
    </Command.Group>
  </Command.List>
</Command.Dialog>
```

---

## Animation Library

### Motion (formerly Framer Motion)

**When to use:** Layout animations; enter/exit animations; spring physics; drag gestures.

**Source:** `refs/motion/packages/motion/`

```tsx
import { motion, AnimatePresence } from 'motion/react'
```

**Never reach for Motion for:** Simple CSS transitions (color, opacity, hover states). Use CSS for those.

See `skills/ui-engineering/references/animation-patterns.md` for detailed Motion patterns.

---

## Color System

### Radix Colors

**When to use:** Any project needing a perceptually uniform color scale with dark mode built in.

**Source:** `refs/radix-colors/src/`

```css
/* Light mode scale */
@import '@radix-ui/colors/blue.css';
/* Dark mode scale */
@import '@radix-ui/colors/blue-dark.css';

/* Variables provided: --blue-1 through --blue-12 */
/* Step 9 is always the brand color */
/* Step 11 is always readable on white backgrounds */
/* Step 12 is always the highest contrast text color */
```

### Open Props

**When to use:** Pure CSS projects; systematic token scales without a JS framework.

**Source:** `refs/open-props/`

---

## CSS Framework

### Tailwind CSS v4

v4 changed significantly from v3. Key differences:
- Configuration moved from `tailwind.config.js` to `@theme` in CSS
- CSS custom properties are automatically generated from theme
- No `tailwind.config.js` file required
- `@import "tailwindcss"` replaces `@tailwind base/components/utilities`

```css
/* Tailwind v4 setup */
@import "tailwindcss";

@theme {
  --color-brand: oklch(0.50 0.21 245);
  --color-surface-1: oklch(0.97 0.01 265);
  --font-family-sans: system-ui, -apple-system, sans-serif;
  --radius-card: 12px;
}
```

**Source:** `refs/tailwindcss/`

---

## Selection Rules

| Need | First choice | Alternative |
|------|-------------|-------------|
| Modal/dialog | Radix Dialog | shadcn Dialog |
| Drawer/sheet | Vaul | Radix Dialog (desktop only) |
| Toast | Sonner | — |
| Command palette | cmdk | — |
| Select/combobox | Radix Select or cmdk | shadcn Select |
| Dropdown menu | Radix DropdownMenu | shadcn DropdownMenu |
| Tabs | Radix Tabs | shadcn Tabs |
| Accordion | Radix Accordion | shadcn Accordion |
| Checkbox/radio | Radix Checkbox/RadioGroup | shadcn form primitives |
| Date picker | shadcn Calendar (uses react-day-picker) | Radix Calendar |
| Data table | TanStack Table + shadcn DataTable | — |
| Form management | React Hook Form + Zod | — |
| Animation | motion/react | CSS transitions (for simple cases) |

---

## Anti-patterns

**Adding libraries you don't need:**
- Don't add `react-modal` if you already have Radix or shadcn
- Don't add `react-toastify` if you have Sonner
- Don't add `framer-motion` if the project already has `motion` (they're the same package)

**Using full libraries for one feature:**
- Don't add all of Material UI for one icon set — use Lucide or Heroicons instead
- Don't add Chakra UI for one styled button — use shadcn or build from Radix

**Mixing style systems:**
- Don't mix Tailwind with CSS Modules in the same component
- Don't mix DaisyUI component classes with manually constructed Tailwind components (duplication risk)
