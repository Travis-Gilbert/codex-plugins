# UI-Design-Pro: Claude Code UI & Design Expertise Plugin

> A Claude Code plugin that makes Claude Code extraordinarily good at web UI design and implementation by combining design theory, visual judgment, and source-code-backed implementation knowledge into a single, tightly coupled system.

**What this is**: A skill directory for Claude Code containing two complementary skills (design theory + UI engineering), specialized agent definitions, framework source repos, and curated design reference documents. When Claude Code works inside this directory (or a project that references it), it can reason about *why* a layout works before writing *how* to build it, then grep through the actual source of shadcn, Radix, Motion, and others to produce code grounded in real implementations.

**What this is NOT**: A library, an npm package, or a runtime tool. Nothing here executes in production. It is all context for Claude Code.

---

## The Problem

Claude Code can write Tailwind. It cannot tell you why your interface feels wrong.

1. **No design judgment**. Claude Code defaults to the same visual vocabulary for every task: white cards with rounded corners, uniform grids, and decorative gradients. It has no concept of visual hierarchy, cognitive load, or when spacing is doing structural work versus decorative work. It treats design as cosmetic rather than functional.

2. **Generic object rendering**. The default AI approach to displaying a collection of items is to wrap each one in an identical card component. A research source, a video project, a field note, and a shelf entry all get the same `rounded-lg bg-white shadow-sm p-6` treatment. This destroys information architecture. Each object type carries different meaning, different affordances, and different user intent. A polymorphic renderer that adapts visual treatment to object type communicates structure that uniform cards flatten.

3. **Stale library knowledge**. shadcn/ui v4 restructured its entire registry system. Radix Colors ships a proper scale system. Motion (formerly Framer Motion) reorganized into `motion-dom` and `motion-utils`. Training data lags behind source code. Having the actual repos means Claude Code can look up what a component really does by reading the implementation.

4. **Surface-level patterns**. Claude Code knows Radix API signatures but not the internals. When debugging why a custom `Popover` loses focus management in a nested context, the answer is in the Radix source, not in Stack Overflow.

5. **Disconnected theory and practice**. Knowing Fitts's Law is useless if you cannot translate it into a Tailwind class decision. Knowing that `motion` supports layout animations is useless if you do not know *when* layout animation helps versus hinders. This plugin bridges the gap: design theory informs the decision, source code informs the implementation.

6. **Missing state coverage**. Claude Code builds the happy path and stops. Loading, empty, error, disabled, destructive, hover, focus-visible, pressed, skeleton, and mobile collapse states are where real products live. The review system catches what the build system skips.

---

## Core Design Philosophy: Polymorphic Object Rendering

This plugin rejects the "white card grid" as a default UI pattern. Instead, it teaches Claude Code to think about UI through object-type-aware rendering:

### The Anti-Pattern

```tsx
// WRONG: Every item gets the same card treatment
{items.map(item => (
  <div className="rounded-lg bg-white shadow-sm p-6">
    <h3>{item.title}</h3>
    <p>{item.description}</p>
  </div>
))}
```

This treats a research source, a video project, and a field note as visually identical. It communicates nothing about what each object *is* or what the user can *do* with it.

### The Principle

Each content type declares its own visual identity. A renderer maps object type to visual treatment. Visual differentiation communicates information architecture without requiring the user to read labels.

```tsx
// RIGHT: Object type determines rendering strategy
const renderers: Record<ContentType, React.FC<RenderProps>> = {
  source:       SourceCard,       // Citation-dense, compact, link-forward
  essay:        EssayPreview,     // Lead paragraph, reading time, stage indicator
  fieldNote:    FieldNoteInline,  // Timestamp-anchored, minimal chrome, diary feel
  shelfEntry:   ShelfTile,        // Visual-first, cover image, rating
  thread:       ThreadTrace,      // Connection-heavy, shows linked nodes
  videoProject: VideoTimeline,    // Phase indicator, thumbnail strip, status
};

function ObjectRenderer({ item }: { item: ContentItem }) {
  const Renderer = renderers[item.type];
  return <Renderer data={item} />;
}
```

### What This Means in Practice

- **Different content types get different visual weight, density, and interaction models.** A source citation is compact and link-forward. An essay preview leads with prose. A field note feels like a timestamped journal entry.
- **Shared chrome is minimal.** Instead of wrapping everything in the same card, the renderer applies only the visual treatment that the content type needs. Some types need a border. Some need a background. Some need neither.
- **Collections are heterogeneous by default.** A feed of mixed content types should feel like a curated editorial layout, not a database dump rendered through a single template.
- **Design tokens still unify the system.** Polymorphic rendering does not mean visual chaos. Shared type scales, spacing rhythms, and color semantics tie different renderers into a coherent visual language.

This philosophy must inform every agent in the plugin. The design-critic should flag uniform card grids as a design smell. The visual-architect should plan object-type-aware layouts before any code is written. The component-builder should scaffold render maps, not generic card components.

---

## Directory Structure

```
ui-design-pro/
├── CLAUDE.md                              # Plugin root config
├── .claude-plugin/
│   └── plugin.json                        # Plugin manifest
├── install.sh                             # Clone repos + register commands
│
├── skills/
│   ├── design-theory/                     # Skill 1: Design principles and judgment
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── visual-fundamentals.md     # Color, type, spacing, ratios, grids
│   │       ├── layout-composition.md      # Hierarchy, Gestalt, scanning, whitespace
│   │       ├── interaction-design.md      # Affordances, Fitts, disclosure, cognitive load
│   │       ├── behavioral-design.md       # Nudge theory, defaults, choice architecture
│   │       ├── design-systems.md          # Tokens, variants, state matrices, naming
│   │       ├── object-rendering.md        # Polymorphic rendering philosophy and patterns
│   │       ├── accessibility.md           # WCAG 2.2, ARIA, focus management, contrast
│   │       └── responsive-strategy.md     # Mobile-first, breakpoints, touch, containers
│   │
│   └── ui-engineering/                    # Skill 2: Implementation expertise
│       ├── SKILL.md
│       └── references/
│           ├── library-selection.md       # When to reach for what (decision matrix)
│           ├── component-patterns.md      # Building from primitives, composition
│           ├── animation-patterns.md      # Motion, springs, layout, reduced-motion
│           ├── tailwind-patterns.md       # Utility strategy, custom plugins, v4 changes
│           ├── state-coverage.md          # Every UI state, with implementation examples
│           └── stack-detection.md         # Project introspection procedures
│
├── agents/
│   ├── design-critic.md                   # Reviews UI for design principle violations
│   ├── visual-architect.md                # Plans layout and hierarchy before code
│   ├── component-builder.md               # Knows which library to reach for
│   ├── animation-engineer.md              # Motion patterns, performance, accessibility
│   ├── a11y-auditor.md                    # WCAG 2.2 deep expertise
│   └── stack-detector.md                  # Reads project, maps what exists
│
├── commands/
│   ├── design-review.md                   # /design-review  (triggers design-critic)
│   ├── ui-build.md                        # /ui-build       (triggers component-builder)
│   ├── design-system.md                   # /design-system   (triggers visual-architect)
│   ├── a11y-audit.md                      # /a11y-audit      (triggers a11y-auditor)
│   ├── animate.md                         # /animate         (triggers animation-engineer)
│   └── detect-stack.md                    # /detect-stack    (triggers stack-detector)
│
├── refs/                                  # Cloned framework and library source code
│   ├── shadcn-ui/                         # shadcn-ui/ui (v4 component registry)
│   ├── radix-primitives/                  # radix-ui/primitives (headless accessible)
│   ├── radix-colors/                      # radix-ui/colors (color scale system)
│   ├── vaul/                              # emilkowalski/vaul (drawer patterns)
│   ├── sonner/                            # emilkowalski/sonner (toast patterns)
│   ├── cmdk/                              # pacocoursey/cmdk (command palette)
│   ├── daisyui/                           # saadeghi/daisyui (Tailwind component layer)
│   ├── motion/                            # motiondivision/motion (animation)
│   ├── tailwindcss/                       # tailwindlabs/tailwindcss (utility internals)
│   ├── open-props/                        # argyleink/open-props (design token reference)
│   └── radix-ui-themes/                   # radix-ui/themes (composed design system)
│
├── scripts/
│   ├── detect_ui_stack.sh                 # Project introspection (from codex-plugins)
│   └── install_refs.sh                    # Clone all reference repos
│
└── examples/
    ├── polymorphic-renderer/              # Object-type-aware rendering patterns
    │   ├── render-map.tsx                 # Type-to-component mapping
    │   ├── content-variants.tsx           # Different density/chrome per type
    │   └── mixed-feed.tsx                 # Heterogeneous collection layout
    ├── design-token-scales/               # Real spacing, type, and color scales
    │   ├── spacing-scale.md               # 4/8/12/16/24/32/48/64 system
    │   ├── type-scale.md                  # Modular scales with line-height pairing
    │   └── color-construction.md          # Building semantic from primitive
    └── state-matrices/                    # Component state coverage templates
        ├── button-states.md               # Full button state matrix
        ├── form-field-states.md           # Input, select, textarea state matrix
        └── data-display-states.md         # Table, list, card state matrix
```

