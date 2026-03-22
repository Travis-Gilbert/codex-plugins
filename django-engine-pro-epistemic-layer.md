# Django-Engine-Pro: Epistemic Learning Layer

> Extension to the Django-Engine-Pro plugin spec. Adds structured, evolving
> knowledge that learns from every session. The plugin becomes a self-improving
> Django backend expert rather than a static collection of prose.

**Companion document**: This extends `django-engine-pro-plugin-spec.md`. Read
that first for the base plugin architecture (agents, refs, templates).

**Architecture choice**: Neuro-symbolic epistemic model over pure neural net.
See Part I for the reasoning.

---

## Part I: Why Epistemic, Not Neural

The learning layer for Django-Engine-Pro uses the epistemic model architecture
(typed knowledge primitives + Bayesian confidence + surgical neural components)
rather than an end-to-end neural network. This section explains why this is
the correct choice for this specific system.

### The Data Regime

Django-Engine-Pro will accumulate approximately 5-10 sessions per week across
three active Django projects (GCLBA portal, Index-API/Theseus, and any future
Django work). After six months, that yields 120-260 data points. After a year,
500-520.

| Approach | Minimum Data for Usefulness | Data After 6 Months | Verdict |
|---|---|---|---|
| Beta distribution (Bayesian) | 3-5 observations per claim | ~120-260 total, 2-10 per claim | Calibrated and useful from day 1 |
| MLP relevance scorer (62K params) | 50+ labeled examples | Reachable by month 2 | Useful after brief cold start |
| GNN over knowledge graph | 1,000+ labeled subgraph samples | Not reachable for years | Overkill, would overfit |
| Transformer-based claim selector | 10,000+ (context, claim, outcome) triples | Not reachable | Absurd for this domain |
| Contextual bandit (per-claim arm) | 20-30 observations per arm | Reachable for top claims only | Viable alternative to MLP, considered below |

The data scarcity alone eliminates pure neural approaches. But the decision
has deeper structural reasons.

### Five Properties the Learning System Needs

**1. Inspectability (non-negotiable)**

The "LLMs propose, humans review" invariant applies to the learning system
itself. When `/knowledge-review` surfaces a claim, you need to see:
- The claim text in plain English
- How many times it was accepted vs. rejected
- Which projects it appeared in
- Whether it contradicts anything else

A neural net's learned representations are opaque. A Claim with a Beta(14, 4)
distribution is transparent. You can look at it and say "yes, that's right"
or "no, that's overconfident given the GCLBA exception."

**2. Composability with Claude Code's context window**

Claude Code loads knowledge as structured text. The top 15-20 claims are
injected into the session as typed JSON objects. This is fundamentally a
text-in-context problem, not a latent-representation problem. Neural
approaches would require a separate inference step to convert latent vectors
back into text, adding complexity and latency for no gain.

**3. Graceful degradation**

The system has four fallback tiers:
1. MLP relevance scorer (best, requires 50+ training examples)
2. Cosine similarity over SBERT embeddings (good, requires only embeddings)
3. Tag matching (basic, requires only claim tags)
4. Full CLAUDE.md static prose (worst case, always available)

A neural net has one tier: trained or untrained. The epistemic model is
useful from the moment the first claim is seeded.

**4. Cold start from existing knowledge**

Django-Engine-Pro's seven agents contain dense knowledge: the inheritance
decision framework in model-architect, the anti-pattern checklist in
orm-specialist, the DRF vs. Ninja comparison table in api-architect, the
performance patterns in polymorphic-engineer. The seed_knowledge.py script
extracts these as typed Claims on day one. A neural net would ignore this
existing knowledge entirely and start from random weights.

**5. Temporal dynamics**

Claims about Django patterns age differently. "Use select_related for
ForeignKey traversals" is stable over years. "django-mcp-server's
MCPToolset requires async ORM in tool functions" might change with library
updates. Beta distributions with temporal decay handle this naturally:
stable claims accumulate evidence and resist decay; volatile claims
(few recent observations) drift toward uncertainty. A neural net would
need explicit temporal features and retraining to handle this.

### Where Neural Components Earn Their Place

The epistemic model uses neural components in exactly two spots:

**SBERT embeddings (pre-trained, zero training required)**
- Purpose: semantic similarity for cross-plugin linking, claim clustering,
  and embedding input to the relevance scorer
- Model: `all-MiniLM-L6-v2` (384 dimensions, CPU, <1ms per claim)
- Justification: cosine similarity over bag-of-words would miss semantic
  relationships ("use select_related" is related to "avoid N+1 queries"
  even though they share few words)

