# Django Migration Strategy

## Core Principles

1. **Every migration must be reversible** unless explicitly documented as irreversible
2. **Data migrations are separate from schema migrations**
3. **Zero-downtime patterns** for production deployments
4. **Test migrations against a copy of production data** before deploying

## Zero-Downtime Patterns

### Adding a Column
1. Add column as nullable with default: `models.CharField(null=True, default=None)`
2. Deploy code that writes to the new column
3. Backfill existing rows (data migration)
4. Change column to non-nullable (if needed) in a separate migration

### Removing a Column
1. Stop reading the column in code
2. Deploy
3. Remove the column in a migration

### Renaming a Column
1. Add new column
2. Copy data (data migration)
3. Update code to use new column
4. Remove old column

### Renaming a Table (Model)
Use `db_table` in Meta to avoid actual rename:
```python
class NewName(models.Model):
    class Meta:
        db_table = "old_app_oldname"
```

## Data Migrations

```python
from django.db import migrations

def forward(apps, schema_editor):
    ContentItem = apps.get_model("myapp", "ContentItem")
    for item in ContentItem.objects.all().iterator():
        item.slug = slugify(item.title)
        item.save(update_fields=["slug"])

def reverse(apps, schema_editor):
    pass  # Or implement reverse

class Migration(migrations.Migration):
    dependencies = [("myapp", "0005_add_slug")]
    operations = [
        migrations.RunPython(forward, reverse),
    ]
```

### Batch Data Migrations (Large Tables)

```python
def forward(apps, schema_editor):
    ContentItem = apps.get_model("myapp", "ContentItem")
    batch_size = 1000
    qs = ContentItem.objects.filter(slug="")
    while True:
        batch = list(qs[:batch_size])
        if not batch:
            break
        for item in batch:
            item.slug = slugify(item.title)
        ContentItem.objects.bulk_update(batch, ["slug"], batch_size=batch_size)
```

## Squashing

When migration count grows large (50+), squash to reduce startup time:
```bash
python manage.py squashmigrations myapp 0001 0050
```

**Rules**:
- Never squash across data migrations with RunPython
- Test the squashed migration on a fresh database
- Keep the originals until all environments run the squashed version

## Polymorphic Migration: Adding polymorphic_ctype

```python
def backfill_ctype(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    ContentItem = apps.get_model("myapp", "ContentItem")
    ct = ContentType.objects.get_for_model(ContentItem)
    ContentItem.objects.filter(polymorphic_ctype__isnull=True).update(
        polymorphic_ctype=ct
    )
```

## Common Mistakes

1. **Running data migrations in the same migration as schema changes**: Split them
2. **Not testing reverse migrations**: Always implement and test `reverse`
3. **Using model methods in data migrations**: Use `apps.get_model()` — the migration
   sees the model as it was at that point, not the current code
4. **Forgetting `update_fields` in save()**: Without it, save() writes all columns