---

## CLAUDE.md (Plugin Root Config)

```markdown
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
```

---

## Plugin Manifest

```json
{
  "name": "ui-design-pro",
  "version": "1.0.0",
  "description": "UI design theory and implementation toolkit. Two skills: design-theory (visual fundamentals, layout composition, interaction design, behavioral design, accessibility, polymorphic object rendering) and ui-engineering (component building, library selection, animation, Tailwind patterns, state coverage, stack detection). Source-code-backed with shadcn v4, Radix, Motion, and more. Agents for design critique, visual architecture, component building, animation, accessibility audit, and project stack detection.",
  "author": {
    "name": "Travis Gilbert"
  },
  "keywords": [
    "design", "ui", "ux", "tailwind", "shadcn", "radix", "motion",
    "accessibility", "wcag", "animation", "components", "design-system",
    "color-theory", "typography", "spacing", "layout", "responsive",
    "vaul", "sonner", "cmdk", "daisyui", "react", "next"
  ]
}
```

---

## Skill 1: design-theory

### SKILL.md

```markdown
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
```

### Reference Files (design-theory)

Each reference file is a curated, opinionated document. These are not textbook reproductions. They are practical design rules with rationale and Tailwind-applicable guidance.

#### references/visual-fundamentals.md (outline)

```markdown
# Visual Fundamentals

## Color Theory for Interfaces
- Hue, saturation, lightness as independent variables
- Semantic color: primary, destructive, warning, success, muted, accent
- Constructing scales: Radix Colors approach (12 steps, perceptual uniformity)
- Dark mode: not inversion, independent scale selection
- Contrast ratios: WCAG AA (4.5:1 text, 3:1 large text/UI), AAA (7:1)
- When to use color vs. when to use position, size, or typography
- Tailwind color utility strategy: extend with CSS variables, not hardcode

## Typography and Measure
- Type scale construction: modular ratios (1.2 minor third, 1.25 major)
- Line height pairing: tighter at display sizes, looser at body sizes
- Measure (line length): 45-75 characters for readability
- Hierarchy through weight and size, not through decoration
- Font pairing: one family with weight variation > two families
- Tailwind type utilities: prose plugin for long-form, custom scale for UI

## Spacing Systems
- Base unit: 4px (0.25rem). Primary scale: 4/8/12/16/24/32/48/64.
- Spatial relationships communicate grouping (Gestalt proximity)
- Padding vs. gap vs. margin: padding is internal, gap is between siblings,
  margin is external relationship to context
- Consistent spacing rhythm: every spacing value should come from the scale
- Tailwind spacing: use the default scale, extend only with named tokens

## Ratios and Proportions
- Golden ratio (1.618) for layout splits (sidebar:content)
- Rule of thirds for asymmetric composition
- Modular scale for consistent sizing progression
- Aspect ratios for media containers (16:9, 4:3, 1:1, 3:4)

## Visual Weight and Density
- Weight signals: size, color saturation, contrast, whitespace, position
- High-density UI (tables, dashboards): reduce chrome, increase data-ink ratio
- Low-density UI (marketing, onboarding): increase whitespace, reduce choices
- Density should match the user's task frequency and expertise level
```

#### references/object-rendering.md (outline)

```markdown
# Polymorphic Object Rendering

## The Problem with Uniform Cards
- Every AI-generated UI defaults to the same card component for every item
- This destroys information architecture: a source citation, an essay preview,
  a field note, and a video project all carry different meaning
- Uniform rendering forces users to READ to distinguish types that should be
  VISUALLY distinct

## The Polymorphic Renderer Pattern
- Each content type declares its own visual treatment
- A render map associates type discriminant to component
- Visual differentiation communicates type without labels
- Shared design tokens (spacing, color, type) unify without homogenizing

## Implementation Patterns

### TypeScript Render Map
- Discriminated union for content types
- Record<ContentType, React.FC<Props>> for the renderer
- Fallback component for unknown types (never silently drop)
- Props interface that each renderer extends, not conforms to

### Visual Differentiation Strategies
- **Density**: sources are compact/citation-dense; essays lead with prose
- **Chrome**: some types get borders, some get backgrounds, some get neither
- **Orientation**: horizontal for media-forward, vertical for text-forward
- **Emphasis**: primary content gets full treatment; linked/referenced content
  gets reduced/inline treatment
- **Status indicators**: per-type progress or state (draft/published/archived)

### Collection Layout Strategies
- **Heterogeneous feed**: mixed types in a single stream, each self-describing
- **Grouped by type**: sections with type-specific rendering within each
- **Hierarchical**: primary objects at full width, related objects nested/compact
- **Graph-aware**: objects positioned by relationship, not by list order

## Common Content Types and Their Visual Identity
- **Source/Citation**: compact, URL-forward, metadata-dense, link-colored accent
- **Essay/Article**: headline + lead paragraph, reading time, stage badge
- **Field Note**: timestamp-anchored, minimal chrome, handwritten feel
- **Shelf Entry**: cover-image-forward, rating, compact metadata
- **Research Thread**: connection indicator, node count, thread-trace feel
- **Video/Media**: thumbnail strip, phase indicator, timeline affordance
- **Tool/Utility**: icon-forward, description, action-oriented
- **Person/Entity**: avatar, role, relationship context

## Anti-Patterns
- `items.map(item => <Card>)` for heterogeneous data
- Adding a `type` badge to a uniform card instead of changing the card
- Using only color to distinguish types
- Forcing all types into the same aspect ratio or grid cell size
```

#### references/layout-composition.md (outline)

