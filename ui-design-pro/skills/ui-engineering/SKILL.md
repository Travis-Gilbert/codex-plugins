---
name: ui-engineering
description: >-
  Source-code-backed UI implementation expertise for React, Next.js, and
  Tailwind CSS ecosystems. Use when Claude Code needs to build, refactor,
  or extend UI components using shadcn, Radix, Vaul, Sonner, cmdk,
  DaisyUI, Motion, or Tailwind CSS. Use when selecting which library to
  reach for, building components from headless primitives, adding
  animation with performance awareness, detecting an existing project's
  UI stack, or ensuring full state coverage across all interaction states.
  Greps real library source code rather than relying on training data.
  Always pair with design-theory for design judgment before
  implementation.
---

# UI Engineering

## Workflow

1. **Detect the existing stack** before writing anything.
   - Run `scripts/detect_ui_stack.sh <repo-root>` or invoke /detect-stack.
   - Map what the project already ships: framework, CSS approach, component
     library, icon system, toast/drawer/dialog implementations.
   - NEVER build a parallel system next to one that already exists.

2. **Consult design-theory first** for new layouts.
   - Load the relevant design-theory reference for WHY decisions.
   - Sketch the layout architecture (hierarchy, density, object types)
     before selecting components.

3. **Select libraries from the decision matrix** in
   `references/library-selection.md`.
   - Always prefer what the project already ships.
   - For new additions, verify by grepping `refs/` source code.

4. **Build from primitives up** using `references/component-patterns.md`.
   - Headless behavior (Radix) + styled wrapper (Tailwind) + composition
   - Polymorphic rendering for mixed content types
   - Slot-based composition over prop explosion

5. **Add animation intentionally** using `references/animation-patterns.md`.
   - Motion for layout transitions and gesture-driven interactions
   - CSS transitions for simple state changes
   - Always respect `prefers-reduced-motion`

6. **Cover all states** using `references/state-coverage.md`.
   - Default, hover, focus-visible, pressed, disabled, loading, empty,
     error, success, destructive, skeleton, mobile-collapsed
   - Every state that is not explicitly handled is a bug

7. **Verify** with the repo's formatter, linter, typecheck, and tests.
   - If the work is visual, inspect in a browser at multiple widths.

## Reference Loading

- Library and dependency decisions: `references/library-selection.md`
- Component architecture and composition: `references/component-patterns.md`
- Animation and motion: `references/animation-patterns.md`
- Tailwind strategy and custom utilities: `references/tailwind-patterns.md`
- Full state coverage: `references/state-coverage.md`
- Project introspection: `references/stack-detection.md`

## Source Code Verification

Before writing implementation code that depends on a library API:

1. Grep the relevant `refs/` directory for the actual API
2. Check exports, prop types, and default behavior
3. If the API has changed from what training data suggests, use the source

Example verification workflow:
```bash
$ grep -r "export.*Dialog" refs/radix-primitives/packages/react/dialog/src/
$ grep -r "DrawerContent\|DrawerOverlay" refs/vaul/src/
$ grep -r "toast\|Toaster" refs/sonner/src/
$ grep -r "Command\|CommandInput" refs/cmdk/src/
```
