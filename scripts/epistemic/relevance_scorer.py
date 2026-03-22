"""Stage 5: Relevance Scorer.

A small MLP that predicts claim relevance given session context.
Replaces tag-matching with learned ranking.

Architecture:
  Input: concat(claim_embedding[384], project_embedding[32], task_embedding[64]) = 480
    -> Linear(480, 128) -> ReLU -> Dropout(0.3)
    -> Linear(128, 32) -> ReLU -> Dropout(0.2)
    -> Linear(32, 1) -> Sigmoid
  Output: relevance probability [0, 1]

~62K parameters. Trains in seconds on CPU.

Training data from session logs:
  Positive: claim was consulted AND suggestion was accepted
  Negative: claim exists in domain but was not consulted (or was rejected)

Falls back to cosine similarity when < 50 training examples.

Weights saved as JSON (not binary) for portability and inspectability.
Note: model.state_dict() values are extracted to numpy arrays then
serialized to JSON lists. No binary serialization is used.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

from .config import (
    CLAIMS_FILE,
    SESSION_LOG_DIR,
    PLUGINS,
    knowledge_path,
    plugin_path,
)
from .embedding_manager import EMBEDDING_DIM, load_embeddings, embed_texts, cosine_similarity


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_EMBED_DIM = 32
TASK_EMBED_DIM = 64
INPUT_DIM = EMBEDDING_DIM + PROJECT_EMBED_DIM + TASK_EMBED_DIM  # 480
HIDDEN_1 = 128
HIDDEN_2 = 32
MIN_TRAINING_EXAMPLES = 50
SCORER_WEIGHTS_FILE = "scorer_weights.json"
LEARNING_RATE = 0.001
EPOCHS = 50
BATCH_SIZE = 32


# ---------------------------------------------------------------------------
# Pure numpy MLP (no PyTorch dependency for inference)
# ---------------------------------------------------------------------------

class RelevanceScorer:
    """Small MLP for claim relevance scoring, implemented in pure numpy.

    Uses PyTorch only for training (gradient computation). Inference
    and weight storage are pure numpy + JSON.
    """

    def __init__(self):
        self.w1: np.ndarray | None = None
        self.b1: np.ndarray | None = None
        self.w2: np.ndarray | None = None
        self.b2: np.ndarray | None = None
        self.w3: np.ndarray | None = None
        self.b3: np.ndarray | None = None
        self.project_embeddings: dict[str, np.ndarray] = {}
        self._trained = False

    @property
    def is_trained(self) -> bool:
        return self._trained

    def predict(self, x: np.ndarray) -> np.ndarray:
        """Forward pass in pure numpy. x: (N, INPUT_DIM) -> (N,) probabilities."""
        if not self._trained:
            raise RuntimeError("Scorer not trained. Call train() or load() first.")
        h1 = np.maximum(x @ self.w1 + self.b1, 0)
        h2 = np.maximum(h1 @ self.w2 + self.b2, 0)
        logits = h2 @ self.w3 + self.b3
        return 1.0 / (1.0 + np.exp(-logits.squeeze(-1)))

    def score_claims(
        self,
        claim_embeddings: np.ndarray,
        project_name: str,
        task_description: str,
    ) -> np.ndarray:
        """Score a batch of claims for relevance."""
        n = claim_embeddings.shape[0]
        proj_emb = self.project_embeddings.get(
            project_name, np.zeros(PROJECT_EMBED_DIM, dtype=np.float32))
        proj_batch = np.tile(proj_emb, (n, 1))
        task_emb = _task_embedding(task_description)
        task_batch = np.tile(task_emb, (n, 1))
        x = np.concatenate([claim_embeddings, proj_batch, task_batch], axis=1)
        return self.predict(x)

    def save(self, filepath: Path) -> None:
        """Save weights as JSON for portability."""
        data = {
            "w1": self.w1.tolist(), "b1": self.b1.tolist(),
            "w2": self.w2.tolist(), "b2": self.b2.tolist(),
            "w3": self.w3.tolist(), "b3": self.b3.tolist(),
            "project_embeddings": {k: v.tolist() for k, v in self.project_embeddings.items()},
            "input_dim": INPUT_DIM, "hidden_1": HIDDEN_1, "hidden_2": HIDDEN_2,
        }
        filepath.write_text(json.dumps(data, indent=2) + "\n")

    def load(self, filepath: Path) -> None:
        """Load weights from JSON."""
        data = json.loads(filepath.read_text())
        self.w1 = np.array(data["w1"], dtype=np.float32)
        self.b1 = np.array(data["b1"], dtype=np.float32)
        self.w2 = np.array(data["w2"], dtype=np.float32)
        self.b2 = np.array(data["b2"], dtype=np.float32)
        self.w3 = np.array(data["w3"], dtype=np.float32)
        self.b3 = np.array(data["b3"], dtype=np.float32)
        self.project_embeddings = {
            k: np.array(v, dtype=np.float32) for k, v in data.get("project_embeddings", {}).items()
        }
        self._trained = True


# ---------------------------------------------------------------------------
# Task embedding (hash-based projection)
# ---------------------------------------------------------------------------

def _task_embedding(task_description: str) -> np.ndarray:
    """Create a fixed-size task embedding via hash projection."""
    if not task_description:
        return np.zeros(TASK_EMBED_DIM, dtype=np.float32)
    tokens = task_description.lower().split()
    emb = np.zeros(TASK_EMBED_DIM, dtype=np.float32)
    for token in tokens:
        emb[hash(token) % TASK_EMBED_DIM] += 1.0
    norm = np.linalg.norm(emb)
    if norm > 0:
        emb /= norm
    return emb


# ---------------------------------------------------------------------------
# Training data extraction
# ---------------------------------------------------------------------------

def _extract_training_data(plugin_name: str) -> tuple[list[dict], list[str]]:
    """Extract labeled examples from session logs."""
    kpath = knowledge_path(plugin_name)
    log_dir = kpath / SESSION_LOG_DIR
    if not log_dir.exists():
        return [], []

    claims_file = kpath / CLAIMS_FILE
    claim_ids_set: set[str] = set()
    claim_domains: dict[str, str] = {}
    if claims_file.exists():
        for line in claims_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                c = json.loads(line)
                claim_ids_set.add(c["id"])
                claim_domains[c["id"]] = c.get("domain", "")

    examples = []
    projects = set()

    for log_file in sorted(log_dir.glob("*.jsonl")):
        session_project = ""
        session_agents: list[str] = []
        session_files: list[str] = []
        consulted_claims: set[str] = set()
        accepted_claims: set[str] = set()
        rejected_claims: set[str] = set()
        suggestion_claims: dict[str, list[str]] = {}

        for line in log_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            etype = event.get("event", "")
            if etype == "session_start":
                session_project = event.get("project", "")
                session_files = event.get("files_open", [])
                projects.add(session_project)
            elif etype == "agent_invoked":
                session_agents.append(event.get("agent", ""))
            elif etype == "claim_consulted":
                consulted_claims.add(event.get("claim_id", ""))
            elif etype == "suggestion":
                sid = event.get("suggestion_id", "")
                suggestion_claims[sid] = event.get("claim_refs", [])
            elif etype == "suggestion_outcome":
                sid = event.get("suggestion_id", "")
                outcome = event.get("outcome", "")
                for cid in suggestion_claims.get(sid, []):
                    if outcome == "accepted":
                        accepted_claims.add(cid)
                    elif outcome in ("rejected", "abandoned"):
                        rejected_claims.add(cid)

        task = " ".join(session_agents + session_files)

        for cid in accepted_claims:
            examples.append({"claim_id": cid, "project": session_project, "task": task, "label": 1.0})
        for cid in rejected_claims:
            examples.append({"claim_id": cid, "project": session_project, "task": task, "label": 0.0})

        if consulted_claims:
            session_domains = set()
            for cid in consulted_claims:
                domain = claim_domains.get(cid, "")
                for i in range(len(domain.split("."))):
                    session_domains.add(".".join(domain.split(".")[:i + 1]))
            for cid in claim_ids_set - consulted_claims:
                domain = claim_domains.get(cid, "")
                if any(domain.startswith(sd) for sd in session_domains):
                    examples.append({"claim_id": cid, "project": session_project, "task": task, "label": 0.0})

    return examples, list(projects)


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train_scorer(plugin_name: str) -> dict:
    """Train the relevance scorer MLP, save weights as JSON."""
    examples, projects = _extract_training_data(plugin_name)

    if len(examples) < MIN_TRAINING_EXAMPLES:
        return {
            "plugin": plugin_name, "status": "skipped",
            "reason": f"Only {len(examples)} examples (need {MIN_TRAINING_EXAMPLES}+)",
        }

    emb_data = load_embeddings(plugin_name)
    if emb_data is None:
        return {"plugin": plugin_name, "status": "error", "reason": "No embeddings"}
    embeddings, claim_ids = emb_data
    id_to_idx = {cid: i for i, cid in enumerate(claim_ids)}

    import torch
    import torch.nn as nn

    project_to_idx = {p: i for i, p in enumerate(projects)}

    X_list, y_list = [], []
    for ex in examples:
        cid = ex["claim_id"]
        if cid not in id_to_idx:
            continue
        claim_emb = embeddings[id_to_idx[cid]]
        proj_emb = np.zeros(PROJECT_EMBED_DIM, dtype=np.float32)
        proj_emb[project_to_idx.get(ex["project"], 0) % PROJECT_EMBED_DIM] = 1.0
        task_emb = _task_embedding(ex["task"])
        X_list.append(np.concatenate([claim_emb, proj_emb, task_emb]))
        y_list.append(ex["label"])

    if len(X_list) < MIN_TRAINING_EXAMPLES:
        return {"plugin": plugin_name, "status": "skipped",
                "reason": f"Only {len(X_list)} valid examples after filtering"}

    X = torch.tensor(np.array(X_list), dtype=torch.float32)
    y = torch.tensor(np.array(y_list), dtype=torch.float32)

    n = len(X)
    perm = torch.randperm(n)
    split = int(n * 0.8)
    X_train, X_test = X[perm[:split]], X[perm[split:]]
    y_train, y_test = y[perm[:split]], y[perm[split:]]

    model = nn.Sequential(
        nn.Linear(INPUT_DIM, HIDDEN_1), nn.ReLU(), nn.Dropout(0.3),
        nn.Linear(HIDDEN_1, HIDDEN_2), nn.ReLU(), nn.Dropout(0.2),
        nn.Linear(HIDDEN_2, 1), nn.Sigmoid(),
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    criterion = nn.BCELoss()

    model.train()
    for epoch in range(EPOCHS):
        for i in range(0, len(X_train), BATCH_SIZE):
            pred = model(X_train[i:i + BATCH_SIZE]).squeeze(-1)
            loss = criterion(pred, y_train[i:i + BATCH_SIZE])
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    model.eval()
    with torch.no_grad():
        test_pred = model(X_test).squeeze(-1)
        accuracy = ((test_pred > 0.5).float() == y_test).float().mean().item()

    print(f"  Scorer accuracy: {accuracy:.3f} ({len(X_train)} train, {len(X_test)} test)", file=sys.stderr)

    # Extract weights to numpy arrays, then save as JSON lists
    scorer = RelevanceScorer()
    state = model.state_dict()
    scorer.w1 = state["0.weight"].numpy().T
    scorer.b1 = state["0.bias"].numpy()
    scorer.w2 = state["3.weight"].numpy().T
    scorer.b2 = state["3.bias"].numpy()
    scorer.w3 = state["6.weight"].numpy().T
    scorer.b3 = state["6.bias"].numpy()
    scorer._trained = True

    for proj, idx in project_to_idx.items():
        emb = np.zeros(PROJECT_EMBED_DIM, dtype=np.float32)
        emb[idx % PROJECT_EMBED_DIM] = 1.0
        scorer.project_embeddings[proj] = emb

    kpath = knowledge_path(plugin_name)
    scorer.save(kpath / SCORER_WEIGHTS_FILE)

    return {
        "plugin": plugin_name, "status": "trained",
        "accuracy": round(accuracy, 4),
        "train_size": len(X_train), "test_size": len(X_test),
        "projects": projects,
    }


# ---------------------------------------------------------------------------
# Fallback: cosine similarity scoring
# ---------------------------------------------------------------------------

def score_claims_fallback(plugin_name: str, task_description: str, top_k: int = 20) -> list[dict]:
    """Score claims using cosine similarity when scorer is not trained."""
    kpath = knowledge_path(plugin_name)
    claims_file = kpath / CLAIMS_FILE
    emb_data = load_embeddings(plugin_name)
    if emb_data is None:
        return []
    embeddings, claim_ids = emb_data

    claims_by_id = {}
    for line in claims_file.read_text(encoding="utf-8").splitlines():
        if line.strip():
            c = json.loads(line)
            if c.get("status") == "active":
                claims_by_id[c["id"]] = c

    task_emb = embed_texts([task_description])
    sims = cosine_similarity(task_emb, embeddings)[0]

    results = []
    for idx in np.argsort(sims)[::-1]:
        cid = claim_ids[idx]
        if cid not in claims_by_id:
            continue
        claim = claims_by_id[cid]
        results.append({
            "claim_id": cid, "text": claim.get("text", ""),
            "relevance": float(sims[idx]),
            "confidence": claim.get("confidence", 0),
            "domain": claim.get("domain", ""),
        })
        if len(results) >= top_k:
            break
    return results


# ---------------------------------------------------------------------------
# Combined scorer
# ---------------------------------------------------------------------------

def score_claims(plugin_name: str, task_description: str, project_name: str = "", top_k: int = 20) -> list[dict]:
    """Score and rank claims for relevance. Uses MLP if trained, else cosine fallback."""
    kpath = knowledge_path(plugin_name)
    weights_file = kpath / SCORER_WEIGHTS_FILE

    if weights_file.exists():
        scorer = RelevanceScorer()
        scorer.load(weights_file)
        emb_data = load_embeddings(plugin_name)
        if emb_data is None:
            return score_claims_fallback(plugin_name, task_description, top_k)
        embeddings, claim_ids = emb_data

        claims_file = kpath / CLAIMS_FILE
        claims_by_id = {}
        for line in claims_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                c = json.loads(line)
                if c.get("status") == "active":
                    claims_by_id[c["id"]] = c

        active_indices = [i for i, cid in enumerate(claim_ids) if cid in claims_by_id]
        if not active_indices:
            return []

        active_embeddings = embeddings[active_indices]
        active_ids = [claim_ids[i] for i in active_indices]
        scores = scorer.score_claims(active_embeddings, project_name, task_description)

        results = []
        for idx in np.argsort(scores)[::-1]:
            cid = active_ids[idx]
            claim = claims_by_id[cid]
            results.append({
                "claim_id": cid, "text": claim.get("text", ""),
                "relevance": round(float(scores[idx]), 4),
                "confidence": claim.get("confidence", 0),
                "domain": claim.get("domain", ""),
            })
            if len(results) >= top_k:
                break
        return results
    else:
        return score_claims_fallback(plugin_name, task_description, top_k)
