"""Pydantic models for the epistemic knowledge layer.

Six primitive types define the knowledge a plugin carries:
- Claim: a typed proposition with confidence and evidence tracking
- Tension: a conflict between two claims
- Method: a reusable solution pattern with usage history
- Question: an open unknown flagged for investigation
- Preference: a user-specific default learned from accept/reject patterns
- Manifest: metadata about the knowledge base itself
"""

from __future__ import annotations

import hashlib
from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def claim_id(plugin: str, text: str) -> str:
    """Deterministic 12-char hex ID from plugin name + claim text."""
    raw = f"{plugin}:{text.strip().lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def today_iso() -> str:
    return date.today().isoformat()


# ---------------------------------------------------------------------------
# Claim
# ---------------------------------------------------------------------------

ClaimType = Literal[
    "best_practice",
    "architectural_rule",
    "preference",
    "empirical",
    "inherited",
    "heuristic",
]

ClaimStatus = Literal["draft", "active", "retired"]


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accepted: int = 0
    rejected: int = 0
    modified: int = 0


class Claim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    text: str
    domain: str
    agent_source: str
    type: ClaimType
    confidence: float = Field(default=0.667, ge=0.0, le=1.0)
    source: str = ""
    embedding_idx: Optional[int] = None
    first_seen: str = Field(default_factory=today_iso)
    last_validated: str = Field(default_factory=today_iso)
    status: ClaimStatus = "draft"
    evidence: Evidence = Field(default_factory=Evidence)
    projects_seen: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    related_claims: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Tension
# ---------------------------------------------------------------------------

TensionStatus = Literal["unresolved", "resolved", "context_dependent", "superseded"]


class ResolutionAttempt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: str
    approach: str
    outcome: str
    project: str = ""


class Tension(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    claim_a: str
    claim_b: str
    description: str
    domain: str
    status: TensionStatus = "unresolved"
    context_dependent: bool = False
    context_note: str = ""
    occurrences: int = 0
    first_seen: str = Field(default_factory=today_iso)
    resolution_attempts: list[ResolutionAttempt] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Method
# ---------------------------------------------------------------------------

class MethodVariant(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project: str
    modifications: str
    commit: str = ""
    date: str = ""


class Method(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    description: str
    template_file: Optional[str] = None
    usage_count: int = 0
    last_used: Optional[str] = None
    avg_satisfaction: float = 0.0
    variants: list[MethodVariant] = Field(default_factory=list)
    failure_modes: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Question
# ---------------------------------------------------------------------------

QuestionStatus = Literal["open", "answered", "deferred"]
Priority = Literal["low", "medium", "high"]


class Question(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    text: str
    domain: str
    status: QuestionStatus = "open"
    raised_by: str = "seeder"
    raised_date: str = Field(default_factory=today_iso)
    related_claims: list[str] = Field(default_factory=list)
    related_tensions: list[str] = Field(default_factory=list)
    priority: Priority = "medium"


# ---------------------------------------------------------------------------
# Preference
# ---------------------------------------------------------------------------

class BetaDistribution(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alpha: float = 2.0
    beta: float = 1.0


class Preference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    text: str
    domain: str
    strength: float = Field(default=0.667, ge=0.0, le=1.0)
    distribution: BetaDistribution = Field(default_factory=BetaDistribution)
    first_observed: str = Field(default_factory=today_iso)
    last_observed: str = Field(default_factory=today_iso)
    exceptions: list[str] = Field(default_factory=list)
    projects: dict[str, dict] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

class ManifestStats(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_claims: int = 0
    active_claims: int = 0
    draft_claims: int = 0
    tensions: int = 0
    methods: int = 0
    questions: int = 0
    preferences: int = 0
    avg_confidence: float = 0.0


class ModelVersions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_ver: str = Field(default="1.0.0", alias="schema")
    seeder: str = "1.0.0"


class UpdateLogEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: str
    action: str
    details: str


class Manifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1.0.0"
    plugin: str
    last_updated: str = Field(default_factory=today_iso)
    stats: ManifestStats = Field(default_factory=ManifestStats)
    model_versions: ModelVersions = Field(default_factory=ModelVersions)
    update_log: list[UpdateLogEntry] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Session Log Events
# ---------------------------------------------------------------------------

EventType = Literal[
    "session_start",
    "session_end",
    "agent_invoked",
    "claim_consulted",
    "suggestion",
    "suggestion_outcome",
    "tension_surfaced",
    "candidate_claim",
]

SuggestionOutcome = Literal[
    "accepted",
    "modified",
    "rejected",
    "abandoned",
]


class SessionEvent(BaseModel):
    """A single event in a session log. Uses discriminated union via `event` field."""
    model_config = ConfigDict(extra="allow")  # allow extra fields per event type

    event: EventType
    timestamp: str = Field(default_factory=lambda: __import__("datetime").datetime.now().isoformat())

    # session_start fields
    project: str = ""
    files_open: list[str] = Field(default_factory=list)

    # session_end fields
    duration_minutes: float = 0
    files_changed: list[str] = Field(default_factory=list)

    # agent_invoked fields
    agent: str = ""
    trigger: str = ""

    # claim_consulted fields
    claim_id: str = ""
    relevance_score: float = 0.0

    # suggestion fields
    suggestion_id: str = ""
    suggestion_type: str = ""
    content_hash: str = ""
    file: str = ""
    lines: list[int] = Field(default_factory=list)
    claim_refs: list[str] = Field(default_factory=list)

    # suggestion_outcome fields
    outcome: str = ""
    modifications: str = ""

    # tension_surfaced / candidate_claim fields
    description: str = ""
    related_claims: list[str] = Field(default_factory=list)
    priority: str = "medium"
