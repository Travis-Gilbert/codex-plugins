"""Central configuration for the epistemic knowledge layer.

All paths are relative to REPO_ROOT so the scripts work from any cwd.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

PLUGINS: dict[str, str] = {
    "django-design": "django-design",
    "ml-pro": "ml-pro",
    "ui-design-pro": "ui-design-pro",
    "animation-pro": "animation-pro",
    "ux-pro": "ux-pro",
}

KNOWLEDGE_DIR = "knowledge"

# JSONL / JSON filenames inside knowledge/
CLAIMS_FILE = "claims.jsonl"
TENSIONS_FILE = "tensions.jsonl"
METHODS_FILE = "methods.jsonl"
QUESTIONS_FILE = "questions.jsonl"
PREFERENCES_FILE = "preferences.jsonl"
MANIFEST_FILE = "manifest.json"
SESSION_LOG_DIR = "session_log"

# ---------------------------------------------------------------------------
# Source file patterns to scan during seeding
# ---------------------------------------------------------------------------

AGENT_GLOB = "agents/*.md"
SKILL_GLOB = "skills/*/SKILL.md"
CLAUDE_MD = "CLAUDE.md"

# ---------------------------------------------------------------------------
# Bayesian priors
# ---------------------------------------------------------------------------

DEFAULT_ALPHA = 2.0
DEFAULT_BETA = 1.0
DEFAULT_CONFIDENCE = DEFAULT_ALPHA / (DEFAULT_ALPHA + DEFAULT_BETA)  # 0.667

# Temporal decay: multiply alpha and beta by this every 30 days without validation
DECAY_FACTOR = 0.95
DECAY_INTERVAL_DAYS = 30
CONFIDENCE_FLOOR = 0.3  # decay alone cannot push below this

# ---------------------------------------------------------------------------
# Seeder settings
# ---------------------------------------------------------------------------

INITIAL_STATUS = "draft"
MIN_CLAIM_LENGTH = 10
MAX_CLAIM_LENGTH = 500

# Imperative verbs that signal a claim in prose (case-insensitive match at sentence start)
IMPERATIVE_MARKERS = [
    "always", "never", "must", "should", "do not", "don't",
    "avoid", "ensure", "verify", "check", "use", "prefer",
    "require", "enforce",
]

# Weak-signal words that suggest heuristic rather than best_practice
HEURISTIC_MARKERS = ["consider", "might", "could", "may", "optional", "when possible"]

# ---------------------------------------------------------------------------
# Domain mapping
# ---------------------------------------------------------------------------

# Agent filename (without .md) -> default domain prefix
AGENT_DOMAIN_MAP: dict[str, str] = {
    # django-design
    "django-architect": "django",
    "django-api-reviewer": "django.api",
    "django-frontend": "django.frontend",
    "django-migrator": "django.migrations",
    "django-profiler": "django.performance",
    # ml-pro
    "model-architect": "ml.architecture",
    "training-engineer": "ml.training",
    "ml-debugger": "ml.debugging",
    "graph-engineer": "ml.graphs",
    "systems-optimizer": "ml.systems",
    # ui-design-pro
    "visual-architect": "ui.layout",
    "component-builder": "ui.components",
    "design-critic": "ui.review",
    "a11y-auditor": "ui.accessibility",
    "stack-detector": "ui.stack",
    "animation-engineer": "ui.animation",
    # animation-pro
    "motion-architect": "animation.motion",
    "spring-engineer": "animation.springs",
    "gesture-engineer": "animation.gestures",
    "scroll-animator": "animation.scroll",
    "scene-animator": "animation.3d",
    "camera-choreographer": "animation.camera",
    "creative-coder": "animation.creative",
    "physics-simulator": "animation.physics",
    "video-compositor": "animation.video",
    "a11y-motion-auditor": "animation.accessibility",
    # ux-pro
    "accessibility-auditor": "ux.accessibility",
    "information-architect": "ux.ia",
    "interaction-designer": "ux.interaction",
    "service-designer": "ux.service",
    "usability-tester": "ux.testing",
    "ux-researcher": "ux.research",
    "ux-writer": "ux.writing",
}

# Markdown heading keywords -> subdomain suffix (appended to agent domain)
HEADING_DOMAIN_MAP: dict[str, str] = {
    "models.py": "models",
    "models": "models",
    "views.py": "views",
    "views": "views",
    "settings": "settings",
    "admin": "admin",
    "urls": "urls",
    "forms": "forms",
    "templates": "templates",
    "cotton": "templates.cotton",
    "htmx": "frontend.htmx",
    "alpine": "frontend.alpine",
    "design token": "frontend.design_system",
    "design system": "frontend.design_system",
    "serializer": "api.serializers",
    "viewset": "api.viewsets",
    "url routing": "api.urls",
    "throttl": "api.throttling",
    "permission": "api.permissions",
    "schema migration": "migrations.schema",
    "data migration": "migrations.data",
    "query": "performance.queries",
    "n+1": "performance.n_plus_one",
    "index": "performance.indexes",
    "cross-pillar": "cross_pillar",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def plugin_path(plugin_name: str) -> Path:
    """Absolute path to a plugin directory."""
    return REPO_ROOT / PLUGINS[plugin_name]


def knowledge_path(plugin_name: str) -> Path:
    """Absolute path to a plugin's knowledge/ directory."""
    return plugin_path(plugin_name) / KNOWLEDGE_DIR
