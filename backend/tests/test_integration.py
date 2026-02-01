"""
Integration tests for complete user workflows.
Week 3: Tests full application flow from auth to habit management.
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
class TestAuthenticationFlow:
    """Test complete authentication workflows."""

    def test_user_registration_and_login_flow(self):
        """Test user can register and login successfully."""
        client = APIClient()

        # Step 1: Register new user
        register_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "password2": "SecurePass123!",
        }

        response = client.post(reverse("core:register"), register_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "access" in response.data
        assert "refresh" in response.data

        # Step 2: Login with credentials
        login_data = {
            "username": "newuser",
            "password": "SecurePass123!",
        }

        response = client.post(reverse("core:login"), login_data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

        # Step 3: Access protected endpoint with token
        access_token = response.data["access"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response = client.get(reverse("core:profile"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "newuser"
        assert response.data["email"] == "newuser@example.com"

    def test_token_refresh_flow(self):
        """Test refresh token can generate new access token."""
        client = APIClient()

        # Register user
        register_data = {
            "username": "tokenuser",
            "email": "token@example.com",
            "password": "SecurePass123!",
            "password2": "SecurePass123!",
        }

        response = client.post(reverse("core:register"), register_data, format="json")
        refresh_token = response.data["refresh"]

        # Use refresh token to get new access token
        refresh_data = {"refresh": refresh_token}
        response = client.post(
            reverse("core:token_refresh"), refresh_data, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

        # Use new access token
        new_access_token = response.data["access"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {new_access_token}")

        response = client.get(reverse("core:profile"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "tokenuser"


@pytest.mark.django_db
class TestHabitManagementFlow:
    """Test complete habit management workflows."""

    def test_create_habit_and_track_progress_flow(self):
        """Test creating a habit and tracking daily progress."""
        # Setup: Create and authenticate user
        user = User.objects.create_user(
            username="habituser", email="habits@example.com", password="SecurePass123!"
        )
        client = APIClient()
        client.force_authenticate(user=user)

        # Step 1: Create a new habit
        habit_data = {
            "name": "Morning Meditation",
            "description": "10 minutes of mindfulness",
            "category": HabitCategory.HEALTH,
            "frequency": HabitFrequency.DAILY,
            "goal_count": 1,
            "start_date": date.today().isoformat(),
        }

        response = client.post(reverse("habits:habit-list"), habit_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        habit_id = response.data["id"]
        assert response.data["name"] == "Morning Meditation"
        assert response.data["current_streak"] == 0

        # Step 2: Log completion for today
        log_data = {
            "date": date.today().isoformat(),
            "completed": True,
            "notes": "Felt peaceful and focused",
        }

        response = client.post(
            reverse("habits:habit-log", args=[habit_id]), log_data, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED

        # Step 3: Verify habit details show updated streak
        response = client.get(reverse("habits:habit-detail", args=[habit_id]))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["current_streak"] == 1
        assert len(response.data["logs"]) == 1

        # Step 4: Check stats endpoint
        response = client.get(reverse("habits:habit-stats", args=[habit_id]))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["current_streak"] == 1
        assert response.data["longest_streak"] == 1
        assert response.data["total_logs"] == 1
        assert response.data["completed_logs"] == 1

    def test_multi_day_habit_tracking_with_streaks(self):
        """Test tracking habit over multiple days and streak calculation."""
        user = User.objects.create_user(
            username="streakuser", email="streak@example.com", password="SecurePass123!"
        )
        client = APIClient()
        client.force_authenticate(user=user)

        # Create habit with start date 5 days ago
        habit_data = {
            "name": "Daily Exercise",
            "category": HabitCategory.HEALTH,
            "frequency": HabitFrequency.DAILY,
            "goal_count": 1,
            "start_date": (date.today() - timedelta(days=5)).isoformat(),
        }

        response = client.post(reverse("habits:habit-list"), habit_data, format="json")
        habit_id = response.data["id"]

        # Log completions for the last 3 consecutive days (including today)
        for i in range(2, -1, -1):
            log_data = {
                "date": (date.today() - timedelta(days=i)).isoformat(),
                "completed": True,
            }
            response = client.post(
                reverse("habits:habit-log", args=[habit_id]), log_data, format="json"
            )
            assert response.status_code == status.HTTP_201_CREATED

        # Verify current streak is 3
        response = client.get(reverse("habits:habit-detail", args=[habit_id]))
        assert response.data["current_streak"] == 3
        assert response.data["longest_streak"] == 3

        # Log missed day (4 days ago) and one completion (5 days ago)
        # This creates: [5 days ago: complete], [4 days ago: missed], [3-2-1 days ago: complete]
        log_data = {
            "date": (date.today() - timedelta(days=5)).isoformat(),
            "completed": True,
        }
        response = client.post(
            reverse("habits:habit-log", args=[habit_id]), log_data, format="json"
        )

        # Current streak should still be 3 (today to 2 days ago)
        # Longest streak should still be 3
        response = client.get(reverse("habits:habit-stats", args=[habit_id]))
        assert response.data["current_streak"] == 3
        assert response.data["longest_streak"] == 3
        assert response.data["total_logs"] == 4
        assert response.data["completed_logs"] == 4

    def test_multiple_habits_management_flow(self):
        """Test user can manage multiple habits simultaneously."""
        user = User.objects.create_user(
            username="multiuser", email="multi@example.com", password="SecurePass123!"
        )
        client = APIClient()
        client.force_authenticate(user=user)

        # Create multiple habits with different categories
        habits_data = [
            {
                "name": "Morning Run",
                "category": HabitCategory.HEALTH,
                "frequency": HabitFrequency.DAILY,
                "goal_count": 1,
                "start_date": date.today().isoformat(),
            },
            {
                "name": "Read Technical Book",
                "category": HabitCategory.LEARNING,
                "frequency": HabitFrequency.DAILY,
                "goal_count": 30,  # 30 minutes
                "start_date": date.today().isoformat(),
            },
            {
                "name": "Budget Review",
                "category": HabitCategory.FINANCE,
                "frequency": HabitFrequency.WEEKLY,
                "goal_count": 1,
                "start_date": date.today().isoformat(),
            },
        ]

        created_habits = []
        for habit_data in habits_data:
            response = client.post(
                reverse("habits:habit-list"), habit_data, format="json"
            )
            assert response.status_code == status.HTTP_201_CREATED
            created_habits.append(response.data["id"])

        # Verify all habits are in user's list
        response = client.get(reverse("habits:habit-list"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

        # Log completion for each habit
        for habit_id in created_habits:
            log_data = {
                "date": date.today().isoformat(),
                "completed": True,
            }
            response = client.post(
                reverse("habits:habit-log", args=[habit_id]), log_data, format="json"
            )
            assert response.status_code == status.HTTP_201_CREATED

        # Verify each habit shows correct stats
        for i, habit_id in enumerate(created_habits):
            response = client.get(reverse("habits:habit-detail", args=[habit_id]))
            # Each habit should have 1 log
            assert len(response.data["logs"]) == 1
            # Current streak is 1 since we logged for today (for daily habits)
            # Note: Only daily habits calculate streaks
            if i < 2:  # First two habits are DAILY
                assert response.data["current_streak"] == 1
            else:  # Third habit is WEEKLY - streak is 0
                assert response.data["current_streak"] == 0

    def test_habit_update_and_deactivation_flow(self):
        """Test updating habit details and deactivating."""
        user = User.objects.create_user(
            username="updateuser", email="update@example.com", password="SecurePass123!"
        )
        client = APIClient()
        client.force_authenticate(user=user)

        # Create habit
        habit_data = {
            "name": "Yoga Practice",
            "category": HabitCategory.HEALTH,
            "frequency": HabitFrequency.DAILY,
            "goal_count": 1,
            "start_date": date.today().isoformat(),
        }

        response = client.post(reverse("habits:habit-list"), habit_data, format="json")
        habit_id = response.data["id"]

        # Update habit details
        update_data = {
            "name": "Advanced Yoga Practice",
            "description": "Added new poses",
            "goal_count": 2,
        }

        response = client.patch(
            reverse("habits:habit-detail", args=[habit_id]), update_data, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Advanced Yoga Practice"
        assert response.data["goal_count"] == 2

        # Deactivate habit
        deactivate_data = {"is_active": False}
        response = client.patch(
            reverse("habits:habit-detail", args=[habit_id]),
            deactivate_data,
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_active"] is False


@pytest.mark.django_db
class TestUserIsolationAndSecurity:
    """Test that user data is properly isolated."""

    def test_users_cannot_access_other_users_habits(self):
        """Test that users can only see their own habits."""
        # Create two users
        user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="SecurePass123!"
        )
        user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="SecurePass123!"
        )

        client = APIClient()

        # User 1 creates a habit
        client.force_authenticate(user=user1)
        habit_data = {
            "name": "User1 Private Habit",
            "category": HabitCategory.HEALTH,
            "frequency": HabitFrequency.DAILY,
            "goal_count": 1,
            "start_date": date.today().isoformat(),
        }
        response = client.post(reverse("habits:habit-list"), habit_data, format="json")
        user1_habit_id = response.data["id"]

        # User 2 tries to access user 1's habit
        client.force_authenticate(user=user2)
        response = client.get(reverse("habits:habit-detail", args=[user1_habit_id]))
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # User 2 tries to update user 1's habit
        response = client.patch(
            reverse("habits:habit-detail", args=[user1_habit_id]),
            {"name": "Hacked!"},
            format="json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # User 2 tries to delete user 1's habit
        response = client.delete(reverse("habits:habit-detail", args=[user1_habit_id]))
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Verify user 2's habit list is empty
        response = client.get(reverse("habits:habit-list"))
        assert response.data["count"] == 0

    def test_unauthenticated_users_cannot_access_habits(self):
        """Test that authentication is required for all habit endpoints."""
        client = APIClient()

        # Try to list habits without auth
        response = client.get(reverse("habits:habit-list"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Try to create habit without auth
        habit_data = {
            "name": "Test",
            "start_date": date.today().isoformat(),
        }
        response = client.post(reverse("habits:habit-list"), habit_data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error scenarios."""

    def test_cannot_log_habit_twice_same_day(self):
        """Test unique constraint prevents duplicate logs for same day."""
        user = User.objects.create_user(
            username="loguser", email="log@example.com", password="SecurePass123!"
        )
        client = APIClient()
        client.force_authenticate(user=user)

        # Create habit
        habit_data = {
            "name": "Test Habit",
            "category": HabitCategory.HEALTH,
            "frequency": HabitFrequency.DAILY,
            "goal_count": 1,
            "start_date": date.today().isoformat(),
        }
        response = client.post(reverse("habits:habit-list"), habit_data, format="json")
        habit_id = response.data["id"]

        # Log once
        log_data = {
            "date": date.today().isoformat(),
            "completed": True,
        }
        response = client.post(
            reverse("habits:habit-log", args=[habit_id]), log_data, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED

        # Try to log again for same day - should fail
        response = client.post(
            reverse("habits:habit-log", args=[habit_id]), log_data, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_habit_with_missing_required_fields(self):
        """Test validation for required fields."""
        user = User.objects.create_user(
            username="validuser", email="valid@example.com", password="SecurePass123!"
        )
        client = APIClient()
        client.force_authenticate(user=user)

        # Missing name
        habit_data = {
            "category": HabitCategory.HEALTH,
            "start_date": date.today().isoformat(),
        }
        response = client.post(reverse("habits:habit-list"), habit_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

        # Missing start_date
        habit_data = {
            "name": "Test Habit",
            "category": HabitCategory.HEALTH,
        }
        response = client.post(reverse("habits:habit-list"), habit_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "start_date" in response.data
