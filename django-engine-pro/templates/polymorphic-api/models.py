"""
Polymorphic content model hierarchy.

Inheritance strategy: django-polymorphic (PolymorphicModel)
Rationale: Need single queryset returning mixed types with automatic downcasting.
Trade-off: ContentType JOIN + child table JOINs per query. Use .non_polymorphic()
           when only base fields are needed.
"""
from django.db import models
from polymorphic.models import PolymorphicModel


class ContentItem(PolymorphicModel):
    """Base for all content types. Queries return correctly-typed children."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Essay(ContentItem):
    """Long-form written content."""
    body = models.TextField()
    word_count = models.IntegerField(default=0)


class FieldNote(ContentItem):
    """Observation recorded at a specific location."""
    location = models.CharField(max_length=200)
    observation = models.TextField()


class Project(ContentItem):
    """Ongoing project with status tracking."""
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[
            ("active", "Active"),
            ("paused", "Paused"),
            ("complete", "Complete"),
            ("archived", "Archived"),
        ],
        default="active",
        db_index=True,
    )