```markdown
# Layout Composition

## Gestalt Principles Applied to UI
- Proximity: elements near each other are perceived as grouped
- Similarity: elements that look alike are perceived as related
- Continuity: aligned elements feel connected
- Closure: incomplete shapes are perceived as complete
- Figure/ground: contrast separates foreground from background
- Common region: shared background or border groups elements

## Visual Hierarchy
- Size: larger elements draw attention first
- Contrast: high-contrast elements emerge from low-contrast surroundings
- Position: top-left in LTR, top-center for headlines
- Whitespace: isolated elements gain emphasis
- Depth: elevation (shadow, overlay) creates layers of importance

## Scanning Patterns
- F-pattern: information-dense pages (articles, search results)
- Z-pattern: minimal pages (landing, hero sections)
- Gutenberg diagram: gravity pulls attention bottom-right
- Implications for action placement and content ordering

## Composition Strategies
- **Asymmetric split**: sidebar (1/3) + content (2/3) for navigation contexts
- **Stack**: single-column for focused flows (forms, onboarding, articles)
- **Dashboard grid**: asymmetric card sizing to establish priority
- **Gallery**: masonry or grid based on content aspect ratios
- **Timeline**: vertical axis for chronological, horizontal for phases

## Whitespace as Structure
- Whitespace is not empty space; it is a structural element
- Macro whitespace: separates sections, establishes page rhythm
- Micro whitespace: separates elements within a component
- Increasing whitespace between groups signals a boundary
- Decreasing whitespace within a group signals belonging
```

#### references/interaction-design.md (outline)

```markdown
# Interaction Design

## Affordances and Signifiers
- Affordance: what an object allows you to do
- Signifier: what indicates the affordance exists
- Buttons afford clicking: signified by raised appearance, color contrast
- Links afford navigation: signified by color, underline, cursor change
- Inputs afford text entry: signified by border, placeholder, label
- Missing signifiers: flat buttons that look like labels, icon-only actions

## Fitts's Law
- Time to reach a target = f(distance to target / size of target)
- Primary actions should be large and near the current focus
- Destructive actions should be small and separated from primary flow
- Touch targets: minimum 44x44px (Apple), 48x48dp (Material)
- Edge and corner targets are fastest (infinite edge)

## Hick's Law
- Decision time increases logarithmically with number of choices
- Reduce visible options: progressive disclosure, smart defaults
- Group related options: chunk choices into categories
- Highlight recommended: reduce decision weight by pre-selecting

## Progressive Disclosure
- Show only what the user needs at each step
- Primary controls visible; advanced controls behind a disclosure
- Wizard patterns for multi-step processes
- Expand-in-place for related details

## Cognitive Load
- Intrinsic load: the complexity of the task itself (irreducible)
- Extraneous load: complexity added by bad design (reducible)
- Germane load: effort that aids learning (desirable)
- Reduce extraneous: remove decoration, simplify choices, group logically
- Support germane: clear labels, consistent patterns, helpful feedback

## Feedback and Response
- Acknowledge every user action (loading spinner, skeleton, optimistic UI)
- Match feedback weight to action weight (toast for save, dialog for delete)
- Inline feedback for field-level issues, summary for form-level issues
- Silence is the worst feedback: never let an action appear to do nothing
```

#### references/behavioral-design.md (outline)

```markdown
# Behavioral Design

## Default Effects
- The pre-selected option is chosen far more often
- Use defaults to guide toward the most common or safest choice
- Never use defaults to trick users into unwanted options
- In forms: pre-fill what you know, leave sensitive fields empty

## Choice Architecture
- The way choices are presented affects which choice is made
- Order effects: first and last items are chosen more often
- Anchoring: the first number seen influences subsequent judgment
- Framing: "95% success rate" vs "5% failure rate"

## Attention Economics
- Attention is finite and non-renewable within a session
- Every element on screen competes for attention
- The cost of a UI element is not just pixels; it is attention budget
- Reduce attention cost: fewer elements, stronger hierarchy, clear paths

## Nudge Theory (applied to UI)
- Make the desired action the easiest action
- Remove friction from positive paths, add friction to destructive ones
- Social proof: "12 people are viewing this" (use honestly)
- Loss aversion: "unsaved changes will be lost" (use for real consequences)

## Error Prevention over Error Recovery
- Constrain inputs to valid ranges
- Disable impossible actions rather than showing errors after submission
- Confirmation dialogs only for destructive or irreversible actions
- Undo is better than "are you sure?" for most reversible actions
```

#### references/design-systems.md (outline)

```markdown
# Design Systems

## Token Hierarchy
- **Primitive tokens**: raw values (color-blue-500: #3b82f6)
- **Semantic tokens**: meaning-mapped (color-primary: var(--color-blue-500))
- **Component tokens**: scoped (button-bg: var(--color-primary))
- Each layer references the one below; never skip layers
- Tailwind implementation: CSS custom properties + theme extension

## Variant and State Matrices
- Every component has variants (size, color, style) and states (hover,
  focus, disabled, loading, error, active, pressed)
- Document the full matrix before building; missing cells become bugs
- Example: Button has [default, primary, destructive, ghost, outline] x
  [default, hover, focus-visible, pressed, disabled, loading]

## Naming Conventions
- Descriptive, not aesthetic: "primary" not "blue", "destructive" not "red"
- Size scale: "sm", "default", "lg" (not "small", "medium", "large" in CSS)
- State naming: match HTML/CSS convention where possible (disabled, not inactive)

## Component API Design
- Props should be semantic, not stylistic: `variant="destructive"` not `color="red"`
- Composition over configuration: prefer slot patterns over prop explosion
- Radix model: headless primitive + styled wrapper
- shadcn model: copy-and-own source, not installed dependency

## Design System Governance
- Tokens change rarely; components change sometimes; pages change often
- Breaking changes to tokens cascade everywhere; treat token changes as major
- Document decisions, not just APIs: "why 4px base unit" matters more than "base unit is 4px"
```

#### references/accessibility.md (outline)

```markdown
# Accessibility

## WCAG 2.2 Core Requirements
- Perceivable: text alternatives, captions, contrast, resize, orientation
- Operable: keyboard, timing, seizure safety, navigation, input modalities
- Understandable: readable, predictable, input assistance
- Robust: compatible with assistive technologies, parsing

## Contrast and Color
- AA: 4.5:1 for normal text, 3:1 for large text and UI components
- AAA: 7:1 for normal text, 4.5:1 for large text
- Never use color as the only way to communicate information
- Test with simulated color vision deficiency tools

## Keyboard Navigation
- Every interactive element must be keyboard-reachable
- Tab order must follow visual order (do not rearrange with tabindex > 0)
- Focus must be visible (focus-visible, not focus for mouse users)
- Focus trapping in modals: focus stays within, Escape dismisses
- Skip-to-content link for page-level keyboard navigation

## ARIA Patterns
- Use semantic HTML first; ARIA is a supplement, not a replacement
- Roles: dialog, alert, alertdialog, navigation, tab, tabpanel, menu
- States: aria-expanded, aria-selected, aria-pressed, aria-disabled
- Properties: aria-label, aria-labelledby, aria-describedby, aria-live
- Live regions: aria-live="polite" for non-urgent, "assertive" for urgent

## Focus Management
- After opening a dialog: move focus to the first interactive element
- After closing a dialog: return focus to the trigger
- After deleting an item: move focus to the next item or a stable landmark
- After form submission: move focus to the result or the error summary

## Touch and Pointer
- Minimum touch target: 44x44px (or 24x24px with 44x44px spacing)
- Drag-and-drop must have a keyboard alternative
- Hover-dependent content must have a focus or click equivalent
- Pointer cancellation: actions fire on release (pointerup), not on press

## Screen Reader Testing
- Test with VoiceOver (macOS/iOS), NVDA (Windows), TalkBack (Android)
- Verify: heading hierarchy, link text, button labels, form labels,
  image alt text, table structure, live region announcements
```

#### references/responsive-strategy.md (outline)

