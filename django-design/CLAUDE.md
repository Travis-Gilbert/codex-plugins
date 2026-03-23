# django-design Plugin

Claude Code plugin (v3.0.0) — Full-stack Django development toolkit.

## Structure

- `.claude-plugin/plugin.json` — Plugin manifest
- `skills/django-design/SKILL.md` — Main skill with 18 reference files in `references/`
  - Backend: models, views, api, forms, auth-and-security, admin, background-tasks, deployment, performance
  - Frontend: templates, htmx, alpine, tailwind, d3-django, design-system
  - Cross-cutting: testing, integrations, cms-and-content
- `commands/` — 5 interactive commands: django-design, django-app, django-model, django-api, django-component
- `agents/` — 5 agents: django-architect, django-api-reviewer, django-frontend, django-migrator, django-profiler

## Conventions

- Agent colors must be valid: blue, cyan, green, yellow, magenta, red
- SKILL.md description: ~550 chars max, no keyword-stuffing
- Commands use YAML frontmatter with: description, allowed-tools, argument-hint
- Agents use YAML frontmatter with: name, description (3 examples), model, color, tools
- Reference files contain working code examples with a consistent content publishing domain
- Use generic placeholder domains (example.com) in code samples, not real domains

## Development

- `plugin-validator` agent validates structure and naming
- `skill-reviewer` agent checks skill quality and progressive disclosure
- No build step — plugin is pure markdown

## Updating the Installed Plugin

The installed copy is a git clone at:
`~/.claude/plugins/marketplaces/local-desktop-app-uploads/django-design/`

After pushing changes to main: `cd` to that path and `git pull origin main`.

## Domain Convention

All code examples use a content publishing domain:
- Core model: `Essay` (title, slug, stage, body, created_by)
- Pipeline stages: drafting → research → production → published
- Related models: FieldNote, ResearchSource, ShelfEntry
- Template paths: `content/`, base template: `base_studio.html`
- URL namespace: `content:`

## File Size Targets

- Reference files: 8-15 KB each (no file under 6K, none over 15K)
- SKILL.md: under 500 lines
- SKILL.md description field: ~550 chars max

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