**MLP relevance scorer (tiny, trains in seconds)**
- Purpose: predict which claims are relevant to the current task context
- Architecture: 480 -> 128 -> 32 -> 1 (62K params)
- Training data: session logs (consulted + accepted = relevant)
- Justification: tag matching surfaces too many claims (15 claims tagged
  "orm" when only 3 matter for this specific migration task). The MLP
  learns project-specific and task-specific relevance.
- Activation threshold: 50+ labeled examples. Below that, fall back to
  cosine similarity.

### Alternative Considered: Contextual Bandit

A contextual bandit (one arm per claim, context = task features, reward =
accept/reject) was considered as an alternative to the MLP scorer. It has
theoretical appeal: it naturally balances exploration (surfacing uncertain
claims) with exploitation (surfacing high-confidence claims).

**Why the MLP was chosen instead:**
- The MLP takes claim embedding as input, so it generalizes across claims.
  A bandit treats each claim independently, meaning a new claim gets zero
  knowledge from similar existing claims.
- The MLP can be trained offline on session logs. A bandit requires online
  updates during sessions, which conflicts with the "in-session tracking
  only, no inference" principle.
- The exploration/exploitation tradeoff is less important here because
  `/knowledge-review` already provides explicit exploration of
  low-confidence claims. The scorer's job is pure relevance ranking.

**Where a bandit could supplement later:** If a future version wants to
optimize which claims to show during a session (rather than just ranking
them), a Thompson Sampling bandit over the Beta distributions could be
added as an optional layer on top of the MLP scorer. This is a Sprint 7+
consideration, not a v1 priority.

---

## Part II: Knowledge Primitives for Django-Engine-Pro

The five primitive types from the epistemic architecture, adapted for
Django backend knowledge.

### 2.1 Claim Types (Domain-Specific)

Django-Engine-Pro claims fall into seven categories:

| Type | Description | Example |
|---|---|---|
| `orm_pattern` | QuerySet optimization pattern | "Use Prefetch with a filtered queryset for M2M relations that need conditional loading" |
| `model_rule` | Model design rule | "Every JSONField gets a docstring describing expected schema structure" |
| `api_convention` | API design convention | "Separate read and write serializers when representation differs from input" |
| `polymorphic_pattern` | django-polymorphic specific | "Use non_polymorphic() when only base-class fields are needed in list views" |
| `mcp_safety` | MCP server safety rule | "Never expose a ModelQueryToolset without a scoped get_queryset()" |
| `bridge_pattern` | Scientific Python integration | "For tables over 100K rows, use pd.read_sql_query with chunksize instead of values_list()" |
| `migration_strategy` | Migration and schema evolution | "Data migrations that touch more than 10K rows should use batch processing with iterator()" |

Plus the inherited types from the base epistemic architecture:
`best_practice`, `architectural_rule`, `preference`, `empirical`,
`inherited`, `heuristic`.

### 2.2 Django-Engine-Pro Claim Schema

```json
{
  "id": "engine-claim-042",
  "text": "Use select_related for ForeignKey traversals in serializers, prefetch_related for reverse relations and M2M. trace the queryset back to its origin to verify.",
  "domain": "django-engine-pro",
  "agent_source": "orm-specialist",
  "type": "orm_pattern",
  "confidence": 0.92,
  "source": "orm-specialist anti-pattern checklist + 14 observed sessions",
  "embedding_idx": 41,
  "first_seen": "2026-03-21",
  "last_validated": null,
  "evidence": {
    "alpha": 2,
    "beta": 1
  },
  "projects_seen": [],
  "tags": ["orm", "performance", "queryset", "serializer", "n+1"],
  "related_claims": [],
  "agent_tags": ["orm-specialist", "api-architect"],
  "status": "active"
}
```

New fields beyond the base spec:
- `agent_tags`: which agents this claim is relevant to (for tag-matching
  fallback when the MLP scorer is not yet trained)
- `status`: `draft` (auto-generated, awaiting review), `active` (reviewed
  and approved), `deprecated` (superseded or disproven), `archived`
  (no longer relevant to current projects)

### 2.3 Tension Schema (Domain-Adapted)

```json
{
  "id": "engine-tension-003",
  "claim_a": "engine-claim-015",
  "claim_b": "engine-claim-031",
  "description": "Fat-models-thin-views rule says business logic belongs on the model, but complex cross-model workflows (e.g., GCLBA compliance state transitions touching 3 models + email service) resist single-model encapsulation",
  "domain": "django-engine-pro",
  "status": "context_dependent",
  "context_dependent": true,
  "context_note": "Single-model operations: fat model wins. Cross-model orchestration with side effects: service layer wins. The boundary is side effects.",
  "resolution_pattern": "If the operation touches only one model's state: model method. If it orchestrates multiple models or external services: service module function that the view calls.",
  "occurrences": 8,
  "first_seen": "2026-04-01",
  "resolution_attempts": []
}
```

