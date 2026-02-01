"""
Tests for habit analytics endpoints.
"""
from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from habits.models import Habit, HabitLog

User = get_user_model()


class TestAnalyticsOverview(TestCase):
    """Test the analytics overview endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        # Create test habits
        self.habit1 = Habit.objects.create(
            user=self.user,
            name="Morning Meditation",
            category="health",
            frequency="daily",
            goal_count=1,
            start_date=date.today() - timedelta(days=10)
        )
        self.habit2 = Habit.objects.create(
            user=self.user,
            name="Read Book",
            category="learning",
            frequency="daily",
            goal_count=1,
            start_date=date.today() - timedelta(days=5)
        )

        # Create logs for habit1 (7 consecutive days)
        for i in range(7):
            HabitLog.objects.create(
                habit=self.habit1,
                date=date.today() - timedelta(days=i),
                completed=True
            )

        # Create logs for habit2 (3 days)
        for i in range(3):
            HabitLog.objects.create(
                habit=self.habit2,
                date=date.today() - timedelta(days=i),
                completed=True
            )

    def test_analytics_overview_success(self):
        """Test analytics overview returns correct aggregated data."""
        response = self.client.get("/api/habits/analytics/overview/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        # Check structure
        self.assertIn("total_habits", data)
        self.assertIn("active_habits", data)
        self.assertIn("total_completions", data)
        self.assertIn("current_streak", data)
        self.assertIn("longest_streak", data)
        self.assertIn("completion_rate", data)
        
        # Check values
        self.assertEqual(data["total_habits"], 2)
        self.assertEqual(data["active_habits"], 2)
        self.assertEqual(data["total_completions"], 10)  # 7 + 3
        self.assertGreaterEqual(data["current_streak"], 3)
        
    def test_analytics_overview_requires_auth(self):
        """Test analytics overview requires authentication."""
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/habits/analytics/overview/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestWeeklyAnalytics(TestCase):
    """Test the weekly analytics endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        self.habit = Habit.objects.create(
            user=self.user,
            name="Exercise",
            category="health",
            frequency="daily",
            goal_count=1,
            start_date=date.today() - timedelta(days=10)
        )

        # Create logs for last 7 days
        for i in range(7):
            HabitLog.objects.create(
                habit=self.habit,
                date=date.today() - timedelta(days=i),
                completed=True
            )

    def test_weekly_analytics_success(self):
        """Test weekly analytics returns last 7 days data."""
        response = self.client.get("/api/habits/analytics/weekly/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        # Check structure
        self.assertIn("daily_data", data)
        self.assertEqual(len(data["daily_data"]), 7)
        
        # Check each day has required fields
        for day in data["daily_data"]:
            self.assertIn("date", day)
            self.assertIn("completions", day)
            self.assertIn("total_habits", day)
            self.assertIn("completion_rate", day)
        
        # Check first day (today) has correct data
        today_data = data["daily_data"][0]
        self.assertEqual(today_data["date"], str(date.today()))
        self.assertEqual(today_data["completions"], 1)

    def test_weekly_analytics_requires_auth(self):
        """Test weekly analytics requires authentication."""
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/habits/analytics/weekly/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestMonthlyAnalytics(TestCase):
    """Test the monthly analytics endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        self.habit = Habit.objects.create(
            user=self.user,
            name="Meditation",
            category="health",
            frequency="daily",
            goal_count=1,
            start_date=date.today().replace(day=1)
        )

        # Create logs for current month (from day 1 to min(today.day, 15))
        days_to_log = min(date.today().day, 15)
        for i in range(days_to_log):
            HabitLog.objects.create(
                habit=self.habit,
                date=date.today() - timedelta(days=i),
                completed=True
            )
        
        self.expected_completions = days_to_log

    def test_monthly_analytics_success(self):
        """Test monthly analytics returns current month data."""
        response = self.client.get("/api/habits/analytics/monthly/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        # Check structure
        self.assertIn("month", data)
        self.assertIn("year", data)
        self.assertIn("total_completions", data)
        self.assertIn("total_habits", data)
        self.assertIn("completion_rate", data)
        self.assertIn("category_breakdown", data)
        
        # Check values
        self.assertEqual(data["total_completions"], self.expected_completions)
        self.assertEqual(data["total_habits"], 1)
        self.assertIsInstance(data["category_breakdown"], list)

    def test_monthly_analytics_requires_auth(self):
        """Test monthly analytics requires authentication."""
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/habits/analytics/monthly/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestCategoryAnalytics(TestCase):
    """Test category-based analytics."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        # Create habits in different categories
        self.health_habit = Habit.objects.create(
            user=self.user,
            name="Exercise",
            category="health",
            frequency="daily",
            goal_count=1,
            start_date=date.today() - timedelta(days=5)
        )
        
        self.learning_habit = Habit.objects.create(
            user=self.user,
            name="Read",
            category="learning",
            frequency="daily",
            goal_count=1,
            start_date=date.today() - timedelta(days=5)
        )

        # Create logs
        for i in range(5):
            HabitLog.objects.create(
                habit=self.health_habit,
                date=date.today() - timedelta(days=i),
                completed=True
            )
        
        for i in range(3):
            HabitLog.objects.create(
                habit=self.learning_habit,
                date=date.today() - timedelta(days=i),
                completed=True
            )

    def test_category_analytics_in_overview(self):
        """Test that overview includes category breakdown."""
        response = self.client.get("/api/habits/analytics/overview/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        # Should include category breakdown
        self.assertIn("category_breakdown", data)
        categories = data["category_breakdown"]
        
        # Check structure
        self.assertIsInstance(categories, list)
        
        # Find health and learning categories
        health_cat = next((c for c in categories if c["category"] == "health"), None)
        learning_cat = next((c for c in categories if c["category"] == "learning"), None)
        
        self.assertIsNotNone(health_cat)
        self.assertIsNotNone(learning_cat)
        
        # Check values
        self.assertEqual(health_cat["habit_count"], 1)
        self.assertEqual(health_cat["total_completions"], 5)
        self.assertEqual(learning_cat["habit_count"], 1)
        self.assertEqual(learning_cat["total_completions"], 3)
