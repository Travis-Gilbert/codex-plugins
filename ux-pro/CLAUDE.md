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
