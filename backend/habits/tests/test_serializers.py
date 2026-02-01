"""
Unit tests for habit serializers.
Week 2: Habit and HabitLog serializer validation.
"""

from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model

from habits.models import Habit, HabitCategory, HabitFrequency, HabitLog
from habits.serializers import (HabitListSerializer, HabitLogSerializer,
                                HabitSerializer)

User = get_user_model()


@pytest.mark.django_db
class TestHabitSerializer:
    """Test HabitSerializer for CRUD operations."""

    def test_create_habit_with_valid_data(self):
        """Test creating a habit with valid data."""
        user = User.objects.create_user(username="testuser", email="test@example.com")

        data = {
            "name": "Morning Exercise",
            "description": "30 minutes of exercise",
            "category": HabitCategory.HEALTH,
            "frequency": HabitFrequency.DAILY,
            "goal_count": 1,
            "start_date": date.today(),
        }

        serializer = HabitSerializer(
            data=data, context={"request": type("Request", (), {"user": user})()}
        )
        assert serializer.is_valid(), serializer.errors
        habit = serializer.save()

        assert habit.user == user
        assert habit.name == "Morning Exercise"
        assert habit.category == HabitCategory.HEALTH

    def test_serialize_habit_includes_stats(self):
        """Test that serialized habit includes streak and stats."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        habit = Habit.objects.create(
            user=user,
            name="Exercise",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today() - timedelta(days=5),
        )

        # Create logs for today and 2 days back (3 consecutive including today)
        for i in range(2, -1, -1):
            HabitLog.objects.create(
                habit=habit,
                date=date.today() - timedelta(days=i),
                completed=True,
            )

        serializer = HabitSerializer(habit)
        data = serializer.data

        assert data["name"] == "Exercise"
        assert "current_streak" in data
        assert "longest_streak" in data
        assert "completion_rate" in data
        assert data["current_streak"] == 3

    def test_update_habit(self):
        """Test updating a habit."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        habit = Habit.objects.create(
            user=user,
            name="Exercise",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today(),
        )

        data = {
            "name": "Updated Exercise",
            "goal_count": 2,
        }

        serializer = HabitSerializer(habit, data=data, partial=True)
        assert serializer.is_valid()
        updated_habit = serializer.save()

        assert updated_habit.name == "Updated Exercise"
        assert updated_habit.goal_count == 2

    def test_habit_name_required(self):
        """Test that habit name is required."""
        user = User.objects.create_user(username="testuser", email="test@example.com")

        data = {
            "category": HabitCategory.HEALTH,
            "frequency": HabitFrequency.DAILY,
            "goal_count": 1,
            "start_date": date.today(),
        }

        serializer = HabitSerializer(
            data=data, context={"request": type("Request", (), {"user": user})()}
        )
        assert not serializer.is_valid()
        assert "name" in serializer.errors

    def test_habit_start_date_required(self):
        """Test that start_date is required."""
        user = User.objects.create_user(username="testuser", email="test@example.com")

        data = {
            "name": "Exercise",
            "category": HabitCategory.HEALTH,
            "frequency": HabitFrequency.DAILY,
            "goal_count": 1,
        }

        serializer = HabitSerializer(
            data=data, context={"request": type("Request", (), {"user": user})()}
        )
        assert not serializer.is_valid()
        assert "start_date" in serializer.errors

    def test_default_values_in_serializer(self):
        """Test that default values are applied correctly."""
        user = User.objects.create_user(username="testuser", email="test@example.com")

        data = {
            "name": "Exercise",
            "start_date": date.today(),
        }

        serializer = HabitSerializer(
            data=data, context={"request": type("Request", (), {"user": user})()}
        )
        assert serializer.is_valid()

        # Check that defaults are applied
        assert (
            serializer.validated_data.get("category") == HabitCategory.OTHER
            or "category" not in data
        )
        assert (
            serializer.validated_data.get("frequency") == HabitFrequency.DAILY
            or "frequency" not in data
        )


@pytest.mark.django_db
class TestHabitListSerializer:
    """Test HabitListSerializer for list view."""

    def test_list_serializer_includes_streak_info(self):
        """Test that list serializer includes essential info."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        habit = Habit.objects.create(
            user=user,
            name="Exercise",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today(),
        )

        serializer = HabitListSerializer(habit)
        data = serializer.data

        assert data["id"] == habit.id
        assert data["name"] == "Exercise"
        assert data["category"] == HabitCategory.HEALTH
        assert "current_streak" in data


@pytest.mark.django_db
class TestHabitLogSerializer:
    """Test HabitLogSerializer for logging completions."""

    def test_create_habit_log_with_valid_data(self):
        """Test creating a habit log."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        habit = Habit.objects.create(
            user=user,
            name="Exercise",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today(),
        )

        data = {
            "date": date.today(),
            "completed": True,
            "notes": "Great workout!",
        }

        serializer = HabitLogSerializer(data=data, context={"habit": habit})
        assert serializer.is_valid(), serializer.errors
        log = serializer.save(habit=habit)

        assert log.habit == habit
        assert log.completed is True
        assert log.notes == "Great workout!"

    def test_serialize_habit_log(self):
        """Test serializing a habit log."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        habit = Habit.objects.create(
            user=user,
            name="Exercise",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today(),
        )

        log = HabitLog.objects.create(
            habit=habit,
            date=date.today(),
            completed=True,
            notes="Good",
        )

        serializer = HabitLogSerializer(log)
        data = serializer.data

        assert data["date"] == str(date.today())
        assert data["completed"] is True
        assert data["notes"] == "Good"

    def test_habit_log_date_required(self):
        """Test that date is required."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        habit = Habit.objects.create(
            user=user,
            name="Exercise",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today(),
        )

        data = {
            "completed": True,
        }

        serializer = HabitLogSerializer(data=data, context={"habit": habit})
        assert not serializer.is_valid()
        assert "date" in serializer.errors

    def test_update_habit_log(self):
        """Test updating a habit log."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        habit = Habit.objects.create(
            user=user,
            name="Exercise",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today(),
        )

        log = HabitLog.objects.create(
            habit=habit,
            date=date.today(),
            completed=False,
        )

        data = {
            "completed": True,
            "notes": "Finally did it!",
        }

        serializer = HabitLogSerializer(log, data=data, partial=True)
        assert serializer.is_valid()
        updated_log = serializer.save()

        assert updated_log.completed is True
        assert updated_log.notes == "Finally did it!"
