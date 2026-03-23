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
    "django-engine-pro": "django-engine-pro",
    "ml-pro": "ml-pro",
    "ui-design-pro": "ui-design-pro",
    "animation-pro": "animation-pro",
    "ux-pro": "ux-pro",
    "next-pro": "next-pro",
    "app-pro": "app-pro",
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
    # django-engine-pro
    "model-architect": "engine.models",
    "orm-specialist": "engine.orm",
    "api-architect": "engine.api",
    "polymorphic-engineer": "engine.polymorphic",
    "mcp-builder": "engine.mcp",
    "data-bridge": "engine.bridge",
    "pydantic-specialist": "engine.pydantic",
    # ux-pro
    "accessibility-auditor": "ux.accessibility",
    "information-architect": "ux.ia",
    "interaction-designer": "ux.interaction",
    "service-designer": "ux.service",
    "usability-tester": "ux.testing",
    "ux-researcher": "ux.research",
    "ux-writer": "ux.writing",
    # next-pro (development track)
    "next-feature": "next.feature",
    "next-data": "next.data",
    "next-routing": "next.routing",
    "next-metadata": "next.metadata",
    "next-middleware": "next.middleware",
    # next-pro (diagnostic track)
    "next-triage": "next.triage",
    "next-hydration": "next.hydration",
    "next-rsc": "next.rsc",
    "next-build": "next.build",
    "next-devserver": "next.devserver",
    "next-debug-route": "next.debug_route",
    "next-runtime": "next.runtime",
    # app-pro
    "pwa-engineer": "app.pwa",
    "rn-architect": "app.react_native",
    "mobile-optimizer": "app.optimization",
    "offline-engineer": "app.offline",
    "mobile-api": "app.api",
    "viz-adapter": "app.visualization",
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
    # django-engine-pro specific
    "inheritance": "models.inheritance",
    "polymorphic": "polymorphic",
    "mcp": "mcp",
    "pydantic": "pydantic",
    "dataframe": "bridge.dataframe",
    "pandas": "bridge.pandas",
    "numpy": "bridge.numpy",
    "scipy": "bridge.scipy",
    "bulk_create": "bridge.bulk",
    "prefetch": "orm.prefetch",
    "select_related": "orm.select_related",
    "window function": "orm.window",
    "manager": "orm.managers",
    "soft-delete": "models.soft_delete",
    "on_delete": "models.on_delete",
    "jsonfield": "models.jsonfield",
    "drf": "api.drf",
    "ninja": "api.ninja",
    "openapi": "api.openapi",
    # next-pro specific
    "server component": "rsc",
    "client component": "client_component",
    "hydration": "hydration",
    "app router": "routing.app_router",
    "page router": "routing.pages_router",
    "layout": "routing.layouts",
    "middleware": "middleware",
    "server action": "data.server_actions",
    "use cache": "data.cache",
    "revalidat": "data.revalidation",
    "fetch": "data.fetching",
    "streaming": "rendering.streaming",
    "ppr": "rendering.ppr",
    "isr": "rendering.isr",
    "ssr": "rendering.ssr",
    "ssg": "rendering.ssg",
    "dynamic": "rendering.dynamic",
    "next/image": "components.image",
    "next/link": "components.link",
    "next/script": "components.script",
    "error boundary": "error_handling",
    "loading": "loading_states",
    "not-found": "error_handling.not_found",
    "edge runtime": "runtime.edge",
    "node runtime": "runtime.node",
    "turbopack": "build.turbopack",
    "webpack": "build.webpack",
    "hmr": "devserver.hmr",
    "fast refresh": "devserver.fast_refresh",
    # app-pro specific
    "service worker": "pwa.service_worker",
    "caching strategy": "pwa.caching",
    "manifest": "pwa.manifest",
    "install prompt": "pwa.install",
    "capacitor": "pwa.capacitor",
    "expo router": "react_native.navigation",
    "react navigation": "react_native.navigation",
    "platform adaptation": "react_native.platform",
    "shared logic": "react_native.shared",
    "touch target": "optimization.touch",
    "thumb zone": "optimization.touch",
    "gesture": "optimization.gestures",
    "safe area": "optimization.viewport",
    "offline": "offline",
    "sync": "offline.sync",
    "conflict": "offline.conflicts",
    "watermelondb": "offline.watermelondb",
    "token auth": "api.auth",
    "simplejwt": "api.auth",
    "cursor pagination": "api.pagination",
    "sparse field": "api.sparse",
    "composite endpoint": "api.composite",
    "push notification": "api.push",
    "quick capture": "api.capture",
    "mobile viz": "visualization",
    "force graph": "visualization.force",
    "skia": "visualization.skia",
    "victory": "visualization.victory",
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