```markdown
# Responsive Strategy

## Mobile-First Implementation
- Start with the smallest viewport and add complexity
- Tailwind: write base styles first, add sm:/md:/lg: overrides
- Content priority: what matters most on a 320px screen?
- If it does not matter on mobile, question whether it matters at all

## Breakpoint Strategy
- Do not design for devices; design for content
- Add a breakpoint when the layout breaks, not at arbitrary widths
- Standard Tailwind breakpoints are starting points, not mandates
- Test at 320px, 375px, 768px, 1024px, 1280px, and 1536px

## Container Queries
- Use container queries for components that live in variable-width contexts
- A card in a sidebar vs. a card in main content should adapt to its container
- Tailwind @container support: define container, query with @sm/@md/@lg

## Touch Targets and Reachability
- Bottom of screen is most reachable on mobile (thumb zone)
- Primary actions should be thumb-reachable, not top-right
- Navigation patterns: bottom tab bar, drawer from bottom, not top hamburger
- Sticky headers + sticky footers together steal too much vertical space

## Responsive Patterns
- **Collapse**: side panel becomes drawer or bottom sheet
- **Stack**: horizontal layout becomes vertical
- **Truncate**: long text gets ellipsis with expand affordance
- **Remove**: decorative elements hidden on small screens
- **Reorder**: CSS order or conditional rendering for priority changes
```

---

## Skill 2: ui-engineering

### SKILL.md

```markdown
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
$ grep -r "export.*Dialog" refs/radix-primitives/packages/react/dialog/src/
$ grep -r "DrawerContent\|DrawerOverlay" refs/vaul/src/
$ grep -r "toast\|Toaster" refs/sonner/src/
$ grep -r "Command\|CommandInput" refs/cmdk/src/
```

### Reference Files (ui-engineering)

#### references/library-selection.md

```markdown
# Library Selection

## Reference Roles
- shadcn-ui/ui (v4): component architecture model, copy-and-own pattern,
  composable registry. Grep `refs/shadcn-ui/apps/v4/registry/new-york-v4/ui/`
- Radix Primitives: accessibility and behavior baseline for all overlays,
  menus, selects, tabs, accordions. Grep `refs/radix-primitives/packages/react/`
- Radix Colors: perceptual color scale system with dark mode built in.
  Grep `refs/radix-colors/src/`
- Radix Themes: composed design system reference for how tokens, components,
  and layouts fit together. Grep `refs/radix-ui-themes/`
- Vaul: mobile-first drawer/sheet with drag gestures and snap points.
  Grep `refs/vaul/src/`
- Sonner: non-blocking toast with queue, positioning, action handling.
  Grep `refs/sonner/src/`
- cmdk: command palette with keyboard navigation and composable commands.
  Grep `refs/cmdk/src/`
- DaisyUI: Tailwind-native component classes and theme system.
  Grep `refs/daisyui/src/`
- Motion: animation library with spring physics, layout animation, gestures.
  Grep `refs/motion/packages/motion/src/`
- Open Props: battle-tested design token scales.
  Grep `refs/open-props/src/`

## Component Choice Matrix
| Need | Default Choice | Why | Verify In |
|------|---------------|-----|-----------|
| Dialog, popover, menu, select, tabs | Radix primitive + Tailwind wrapper | Accessible, composable, ownable | refs/radix-primitives/ |
| Mobile drawer, bottom sheet | Vaul | Drag gestures, snap points, touch-native | refs/vaul/ |
| Toast, notification | Sonner | Clean queue, stack behavior, action slots | refs/sonner/ |
| Command palette, search | cmdk | Keyboard-native, composable, filterable | refs/cmdk/ |
| Animation, layout transition | Motion | Spring physics, layout projection, gestures | refs/motion/ |
| Component architecture model | shadcn v4 registry | Copy-and-own, composable, well-structured | refs/shadcn-ui/ |
| Color scales | Radix Colors | 12-step perceptual, dark mode built in | refs/radix-colors/ |
| Design tokens | Open Props | Spacing, easing, type scales | refs/open-props/ |
| Tailwind component classes | DaisyUI | Theme system, semantic class names | refs/daisyui/ |
| Icons | Existing set first; else Iconoir or Lucide | Consistency over variety | project-specific |

## Dependency Rules
- Reuse what the repo already ships before adding new packages.
- If the repo has a dialog, drawer, or toast: extend it, do not replace it.
- In Next.js, keep the server/client boundary deliberate. UI libraries are
  not a reason to move whole routes to 'use client'.
- Prefer one icon set per project. Mixing sets breaks visual rhythm.
- Prefer CSS variables for theme tokens over Tailwind config extension when
  the project needs runtime theming.
```

#### references/component-patterns.md (outline)

```markdown
# Component Patterns

## Composition Model
- Headless primitive (behavior + accessibility) from Radix or equivalent
- Styled wrapper using Tailwind utilities
- Slot pattern: children compose into named positions
- Compound component: Parent provides context, children consume it

## Polymorphic Component Building
- Accept `as` or `asChild` prop for element polymorphism
- Render map for content-type polymorphism (see object-rendering.md)
- Type-safe discriminated unions in TypeScript

## shadcn v4 Architecture
- Registry-based: components registered with metadata
- New-York style: the default variant with refined defaults
- File structure: one file per component, exports from index
- CVA (class-variance-authority) for variant management
- tailwind-merge for class conflict resolution

## Composition Boundaries
- Keep components small and single-purpose
- Use composition (children, slots) over configuration (many props)
- Data fetching at the page level, rendering at the component level
- In Next.js: server components for data + static structure, client
  components only for interaction, local state, or browser APIs

## Form Patterns
- Controlled vs. uncontrolled: prefer controlled for validation
- Field component: label + input + description + error in one composable
- Validation: field-level inline, form-level summary near submit
- Accessible labels: always visible, never placeholder-only
```

#### references/animation-patterns.md (outline)

```markdown
# Animation Patterns

## When to Animate
- State transitions: entering/exiting, expanding/collapsing
- Layout changes: reordering, resizing, repositioning
- Feedback: success, error, loading progress
- Navigation: page transitions, route changes
- Gesture response: drag, swipe, pinch

## When NOT to Animate
- Dense task-focused screens where motion distracts
- Repeated interactions (the 100th toast does not need a flourish)
- When the user has set prefers-reduced-motion: reduce

## Motion Library Usage (refs/motion/)
- `motion.div` for declarative enter/exit animations
- `AnimatePresence` for exit animations before unmount
- `layout` prop for automatic layout animation
- `useSpring` for spring-based values
- `useDragControls` for drag gestures
- Verify API in refs/motion/packages/motion/src/

## CSS Transitions for Simple Cases
- Prefer CSS transition for hover, focus, color, and opacity changes
- Tailwind: transition-colors, transition-opacity, duration-150
- No library needed for single-property state changes

## Performance
- Animate transform and opacity (composited properties)
- Avoid animating width, height, top, left (trigger layout)
- Motion's layout animation handles this correctly by default
- will-change: use sparingly, remove after animation completes

## Reduced Motion
- Always check prefers-reduced-motion
- Tailwind: motion-safe: and motion-reduce: variants
- Motion: respects reduced motion when using layout animations
- Fallback: instant state change with no transition
```

#### references/state-coverage.md