New field: `resolution_pattern`. When a tension reaches `context_dependent`
status, the resolution pattern captures the decision heuristic so future
sessions can apply it directly instead of re-debating.

### 2.4 Method Schema (Domain-Adapted)

```json
{
  "id": "engine-method-007",
  "name": "Polymorphic API with type-dispatching serializer",
  "description": "PolymorphicModel base + child models, DRF serializer with to_representation dispatch by isinstance check, non_polymorphic() for list endpoints that only need base fields",
  "template_file": "templates/polymorphic-api/",
  "usage_count": 0,
  "last_used": null,
  "avg_satisfaction": null,
  "variants": [],
  "failure_modes": [
    "Forgetting to register child models in PolymorphicParentModelAdmin",
    "Missing polymorphic_ctype backfill in data migration when converting existing models",
    "select_related through polymorphic hierarchy requires explicit polymorphic_ctype inclusion"
  ],
  "tags": ["polymorphic", "api", "drf", "serializer"],
  "agent_tags": ["polymorphic-engineer", "api-architect"]
}
```

### 2.5 Django-Engine-Pro Specific Preferences

```json
{
  "id": "engine-pref-001",
  "text": "Cross-service references use slug strings, not ForeignKeys, when linking between separate Django services with their own databases",
  "domain": "django-engine-pro",
  "strength": 0.95,
  "distribution": {"alpha": 12, "beta": 0},
  "first_observed": "2026-03-21",
  "last_observed": "2026-03-21",
  "exceptions": [],
  "projects": {
    "apply.thelandbank.org": {"accepted": 5, "rejected": 0},
    "Index-API": {"accepted": 7, "rejected": 0}
  }
}
```

---

## Part III: Knowledge Seeds for Django-Engine-Pro

The seven agents produce an estimated 75-95 initial claims. Here is the
extraction plan for each agent.

### 3.1 model-architect (estimated: 18-22 claims)

**Sources for extraction:**
- Inheritance decision framework table (4 patterns, each becomes a claim)
- TimeStamped + SoftDeletable base pattern (1 claim)
- Slug-based cross-service reference pattern (1 claim)
- JSONField with schema discipline pattern (1 claim)
- ForeignKey on_delete rules (1 claim)
- db_index rules for filter/order fields (1 claim)
- CLAUDE.md Rules 1 and 6 (inheritance trade-offs, soft-delete)

**Sample seed claims:**
- "Abstract base classes for shared fields/methods when no cross-type queries are needed. Zero cost at query time."
- "Multi-table inheritance when you need to query the parent type directly AND each child adds columns. Cost: extra JOIN per inheritance level."
- "django-polymorphic when ALL four conditions are met: single queryset returning mixed types, each type has own fields, need actual subclass instances, type count is bounded."
- "Every ForeignKey gets an explicit on_delete argument with a comment explaining the rationale."
- "Every JSONField gets a docstring describing the expected schema per content type."

**High-value tensions to seed:**
- Abstract base vs. django-polymorphic when types share 80%+ fields
- JSONField flexibility vs. normalized relations for queryability
- GeneratedField (Django 5+) vs. annotation for computed columns

### 3.2 orm-specialist (estimated: 15-18 claims)

**Sources for extraction:**
- Anti-pattern detection list (6 anti-patterns, each becomes a claim)
- QuerySet performance checklist (7 checklist items)
- Source reference patterns (select_related, prefetch_related, Prefetch object)

**Sample seed claims:**
- "N+1 in templates: every `{{ item.related.field }}` without select_related on the queryset is a per-row query."
- "Use Prefetch objects (not bare string prefetch_related) when the related queryset needs filtering."
- "len(queryset) forces full evaluation. Use queryset.count() for SQL COUNT."
- "if queryset: evaluates the full queryset. Use queryset.exists() for SQL EXISTS."
- "For large querysets (10K+ rows), use .iterator() to avoid caching the full result in memory."

**Tensions to seed:**
- .only()/.defer() for column projection vs. risk of deferred field access triggering extra queries
- Raw SQL for complex analytics vs. ORM composability
- QuerySet caching (evaluate once with list()) vs. memory pressure on large results

### 3.3 api-architect (estimated: 12-15 claims)

**Sources for extraction:**
- DRF vs. Ninja decision framework table (8 dimensions, each a claim)
- Serializer design principles (4 principles)
- CLAUDE.md Rules 2 and 3 (view/serializer FK traversal, queryset scoping)

