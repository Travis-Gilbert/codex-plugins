# API Framework Decision: DRF vs Django Ninja

## Structured Comparison

| Dimension | DRF | Django Ninja |
|-----------|-----|-------------|
| Type safety | Runtime (serializer validation) | Build-time (Pydantic + type hints) |
| Boilerplate | Higher (serializer + viewset + router) | Lower (function + decorator + schema) |
| Nested writes | Built-in (WritableNestedSerializer) | Manual (you handle the transaction) |
| OpenAPI | Via drf-spectacular (add-on) | Built-in, auto-generated |
| Async support | Partial (views only, serializers sync) | Full (async views, async ORM) |
| Ecosystem | Massive (filters, auth, pagination) | Smaller but growing |
| Browsable API | Yes | No (Swagger UI instead) |
| Learning curve | Steeper (many abstractions) | Flatter (function-based) |
| Maturity | 10+ years, battle-tested | Newer, rapidly evolving |

## Decision Matrix

### Choose DRF when:
- API serves complex nested resources with write operations
- Existing DRF codebase (don't mix frameworks)
- Need browsable API for developer exploration
- Complex permission model (object-level permissions)
- Heavy use of third-party DRF packages (django-filter, drf-spectacular, etc.)

### Choose Ninja when:
- Greenfield project with no DRF dependencies
- Read-heavy API (Ninja's function-based views are lighter)
- Need full async support (async views + async ORM)
- Pydantic schemas already in use (e.g., PydanticAI, data pipelines)
- Type safety is a priority (Pydantic validation at build time)
- Want auto-generated OpenAPI without extra packages

### Don't mix unless:
- Migrating incrementally from DRF to Ninja
- Different API versions use different frameworks
- Internal API (Ninja) vs. public API (DRF) split

## Serializer/Schema Design Principles

### DRF Serializers
1. Separate read and write serializers when representation differs from input
2. Never nest deeper than two levels in a single serializer
3. Use SerializerMethodField sparingly (per-instance, not ORM-optimizable)
4. HyperlinkedModelSerializer for public APIs, PrimaryKeyRelatedField for internal

### Ninja Schemas
1. Use ModelSchema for simple CRUD, manual Schema for complex validation
2. Pydantic validators replace DRF's validate_<field> pattern
3. from_attributes=True for Django model conversion
4. FilterSchema for query parameter validation

## Pagination Strategy

| Strategy | Use When | Trade-off |
|----------|----------|-----------|
| Offset/limit | Simple APIs, small datasets | Inconsistent on inserts/deletes |
| Cursor | Large datasets, real-time feeds | No random page access |
| Keyset | High-performance, ordered data | Requires unique sort key |

## Error Response Format

Standardize across the API (regardless of framework):

```json
{
  "error": {
    "code": "validation_error",
    "message": "Human-readable description",
    "details": [
      {"field": "email", "message": "Already in use"}
    ]
  }
}
```
