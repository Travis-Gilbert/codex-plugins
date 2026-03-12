---
name: design-theory
description: >-
  Design principles, visual judgment, and layout architecture for web
  interfaces. Use when Claude Code needs to evaluate WHY a design works or
  fails, plan visual hierarchy and layout composition before writing code,
  choose between design approaches based on user behavior and cognitive
  load, review existing UI for design principle violations, build or extend
  a design token system, or reason about accessibility as a design concern
  rather than a compliance checkbox. Covers color theory, typography and
  measure, spacing systems, modular ratios, Gestalt principles, Fitts's
  Law, Hick's Law, progressive disclosure, affordances, signifiers,
  behavioral design, attention economics, and polymorphic object rendering.
  Always consult this skill before building new layouts or reviewing
  existing ones.
---

# Design Theory

## When to Load References

- Planning a layout or page structure: `references/layout-composition.md`
- Choosing colors, type, or spacing: `references/visual-fundamentals.md`
- Designing interactions or flows: `references/interaction-design.md`
- Working with defaults, nudges, or choice: `references/behavioral-design.md`
- Building or extending a token system: `references/design-systems.md`
- Rendering collections of mixed content: `references/object-rendering.md`
- Evaluating or improving accessibility: `references/accessibility.md`
- Handling responsive or mobile concerns: `references/responsive-strategy.md`

## Quick Decision Framework

Before writing any UI code, answer these questions:

1. **What is the user trying to accomplish on this screen?**
   The answer determines hierarchy: the primary task gets the most visual
   weight, secondary actions recede, and navigation stays predictable.

2. **What are the objects being displayed, and are they the same type?**
   If mixed types: use polymorphic rendering (see object-rendering.md).
   If same type: vary visual weight by priority, not by chrome.

3. **What states can this interface be in?**
   Default, loading, empty, error, success, disabled, destructive,
   skeleton, and mobile-collapsed. Design for all of them, not just the
   happy path with sample data.

4. **What is the user's next action after seeing this screen?**
   The answer determines what the primary affordance should be and where
   it should sit (Fitts's Law: near the current focus, large enough to
   target without precision).

5. **Does this design rely on color alone to communicate anything?**
   If yes, add a redundant signal (icon, label, position, pattern).

## Design Smell Catalog

These patterns indicate design problems. Flag them during review:

- **Uniform card grid for heterogeneous data.** Each object type deserves
  its own visual treatment. See object-rendering.md.
- **Decoration without hierarchy.** Gradients, shadows, and borders that
  do not establish visual priority are noise.
- **Placeholder-as-label.** Placeholders disappear on focus. Labels persist.
- **Color-only status.** Red/green status dots without text or icon fail
  for colorblind users and add no information for sighted users in a hurry.
- **Equal-weight everything.** When all cards, buttons, or sections have
  the same size and emphasis, nothing has emphasis.
- **Missing empty state.** A blank screen with no guidance is a dead end.
- **Desktop-only assumptions.** Side panels that become unusable below 768px.
  Hover-dependent interactions with no touch equivalent.
- **Motion without purpose.** Decorative animation on dense, task-focused
  screens increases cognitive load.
- **Symmetry as default.** Asymmetric layouts establish priority more
  effectively than grids of identical panels.
