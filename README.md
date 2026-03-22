# Codex Plugins

Most Claude Code plugins give you a set of slash commands and some domain knowledge. These plugins do something different: they learn.

Each plugin in this repo is a **domain-specialized engineering intelligence** that accumulates knowledge across sessions, grounds itself in real library source code (not training data), and coordinates with a companion chat skill on Claude.ai. The plugin implements. The chat skill plans. Over time, the plugin gets better at its job because it tracks what works, what doesn't, and what it's still uncertain about.

This is the two-surface architecture: one surface for thinking, one for building.

## What's Inside Each Plugin

A typical plugin contains four layers:

**Specialist agents and slash commands.** Each plugin ships with 3 to 7 agents that handle specific subtasks. UI-Design-Pro has a design critic, a component builder, an accessibility auditor, an animation engineer, and a visual architect. Django-Engine-Pro has agents for model design, ORM optimization, migration planning, and MCP server exposure. Agents compose in defined sequences: you always run the stack detector before the component builder, always run the design critic after.

**Source-code references.** Plugins include `install.sh` scripts that shallow-clone real library repos into a local `refs/` directory. When UI-Design-Pro needs to know how Radix handles focus restoration, it greps the actual Radix source, not its training data. When D3-Pro needs to verify a scale constructor's API, it reads the Observable source directly. This matters because training data goes stale. Source code doesn't.

**Skills and decision frameworks.** Static knowledge: inheritance decision tables, ORM anti-pattern catalogs, polymorphic rendering rules, animation physics constants. These encode the expert judgment that doesn't change between sessions.

**An epistemic knowledge layer.** This is the part that learns. Each plugin maintains a `knowledge/` directory containing typed claims in JSONL, confidence scores, session logs, and (for some plugins) SBERT embeddings. Claims start as drafts. After review, they become active. Active claims carry Bayesian confidence that updates based on session outcomes: when a suggestion informed by a claim gets accepted, confidence rises; when it gets rejected, confidence drops. Over time, each plugin develops its own body of verified, weighted knowledge about its domain.

## The Two-Surface Architecture

Each plugin here has a counterpart: a chat skill that runs on Claude.ai (or Claude Desktop). The division of labor is deliberate.

The **chat skill** handles planning, reasoning, and decision-making. When you're deciding between DRF and Ninja for an API, or choosing an inheritance strategy for a model hierarchy, or evaluating whether a component needs polymorphic rendering, the chat skill walks you through the tradeoffs and produces a structured handoff document.

The **Claude Code plugin** handles implementation and learning. It takes the handoff document, builds the thing, greps real source code when it needs to verify an API, logs what it tried, and updates its knowledge base with what it learned.

The chat skill never sees `knowledge/claims.jsonl`. The plugin never produces planning documents. Each surface does what it's good at.

| Chat Skill (Claude.ai) | Claude Code Plugin |
|------------------------|-------------------|
| Decision frameworks | Slash commands and agents |
| Tradeoff analysis | Source-code grepping |
| Structured handoff docs | Implementation and testing |
| Domain reasoning | Session logging and learning |
| Static (expert knowledge) | Dynamic (knowledge that evolves) |

## The Epistemic Layer

Every plugin with a `knowledge/` directory runs the same protocol:

**Session start:** Read `manifest.json` for current state. Load active claims sorted by confidence. Check `tensions.jsonl` for unresolved conflicts in the task's domain. Surface tensions before making decisions, not after.

**During work:** Track which claims informed each suggestion. Note when the user accepts, modifies, or rejects a recommendation.

**Session end:** Write observations to `session_log/`. Flag contradictions as tension signals. Note recurring patterns the knowledge base doesn't yet cover.

The knowledge types are borrowed from Theseus (a separate epistemic engine project):

- **Claims**: factual assertions with confidence scores and evidence links
- **Tensions**: unresolved conflicts between claims or approaches
- **Questions**: open research threads the plugin hasn't resolved
- **Methods**: process knowledge (how to do X effectively)
- **Preferences**: user-specific defaults that override generic best practices

Current knowledge stats across the fleet:

| Plugin | Total Claims | Active | Avg Confidence |
|--------|-------------|--------|----------------|
| UI-Design-Pro | 140 | 135 | 0.667 |
| Django-Engine-Pro | 111 | 29 | 0.75 |

## Available Plugins

| Plugin | Domain | What It Knows |
|--------|--------|---------------|
| **[ML-Pro](./ml-pro)** | Machine Learning | PyTorch, GNNs, Transformers, training loops, model architecture, deployment |
| **[SciPy-Pro](./scipy-pro)** | Epistemic Engineering | NLP pipelines, graph theory, causal inference, knowledge representation, Bayesian reasoning |
| **[UI-Design-Pro](./ui-design-pro)** | Web UI Design | Design theory, visual judgment, shadcn/Radix internals, polymorphic rendering, accessibility |
| **[UX-Pro](./ux-pro)** | UX Research | Interaction design, information architecture, accessibility auditing, service design |
| **[Django-Design](./django-design)** | Full-Stack Django | HTMX, Alpine.js, Tailwind, D3 integration, Cotton components, design systems |
| **[Django-Engine-Pro](./django-engine-pro)** | Backend Engine | ORM optimization, DRF vs. Ninja, django-polymorphic, Pydantic v2, MCP server design |
| **[D3-Pro](./d3-pro)** | Data Visualization | D3.js scales, transitions, force layouts, geographic projections, math-heavy viz |
| **[Three-Pro](./three-pro)** | 3D Visualization | Three.js, shaders, physics simulation, WebGL, 3D graph embeddings |
| **[Animation-Pro](./animation-pro)** | Motion Design | Spring physics, state-driven animation, CSS/JS motion patterns, performance |
| **[JS-Pro](./ui-lab/JS-Pro)** | JS Engineering | Advanced JavaScript/TypeScript patterns, React internals, architectural standards |
| **[Shipit](./shipit)** | Deployment | Handoff documents, CI/CD configuration, shipping protocols |

