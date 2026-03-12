# ui-design-pro

A Claude Code plugin that makes Claude Code extraordinarily good at web UI design and implementation by combining design theory, visual judgment, and source-code-backed implementation knowledge into a single, tightly coupled system.

## What This Is

A documentation plugin for Claude Code containing:

- **Two skills**: `design-theory` (WHY decisions) and `ui-engineering` (HOW to build)
- **Six specialized agents**: design-critic, visual-architect, component-builder, animation-engineer, a11y-auditor, stack-detector
- **Six slash commands**: `/design-review`, `/ui-build`, `/design-system`, `/a11y-audit`, `/animate`, `/detect-stack`
- **Reference source repos**: shadcn v4, Radix, Motion, Vaul, Sonner, cmdk, DaisyUI, Tailwind, Open Props
- **Curated design reference documents**: visual fundamentals, layout composition, interaction design, behavioral design, accessibility, responsive strategy

**What this is NOT**: A library, an npm package, or a runtime tool. Nothing here executes in production. It is all context for Claude Code.

## Core Philosophy: Polymorphic Object Rendering

This plugin rejects the "white card grid" as a default UI pattern. Each content type gets its own visual treatment based on what it *is*, not where it appears. A source citation, an essay preview, a field note, and a video project should look and behave differently — because they *are* different.

```tsx
// WRONG: Every item gets the same treatment
{items.map(item => <div className="rounded-lg bg-white shadow-sm p-6">...</div>)}

// RIGHT: Object type determines rendering strategy
const renderers: Record<ContentType, React.FC<RenderProps>> = {
  source:       SourceCard,       // Citation-dense, compact, link-forward
  essay:        EssayPreview,     // Lead paragraph, reading time, stage indicator
  fieldNote:    FieldNoteInline,  // Timestamp-anchored, minimal chrome
  shelfEntry:   ShelfTile,        // Visual-first, cover image, rating
  thread:       ThreadTrace,      // Connection-heavy, shows linked nodes
  videoProject: VideoTimeline,    // Phase indicator, thumbnail strip
};
```

## Installation

```bash
./install.sh
```

This clones the reference repos into `refs/` and makes all commands available. The `refs/` directory is gitignored (~200MB of source code).

## Commands

| Command | Agent | Purpose |
|---------|-------|---------|
| `/design-review <file>` | design-critic | Review UI for principle violations and polymorphic rendering opportunities |
| `/ui-build <description>` | component-builder | Build components with correct libraries and full state coverage |
| `/design-system` | visual-architect | Plan or audit a design token system |
| `/a11y-audit <file>` | a11y-auditor | WCAG 2.2 accessibility audit |
| `/animate <component>` | animation-engineer | Add motion with spring physics and reduced-motion support |
| `/detect-stack` | stack-detector | Map the project's existing UI stack |

## Reference Repos

After running `./install.sh`, these repos are available in `refs/`:

- `refs/shadcn-ui/` — shadcn v4 component registry
- `refs/radix-primitives/` — Radix headless accessible primitives
- `refs/radix-colors/` — Perceptual color scale system
- `refs/vaul/` — Mobile-first drawer with drag gestures
- `refs/sonner/` — Non-blocking toast notifications
- `refs/cmdk/` — Composable command palette
- `refs/daisyui/` — Tailwind-native component classes
- `refs/motion/` — Spring physics animation
- `refs/tailwindcss/` — Tailwind utility internals
- `refs/open-props/` — Battle-tested design token scales
- `refs/radix-ui-themes/` — Composed design system reference

## Design Skills

### design-theory

Covers visual fundamentals, layout composition, interaction design, behavioral design, design systems, polymorphic object rendering, accessibility, and responsive strategy. Load this **before writing code** to understand *why* a design decision is correct.

### ui-engineering

Covers library selection, component patterns, animation patterns, Tailwind strategy, state coverage, and stack detection. Load this **while writing code** to understand *how* to build correctly with real source-code-backed examples.

## Agent Composition

For most UI tasks, run agents in this order:

1. **stack-detector** — map what already exists
2. **visual-architect** — plan layout and hierarchy
3. **component-builder** — build the implementation
4. **design-critic** — review the result
5. **a11y-auditor** — verify accessibility
6. **animation-engineer** — add motion if relevant