**Sample seed claims:**
- "DRF for complex nested writes with related objects. Ninja for type-safe, async, read-heavy APIs."
- "Separate read and write serializers when the API representation includes nested objects but the write input accepts IDs."
- "Never nest serializers deeper than two levels. Create a dedicated endpoint for the deeper resource."
- "SerializerMethodField runs per-instance and cannot be optimized by the ORM. Prefer queryset annotations."
- "Use HyperlinkedModelSerializer for public APIs (discoverability). PrimaryKeyRelatedField for internal APIs (consumers know the schema)."

**Tensions to seed:**
- DRF browsable API convenience vs. Ninja's type safety
- ViewSet CRUD grouping vs. individual view functions for fine-grained permissions
- drf-spectacular schema generation vs. Ninja's built-in OpenAPI

### 3.4 polymorphic-engineer (estimated: 8-12 claims)

**Sources for extraction:**
- When-to-use conditions (4 conditions, composite claim)
- Performance patterns (non_polymorphic, prefetching, ContentType join cost)
- DRF serialization dispatch pattern
- Admin integration pattern
- Migration patterns for polymorphic conversion

**Sample seed claims:**
- "non_polymorphic() skips the ContentType JOIN and child table JOINs. Use it for list views that only need base fields."
- "Polymorphic + DRF requires a dispatching serializer: to_representation checks isinstance and delegates to the correct child serializer."
- "When prefetching through a polymorphic ForeignKey, include polymorphic_ctype in select_related explicitly."
- "Converting an existing model to polymorphic requires a data migration that backfills polymorphic_ctype for all existing rows."

**Tensions to seed:**
- Polymorphic admin complexity vs. separate admin for each child type
- Automatic downcasting convenience vs. performance cost on large querysets
- django-polymorphic's ContentType approach vs. django-model-utils InheritanceManager

### 3.5 mcp-builder (estimated: 8-10 claims)

**Sources for extraction:**
- Safety rules (5 rules from the agent definition)
- Pattern examples (ModelQueryToolset, MCPToolset, DRF bridge)
- Auth configuration guidance

**Sample seed claims:**
- "Every ModelQueryToolset MUST override get_queryset() with appropriate filtering. Unscoped model exposure is a security and performance hazard."
- "Async MCP tool functions MUST use Django's async ORM (afilter, aget, acreate). Sync ORM in async functions causes thread-safety issues."
- "Tool docstrings become MCP tool descriptions. Write them for an AI agent audience, not a human developer audience."
- "Never return a lazy QuerySet from an MCP tool. Convert to list/dict first."
- "DRF-to-MCP bridge: drf_publish_list_mcp_tool disables pagination_class. Account for this in existing paginated views."

**Tensions to seed:**
- django-mcp-server's DRF bridge vs. custom MCPToolset for control
- Stateful sessions (Django session backend) vs. stateless for scalability
- OAuth2 (spec-compliant) vs. Token auth (simpler but non-standard for MCP)

### 3.6 data-bridge (estimated: 8-10 claims)

**Sources for extraction:**
- Memory rules (4 tiers by data volume)
- Conversion patterns (QuerySet-to-DataFrame, DataFrame-to-Django, pipeline)
- NaN/None boundary handling

**Sample seed claims:**
- "Under 10K rows: values() + DataFrame constructor. 10K-100K: values_list(named=True). 100K+: iterator() or pd.read_sql_query with chunksize."
- "DataFrame.where(pd.notna(df), None) before creating Django model instances. NaN is not None and Django fields do not accept NaN."
- "Always specify exact fields in values() or values_list() when extracting for pandas. Never SELECT * on a wide table."
- "Bulk operations (bulk_create, bulk_update) always specify batch_size. Default is unlimited, which can exhaust memory on large datasets."
- "For computation pipelines: extract minimal columns, compute in numpy/scipy, write results back with update_or_create or bulk_update."

**Tensions to seed:**
- django-pandas DataFrameManager convenience vs. explicit values_list() for control
- In-database computation (SQL aggregation) vs. Python-side computation (pandas) for complex statistics
- dj-notebook for exploration vs. management command for reproducible pipelines

### 3.7 pydantic-specialist (estimated: 6-8 claims)

**Sources for extraction:**
- Three-layer mapping diagram (Model/Serializer/Schema)
- PydanticAI agent construction pattern
- Boundary validation pattern
- from_attributes=True usage

**Sample seed claims:**
- "Pydantic schemas use from_attributes=True when validating Django model instances."
- "Pydantic validates structure and types at boundaries. DRF serializers handle persistence and nested writes. They serve different purposes; do not collapse them unless the use case demands a single layer."
- "PydanticAI agents with Django backends: define explicit output_type schemas. Never let the agent return unstructured text when structured data is expected."
- "Pydantic field_validators that reference numpy/scipy should catch inf and NaN explicitly. These are valid floats that will pass Pydantic's float validation but break downstream computation."

