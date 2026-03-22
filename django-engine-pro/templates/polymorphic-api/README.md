# Polymorphic API Template

Complete example of PolymorphicModel + DRF with type-dispatching serialization.

## Domain: Content Publishing

- **ContentItem** (PolymorphicModel base): title, slug, created_at
- **Essay** (child): body, word_count
- **FieldNote** (child): location, observation
- **Project** (child): description, status

## Files

- `models.py` — PolymorphicModel hierarchy with TimeStamped base
- `serializers.py` — Type-dispatching serializer with read/write split
- `views.py` — ViewSet with polymorphic queryset optimization
- `admin.py` — PolymorphicParentModelAdmin + PolymorphicChildModelAdmin
- `urls.py` — DRF router configuration
- `tests.py` — Tests for polymorphic CRUD and serialization

## Usage

Copy this template into your Django app and customize the model fields.
The serialization dispatch pattern works with any PolymorphicModel hierarchy.
