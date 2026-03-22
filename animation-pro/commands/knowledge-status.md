---
description: Show epistemic knowledge status — claim counts, confidence distribution, unresolved tensions, and open questions
allowed-tools: Read, Bash
argument-hint: (no arguments)
---

# Knowledge Status

Show the current state of this plugin's epistemic knowledge base.

## Steps

1. Read `knowledge/manifest.json` for last update time and summary stats.

2. Read `knowledge/claims.jsonl` and compute:
   - Total claims, active claims, draft claims, retired claims
   - Average confidence of active claims
   - Claims grouped by domain (top 10 domains)
   - 5 lowest-confidence active claims (these may need re-evaluation)
   - 5 highest-confidence active claims (most validated knowledge)

3. Read `knowledge/tensions.jsonl` and count:
   - Unresolved tensions
   - Context-dependent tensions
   - Resolved tensions

4. Read `knowledge/questions.jsonl` and count:
   - Open questions
   - Answered questions

5. Read `knowledge/preferences.jsonl` and count total preferences.

6. Read `knowledge/methods.jsonl` and count total methods.

## Output Format

Present a formatted summary:

```
## Knowledge Status: {plugin_name}

Last updated: {date}
Schema version: {version}

### Claims
| Status | Count |
|--------|-------|
| Active | {n} |
| Draft  | {n} |
| Retired| {n} |
| Total  | {n} |

Average confidence (active): {n:.2f}

### Top Domains
| Domain | Claims |
|--------|--------|
| ... | ... |

### Lowest Confidence (active)
| Claim | Confidence | Domain |
|-------|-----------|--------|
| ... | ... | ... |

### Tensions: {n} unresolved, {n} context-dependent, {n} resolved
### Questions: {n} open, {n} answered
### Methods: {n} total
### Preferences: {n} total
```