**Tensions to seed:**
- Manual Pydantic schema (explicit, maintained separately) vs. Django Ninja ModelSchema (auto-generated, may drift)
- Pydantic validation at API boundary vs. Django model clean() for database-level validation
- PydanticAI structured output vs. raw LLM text with post-processing

---

## Part IV: Extended Directory Structure

The base plugin directory gains a `knowledge/` directory and a `scripts/`
directory for the learning pipeline:

```
Django-Engine-Pro/
├── [everything from base spec]
│
├── knowledge/                             # Epistemic knowledge layer
│   ├── manifest.json                      # Schema version, stats, update log
│   ├── claims.jsonl                       # Typed propositions with confidence
│   ├── tensions.jsonl                     # Competing claims, unresolved conflicts
│   ├── methods.jsonl                      # Solution patterns with usage history
│   ├── questions.jsonl                    # Open unknowns
│   ├── preferences.jsonl                  # Travis-specific defaults
│   ├── embeddings.npz                     # SBERT embeddings (384-dim, numpy)
│   ├── scorer_weights.json                # MLP relevance scorer parameters
│   └── session_log/                       # Per-session tracking
│       └── *.jsonl
│
└── scripts/
    └── epistemic/
        ├── __init__.py
        ├── schema.py                      # Pydantic models for all primitives
        ├── seed_knowledge.py              # Extract claims from agents + CLAUDE.md
        ├── evidence_collector.py          # Session logs + git diffs -> evidence
        ├── confidence_updater.py          # Bayesian Beta distribution updates
        ├── pattern_extractor.py           # SBERT + HDBSCAN on code changes
        ├── tension_detector.py            # Contradiction and conflict finder
        ├── relevance_scorer.py            # MLP training and inference
        ├── embedding_manager.py           # SBERT embedding generation + storage
        ├── question_generator.py          # Flag low-confidence, propose questions
        ├── cross_linker.py                # Cross-plugin semantic neighbor search
        ├── run_pipeline.py                # Orchestrator: stages 1-8
        └── config.py                      # Paths, model names, hyperparameters
```

### Dependencies

```
# requirements-epistemic.txt (extends base plugin, which has no deps)
sentence-transformers>=2.2.0    # SBERT embeddings
torch>=2.0                       # MLP scorer + SBERT backend
hdbscan>=0.8.33                  # Pattern clustering
numpy>=1.24                      # Embedding storage and math
scikit-learn>=1.3                # TF-IDF for task embeddings, metrics
pydantic>=2.0                    # Schema validation
gitpython>=3.1                   # Git log and diff access
```

All CPU-only. No GPU required. Heaviest operation: SBERT embedding of
~95 claims takes <2 seconds on a modern laptop.

---

## Part V: CLAUDE.md Additions

Add this section to the Django-Engine-Pro CLAUDE.md, after the existing
rules and cross-references:

```markdown
## Epistemic Knowledge System

This plugin carries structured, evolving knowledge in `knowledge/`.

### Session Start Protocol

1. Read `knowledge/manifest.json` for current state.
2. Read `knowledge/scorer_weights.json` if it exists.
3. Based on the current project and open files, score all claims
   for relevance using the scorer. Fallback chain:
   a. MLP scorer (if scorer_weights.json exists and has 50+ training points)
   b. Cosine similarity: embed the task description with SBERT, compare
      against claims in embeddings.npz, rank by similarity
   c. Tag matching: match claim tags against agent_tags for the active agents
   d. Load all claims (last resort, only if knowledge/ has <20 claims)
4. Load the top 15-20 most relevant claims into active context.
5. Check `knowledge/tensions.jsonl` for unresolved tensions in the
   active domain. If the current task touches a tension, surface it
   to the user BEFORE making a decision.
6. Check `knowledge/preferences.jsonl` for defaults that override
   generic best practices.

### During Work

7. When your reasoning draws on a specific claim, note its ID
   in the session log.
8. When you make a suggestion, log which claims informed it.
9. When the user accepts, modifies, or rejects a suggestion,
   log the outcome.
10. When you encounter a situation where two claims give conflicting
    advice, log it as a HIGH-PRIORITY tension signal.

### Session End Protocol

11. Write the session log to `knowledge/session_log/{timestamp}.jsonl`.
12. If you discovered something that contradicts an existing claim,
    note it in the session log with event type `tension_signal`.
13. If you noticed a pattern the knowledge base doesn't cover,
    note it as event type `candidate_claim`.

### Knowledge Priority Rules

- When a claim conflicts with static prose in this CLAUDE.md:
  confidence > 0.8: claim wins.
  confidence < 0.5: prose wins.
  Between 0.5 and 0.8: surface the conflict to the user.
- Preferences defer to explicit user instructions in the current session.
- Tensions are information, not blockers. Surface them, let the user
  decide, log the decision.

### Commands

| Command | What It Does |
|---|---|
| `/knowledge-status` | Claim count, avg confidence, unresolved tensions, open questions, scorer accuracy, days since last update |
| `/knowledge-update` | Run the between-session learning pipeline (stages 1-8) |
| `/knowledge-review` | Surface the 5 lowest-confidence claims, 3 oldest unresolved tensions, and any draft candidate claims for human review |
| `/session-save` | Flush the current session log to disk (normally happens at session end automatically) |
```