```markdown
# State Coverage

## The Full State Matrix

Every interactive UI element exists in some combination of these states.
If your implementation does not handle a state, that state is a bug that
users will encounter.

### Interaction States
- **Default**: the resting state with no user interaction
- **Hover**: pointer over the element (desktop)
- **Focus-visible**: keyboard focus (visible ring, not on mouse click)
- **Pressed/Active**: during click or tap
- **Disabled**: interaction is not available
- **Loading**: action is in progress, outcome unknown
- **Dragging**: element is being repositioned

### Data States
- **Empty**: no data to display (distinct from loading)
- **Error**: data fetch or action failed
- **Success**: action completed successfully
- **Partial**: some data loaded, more available (pagination, infinite scroll)
- **Stale**: data is present but may be outdated

### Content States
- **Skeleton**: placeholder while content loads
- **Truncated**: content exceeds available space
- **Overflow**: content exceeds container (scroll, ellipsis, expand)
- **Collapsed**: content hidden behind disclosure

### Responsive States
- **Mobile collapsed**: content reorganized for small viewport
- **Touch mode**: larger targets, different interaction patterns
- **Reduced motion**: animations minimized or removed

## Implementation Checklist

For each component, verify:
- [ ] Default state renders correctly with real content
- [ ] Hover state has visible feedback (not just cursor change)
- [ ] Focus-visible state has a clear ring/outline
- [ ] Disabled state is visually distinct AND not interactive
- [ ] Loading state shows progress or indeterminate indicator
- [ ] Empty state explains what should be here and how to add it
- [ ] Error state is actionable (retry, fix, contact support)
- [ ] Success state matches the weight of the action
- [ ] Skeleton matches the shape of the content it replaces
- [ ] Mobile layout is usable at 320px width
- [ ] Keyboard-only navigation works for all interactive elements
- [ ] Screen reader announces state changes via aria-live

## State Transitions

- Loading to success: show result, toast confirmation for async
- Loading to error: show error with retry action
- Empty to populated: no jarring layout shift
- Expanded to collapsed: animate with purpose, instant for dense UIs
- Enabled to disabled: explain why (tooltip or inline text)
```

---

## Agent Definitions

### agents/design-critic.md

```yaml
---
name: design-critic
description: >-
  Reviews existing UI for design principle violations, visual hierarchy
  problems, and polymorphic rendering opportunities. Use for: "Review this
  page for design issues", "Why does this layout feel wrong?", "Audit the
  visual hierarchy of this dashboard".
model: claude-sonnet-4-20250514
color: magenta
tools:
  - Read
  - Grep
  - Glob
  - LS
---
```

```markdown
# Design Critic

You are a design critic who evaluates UI implementations against design
theory principles. You find problems that code reviewers miss: hierarchy
failures, cognitive load issues, missing states, uniform rendering of
heterogeneous data, and accessibility gaps.

## Review Process

1. Read the component or page code to understand what it renders.
2. Load `skills/design-theory/references/layout-composition.md` for
   hierarchy and composition evaluation.
3. Load `skills/design-theory/references/object-rendering.md` to check
   whether the rendering is polymorphic where it should be.
4. Evaluate against the Design Smell Catalog in the design-theory SKILL.md.
5. Check state coverage against `skills/ui-engineering/references/state-coverage.md`.

## Severity Levels

- **Critical**: Accessibility violation, broken interaction, missing
  essential state (empty, error, loading).
- **Should fix**: Hierarchy failure, uniform card grid for mixed types,
  missing hover/focus states, mobile breakage.
- **Polish**: Spacing rhythm inconsistency, animation timing, micro-copy
  improvement, icon consistency.

## Output Format

For each finding:
1. What the problem is (specific, not vague)
2. Where it is (file, line range, component)
3. Why it matters (which design principle it violates)
4. How to fix it (concrete suggestion, not "improve the hierarchy")

## Things You Always Check
- Is heterogeneous data rendered through a uniform card component?
- Is there a clear primary action per region?
- Does the layout establish priority through asymmetry?
- Are empty, error, and loading states explicit?
- Does anything rely on color alone to communicate meaning?
- Would a first-time user understand what to do on this screen?
- Does the spacing follow a consistent scale?
- Is there hover/focus-visible feedback on all interactive elements?
```

### agents/visual-architect.md

```yaml
---
name: visual-architect
description: >-
  Plans layout architecture, visual hierarchy, and composition before code
  is written. Use for: "Design the layout for a settings page", "Plan the
  information architecture for this dashboard", "How should I structure
  this multi-step form?".
model: claude-sonnet-4-20250514
color: cyan
tools:
  - Read
  - Grep
  - Glob
  - LS
---
```

```markdown
# Visual Architect

You plan the visual structure of interfaces before any code is written.
You think in terms of hierarchy, composition, information density, and
user flow, not in terms of specific components or libraries.

## Planning Process

1. Identify the user's primary task on this screen.
2. Identify the content types being displayed (for polymorphic rendering).
3. Determine the density appropriate for the task frequency and user expertise.
4. Sketch the hierarchy: what has the most visual weight, what recedes?
5. Choose a composition strategy (asymmetric split, stack, dashboard grid, etc.).
6. Specify whitespace relationships between major sections.
7. Define the state landscape: what states can this screen be in?

## Reference Files to Consult
- `skills/design-theory/references/layout-composition.md`
- `skills/design-theory/references/visual-fundamentals.md`
- `skills/design-theory/references/object-rendering.md`
- `skills/design-theory/references/interaction-design.md`

## Output Format

Deliver a layout specification that includes:
1. **Screen purpose**: one sentence describing the primary user task
2. **Content types**: list of distinct object types, each with its rendering approach
3. **Hierarchy map**: which elements have primary, secondary, and tertiary weight
4. **Composition**: the spatial arrangement (annotated with rationale)
5. **State inventory**: every state this screen can be in
6. **Responsive behavior**: what changes at mobile widths
7. **Recommended density**: high (dashboard), medium (detail), or low (landing)

This output feeds directly into the component-builder agent.
```

### agents/component-builder.md

```yaml
---
name: component-builder
description: >-
  Builds UI components from headless primitives with the right library for
  each need. Knows when to reach for Radix, Vaul, Sonner, cmdk, DaisyUI,
  or raw Tailwind. Use for: "Build a command palette", "Create a settings
  form with validation", "Implement this design spec as components".
model: claude-sonnet-4-20250514
color: green
tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - LS
  - Bash
---
```

```markdown
# Component Builder

You build UI components from primitives up, selecting the right library
for each need and composing them into production-ready implementations.

## Build Process

1. Run /detect-stack or `scripts/detect_ui_stack.sh` to understand
   what the project already ships.
2. Consult `skills/ui-engineering/references/library-selection.md`
   for the right tool for each component need.
3. Grep the relevant `refs/` directory to verify the actual API.
4. Build with the composition model:
   - Headless primitive (Radix or equivalent) for behavior
   - Tailwind utilities for styling
   - Slot/compound pattern for composition
   - CVA for variant management when variants > 2
5. Cover all states from `skills/ui-engineering/references/state-coverage.md`.
6. For mixed content collections, implement a polymorphic renderer
   (see `skills/design-theory/references/object-rendering.md` and
   `examples/polymorphic-renderer/`).

## Library Verification

ALWAYS grep source before writing implementation code:
$ grep -r "export" refs/shadcn-ui/apps/v4/registry/new-york-v4/ui/dialog.tsx
$ grep -r "SnapPoint\|snapPoints" refs/vaul/src/
$ grep -r "useCommandState" refs/cmdk/src/

If the API has changed from training data, use the source code version.

## Rules
- Never build a parallel system next to one that already exists.
- Never default every component to 'use client' in Next.js.
- Never render heterogeneous data through a uniform card component.
- Always include loading, empty, error, and disabled states.
- Always check keyboard navigation and focus management.
- Always run the project's formatter and linter after making changes.
```

### agents/animation-engineer.md

```yaml
---
name: animation-engineer
description: >-
  Implements motion and animation with performance awareness and
  accessibility respect. Use for: "Add a page transition", "Animate this
  list reorder", "Make this drawer feel smooth", "Add enter/exit
  animations to this dialog".
model: claude-sonnet-4-20250514
color: yellow
tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - LS
  - Bash
---
```

