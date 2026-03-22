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

## Plugin Installation

This plugin is registered at `~/.claude/plugins/marketplaces/local-desktop-app-uploads/ui-design-pro/`.
Claude Code resolves plugins via `installed_plugins.json` — only the path in that file is read.
Copying to `~/.claude/plugins/ui-design-pro/` (without the marketplace namespace) has NO effect.

To update the global install:
```bash
rm -rf ~/.claude/plugins/marketplaces/local-desktop-app-uploads/ui-design-pro
cp -R /path/to/source/ui-design-pro ~/.claude/plugins/marketplaces/local-desktop-app-uploads/ui-design-pro
```
Then bump the version in `~/.claude/plugins/installed_plugins.json`.

## Agent System

Seven slash commands available, plus a Claude.ai chat-skill companion:

| Command | Agent | What It Does |
|---------|-------|--------------|
| `/design-review` | design-critic | Reviews for principle violations |
| `/ui-build` | component-builder | Builds with the right libraries |
| `/design-system` | visual-architect | Plans or extends token systems |
| `/a11y-audit` | a11y-auditor | WCAG 2.2 conformance audit |
| `/animate` | animation-engineer | Motion with perf + a11y awareness |
| `/detect-stack` | stack-detector | Maps existing UI layer |
| `/design-rationale` | visual-architect | Structured design reasoning document |

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
- Run /design-rationale BEFORE major UI changes to document intent.
- Run /design-review AFTER changes to verify the rationale was followed.

### Cross-Reference with Other Plugins

If the project also uses JS-Pro or Django-Design:

- For React internals (hooks, server components, compiler): defer to JS-Pro
  react-specialist and its refs/react-main/ source.
- For D3 visualization: defer to JS-Pro data-analyst and its D3 examples.
- For Django template + HTMX frontend: defer to Django-Design django-frontend.
- This plugin owns: design judgment, component library selection, animation,
  accessibility, visual architecture, and the polymorphic rendering philosophy.

## Epistemic Knowledge System

This plugin maintains structured, evolving knowledge in `knowledge/`. Claims carry confidence scores, evidence tracking, and domain tags. Over time, accepted claims strengthen and rejected claims weaken through Bayesian updates.

### Session Start Protocol

1. Read `knowledge/manifest.json` for current state and last update time.
2. Read `knowledge/claims.jsonl` and filter for `status: "active"`.
3. Sort active claims by confidence (descending) and load the top 15-20 into working context.
4. Check `knowledge/tensions.jsonl` for unresolved tensions in the domains relevant to the current task. If the task touches a tension, surface it to the user BEFORE making a decision.
5. Check `knowledge/preferences.jsonl` for user-specific defaults that may override generic best practices.

### During Work

6. When your reasoning draws on a specific claim, note its ID internally.
7. When you make a suggestion informed by a claim, track which claims influenced the decision.
8. When the user accepts, modifies, or rejects a suggestion, note the outcome.

### Session End Protocol

9. Run `/session-save` to write session observations to `knowledge/session_log/{timestamp}.jsonl`. This captures agents invoked, claims consulted, suggestions made, and their outcomes.
10. If you discovered something that contradicts an existing claim, flag it as a HIGH-PRIORITY tension signal in the session log.
11. If you noticed a recurring pattern the knowledge base doesn't cover, note it as a candidate claim in the session log.

### Knowledge Priority Rules

- Active claims with confidence > 0.8 take precedence over static prose when they conflict.
- Draft claims are informational only — they never override static agent instructions.
- Preferences defer to explicit user instructions in the current session. Preferences inform defaults, not mandates.
- When two active claims conflict, check `knowledge/tensions.jsonl` for a resolution. If none exists, surface the conflict to the user and let them decide.
- Tensions are information, not blockers. Surface them, let the user decide, log the decision.

### Commands

- `/knowledge-status` — View claim counts, confidence distribution, tensions, questions
- `/knowledge-review` — Activate draft claims, resolve tensions, triage questions
- `/knowledge-update` — Run between-session learning pipeline (all 8 stages)
- `/session-save` — Flush session observations to the session log
