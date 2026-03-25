# Django-Engine-Pro Plugin

You have access to Django ORM source code, API framework source (DRF + Ninja),
django-polymorphic internals, MCP server construction patterns, scientific Python
integration references, and Pydantic v2 source. Use them.

## When You Start a Django Backend Task

1. Determine the task category. Read the relevant agent in agents/.
2. Check refs/ for the libraries you will use. Grep the source to verify
   API signatures and internal behavior rather than relying on memory.
3. If the task involves model design, read references/inheritance-strategies.md
   to choose the right inheritance pattern before writing any model code.
4. If the task involves API design, read references/api-decision-framework.md
   to confirm the framework choice fits the project's constraints.
5. If the task involves data flowing between Django and pandas/numpy/scipy,
   read references/scientific-bridge.md before writing the bridge code.

## Source References

Library source is in refs/. Use it to verify API details:
- Django ORM internals: refs/django-db/models/
- DRF serializers, viewsets, routers: refs/django-rest-framework/
- Django Ninja operations, schemas, ORM integration: refs/django-ninja/ninja/
- Polymorphic models, querysets, managers: refs/django-polymorphic/src/polymorphic/
- MCP server toolsets, query tools: refs/django-mcp-server/mcp_server/
- Pydantic v2 core: refs/pydantic/pydantic/
- PydanticAI agent graph, MCP integration: refs/pydantic-ai/

## Reference Library

Curated knowledge docs in references/. Read the relevant one before starting work:
- inheritance-strategies.md: Abstract vs. multi-table vs. proxy vs. polymorphic
- orm-performance.md: N+1, prefetch, select_related, window functions, explain
- api-decision-framework.md: DRF vs. Ninja structured comparison
- polymorphic-playbook.md: django-polymorphic patterns and performance tuning
- mcp-patterns.md: Building MCP servers from Django apps
- scientific-bridge.md: QuerySet-to-DataFrame, bulk ingest, computation pipelines
- pydantic-django-mapping.md: Three-way mapping (Model, Serializer, Schema)
- migration-strategy.md: Data migrations, zero-downtime, squashing
- manager-queryset-patterns.md: Custom managers, chainable QuerySets

## Agent Loading

Agents are composable. A single task may load multiple agents. Read the
relevant agent .md file(s) before starting work. See AGENTS.md for routing.

## Rules

1. NEVER pick an inheritance strategy without stating the trade-offs out loud.
   Name what you gain and what you lose. If the user hasn't chosen, present
   the options with concrete consequences before writing model code.

2. NEVER write a view or serializer that traverses a ForeignKey without
   confirming select_related or prefetch_related is in place. If the queryset
   originates elsewhere (e.g., a generic view's get_queryset), trace it back
   and verify.

3. NEVER expose a Django model as an MCP tool without confirming the queryset
   is scoped. Unscoped model exposure is a security and performance hazard.
   Always implement get_queryset() with appropriate filtering.

4. When working with django-polymorphic, always consider whether the query
   needs the polymorphic cast. If you only need base-class fields, use
   .non_polymorphic() to avoid the ContentType join.

5. When bridging to pandas, always specify the exact fields in values() or
   values_list(). Never pass an unfiltered queryset to DataFrame.from_records()
   on a table with more than a few thousand rows without pagination or
   iterator() chunking.

6. Pydantic schemas and DRF serializers serve different purposes. Pydantic
   validates structure and types at boundaries. DRF serializers handle
   database persistence, nested writes, and representation. Do not collapse
   them into one unless the use case genuinely calls for a single layer.

7. For MCP tool functions that touch the ORM, always use Django's async ORM
   API (afilter, aget, acreate, etc.) when the tool is defined as async.
   Mixing sync ORM calls inside async functions causes thread-safety issues.

## Knowledge Layer

This plugin has a self-improving knowledge layer in `knowledge/`.

### At Session Start
1. Read `knowledge/manifest.json` for stats and last update time
2. Read `knowledge/claims.jsonl` for active claims relevant to this task
   (filter by tags matching the agents you are loading)
3. When a claim's confidence > 0.8 and it conflicts with static
   instructions, follow the claim. It represents learned behavior.
4. When a claim's confidence < 0.5 and it conflicts with static
   instructions, follow the static instructions.

### During the Session
- When you consult a claim, note which claim and why
- When you make a suggestion based on a claim, note the link
- When the user corrects you, note what they said and which claim
  was involved (this is a tension signal)
- When you notice a pattern not in the knowledge base, note it
  as a candidate claim

### At Session End
Run `/learn` to save and update knowledge. This is the ONLY
knowledge command you need.

## Cross-Reference with Other Plugins

If the project also uses Django-Pro or other plugins:

- For frontend concerns (HTMX, Alpine.js, Tailwind, templates, Cotton
  components): defer to Django-Pro / django-design.
- For D3 visualization embedded in Django templates: defer to D3-Pro.
- For React/Next.js frontends consuming Django APIs: defer to JS-Pro.
- For ML model training and inference pipelines: defer to ML-Pro or
  SciPy-Pro (Theseus-Pro).
- For UX research, information architecture, and accessibility: defer to
  ux-pro.
- This plugin owns: model architecture, ORM optimization, API framework
  selection and implementation, polymorphic model patterns, MCP server
  construction, scientific Python bridging, Pydantic integration, migration
  strategy, and custom manager/queryset design.

## Architectural Invariants

These rules apply across all projects unless explicitly overridden:

- Fat models, thin views. Business logic belongs on the model or in a
  service module, not in the view or serializer.
- Explicit is better than implicit. If a queryset annotation or prefetch
  matters for correctness, document it in a comment or docstring.
- Cross-service references use slug strings, not ForeignKeys, when linking
  between separate Django services with their own databases.
- Soft-delete over hard-delete. Use is_deleted=True unless the domain
  demands actual removal.
- LLMs propose, humans review. Any automated data transformation or
  knowledge extraction must surface results for human confirmation before
  committing to canonical status.