```markdown
# Animation Engineer

You add motion to interfaces with purpose, performance awareness, and
accessibility respect. You know when CSS transitions suffice and when
Motion's spring physics are needed.

## Decision Framework

1. Is this a simple state change (color, opacity, scale)?
   YES: Use CSS transition via Tailwind utilities.
   NO: Continue to step 2.

2. Does this involve layout changes (reorder, resize, enter/exit)?
   YES: Use Motion's layout animation or AnimatePresence.
   NO: Continue to step 3.

3. Does this involve gesture interaction (drag, swipe)?
   YES: Use Motion's gesture system (useDragControls, etc.).
   NO: CSS transition is probably sufficient after all.

## Reference Files
- `skills/ui-engineering/references/animation-patterns.md`
- Verify API: grep `refs/motion/packages/motion/src/`
- Verify Vaul drag: grep `refs/vaul/src/`

## Performance Rules
- Only animate transform and opacity (composited properties)
- Use Motion's layout prop for layout animation (avoids layout thrash)
- Profile animation frame rate in browser DevTools
- Set will-change only during active animation, not permanently

## Accessibility Rules
- ALWAYS check prefers-reduced-motion
- Tailwind: motion-safe: prefix for animation classes
- Motion: layout animations respect reduced-motion by default
- Reduced-motion fallback: instant state change, no transition
- Never use flashing or strobing effects (seizure risk)

## Common Patterns
- **Enter/exit**: AnimatePresence + initial/animate/exit props
- **List reorder**: layout prop on each item + LayoutGroup
- **Page transition**: AnimatePresence at the route level
- **Drawer/sheet**: Vaul handles gesture animation internally
- **Toast**: Sonner handles enter/exit/stack animation internally
- **Skeleton to content**: crossfade with opacity transition
- **Hover preview**: scale + shadow via CSS transition
```

### agents/a11y-auditor.md

```yaml
---
name: a11y-auditor
description: >-
  Deep accessibility expertise grounded in WCAG 2.2. Audits components,
  pages, and flows for accessibility violations. Use for: "Audit this page
  for accessibility", "Is this dialog accessible?", "Check the keyboard
  navigation on this form", "Review ARIA usage in this component".
model: claude-sonnet-4-20250514
color: blue
tools:
  - Read
  - Grep
  - Glob
  - LS
  - Bash
---
```

```markdown
# Accessibility Auditor

You audit UI implementations for WCAG 2.2 conformance with deep knowledge
of ARIA patterns, keyboard navigation, focus management, color contrast,
and screen reader behavior.

## Audit Process

1. Read the component or page code.
2. Check against `skills/design-theory/references/accessibility.md`.
3. Verify Radix primitive usage by grepping `refs/radix-primitives/`.
4. Test keyboard flow: can every action be completed without a mouse?
5. Test focus management: does focus move predictably after state changes?
6. Test color contrast: do all text and UI components meet AA minimums?
7. Test screen reader: are labels, roles, and state changes announced?

## Severity Levels
- **Critical**: No keyboard access, missing labels on form inputs, focus
  trap without escape, contrast below 3:1 for UI components.
- **Should fix**: Missing focus-visible styles, aria-live not used for
  dynamic updates, missing skip-to-content link, images without alt text.
- **Polish**: Redundant ARIA (roles on semantic elements), heading hierarchy
  gaps (h1 to h3 with no h2), link text that says "click here".

## Common Violations to Check
- Dialogs without focus trapping or Escape dismissal
- Custom selects without arrow key navigation
- Drag-and-drop without keyboard alternative
- Toast notifications without aria-live announcement
- Icon-only buttons without aria-label
- Form errors not associated with fields via aria-describedby
- Tab order broken by CSS positioning or z-index stacking
- Color-only status indicators

## Radix Verification
Radix primitives handle most accessibility patterns correctly. When a
project uses Radix, verify that:
- The primitive is used correctly (not wrapped in a way that breaks ARIA)
- Custom styling does not hide focus indicators
- Custom events do not prevent default keyboard behavior
Grep `refs/radix-primitives/packages/react/` for the specific component
to understand what accessibility it provides out of the box.
```

### agents/stack-detector.md

```yaml
---
name: stack-detector
description: >-
  Reads a project's code to map its existing UI layer, component library,
  icon system, toast/drawer/dialog implementations, and design token
  approach. Always run before component-builder on a new project. Use for:
  "What UI stack does this project use?", "Detect the component library",
  "Map the existing design system".
model: claude-sonnet-4-20250514
color: red
tools:
  - Read
  - Grep
  - Glob
  - LS
  - Bash
---
```

```markdown
# Stack Detector

You inspect a project to understand its existing UI layer before any
design or implementation work begins. Your output prevents the other
agents from building parallel systems.

## Detection Process

1. Run `scripts/detect_ui_stack.sh <repo-root>` for automated detection.
2. Supplement with manual inspection:
   - Grep package.json for UI dependencies
   - Check for components/ui or similar component directories
   - Look for theme config files (tailwind.config, CSS custom properties)
   - Identify icon imports (lucide, iconoir, heroicons, etc.)
   - Check for existing toast, drawer, dialog implementations
   - Look for design token files (CSS variables, theme objects)

## Report Format

Deliver a stack report that maps:
- **Framework**: React, Next.js (app/pages router), Vue, Svelte, etc.
- **CSS approach**: Tailwind, CSS Modules, styled-components, etc.
- **Component library**: shadcn, Radix, DaisyUI, Chakra, MUI, etc.
- **Component directory**: where local components live
- **Icon system**: which icon library, where imported
- **Overlays**: existing dialog, drawer, popover, sheet implementations
- **Feedback**: existing toast, notification, alert implementations
- **Tokens**: CSS variables, Tailwind theme extension, design token files
- **Animation**: existing motion library or CSS transition patterns

## Recommendations

Based on the detected stack, recommend:
- Which libraries to USE (already in the project)
- Which libraries to CONSIDER (compatible additions)
- Which libraries to AVOID (would conflict with existing choices)
- Which patterns to FOLLOW (established in the codebase)
```

---

## Commands

### commands/design-review.md

```yaml
---
description: Review a UI component or page for design principle violations, accessibility issues, and polymorphic rendering opportunities. Triggers design-critic and a11y-auditor agents.
allowed-tools: Read, Grep, Glob, LS
argument-hint: <file-or-directory-to-review>
---
```

```markdown
Review the specified file or directory for design quality.

1. Load the design-critic agent.
2. Load the a11y-auditor agent.
3. Run both reviews on the target.
4. Combine findings, deduplicate, and sort by severity.
5. For each Critical finding, propose a specific fix.
```

### commands/ui-build.md

```yaml
---
description: Build a UI component or page with the right libraries, full state coverage, and polymorphic rendering for mixed content. Triggers stack-detector, visual-architect, and component-builder agents.
allowed-tools: Read, Write, Edit, Grep, Glob, LS, Bash
argument-hint: <description-of-what-to-build>
---
```

```markdown
Build the described UI component or page.

1. Run /detect-stack to understand the existing project UI layer.
2. Load the visual-architect agent to plan the layout.
3. Load the component-builder agent to implement.
4. Verify all states from the state coverage checklist.
5. Run the project's formatter and linter.
```

### commands/design-system.md

```yaml
---
description: Plan or extend a design token system with spacing, color, type, and component variant matrices. Triggers visual-architect agent with design-systems reference.
allowed-tools: Read, Write, Edit, Grep, Glob, LS
argument-hint: <scope-of-design-system-work>
---
```

### commands/a11y-audit.md

```yaml
---
description: Audit a component, page, or flow for WCAG 2.2 accessibility conformance. Triggers a11y-auditor agent.
allowed-tools: Read, Grep, Glob, LS, Bash
argument-hint: <file-or-directory-to-audit>
---
```

