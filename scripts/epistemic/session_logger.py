"""Session event logger — pure file I/O, no ML dependencies.

This module provides a lightweight logger that writes JSONL events to
knowledge/session_log/{timestamp}.jsonl. It is designed to be called
from Claude Code agents during sessions via simple file operations.

The session log is the raw material for Sprint 3's between-session
learning pipeline (evidence collection, confidence updates).

Usage from Python:
    from scripts.epistemic.session_logger import SessionLogger

    logger = SessionLogger("django-design", project="apply.thelandbank.org")
    logger.start(files_open=["views.py", "models.py"])
    logger.agent_invoked("orm-specialist", trigger="writing queryset")
    logger.claim_consulted("django-claim-042", relevance_score=0.89)
    logger.suggestion("code_pattern", file="views.py", lines=[45, 52],
                       claim_refs=["django-claim-042"])
    logger.suggestion_outcome("sug-001", outcome="accepted")
    logger.end(files_changed=["views.py", "models.py", "admin.py"])

Usage from Claude Code (file I/O approach):
    Agents can also write events directly to the session log file
    as JSON lines. See the /session-save command for the flush protocol.
"""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime
from pathlib import Path

from .config import knowledge_path, SESSION_LOG_DIR


class SessionLogger:
    """Append-only JSONL logger for session events."""

    def __init__(self, plugin_name: str, project: str = ""):
        self.plugin_name = plugin_name
        self.project = project
        self._start_time = time.time()
        self._suggestion_counter = 0

        # Create session log directory
        self._log_dir = knowledge_path(plugin_name) / SESSION_LOG_DIR
        self._log_dir.mkdir(parents=True, exist_ok=True)

        # Session file named by start timestamp
        ts = datetime.now().strftime("%Y%m%dT%H%M%S")
        self._log_file = self._log_dir / f"{ts}.jsonl"
        self._events: list[dict] = []

    def _write_event(self, event: dict) -> None:
        """Append a single event to the log file."""
        event.setdefault("timestamp", datetime.now().isoformat())
        self._events.append(event)
        with open(self._log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def start(self, files_open: list[str] | None = None) -> None:
        """Log session start."""
        self._write_event({
            "event": "session_start",
            "project": self.project,
            "files_open": files_open or [],
        })

    def end(self, files_changed: list[str] | None = None) -> None:
        """Log session end with duration."""
        elapsed = (time.time() - self._start_time) / 60.0
        self._write_event({
            "event": "session_end",
            "duration_minutes": round(elapsed, 1),
            "files_changed": files_changed or [],
        })

    def agent_invoked(self, agent: str, trigger: str = "") -> None:
        """Log when an agent is invoked."""
        self._write_event({
            "event": "agent_invoked",
            "agent": agent,
            "trigger": trigger,
        })

    def claim_consulted(self, claim_id: str, relevance_score: float = 0.0) -> None:
        """Log when a knowledge claim is consulted."""
        self._write_event({
            "event": "claim_consulted",
            "claim_id": claim_id,
            "relevance_score": round(relevance_score, 3),
        })

    def suggestion(
        self,
        suggestion_type: str,
        file: str = "",
        lines: list[int] | None = None,
        claim_refs: list[str] | None = None,
        content_hash: str = "",
    ) -> str:
        """Log a suggestion made during the session. Returns the suggestion ID."""
        self._suggestion_counter += 1
        sug_id = f"sug-{self._suggestion_counter:03d}"

        if not content_hash and file:
            # Generate a hash from the file + lines for matching later
            raw = f"{file}:{lines or []}"
            content_hash = hashlib.sha256(raw.encode()).hexdigest()[:8]

        self._write_event({
            "event": "suggestion",
            "suggestion_id": sug_id,
            "suggestion_type": suggestion_type,
            "content_hash": content_hash,
            "file": file,
            "lines": lines or [],
            "claim_refs": claim_refs or [],
        })
        return sug_id

    def suggestion_outcome(
        self,
        suggestion_id: str,
        outcome: str,
        modifications: str = "",
    ) -> None:
        """Log the outcome of a suggestion (accepted/modified/rejected/abandoned)."""
        self._write_event({
            "event": "suggestion_outcome",
            "suggestion_id": suggestion_id,
            "outcome": outcome,
            "modifications": modifications,
        })

    def tension_surfaced(
        self,
        description: str,
        related_claims: list[str] | None = None,
        priority: str = "medium",
    ) -> None:
        """Log when a tension between claims is discovered during the session."""
        self._write_event({
            "event": "tension_surfaced",
            "description": description,
            "related_claims": related_claims or [],
            "priority": priority,
        })

    def candidate_claim(
        self,
        description: str,
        related_claims: list[str] | None = None,
    ) -> None:
        """Log when a potential new claim is observed during the session."""
        self._write_event({
            "event": "candidate_claim",
            "description": description,
            "related_claims": related_claims or [],
        })

    @property
    def log_path(self) -> Path:
        return self._log_file

    @property
    def event_count(self) -> int:
        return len(self._events)


def read_session_log(filepath: Path) -> list[dict]:
    """Read all events from a session log file."""
    events = []
    for line in filepath.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            events.append(json.loads(line))
    return events


def list_session_logs(plugin_name: str) -> list[Path]:
    """List all session log files for a plugin, newest first."""
    log_dir = knowledge_path(plugin_name) / SESSION_LOG_DIR
    if not log_dir.exists():
        return []
    return sorted(log_dir.glob("*.jsonl"), reverse=True)