### Agent Integration

Each of the seven agent files (model-architect, orm-specialist, api-architect,
polymorphic-engineer, mcp-builder, data-bridge, pydantic-specialist) gains
this block at the top:

```markdown
## Knowledge-Aware Operation

Before executing your checklist/workflow:
1. Check knowledge/claims.jsonl for claims tagged with your agent name
   in agent_tags.
2. If a claim contradicts your static instructions, and the claim's
   confidence > 0.8, follow the claim. It represents learned behavior.
3. If a method in knowledge/methods.jsonl matches the current task
   context (same project, similar file types), start from that method's
   variant rather than the generic template.
4. Log your work to the session log.
```

---

## Part VI: The Learning Pipeline (Detailed)

### Stage 1: Evidence Collector

Reads `knowledge/session_log/*.jsonl` for all unprocessed sessions.
Reads `git log --since=<last_update> --diff-filter=M` for the project repos.

Matches suggestions to commits by:
- File path overlap (suggestion was in views.py, commit touches views.py)
- Line range proximity (suggestion targeted lines 45-52, commit hunk covers 40-60)
- Temporal proximity (suggestion and commit within the same session window)

Classifies outcomes:
- `accepted`: suggestion content appears in the commit (fuzzy match via embedding similarity > 0.85)
- `modified`: partial match (similarity 0.5-0.85)
- `rejected`: suggestion not in commit, but file was committed (explicit rejection)
- `abandoned`: file mentioned in suggestion was not committed at all

### Stage 2: Confidence Updater (Bayesian)

Updates Beta distributions on each claim based on evidence:

```python
# Update rules
if outcome == "accepted":
    claim.evidence["alpha"] += 1.0
elif outcome == "modified":
    claim.evidence["alpha"] += 0.5
    claim.evidence["beta"] += 0.3
elif outcome == "rejected":
    claim.evidence["beta"] += 1.5  # rejections are stronger signal
elif outcome == "not_consulted_but_relevant":
    claim.evidence["beta"] += 0.1  # weak negative: wasn't useful enough to surface

# Temporal decay: every 30 days without validation
claim.evidence["alpha"] *= 0.95
claim.evidence["beta"] *= 0.95
# Floor: decay alone cannot push confidence below 0.3
# Only actual rejections can push below 0.3

# Confidence = posterior mean
claim.confidence = claim.evidence["alpha"] / (
    claim.evidence["alpha"] + claim.evidence["beta"]
)
```

### Stage 3: Pattern Extractor (SBERT + HDBSCAN)

Runs on git diffs accumulated over multiple sessions:

1. Extract code hunks from `git diff` for Django backend files
   (.py files in models/, views/, serializers/, urls/, admin/, managers/,
   querysets/, services/, mcp.py, schemas.py)
2. Embed each hunk with SBERT
3. Cluster with HDBSCAN (min_cluster_size=3, min_samples=2)
4. For each cluster with 3+ members: propose a new Claim
5. For each cluster that represents a recurring multi-step solution:
   propose a new Method
6. All proposals start at status="draft"

Django-Engine-Pro specific cluster targets:
- Model field patterns (repeated use of specific field configurations)
- QuerySet optimization patterns (repeated prefetch/select_related chains)
- Serializer structures (repeated read/write separation patterns)
- MCP tool scoping patterns (repeated get_queryset filters)

### Stage 4: Tension Detector

Two detection modes:

**Outcome contradictions:**
Same claim accepted in one project, rejected in another. Example:
- engine-claim-015 ("fat models for business logic") accepted 8x in
  Index-API, rejected 3x in GCLBA portal
- Proposes a tension with context analysis

**Semantic contradictions:**
Claims with high embedding similarity but opposite advice. Example:
- "Always use DRF ViewSets for CRUD endpoints" (0.75 confidence)
- "Prefer function-based views for standard CRUD" (0.78 confidence, preference)
- Embedding similarity: 0.82 (same topic, different advice)
- Proposes a tension for human review

### Stage 5: Relevance Scorer Training

