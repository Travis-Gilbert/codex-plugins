# Pydantic-Validated API Template

Django Ninja API using Pydantic schemas for request/response validation,
with from_attributes=True for Django model conversion and a PydanticAI
agent endpoint with structured output.

## Files

- `schemas.py` — Pydantic schemas with from_attributes and validators
- `api.py` — Django Ninja router with typed endpoints
- `agent.py` — PydanticAI agent with structured output type

## Patterns Demonstrated

- Manual Pydantic schema (preferred over auto-generated)
- from_attributes=True for Django model instances
- Pydantic field_validator for domain rules
- PydanticAI agent with output_type
- Async ORM in Ninja views
