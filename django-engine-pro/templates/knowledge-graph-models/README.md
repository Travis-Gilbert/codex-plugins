# Knowledge Graph Models Template

Typed node/edge models using django-polymorphic as the base, with a
PolymorphicModel hierarchy for different node types and typed edges
with reason fields.

## Domain: Content Publishing (neutral example)

- **KnowledgeObject** (PolymorphicModel base): title, slug, body
- **Concept** (child): definition, domain
- **Claim** (child): statement, confidence, evidence_count
- **Tension** (child): description, resolution_status
- **Edge**: from_object, to_object, edge_type, reason, strength

## Patterns Demonstrated

- Polymorphic node hierarchy with typed children
- Edge model with reason and strength fields
- Custom managers for graph traversal queries
- non_polymorphic() for performance in graph algorithms
- Pydantic schemas for edge validation
