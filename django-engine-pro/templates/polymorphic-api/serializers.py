"""
Type-dispatching serializers for the polymorphic content hierarchy.

Pattern: Base serializer's to_representation dispatches to the correct
child serializer based on instance type. This preserves type information
through the API layer.
"""
from rest_framework import serializers
from .models import ContentItem, Essay, FieldNote, Project


class EssaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Essay
        fields = [
            "id", "title", "slug", "body", "word_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class FieldNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldNote
        fields = [
            "id", "title", "slug", "location", "observation",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id", "title", "slug", "description", "status",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ContentItemSerializer(serializers.ModelSerializer):
    """Base serializer with type-dispatching to_representation."""
    resource_type = serializers.SerializerMethodField()

    def get_resource_type(self, instance):
        return instance.__class__.__name__.lower()

    def to_representation(self, instance):
        if isinstance(instance, Essay):
            data = EssaySerializer(instance, context=self.context).data
        elif isinstance(instance, FieldNote):
            data = FieldNoteSerializer(instance, context=self.context).data
        elif isinstance(instance, Project):
            data = ProjectSerializer(instance, context=self.context).data
        else:
            data = super().to_representation(instance)
        data["resource_type"] = instance.__class__.__name__.lower()
        return data

    class Meta:
        model = ContentItem
        fields = ["id", "title", "slug", "created_at", "resource_type"]
