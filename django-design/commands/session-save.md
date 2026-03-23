---
description: Save session observations to the knowledge session log — records which claims were used, which suggestions were made, and their outcomes
allowed-tools: Read, Write, Bash, Grep, Glob
argument-hint: "[project-name]  (optional, auto-detected from git remote)"
---

# Session Save

Flush the current session's observations to `knowledge/session_log/`. This creates the raw evidence that the between-session learning pipeline (Sprint 3+) uses to update claim confidence.

## What to Record

Review the current session's work and write a JSONL session log capturing:

### 1. Session Context

```json
{"event": "session_start", "project": "<project-name>", "files_open": ["<files touched>"], "timestamp": "<ISO>"}
```

Detect the project name from `git remote get-url origin` or from the argument. List the files that were read or modified during this session.

### 2. Agents Invoked

For each agent that was used during this session:

```json
{"event": "agent_invoked", "agent": "<agent-name>", "trigger": "<why it was invoked>", "timestamp": "<ISO>"}
```

### 3. Claims Consulted

For each claim from `knowledge/claims.jsonl` that influenced a decision:

```json
{"event": "claim_consulted", "claim_id": "<id>", "relevance_score": 0.0, "timestamp": "<ISO>"}
```

If the knowledge-aware operation protocol was followed, note which active claims were loaded and which actually influenced the work.

### 4. Suggestions and Outcomes

For each significant suggestion made during the session (code patterns applied, architectural decisions, review findings):

```json
{"event": "suggestion", "suggestion_id": "sug-001", "suggestion_type": "<code_pattern|review_finding|architectural_decision>", "file": "<file>", "lines": [<start>, <end>], "claim_refs": ["<claim-ids>"], "timestamp": "<ISO>"}
```

Then for each suggestion, record the outcome:

```json
{"event": "suggestion_outcome", "suggestion_id": "sug-001", "outcome": "<accepted|modified|rejected|abandoned>", "modifications": "<what changed if modified>", "timestamp": "<ISO>"}
```

**How to determine outcomes:**
- **accepted**: The suggestion was applied as-is (check git diff or current file state)
- **modified**: The suggestion was partially applied with changes
- **rejected**: The user explicitly said no or reverted the change
- **abandoned**: The file was not committed or the suggestion was ignored

### 5. Tensions Discovered

If a claim was contradicted during this session or two claims conflicted:

```json
{"event": "tension_surfaced", "description": "<what conflicted>", "related_claims": ["<id1>", "<id2>"], "priority": "high", "timestamp": "<ISO>"}
```

### 6. Candidate Claims

If a recurring pattern was observed that the knowledge base doesn't cover:

```json
{"event": "candidate_claim", "description": "<the pattern>", "related_claims": [], "timestamp": "<ISO>"}
```

### 7. Session End

```json
{"event": "session_end", "duration_minutes": <minutes>, "files_changed": ["<committed files>"], "timestamp": "<ISO>"}
```

## Output

Write all events to `knowledge/session_log/{YYYYMMDD}T{HHMMSS}.jsonl`.

After writing, report:
- Session log file path
- Number of events recorded
- Claims consulted count
- Suggestions made and their outcomes
- Any tensions or candidate claims flagged

## Important Notes

- This is pure observation — do not modify claims.jsonl or any knowledge files.
- Be honest about outcomes — rejected suggestions are the most valuable signal for learning.
- If no claims were consulted (knowledge system not yet active), that's fine — still log agents and suggestions.
- Session logs are the raw training data for confidence updates. Quality > quantity.