Architecture:
```
Input: concat(
    claim_embedding[384],      # SBERT embedding of claim text
    project_embedding[32],     # learned per-project embedding
    task_embedding[64],        # TF-IDF of open files + agent types, projected
    agent_one_hot[7]           # which agent is active (7 agents)
) = 487 dims

Linear(487, 128) -> ReLU -> Dropout(0.3)
Linear(128, 32) -> ReLU -> Dropout(0.2)
Linear(32, 1) -> Sigmoid

Output: relevance probability [0, 1]
```

~63K parameters. Trains in <10 seconds on CPU.

Training data from session logs:
- Positive: claim was consulted AND suggestion was accepted
- Negative: claim is tagged for this domain but was not consulted
  (or was consulted and rejected)

Project embeddings: learned 32-dim embedding per project. Initialized
randomly, updated during scorer training. Projects: apply.thelandbank.org,
Index-API, travisgilbert.me, plus a catch-all "other" embedding.

Task embedding: TF-IDF of the file names and agent types involved in
the session, projected to 64 dims via SVD.

Activation threshold: 50+ labeled examples. Below that, the scorer is
not trained and the system falls back to cosine similarity.

Weights saved to `scorer_weights.json` (serialized as JSON for
portability and inspectability).

### Stage 6: Embedding Update

Re-embeds any new or modified claims using all-MiniLM-L6-v2.
Saves all embeddings to `embeddings.npz` (numpy compressed sparse row).

### Stage 7: Question Generator

