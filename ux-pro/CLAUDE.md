# UX-Pro Plugin

You have access to a curated library of design system source code,
specialist agent definitions for every UX discipline, and reference
documents covering research methods, interaction patterns, accessibility
standards, and service design frameworks. Use them.

## Agents

This plugin has seven specialist agents. Each covers a distinct UX discipline:

| Agent | Domain | When to invoke |
|-------|--------|---------------|
| ux-researcher | Research planning, method selection, study design | Any research or measurement question |
| interaction-designer | Flows, micro-interactions, patterns, states | Component behavior or flow design |
| information-architect | Navigation, taxonomy, content structure, labeling | Navigation or IA work |
| accessibility-auditor | WCAG evaluation, ARIA, keyboard, inclusive design | Any accessibility question or audit |
| ux-writer | Microcopy, error messages, voice and tone | UI text, labels, error copy |
| usability-tester | Test scripts, facilitation, analysis, reporting | Usability evaluation work |
| service-designer | Blueprints, journey maps, experience mapping | System-level UX or cross-channel work |

## Relationship to Other Skills and Plugins

| Existing | Relationship |
|----------|-------------|
| **design-pro** (chat skill) | Owns visual design, layout, prototyping. UX-Pro owns the broader UX discipline: research, IA, interaction, accessibility, content, service design. |
| **ui-design-pro** (Claude Code plugin) | Owns component implementation and design-to-code. UX-Pro provides the UX reasoning and accessibility verification layer. |
| **animation-pro** (Claude Code plugin) | Owns motion and animation. UX-Pro evaluates whether animation serves users (Purpose Test lives in animation-pro). |

## The Handoff Flow

1. **UX-Pro chat skill** produces research insights, user flows, IA structures, heuristic evaluations
2. **design-pro** translates those into layouts and prototypes
3. **ui-design-pro** / **UX-Pro plugin** turns those into production code with accessibility and interaction patterns baked in

## When to Use Reference Source Code

Do NOT rely on training data for accessibility patterns or component behavior.
Instead, grep the actual implementations:

- **Accessible component patterns**: grep `refs/radix-primitives/packages/react/`
  for Dialog, Menu, Tabs, Select, Accordion, Tooltip focus management and ARIA
- **Accessibility hooks**: grep `refs/react-spectrum/packages/@react-aria/`
  for usePress, useFocus, useHover, useOverlay, useSelection
- **Headless UI patterns**: grep `refs/headlessui/packages/@headlessui-react/src/`
  for minimal accessible implementations
- **WCAG rules as code**: grep `refs/axe-core/lib/rules/` and `refs/axe-core/lib/checks/`
  for WCAG success criteria translated into testable assertions
- **ARIA keyboard patterns**: grep `refs/aria-practices/content/patterns/`
  for normative keyboard interaction models per widget
- **Research-backed patterns**: grep `refs/govuk-design-system/src/patterns/`
  for patterns with documented user research rationale
- **Form design**: grep `refs/govuk-frontend/packages/govuk-frontend/src/govuk/components/`
  for error messages, validation, progressive enhancement
- **Enterprise UX**: grep `refs/polaris/polaris-react/src/components/` for
  data tables, resource lists, filters, bulk actions
- **Complex interactions**: grep `refs/primer-react/packages/react/src/`
  for tree views, action lists, command palettes
- **Design tokens**: grep `refs/carbon/packages/` for type, color, layout, spacing tokens

## Rules

1. Always verify component accessibility patterns against source code in refs/
   before writing code. Training data may be outdated.

2. Every custom interactive component must implement correct ARIA roles, states,
   and keyboard interaction per WAI-ARIA Authoring Practices. Load
   `references/aria-patterns.md` for the normative patterns.

3. All implementations must meet WCAG 2.2 Level AA. Load
   `references/wcag-22-design-guide.md` for the organized checklist.

4. Keyboard accessibility is not optional. Every interactive element must be
   operable via keyboard. No keyboard traps. Focus must be visible.

5. Error messages must follow the pattern: what happened + why + how to fix.
   Never use color alone to indicate errors.

6. When recommending UX patterns, cite the research or heuristic that supports
   the recommendation. Load `references/nielsen-heuristics.md` or
   `references/laws-of-ux.md` as appropriate.

7. Use the `templates/` directory for deliverable scaffolds. Do not reinvent
   report formats; use the tested templates.

8. For form design, follow single-column layout, mark optional fields (not
   required), validate after blur (not on keystroke), and provide clear
   error recovery.

## Knowledge Layer

This plugin has a self-improving knowledge layer in `knowledge/`.

### At Session Start
1. Read `knowledge/manifest.json` for stats and last update time
2. Read `knowledge/claims.jsonl` for active claims relevant to this task
   (filter by tags matching the agents you are loading)
3. When a claim's confidence > 0.8 and it conflicts with static
   instructions, follow the claim. It represents learned behavior.
4. When a claim's confidence < 0.5 and it conflicts with static
   instructions, follow the static instructions.

### During the Session
- When you consult a claim, note which claim and why
- When you make a suggestion based on a claim, note the link
- When the user corrects you, note what they said and which claim
  was involved (this is a tension signal)
- When you notice a pattern not in the knowledge base, note it
  as a candidate claim

### At Session End
Run `/learn` to save and update knowledge. This is the ONLY
knowledge command you need.
