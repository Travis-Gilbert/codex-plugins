---
description: Review and activate draft claims, resolve tensions, and triage open questions
allowed-tools: Read, Write, Edit, AskUserQuestion
argument-hint: "[claims|tensions|questions]  (default: claims)"
---

# Knowledge Review

Interactive review of the epistemic knowledge base. Presents items for human decision-making.

## Arguments

- `claims` (default): Review draft claims for activation or retirement
- `tensions`: Review unresolved tensions for resolution
- `questions`: Review open questions for answers or deferral

## Reviewing Claims

1. Read `knowledge/claims.jsonl` and filter for `status: "draft"`.

2. Group draft claims by domain for contextual review.

3. Present claims in batches of 10, showing:
   - Claim text
   - Domain
   - Source (which agent/file extracted it)
   - Type classification

4. For each batch, ask the user:
   - **Activate**: Promote to `status: "active"` — this claim will influence future agent behavior
   - **Retire**: Set `status: "retired"` — this is not useful domain knowledge (structural metadata, duplicates, etc.)
   - **Edit**: Modify the claim text before activating
   - **Skip**: Leave as draft for later review
   - **Activate all**: Activate all claims in this batch
   - **Retire all**: Retire all claims in this batch (useful for batches of structural noise)

5. After each batch, update `knowledge/claims.jsonl` in place:
   - Read all lines, update matching IDs, write back

6. After all batches, update `knowledge/manifest.json` stats.

## Reviewing Tensions

1. Read `knowledge/tensions.jsonl` and filter for `status: "unresolved"`.

2. For each tension, show:
   - The two competing claims (read full text from claims.jsonl)
   - The tension description
   - Number of occurrences
   - Any previous resolution attempts

3. Ask the user to:
   - **Resolve**: Mark as resolved with a resolution note
   - **Context-dependent**: Both claims are valid in different contexts — add a context note
   - **Supersede**: One claim supersedes the other
   - **Skip**: Leave unresolved

## Reviewing Questions

1. Read `knowledge/questions.jsonl` and filter for `status: "open"`.

2. For each question, show:
   - Question text
   - Related claims and tensions
   - Priority level

3. Ask the user to:
   - **Answer**: Provide an answer (may generate a new claim)
   - **Defer**: Lower priority or mark for later
   - **Close**: Question is no longer relevant

## Important

- Never auto-activate claims. Human review is the gatekeeper.
- Present context: show the source agent and line number so the user can verify.
- After review, report how many items were activated, retired, resolved, etc.
