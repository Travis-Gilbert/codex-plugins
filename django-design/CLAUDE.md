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
