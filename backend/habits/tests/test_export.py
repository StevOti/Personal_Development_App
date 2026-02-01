"""
Tests for habit data export endpoints.
Week 4.4: CSV and JSON export functionality.
"""

import csv
import json
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from habits.models import Habit, HabitLog

User = get_user_model()


class TestCSVExport(TestCase):
    """Test CSV export endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        # Create test habits
        self.habit1 = Habit.objects.create(
            user=self.user,
            name="Morning Meditation",
            description="Daily meditation practice",
            category="health",
            frequency="daily",
            goal_count=1,
            start_date=date.today() - timedelta(days=10),
        )
        self.habit2 = Habit.objects.create(
            user=self.user,
            name="Read Book",
            description="Read for 30 minutes",
            category="learning",
            frequency="daily",
            goal_count=1,
            start_date=date.today() - timedelta(days=5),
        )

        # Create logs
        for i in range(7):
            HabitLog.objects.create(
                habit=self.habit1,
                date=date.today() - timedelta(days=i),
                completed=True,
                notes=f"Day {i+1} completed",
            )

        for i in range(3):
            HabitLog.objects.create(
                habit=self.habit2, date=date.today() - timedelta(days=i), completed=True
            )

    def test_csv_export_success(self):
        """Test CSV export returns valid CSV file."""
        response = self.client.get("/api/habits/export/csv/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("attachment", response["Content-Disposition"])

        # Verify CSV content
        content = response.content.decode("utf-8")
        lines = content.strip().split("\n")

        # Should have header + 10 habit logs
        self.assertGreater(len(lines), 1)

    def test_csv_export_requires_auth(self):
        """Test CSV export requires authentication."""
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/habits/export/csv/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_csv_export_only_user_data(self):
        """Test CSV export only includes user's own habits."""
        # Create another user's habit
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        Habit.objects.create(
            user=other_user,
            name="Other Habit",
            category="health",
            frequency="daily",
            goal_count=1,
            start_date=date.today(),
        )

        response = self.client.get("/api/habits/export/csv/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = response.content.decode("utf-8")

        # Should not contain "Other Habit"
        self.assertNotIn("Other Habit", content)
        self.assertIn("Morning Meditation", content)


class TestJSONExport(TestCase):
    """Test JSON export endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        # Create test habit
        self.habit = Habit.objects.create(
            user=self.user,
            name="Exercise",
            description="30 minutes of exercise",
            category="health",
            frequency="daily",
            goal_count=1,
            start_date=date.today() - timedelta(days=5),
        )

        # Create logs
        for i in range(5):
            HabitLog.objects.create(
                habit=self.habit, date=date.today() - timedelta(days=i), completed=True
            )

    def test_json_export_success(self):
        """Test JSON export returns valid JSON."""
        response = self.client.get("/api/habits/export/json/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIn("attachment", response["Content-Disposition"])

        # Verify JSON content
        data = json.loads(response.content.decode("utf-8"))

        self.assertIn("user", data)
        self.assertIn("habits", data)
        self.assertIn("export_date", data)

        # Check habit data
        self.assertEqual(len(data["habits"]), 1)
        self.assertEqual(data["habits"][0]["name"], "Exercise")

    def test_json_export_requires_auth(self):
        """Test JSON export requires authentication."""
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/habits/export/json/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_json_export_includes_logs(self):
        """Test JSON export includes all habit logs."""
        response = self.client.get("/api/habits/export/json/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content.decode("utf-8"))

        # Check that logs are included
        habit_data = data["habits"][0]
        self.assertIn("logs", habit_data)
        self.assertEqual(len(habit_data["logs"]), 5)

    def test_json_export_only_user_data(self):
        """Test JSON export only includes user's own data."""
        # Create another user's habit
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        Habit.objects.create(
            user=other_user,
            name="Other Habit",
            category="health",
            frequency="daily",
            goal_count=1,
            start_date=date.today(),
        )

        response = self.client.get("/api/habits/export/json/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content.decode("utf-8"))

        # Should only have 1 habit (user's own)
        self.assertEqual(len(data["habits"]), 1)
        self.assertEqual(data["habits"][0]["name"], "Exercise")


class TestBulkExport(TestCase):
    """Test exporting all data at once."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        # Create multiple habits
        for i in range(3):
            Habit.objects.create(
                user=self.user,
                name=f"Habit {i+1}",
                category="health",
                frequency="daily",
                goal_count=1,
                start_date=date.today(),
            )

    def test_csv_export_multiple_habits(self):
        """Test CSV export with multiple habits."""
        response = self.client.get("/api/habits/export/csv/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = response.content.decode("utf-8")

        # Should contain all habits
        self.assertIn("Habit 1", content)
        self.assertIn("Habit 2", content)
        self.assertIn("Habit 3", content)

    def test_json_export_multiple_habits(self):
        """Test JSON export with multiple habits."""
        response = self.client.get("/api/habits/export/json/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content.decode("utf-8"))

        self.assertEqual(len(data["habits"]), 3)

    def test_empty_habits_export(self):
        """Test export when user has no habits."""
        # Create new user with no habits
        user2 = User.objects.create_user(
            username="emptyuser", email="empty@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=user2)

        response = self.client.get("/api/habits/export/json/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content.decode("utf-8"))

        self.assertEqual(len(data["habits"]), 0)
