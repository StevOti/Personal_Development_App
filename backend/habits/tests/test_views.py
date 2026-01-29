"""
Unit tests for habit API endpoints (CRUD operations).
Week 2: Tests for habit list, create, update, delete, daily tracking.
"""

import pytest
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from habits.models import Habit, HabitLog, HabitCategory, HabitFrequency

User = get_user_model()


@pytest.mark.django_db
class TestHabitListView:
    """Test habit list and create endpoints."""

    def test_list_habits(self):
        """Test getting user's habits list."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        habit = Habit.objects.create(
            user=user,
            name="Exercise",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today(),
        )

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(reverse("habits:habit-list"))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Exercise"

    def test_list_habits_only_own(self):
        """Test that users only see their own habits."""
        user1 = User.objects.create_user(username="user1", email="user1@example.com")
        user2 = User.objects.create_user(username="user2", email="user2@example.com")

        Habit.objects.create(
            user=user1,
            name="User1 Exercise",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today(),
        )
        Habit.objects.create(
            user=user2,
            name="User2 Reading",
            category=HabitCategory.LEARNING,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today(),
        )

        client = APIClient()
        client.force_authenticate(user=user1)
        response = client.get(reverse("habits:habit-list"))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "User1 Exercise"

    def test_create_habit(self):
        """Test creating a new habit."""
        user = User.objects.create_user(username="testuser", email="test@example.com")

        data = {
            "name": "Morning Run",
            "description": "5K run",
            "category": HabitCategory.HEALTH,
            "frequency": HabitFrequency.DAILY,
            "goal_count": 1,
            "start_date": date.today().isoformat(),
        }

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(reverse("habits:habit-list"), data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Habit.objects.filter(user=user, name="Morning Run").exists()

    def test_create_habit_requires_auth(self):
        """Test that creating habit requires authentication."""
        client = APIClient()
        data = {
            "name": "Exercise",
            "start_date": date.today().isoformat(),
        }

        response = client.post(reverse("habits:habit-list"), data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestHabitDetailView:
    """Test habit detail endpoints."""

    def test_retrieve_habit(self):
        """Test getting habit details."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        habit = Habit.objects.create(
            user=user,
            name="Exercise",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today(),
        )

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(reverse("habits:habit-detail", args=[habit.id]))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Exercise"
        assert "current_streak" in response.data

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

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.patch(
            reverse("habits:habit-detail", args=[habit.id]), data, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        habit.refresh_from_db()
        assert habit.name == "Updated Exercise"
        assert habit.goal_count == 2

    def test_delete_habit(self):
        """Test deleting a habit."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        habit = Habit.objects.create(
            user=user,
            name="Exercise",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today(),
        )

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.delete(reverse("habits:habit-detail", args=[habit.id]))

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Habit.objects.filter(id=habit.id).exists()

    def test_cannot_access_other_user_habit(self):
        """Test that users can't access other users' habits."""
        user1 = User.objects.create_user(username="user1", email="user1@example.com")
        user2 = User.objects.create_user(username="user2", email="user2@example.com")

        habit = Habit.objects.create(
            user=user1,
            name="Exercise",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today(),
        )

        client = APIClient()
        client.force_authenticate(user=user2)
        response = client.get(reverse("habits:habit-detail", args=[habit.id]))

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestHabitLogView:
    """Test habit logging endpoints."""

    def test_log_habit_completion(self):
        """Test logging habit completion."""
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
            "date": date.today().isoformat(),
            "completed": True,
            "notes": "Great workout!",
        }

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            reverse("habits:habit-log", args=[habit.id]), data, format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert HabitLog.objects.filter(habit=habit, completed=True).exists()

    def test_update_habit_log(self):
        """Test updating habit log."""
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

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.patch(
            reverse("habits:habitlog-detail", args=[log.id]), data, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        log.refresh_from_db()
        assert log.completed is True


@pytest.mark.django_db
class TestHabitStatsView:
    """Test habit statistics endpoints."""

    def test_get_habit_stats(self):
        """Test getting habit statistics."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        habit = Habit.objects.create(
            user=user,
            name="Exercise",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today() - timedelta(days=5),
        )

        # Create logs for today and 2 days back (3 consecutive days including today)
        for i in range(2, -1, -1):
            HabitLog.objects.create(
                habit=habit,
                date=date.today() - timedelta(days=i),
                completed=True,
            )

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(reverse("habits:habit-stats", args=[habit.id]))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["current_streak"] == 3
        assert response.data["longest_streak"] == 3
        assert "completion_rate" in response.data
