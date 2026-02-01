"""
Serializers for habits app.
Week 2: Habit and HabitLog serializers with streak calculations.
"""

from rest_framework import serializers

from habits.models import Habit, HabitLog


class HabitLogSerializer(serializers.ModelSerializer):
    """Serializer for HabitLog model."""

    class Meta:
        model = HabitLog
        fields = ["id", "date", "completed", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]


class HabitListSerializer(serializers.ModelSerializer):
    """Serializer for Habit list view (minimal info)."""

    current_streak = serializers.SerializerMethodField()

    class Meta:
        model = Habit
        fields = [
            "id",
            "name",
            "category",
            "frequency",
            "is_active",
            "current_streak",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_current_streak(self, obj):
        """Get current streak for the habit."""
        return obj.calculate_current_streak()


class HabitSerializer(serializers.ModelSerializer):
    """Serializer for Habit model with full details."""

    current_streak = serializers.SerializerMethodField()
    longest_streak = serializers.SerializerMethodField()
    completion_rate = serializers.SerializerMethodField()
    logs = HabitLogSerializer(many=True, read_only=True)

    class Meta:
        model = Habit
        fields = [
            "id",
            "name",
            "description",
            "category",
            "frequency",
            "goal_count",
            "start_date",
            "is_active",
            "current_streak",
            "longest_streak",
            "completion_rate",
            "logs",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        """Create habit with authenticated user."""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def get_current_streak(self, obj):
        """Get current streak for the habit."""
        return obj.calculate_current_streak()

    def get_longest_streak(self, obj):
        """Get longest streak achieved."""
        return obj.get_longest_streak()

    def get_completion_rate(self, obj):
        """Get completion rate percentage."""
        rate = obj.get_completion_rate()
        return round(rate, 2)
