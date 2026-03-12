# UI-Design-Pro Plugin

You have access to a curated library of design theory, UI framework source
code, and specialized agent definitions. Use them.

## Two Skills, One System

This plugin has two complementary skills:

1. **design-theory**: Design principles, visual judgment, layout composition,
   behavioral design, and accessibility theory. Consult this BEFORE writing
   code to understand WHY a design decision is correct.

2. **ui-engineering**: Implementation patterns, library selection, animation,
   Tailwind strategy, and state coverage. Consult this WHEN writing code to
   understand HOW to build it correctly.

Most tasks require both skills. Plan with design-theory, build with
ui-engineering.

## Core Principle: Polymorphic Object Rendering

NEVER default to uniform card grids for mixed content. Each content type
gets its own visual treatment based on what it IS, not where it appears.
Read `skills/design-theory/references/object-rendering.md` before building
any collection, list, feed, or gallery component.

If you find yourself writing `items.map(item => <Card>...</Card>)` for
heterogeneous data, STOP. Consult the polymorphic renderer examples in
`examples/polymorphic-renderer/`.

## When to Use Reference Source Code

Do NOT rely on training data for library internals. Instead:

- **shadcn component questions**: grep `refs/shadcn-ui/apps/v4/registry/`
  for the actual component implementations. The v4 registry restructured
  everything around composable primitives.

- **Radix behavior questions**: grep `refs/radix-primitives/packages/react/`
  for the real accessibility, focus management, and interaction code.

- **Animation questions**: grep `refs/motion/packages/motion/` and
  `refs/motion/packages/motion-dom/` for spring physics, layout animation,
  and gesture handling internals.

- **Color system questions**: grep `refs/radix-colors/src/` for the actual
  scale construction. The scales are perceptually designed with dark mode
  built in.

- **Tailwind internals**: grep `refs/tailwindcss/` for plugin system, theme
  resolution, and utility generation. Particularly useful for custom plugins.

- **Design token patterns**: grep `refs/open-props/` for battle-tested token
  scales (spacing, type, easing, color) that work across frameworks.

- **Command palette patterns**: grep `refs/cmdk/` for keyboard navigation,
  filtering, and composable command structures.

- **Drawer/sheet patterns**: grep `refs/vaul/` for drag gesture handling,
  snap points, and mobile-first overlay behavior.

- **Toast patterns**: grep `refs/sonner/` for queue management, positioning,
  animation lifecycle, and action handling.

- **DaisyUI patterns**: grep `refs/daisyui/` for Tailwind-native component
  class composition and theme system internals.

## Agent System

Six agents, each with a distinct role:

| Agent | Role | When to Use |
|-------|------|-------------|
| design-critic | Reviews existing UI for principle violations | After build, during review |
| visual-architect | Plans layout and hierarchy before code | Before build, during design |
| component-builder | Selects libraries, builds from primitives | During build |
| animation-engineer | Motion patterns, spring physics, perf | When adding animation |
| a11y-auditor | WCAG 2.2, ARIA, focus, screen readers | During and after build |
| stack-detector | Reads project, maps existing UI layer | Before any work begins |

### Composition Rules

- ALWAYS run stack-detector before component-builder on a new project.
- ALWAYS consult visual-architect before component-builder on new layouts.
- ALWAYS run design-critic after component-builder on completed work.
- ALWAYS run a11y-auditor on any interactive component.
- animation-engineer is invoked when motion is relevant, not by default.

### Cross-Reference with Other Plugins

If the project also uses JS-Pro or Django-Design:

- For React internals (hooks, server components, compiler): defer to JS-Pro
  react-specialist and its refs/react-main/ source.
- For D3 visualization: defer to JS-Pro data-analyst and its D3 examples.
- For Django template + HTMX frontend: defer to Django-Design django-frontend.
- This plugin owns: design judgment, component library selection, animation,
  accessibility, visual architecture, and the polymorphic rendering philosophy.