### commands/animate.md

```yaml
---
description: Add animation to a component or flow with performance and accessibility awareness. Triggers animation-engineer agent.
allowed-tools: Read, Write, Edit, Grep, Glob, LS, Bash
argument-hint: <what-to-animate>
---
```

### commands/detect-stack.md

```yaml
---
description: Detect the existing UI stack in a project and report framework, component library, icon system, overlays, feedback, tokens, and animation patterns. Triggers stack-detector agent.
allowed-tools: Read, Grep, Glob, LS, Bash
argument-hint: <repo-root-path>
---
```

---

## install.sh

```bash
#!/bin/bash
# install.sh
# Sets up ui-design-pro as a Claude Code plugin
#
# What this does:
#   1. Verifies directory structure
#   2. Clones reference source repos into refs/
#   3. Creates slash command symlinks
#
# Usage:
#   ./install.sh              # Local install
#   ./install.sh --global     # Global install

set -e

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo "${BOLD}UI-Design-Pro Plugin Installer${NC}"
echo "================================"
echo "Directory: ${CYAN}$PLUGIN_DIR${NC}"
echo ""

# 1. Ensure directory structure
echo "${BOLD}1. Directory structure${NC}"
for dir in agents refs examples commands scripts \
           skills/design-theory/references \
           skills/ui-engineering/references \
           examples/polymorphic-renderer \
           examples/design-token-scales \
           examples/state-matrices; do
  if [ ! -d "$PLUGIN_DIR/$dir" ]; then
    mkdir -p "$PLUGIN_DIR/$dir"
    echo "   ${GREEN}Created${NC} $dir/"
  else
    echo "   ${GREEN}OK${NC}      $dir/"
  fi
done
echo ""

# 2. Clone reference repos
echo "${BOLD}2. Cloning reference source repos${NC}"

clone_ref() {
  local repo="$1"
  local target="$2"
  local depth="${3:-1}"

  if [ -d "$PLUGIN_DIR/refs/$target" ] && [ -n "$(ls -A "$PLUGIN_DIR/refs/$target" 2>/dev/null)" ]; then
    echo "   ${GREEN}OK${NC}      refs/$target/"
  else
    echo "   ${YELLOW}Cloning${NC} $repo -> refs/$target/"
    git clone --depth "$depth" --single-branch \
      "https://github.com/$repo.git" "$PLUGIN_DIR/refs/$target" 2>/dev/null || {
      echo "   ${RED}Failed${NC}  $repo"
      return 1
    }
    # Remove .git to save space (we only need source, not history)
    rm -rf "$PLUGIN_DIR/refs/$target/.git"
    echo "   ${GREEN}Cloned${NC}  refs/$target/"
  fi
}

clone_ref "shadcn-ui/ui"                    "shadcn-ui"
clone_ref "radix-ui/primitives"             "radix-primitives"
clone_ref "radix-ui/colors"                 "radix-colors"
clone_ref "radix-ui/themes"                 "radix-ui-themes"
clone_ref "emilkowalski/vaul"               "vaul"
clone_ref "emilkowalski/sonner"             "sonner"
clone_ref "pacocoursey/cmdk"                "cmdk"
clone_ref "saadeghi/daisyui"                "daisyui"
clone_ref "motiondivision/motion"           "motion"
clone_ref "tailwindlabs/tailwindcss"        "tailwindcss"
clone_ref "argyleink/open-props"            "open-props"

echo ""

# 3. Create slash command symlinks
echo "${BOLD}3. Registering commands${NC}"
GLOBAL=""
if [[ "$1" == "--global" ]]; then
  GLOBAL="--global"
  CMD_DIR="$HOME/.claude/commands"
else
  CMD_DIR="$PLUGIN_DIR/.claude/commands"
fi

mkdir -p "$CMD_DIR"
for cmd in "$PLUGIN_DIR/commands/"*.md; do
  [ -f "$cmd" ] || continue
  name=$(basename "$cmd" .md)
  ln -sf "$cmd" "$CMD_DIR/$name.md"
  echo "   ${GREEN}Registered${NC} /$name"
done
echo ""

# 4. Summary
echo "${BOLD}Summary${NC}"
echo "   Agents:     $(ls "$PLUGIN_DIR/agents/"*.md 2>/dev/null | wc -l | tr -d ' ')"
echo "   Commands:   $(ls "$PLUGIN_DIR/commands/"*.md 2>/dev/null | wc -l | tr -d ' ')"
echo "   Refs:       $(ls -d "$PLUGIN_DIR/refs/"*/ 2>/dev/null | wc -l | tr -d ' ')"
echo "   Skills:     2 (design-theory, ui-engineering)"
echo ""
echo "${GREEN}UI-Design-Pro plugin installed.${NC}"
echo "Launch Claude Code from ${CYAN}$PLUGIN_DIR${NC} to use."
```

---

## scripts/detect_ui_stack.sh

Upgraded version of the original from codex-plugins. Adds detection for
more libraries and outputs structured recommendations.

```bash
#!/usr/bin/env bash
set -euo pipefail

root="${1:-.}"

find_package_json() {
  if [[ -f "$root/package.json" ]]; then
    printf '%s\n' "$root/package.json"
    return
  fi
  local found
  found="$(find "$root" -maxdepth 3 -name package.json -not -path '*/node_modules/*' | head -n 1 || true)"
  if [[ -n "$found" ]]; then
    printf '%s\n' "$found"
  fi
}

has_file() {
  find "$root" -maxdepth 4 -name "$1" -not -path '*/node_modules/*' | grep -q .
}

has_path() {
  find "$root" -maxdepth 5 -path "$1" -not -path '*/node_modules/*' | grep -q .
}

pkg="$(find_package_json || true)"

echo "=== UI Stack Report ==="
echo "Root: $(cd "$root" && pwd)"

if [[ -z "${pkg:-}" ]]; then
  echo "package.json: not found"
  echo "RECOMMENDATION: Cannot detect UI stack without package.json."
  exit 0
fi

echo "package.json: $pkg"

# Framework detection
if grep -q '"next"' "$pkg" 2>/dev/null; then
  echo "Framework: Next.js"
  if has_path "*/app" || has_path "*/src/app"; then
    echo "Router: App Router"
  elif has_path "*/pages" || has_path "*/src/pages"; then
    echo "Router: Pages Router"
  fi
elif grep -q '"react"' "$pkg" 2>/dev/null; then
  echo "Framework: React (no Next.js)"
elif grep -q '"vue"' "$pkg" 2>/dev/null; then
  echo "Framework: Vue"
elif grep -q '"svelte"' "$pkg" 2>/dev/null; then
  echo "Framework: Svelte"
else
  echo "Framework: Unknown"
fi

# CSS approach
if has_file "tailwind.config.*" || has_file "tailwind.css"; then
  echo "CSS: Tailwind CSS"
  # Check Tailwind version
  if grep -q '"tailwindcss": ".*4\.' "$pkg" 2>/dev/null; then
    echo "Tailwind version: v4 (CSS-first config)"
  elif grep -q '"tailwindcss": ".*3\.' "$pkg" 2>/dev/null; then
    echo "Tailwind version: v3 (JS config)"
  fi
fi

# Component library
check_dep() {
  local label="$1"
  local pattern="$2"
  if grep -q "$pattern" "$pkg" 2>/dev/null; then
    echo "$label: yes"
    return 0
  else
    echo "$label: no"
    return 1
  fi
}

echo ""
echo "--- Dependencies ---"
check_dep "shadcn/ui (components.json)" "" || true
if has_file "components.json"; then
  echo "shadcn config: present"
fi

check_dep "Radix UI"        '@radix-ui/'
check_dep "Sonner"          '"sonner"'
check_dep "Vaul"            '"vaul"'
check_dep "cmdk"            '"cmdk"'
check_dep "DaisyUI"         '"daisyui"'
check_dep "Motion"          '"motion"\|"framer-motion"'
check_dep "CVA"             '"class-variance-authority"'
check_dep "tailwind-merge"  '"tailwind-merge"'
check_dep "clsx"            '"clsx"'

echo ""
echo "--- Icons ---"
check_dep "Lucide"          '"lucide-react"'
check_dep "Iconoir"         '"iconoir-react"\|"iconoir"'
check_dep "Heroicons"       '"@heroicons/"'

echo ""
echo "--- Component Directories ---"
for dir in "components/ui" "src/components/ui" "app/components" "src/app/components" "components" "src/components"; do
  if [[ -d "$root/$dir" ]]; then
    count=$(find "$root/$dir" -maxdepth 1 -name "*.tsx" -o -name "*.jsx" 2>/dev/null | wc -l | tr -d ' ')
    echo "Found: $dir/ ($count component files)"
  fi
done

echo ""
echo "--- Design Tokens ---"
if find "$root" -maxdepth 3 -name "*.css" -not -path '*/node_modules/*' -exec grep -l '\-\-' {} \; 2>/dev/null | head -1 | grep -q .; then
  echo "CSS custom properties: detected"
fi
if has_file "theme.ts" || has_file "theme.js" || has_file "theme.config.*"; then
  echo "Theme config file: detected"
fi

echo ""
echo "=== Recommendations ==="
echo "USE:     Libraries already in the project (extend, do not replace)"
echo "DETECT:  Run /design-review after inspecting existing component patterns"
echo "AVOID:   Adding a second dialog/drawer/toast stack if one exists"
```