Flags:
- Claims with confidence < 0.5 and 5+ observations (uncertain despite evidence)
- Methods with avg_satisfaction < 0.6 (solutions that aren't working well)
- Tensions unresolved for >30 days with 5+ occurrences
- Claims not consulted in the last 60 days (potentially stale or irrelevant)

Each flag becomes a Question with status="open" for `/knowledge-review`.

### Stage 8: Cross-Plugin Linker

Loads embeddings.npz from Django-Engine-Pro and all other epistemic-enabled
plugins. For each claim, finds top-3 nearest neighbors in OTHER plugins.
Threshold: cosine similarity > 0.75.

Expected cross-plugin links for Django-Engine-Pro:
- ORM claims link to django-design's template rendering claims
  ("prefetch_related in serializers" relates to "prefetch_related in templates")
- Polymorphic claims link to ui-design-pro's polymorphic rendering claims
  (backend type preservation enables frontend type branching)
- API claims link to ux-pro's error message claims
  ("consistent error response format" relates to "error pattern: what + why + fix")
- MCP claims link to any future MCP-related claims in other plugins
- Data bridge claims link to ml-pro's data pipeline claims
  ("QuerySet to DataFrame" relates to "feature engineering from database")

---

## Part VII: Implementation Order

### Sprint 1: Schema + Seeding (1 week)

1. `scripts/epistemic/schema.py` with Pydantic models for all primitives
2. `scripts/epistemic/seed_knowledge.py` adapted for Django-Engine-Pro's
   seven agents (the extraction patterns differ from django-design because
   the knowledge is in decision tables and anti-pattern lists rather than
   numbered checklists)
3. `scripts/epistemic/config.py` with paths and hyperparameters
4. Run seeder on all seven agents, producing ~75-95 draft claims
5. Human review: promote good claims to active, reject weak ones, refine text
6. Add the Epistemic Knowledge System section to CLAUDE.md
7. Add Knowledge-Aware Operation block to each agent
8. Test: run a real Django backend task with knowledge layer active

### Sprint 2: Session Logger (1 week)

1. Session log format and writer (pure file I/O)
2. `/session-save` command
3. Run 5-8 real sessions, accumulate session logs
4. Verify logs capture the right granularity (not too verbose, not too sparse)

### Sprint 3: Evidence + Bayesian Updates (1 week)

1. `evidence_collector.py`
2. `confidence_updater.py`
3. `run_pipeline.py` stages 1-2
4. Run pipeline on accumulated session logs
5. Verify: do confidence updates make sense? Do rejected suggestions
   actually lower the relevant claim's confidence?

### Sprint 4: Embeddings + Pattern Discovery (1 week)

1. `embedding_manager.py` (SBERT encoding, .npz storage)
2. `pattern_extractor.py` (HDBSCAN clustering of code changes)
3. `tension_detector.py` (outcome + semantic contradiction detection)
4. `question_generator.py`
5. Run pipeline stages 1-7
6. Review auto-generated tensions and questions for quality

### Sprint 5: Relevance Scorer + Cross-Plugin (1 week)

1. `relevance_scorer.py` (MLP training and inference)
2. `cross_linker.py` (semantic neighbor search)
3. Full pipeline stages 1-8
4. `/knowledge-status`, `/knowledge-update`, `/knowledge-review` commands
5. Cross-plugin report: which plugins have inter-connections with
   Django-Engine-Pro

### Sprint 6: Evaluation (1 week)

1. Measure: does the scorer surface better claims than tag matching?
   (A/B test over 10 sessions: scorer vs. tag matching, measure
   suggestion acceptance rate)
2. Measure: are auto-generated tensions actionable?
3. Measure: do sessions with the knowledge layer active produce fewer
   N+1 queries, better inheritance decisions, more appropriate API
   framework choices? (qualitative review of 5 sessions)
4. Tune: adjust confidence update rates, decay rates, scorer hyperparameters
5. Document: what works, what needs iteration

---

## Part VIII: What This Enables

### After Sprint 1

- Django-Engine-Pro reads typed claims alongside static prose
- Claims carry confidence scores; uncertain advice is flagged
- The plugin knows its own knowledge gaps (e.g., "mcp-builder has only
  4 claims, all at prior confidence, because no MCP sessions have run yet")

### After Sprint 3

- Claims strengthen when accepted, weaken when rejected
- Stale knowledge decays: if "use DRF for all APIs" hasn't been validated
  in 3 months and Ninja has been chosen 4 times, the claim's confidence
  reflects that shift
- Each Django backend session makes the next one marginally smarter

### After Sprint 5

- Neural scorer selects the most relevant 10-15 claims per task
  (from 75-95 total) based on project, file types, and active agent
- Cross-plugin insight: "your polymorphic model design should align with
  ui-design-pro's polymorphic rendering philosophy" (surfaced as a
  related_claims link, not as a runtime query)
- New patterns discovered from git history: "Travis consistently adds
  batch_size=1000 to bulk_create in data-bridge tasks" becomes a claim
  without anyone manually encoding it

### After Sprint 6

- Measurable improvement in suggestion acceptance rates
- Django-Engine-Pro honestly reports when it lacks experience with a
  pattern (low-confidence claims flagged, questions auto-generated)
- The tension between fat-models and service-layer has a resolution
  pattern with project-specific context, not a one-size-fits-all rule
- Each agent is a small, focused expert that gets better at the specific
  Django backend problems you actually encounter

---

## Part IX: Risk Assessment

| Risk | Signal | Mitigation |
|---|---|---|
| Knowledge bloat exceeds context budget | Top-20 claims > 3K tokens | Enforce max 20 claims per session; summarize claim text to <50 words each |
| Scorer overfits to Index-API patterns | Accuracy drops on GCLBA portal tasks | Include project_embedding as feature; require 5+ sessions per project before project-specific scoring |
| MCP claims stale quickly as library evolves | Claims about django-mcp-server API become wrong | Tag MCP claims with library version; flag for re-validation when refs/ are updated |
| Polymorphic claims over-generalize | Not all polymorphic patterns apply to all hierarchies | Include "hierarchy depth" and "child count" as context features in tension detection |
| Data bridge claims assume PostgreSQL | Patterns that depend on PostgreSQL features fail on SQLite in tests | Tag claims with database backend applicability; flag when running against non-PostgreSQL |
| Cross-plugin links between engine and design create circular advice | Design plugin says "API should support X," engine plugin says "design should accommodate Y" | Cross-plugin links are read-only references, not directives. Surface for human judgment, never auto-apply. |
| Session logging makes Claude Code verbose | User perceives slowdown or extra output | Keep logging invisible (no user-facing output from log writes); flush at session end, not per-event |

---

## Part X: What NOT to Build (Django-Engine-Pro Specific)

1. **No auto-migration generation.** The learning system discovers model
   patterns and proposes claims about migration strategy. It does NOT
   generate Django migrations. That remains Claude Code's job, guided by
   claims.

2. **No live query analysis.** The learning system does NOT connect to a
   running database to analyze query plans. It learns from session logs
   and git diffs. EXPLAIN ANALYZE is a tool the orm-specialist agent
   recommends; the learning system tracks whether that recommendation was
   followed.

3. **No automatic claim promotion.** All auto-generated claims (from
   pattern extraction, tension detection) start at status="draft".
   Human review via `/knowledge-review` is required before they affect
   behavior. LLMs propose, humans review. Always.

4. **No cross-plugin claim modification.** Django-Engine-Pro's cross-linker
   can discover that an ORM claim is related to a django-design template
   claim. It writes a related_claims reference. It does NOT modify the
   other plugin's claim. Each plugin owns its own knowledge.

5. **No in-session model inference.** SBERT and the MLP scorer run between
   sessions. During sessions, Claude Code reads pre-computed embeddings and
   scorer weights. No PyTorch imports during active work.
