"""
Unit tests for habits models (Habit, HabitLog).
Week 2: Habit tracking with streaks and logging.
"""

from datetime import date, datetime, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from habits.models import Habit, HabitCategory, HabitFrequency, HabitLog

User = get_user_model()


@pytest.mark.django_db
class TestHabitModel:
    """Test Habit model creation and validation."""

    def test_create_habit_success(self):
        """Test creating a habit with valid data."""
        user = User.objects.create_user(username="testuser", email="test@example.com")

        habit = Habit.objects.create(
            user=user,
            name="Morning Exercise",
            description="30 minutes of exercise",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today(),
        )

        assert habit.user == user
        assert habit.name == "Morning Exercise"
        assert habit.category == HabitCategory.HEALTH
        assert habit.frequency == HabitFrequency.DAILY
        assert habit.goal_count == 1
        assert habit.is_active is True

    def test_habit_string_representation(self):
        """Test habit string representation."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        habit = Habit.objects.create(
            user=user,
            name="Read",
            category=HabitCategory.LEARNING,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today(),
        )

        assert str(habit) == "Read (Daily)"

    def test_habit_categories(self):
        """Test all habit categories are available."""
        user = User.objects.create_user(username="testuser", email="test@example.com")

        for category in [
            HabitCategory.HEALTH,
            HabitCategory.PRODUCTIVITY,
            HabitCategory.FINANCE,
            HabitCategory.LEARNING,
            HabitCategory.RELATIONSHIPS,
            HabitCategory.OTHER,
        ]:
            habit = Habit.objects.create(
                user=user,
                name=f"Habit {category}",
                category=category,
                frequency=HabitFrequency.DAILY,
                goal_count=1,
                start_date=date.today(),
            )
            assert habit.category == category

    def test_habit_frequencies(self):
        """Test all habit frequencies are available."""
        user = User.objects.create_user(username="testuser", email="test@example.com")

        for frequency in [
            HabitFrequency.DAILY,
            HabitFrequency.WEEKLY,
            HabitFrequency.MONTHLY,
        ]:
            habit = Habit.objects.create(
                user=user,
                name=f"Habit {frequency}",
                category=HabitCategory.HEALTH,
                frequency=frequency,
                goal_count=1,
                start_date=date.today(),
            )
            assert habit.frequency == frequency

    def test_habit_goal_count_validation(self):
        """Test that goal_count must be positive."""
        user = User.objects.create_user(username="testuser", email="test@example.com")

        habit = Habit(
            user=user,
            name="Test",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=0,  # Invalid: must be > 0
            start_date=date.today(),
        )

        with pytest.raises(ValidationError):
            habit.full_clean()

    def test_habit_deactivation(self):
        """Test deactivating a habit."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        habit = Habit.objects.create(
            user=user,
            name="Test",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today(),
        )

        assert habit.is_active is True
        habit.is_active = False
        habit.save()

        habit.refresh_from_db()
        assert habit.is_active is False

    def test_habit_timestamps(self):
        """Test that created_at and updated_at are set correctly."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        habit = Habit.objects.create(
            user=user,
            name="Test",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today(),
        )

        assert habit.created_at is not None
        assert habit.updated_at is not None
        assert habit.created_at <= habit.updated_at


@pytest.mark.django_db
class TestHabitLogModel:
    """Test HabitLog model for tracking completions."""

    def test_create_habit_log_success(self):
        """Test logging a habit completion."""
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
            notes="Great workout!",
        )

        assert log.habit == habit
        assert log.date == date.today()
        assert log.completed is True
        assert log.notes == "Great workout!"

    def test_habit_log_string_representation(self):
        """Test habit log string representation."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        habit = Habit.objects.create(
            user=user,
            name="Exercise",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today(),
        )

        today = date.today()
        log = HabitLog.objects.create(habit=habit, date=today, completed=True)

        assert str(log) == f"Exercise - {today} (✓)"

    def test_habit_log_incomplete(self):
        """Test logging incomplete habit."""
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

        assert log.completed is False

    def test_habit_log_unique_constraint(self):
        """Test that only one log per habit per day is allowed."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        habit = Habit.objects.create(
            user=user,
            name="Exercise",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today(),
        )

        today = date.today()
        HabitLog.objects.create(habit=habit, date=today, completed=True)

        # Try to create duplicate
        with pytest.raises(Exception):  # IntegrityError
            HabitLog.objects.create(habit=habit, date=today, completed=False)

    def test_habit_log_multiple_days(self):
        """Test logging the same habit on different days."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        habit = Habit.objects.create(
            user=user,
            name="Exercise",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today(),
        )

        today = date.today()
        yesterday = today - timedelta(days=1)

        log_today = HabitLog.objects.create(habit=habit, date=today, completed=True)
        log_yesterday = HabitLog.objects.create(
            habit=habit, date=yesterday, completed=True
        )

        assert log_today.date == today
        assert log_yesterday.date == yesterday
        assert HabitLog.objects.filter(habit=habit).count() == 2


@pytest.mark.django_db
class TestHabitStreakCalculation:
    """Test streak calculation logic."""

    def test_calculate_current_streak(self):
        """Test calculating current streak."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        habit = Habit.objects.create(
            user=user,
            name="Exercise",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today() - timedelta(days=5),
        )

        today = date.today()
        # Create logs for today and 2 days back (3 consecutive including today)
        for i in range(2, -1, -1):
            HabitLog.objects.create(
                habit=habit,
                date=today - timedelta(days=i),
                completed=True,
            )

        streak = habit.calculate_current_streak()
        assert streak == 3

    def test_streak_broken_by_missed_day(self):
        """Test that streak breaks when day is missed."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        habit = Habit.objects.create(
            user=user,
            name="Exercise",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today() - timedelta(days=10),
        )

        today = date.today()
        # Create logs with a gap
        HabitLog.objects.create(
            habit=habit, date=today - timedelta(days=3), completed=True
        )
        HabitLog.objects.create(
            habit=habit, date=today - timedelta(days=2), completed=True
        )
        # Day 1 ago is missing (broken streak)
        HabitLog.objects.create(habit=habit, date=today, completed=True)

        streak = habit.calculate_current_streak()
        assert streak == 1  # Only today counts

    def test_longest_streak(self):
        """Test tracking longest streak."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        habit = Habit.objects.create(
            user=user,
            name="Exercise",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today() - timedelta(days=20),
        )

        today = date.today()
        # Create a 5-day streak from 10 days ago
        for i in range(15, 10, -1):
            HabitLog.objects.create(
                habit=habit,
                date=today - timedelta(days=i),
                completed=True,
            )

        longest = habit.get_longest_streak()
        assert longest == 5

    def test_no_logs_streak_is_zero(self):
        """Test that streak is 0 with no logs."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        habit = Habit.objects.create(
            user=user,
            name="Exercise",
            category=HabitCategory.HEALTH,
            frequency=HabitFrequency.DAILY,
            goal_count=1,
            start_date=date.today(),
        )

        streak = habit.calculate_current_streak()
        assert streak == 0