---

## Examples

### examples/polymorphic-renderer/render-map.tsx

```tsx
// Polymorphic Object Renderer
//
// Each content type gets its own visual treatment.
// The render map associates type discriminant to component.
// Shared tokens (spacing, color, type) unify without homogenizing.

import type { ReactNode } from "react";

// Discriminated union for content types
type ContentItem =
  | { type: "source"; slug: string; title: string; url: string; domain: string; excerpt: string }
  | { type: "essay"; slug: string; title: string; lead: string; readingTime: number; stage: string }
  | { type: "fieldNote"; slug: string; body: string; timestamp: string }
  | { type: "shelfEntry"; slug: string; title: string; coverUrl: string; rating: number; author: string }
  | { type: "thread"; slug: string; title: string; nodeCount: number; connectionCount: number }
  | { type: "videoProject"; slug: string; title: string; phase: string; thumbnailUrl: string };

// Type-safe render map
const renderers: Record<ContentItem["type"], (item: any) => ReactNode> = {
  source: (item) => (
    <a href={item.url} className="group block py-3 border-b border-neutral-100">
      <span className="text-xs tracking-wide text-neutral-400 uppercase">
        {item.domain}
      </span>
      <p className="text-sm font-medium text-neutral-800 group-hover:text-blue-700 mt-0.5">
        {item.title}
      </p>
      <p className="text-xs text-neutral-500 mt-1 line-clamp-2">{item.excerpt}</p>
    </a>
  ),

  essay: (item) => (
    <article className="py-6">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-[10px] font-medium uppercase tracking-widest text-neutral-400">
          {item.stage}
        </span>
        <span className="text-[10px] text-neutral-300">
          {item.readingTime} min
        </span>
      </div>
      <h3 className="text-lg font-semibold text-neutral-900">{item.title}</h3>
      <p className="text-sm text-neutral-600 mt-2 leading-relaxed line-clamp-3">
        {item.lead}
      </p>
    </article>
  ),

  fieldNote: (item) => (
    <div className="py-4 pl-4 border-l-2 border-neutral-200">
      <time className="text-[10px] text-neutral-400 font-mono">
        {item.timestamp}
      </time>
      <p className="text-sm text-neutral-700 mt-1 italic">{item.body}</p>
    </div>
  ),

  shelfEntry: (item) => (
    <div className="flex gap-3 py-3">
      <img
        src={item.coverUrl}
        alt=""
        className="w-12 h-16 object-cover rounded-sm flex-shrink-0"
      />
      <div className="min-w-0">
        <p className="text-sm font-medium text-neutral-800 truncate">
          {item.title}
        </p>
        <p className="text-xs text-neutral-500">{item.author}</p>
        <div className="flex gap-0.5 mt-1">
          {Array.from({ length: 5 }, (_, i) => (
            <span
              key={i}
              className={i < item.rating ? "text-amber-400" : "text-neutral-200"}
            >
              ●
            </span>
          ))}
        </div>
      </div>
    </div>
  ),

  thread: (item) => (
    <div className="py-3 flex items-center gap-3">
      <div className="w-8 h-8 rounded-full bg-violet-50 flex items-center justify-center">
        <span className="text-xs font-mono text-violet-600">{item.nodeCount}</span>
      </div>
      <div>
        <p className="text-sm font-medium text-neutral-800">{item.title}</p>
        <p className="text-[10px] text-neutral-400">
          {item.connectionCount} connections
        </p>
      </div>
    </div>
  ),

  videoProject: (item) => (
    <div className="py-3 flex gap-3">
      <div className="relative w-24 h-14 rounded overflow-hidden flex-shrink-0 bg-neutral-100">
        <img src={item.thumbnailUrl} alt="" className="w-full h-full object-cover" />
        <span className="absolute bottom-1 right-1 text-[9px] bg-black/70 text-white px-1 rounded">
          {item.phase}
        </span>
      </div>
      <p className="text-sm font-medium text-neutral-800 self-center">
        {item.title}
      </p>
    </div>
  ),
};

// The renderer itself
export function ObjectRenderer({ item }: { item: ContentItem }) {
  const render = renderers[item.type];
  if (!render) {
    console.warn(`No renderer for type: ${(item as any).type}`);
    return null;
  }
  return <>{render(item)}</>;
}

// Usage in a heterogeneous feed
export function ContentFeed({ items }: { items: ContentItem[] }) {
  return (
    <div className="divide-y divide-neutral-50">
      {items.map((item) => (
        <ObjectRenderer key={item.slug} item={item} />
      ))}
    </div>
  );
}
```

---

## Future Additions

### More Reference Repos

| Library | Why |
|---------|-----|
| `unovue/radix-vue` | Vue equivalent of Radix for Vue projects |
| `huntabyte/bits-ui` | Svelte headless primitives |
| `shoelace-style/shoelace` | Web Components design system |
| `adobe/react-spectrum` | Adobe's accessibility-first component system |
| `chakra-ui/ark` | Framework-agnostic headless components |

### Benchmark Suite

Design quality challenges with known-good solutions:

```
benchmarks/
├── hierarchy-test/        # Can the agent fix a flat hierarchy?
├── polymorphic-test/      # Does it use render maps for mixed data?
├── state-coverage-test/   # Does it handle all states?
├── a11y-test/             # Does it pass WCAG 2.2 AA?
├── responsive-test/       # Does it work at 320px?
└── scoring.md             # Evaluation criteria
```

### Design Critique Training Data

Annotated before/after examples of real UI improvements:

```
training/
├── hierarchy-fixes/       # Flat layout -> clear hierarchy
├── card-to-polymorphic/   # Uniform cards -> type-aware rendering
├── state-additions/       # Happy path -> full state coverage
├── a11y-fixes/            # Violations -> conformant implementations
└── density-adjustments/   # Generic -> task-appropriate density
```