## Source-Code References

Many plugins grep real library source instead of relying on training data. Each plugin's `install.sh` clones the repos it needs:

**UI-Design-Pro** references: shadcn/ui, Radix Primitives, Motion, Radix Colors, Tailwind CSS, Open Props, cmdk, Vaul, Sonner, DaisyUI, Park UI (~115 MB total with `--depth=1`)

**ML-Pro** references: PyTorch source, Hugging Face Transformers

**D3-Pro** references: Observable's D3 modules, examples collection

**Three-Pro** references: Three.js core, examples, shader chunks

The pattern is always the same: shallow-clone into `refs/`, then grep when you need an answer. The `refs/` directories are gitignored. Run `./install.sh` inside any plugin to populate them.

## Chat Skill Companions

Standalone specifications and chat skills for Claude.ai live in the root directory:

- `django-engine-pro-plugin-spec.md` (60K): Full specification for the Django backend plugin
- `ui-design-pro-plugin-spec.md` (77K): Full specification for the UI design plugin
- `django-engine-pro-epistemic-layer.md` (39K): Epistemic layer specification shared across plugins

These specs serve as the bridge between the planning surface (chat skills) and the implementation surface (Claude Code plugins). The chat skills are installed separately via Claude.ai's custom skill system.

## Installation

```bash
# Clone the repo
git clone https://github.com/Travis-Gilbert/Plugins-building.git codex-plugins
cd codex-plugins

# Sync all plugins to Claude Code
./sync-plugins.sh

# Sync a single plugin
./sync-plugins.sh d3-pro

# Check what's linked
./sync-plugins.sh --status

# Remove a plugin
./sync-plugins.sh --uninstall d3-pro
```

The sync script handles three things: symlinking plugin directories into the Claude Code marketplace path (`~/.claude/plugins/marketplaces/local-desktop-app-uploads/`), registering them in `installed_plugins.json`, and enabling them in `settings.json`. If the enablement step fails, manually add `"<plugin-name>@local-desktop-app-uploads": true` to `enabledPlugins` in `~/.claude/settings.json`.

After syncing, populate source references for any plugin you plan to use:

```bash
cd ui-design-pro && ./install.sh   # clones 11 repos (~115 MB)
cd ../ml-pro && ./install.sh        # clones ML source refs
```

## How This Compares

The Claude Code plugin ecosystem is growing fast. A few projects are working in adjacent territory:

**Empirica** (Nubaeon/empirica) is an epistemic measurement system with 13 confidence vectors, a Sentinel gate, and Brier score calibration. It's horizontal: one measurement layer across all of Claude Code, domain-agnostic. It asks "does the agent know enough to act right now?"

**epistemic-protocols** (jongwony) offers Socratic self-questioning plugins for surfacing unknowns. Lightweight, no persistence.

**Anthropic's knowledge-work-plugins** provide role-based starter kits (sales, support, product management) with skills and connectors. No epistemic layer, no source-code references.

This repo takes a different approach. Each plugin is a *vertical* specialist that accumulates domain-specific knowledge over time, greps real source code instead of trusting training data, and coordinates with a planning-layer chat skill through structured handoff documents. The question it asks is not "is the agent ready to act?" but "what has this specialist learned across every session it has ever run, and how confident should it be in each piece of that knowledge?"

## Structure

```
codex-plugins/
├── sync-plugins.sh              # Installs/syncs all plugins to Claude Code
├── django-engine-pro/           # Backend Django specialist
│   ├── .claude-plugin/          # Plugin manifest
│   ├── agents/                  # Specialist agent definitions
│   ├── commands/                # Slash commands
│   ├── knowledge/               # Epistemic layer (claims, tensions, sessions)
│   ├── references/              # Static decision frameworks
│   ├── skills/                  # Domain knowledge files
│   └── templates/               # Output templates
├── ui-design-pro/               # UI design specialist
│   ├── chat-skill/              # Companion Claude.ai skill
│   ├── knowledge/               # Epistemic layer + SBERT embeddings
│   ├── refs/                    # Cloned library source (gitignored)
│   └── ...
├── ml-pro/                      # Machine learning specialist
├── scipy-pro/                   # Epistemic engineering specialist
├── d3-pro/                      # D3 visualization specialist
├── three-pro/                   # Three.js 3D specialist
├── animation-pro/               # Motion design specialist
├── ux-pro/                      # UX research specialist
├── django-design/               # Django frontend specialist
├── shipit/                      # Deployment and handoff
├── ui-lab/JS-Pro/               # JavaScript engineering
├── skills/                      # Legacy skill workflows
└── *.md                         # Plugin specs and chat skill definitions
```
