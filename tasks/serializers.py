"""
Serializers for the tasks app.
Converts Task model instances to/from JSON for API responses.
"""
from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    """Full serializer for Task model."""
    tags_list = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'due_date', 'tags', 'tags_list', 'order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'tags_list']

    def get_tags_list(self, obj):
        """Return tags as a list instead of comma-separated string."""
        if not obj.tags:
            return []
        return [tag.strip() for tag in obj.tags.split(',') if tag.strip()]

    def validate_title(self, value):
        """Ensure title is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError('Title cannot be empty.')
        return value.strip()

    def validate_status(self, value):
        """Ensure status is valid."""
        valid_statuses = ['todo', 'in_progress', 'done']
        if value not in valid_statuses:
            raise serializers.ValidationError(f'Status must be one of: {", ".join(valid_statuses)}')
        return value

    def validate_priority(self, value):
        """Ensure priority is valid."""
        valid_priorities = ['low', 'medium', 'high']
        if value not in valid_priorities:
            raise serializers.ValidationError(f'Priority must be one of: {", ".join(valid_priorities)}')
        return value


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating tasks."""

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'due_date', 'tags', 'order'
        ]
        read_only_fields = ['id']

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Title cannot be empty.')
        return value.strip()


class TaskStatusUpdateSerializer(serializers.Serializer):
    """Serializer for drag-and-drop status update."""
    status = serializers.ChoiceField(choices=['todo', 'in_progress', 'done'])
    order = serializers.IntegerField(min_value=0, required=False, default=0)
