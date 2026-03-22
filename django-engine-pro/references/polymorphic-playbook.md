# django-polymorphic Playbook

## Setup Pattern

```python
from polymorphic.models import PolymorphicModel
from django.db import models

class ContentItem(PolymorphicModel):
    """Base for all content types. Queries return correctly-typed children."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-created_at"]

class Essay(ContentItem):
    body = models.TextField()
    word_count = models.IntegerField(default=0)

class FieldNote(ContentItem):
    location = models.CharField(max_length=200)
    observation = models.TextField()

class Project(ContentItem):
    description = models.TextField()
    status = models.CharField(max_length=20, default="active")
```

## Performance Controls

### non_polymorphic()
Skip the ContentType join when you only need base fields:
```python
# List view: only needs title and date
items = ContentItem.objects.non_polymorphic().only(
    "title", "slug", "created_at"
)
```

### instance_of()
Filter to specific child types efficiently:
```python
essays = ContentItem.objects.instance_of(Essay)
non_projects = ContentItem.objects.not_instance_of(Project)
```

### Combining with select_related/prefetch_related
```python
# The polymorphic_ctype field is a ForeignKey to ContentType
items = ContentItem.objects.select_related("polymorphic_ctype")

# Prefetch through polymorphic relations
collections = Collection.objects.prefetch_related(
    Prefetch(
        "items",
        queryset=ContentItem.objects.select_related("polymorphic_ctype")
    )
)
```

## Admin Integration

```python
from polymorphic.admin import (
    PolymorphicParentModelAdmin,
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
)

class EssayAdmin(PolymorphicChildModelAdmin):
    base_model = ContentItem

class FieldNoteAdmin(PolymorphicChildModelAdmin):
    base_model = ContentItem

class ContentItemAdmin(PolymorphicParentModelAdmin):
    base_model = ContentItem
    child_models = (Essay, FieldNote, Project)
    list_filter = (PolymorphicChildModelFilter,)
```

## DRF Serialization

### Type-Dispatching Serializer
```python
class ContentItemSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        if isinstance(instance, Essay):
            return EssaySerializer(instance, context=self.context).data
        elif isinstance(instance, FieldNote):
            return FieldNoteSerializer(instance, context=self.context).data
        elif isinstance(instance, Project):
            return ProjectSerializer(instance, context=self.context).data
        return super().to_representation(instance)

    class Meta:
        model = ContentItem
        fields = ["id", "title", "slug", "created_at", "polymorphic_ctype"]
```

## Migration Patterns

### Adding a New Child Type
1. Create the model class
2. `makemigrations` generates the child table + implicit OneToOneField
3. No data migration needed (new table is empty)

### Converting Existing Model to Polymorphic
1. Make the base class inherit from PolymorphicModel
2. `makemigrations` adds `polymorphic_ctype` field
3. Data migration to backfill polymorphic_ctype for existing rows:

```python
def backfill_ctype(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    ContentItem = apps.get_model("myapp", "ContentItem")
    ct = ContentType.objects.get_for_model(ContentItem)
    ContentItem.objects.filter(polymorphic_ctype__isnull=True).update(
        polymorphic_ctype=ct
    )
```

## Common Pitfalls

1. **Forgetting non_polymorphic()**: Every `.all()` pays the JOIN cost
2. **Deep hierarchies**: More than 2 levels creates excessive JOINs
3. **Missing polymorphic_ctype backfill**: Existing rows need the ContentType set
4. **Bulk operations**: `bulk_create()` skips polymorphic signals; set polymorphic_ctype manually
