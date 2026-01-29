"""
Models for habit tracking module.
Week 2: Habit and HabitLog with streak calculations.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from datetime import date, timedelta

User = get_user_model()


class HabitCategory(models.TextChoices):
    """Habit category choices."""

    HEALTH = "health", "Health"
    PRODUCTIVITY = "productivity", "Productivity"
    FINANCE = "finance", "Finance"
    LEARNING = "learning", "Learning"
    RELATIONSHIPS = "relationships", "Relationships"
    OTHER = "other", "Other"


class HabitFrequency(models.TextChoices):
    """Habit frequency choices."""

    DAILY = "daily", "Daily"
    WEEKLY = "weekly", "Weekly"
    MONTHLY = "monthly", "Monthly"


class Habit(models.Model):
    """Model for tracking habits."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="habits")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    category = models.CharField(
        max_length=20,
        choices=HabitCategory.choices,
        default=HabitCategory.OTHER,
    )
    frequency = models.CharField(
        max_length=20,
        choices=HabitFrequency.choices,
        default=HabitFrequency.DAILY,
    )
    goal_count = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Number of times per period (e.g., 5 for 5x per week)",
    )
    start_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        """Return habit name with frequency."""
        frequency_display = dict(HabitFrequency.choices).get(
            self.frequency, self.frequency
        )
        return f"{self.name} ({frequency_display})"

    def calculate_current_streak(self) -> int:
        """
        Calculate current streak (consecutive days completed).
        For daily habits only.
        """
        if self.frequency != HabitFrequency.DAILY:
            return 0

        today = date.today()
        streak = 0

        # Check backward from today
        current_date = today

        while True:
            log = HabitLog.objects.filter(
                habit=self, date=current_date, completed=True
            ).first()

            if log:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break

        return streak

    def get_longest_streak(self) -> int:
        """Calculate longest streak ever achieved."""
        logs = (
            HabitLog.objects.filter(habit=self, completed=True)
            .order_by("date")
            .values_list("date", flat=True)
        )

        if not logs:
            return 0

        longest = 1
        current = 1
        logs_list = list(logs)

        for i in range(1, len(logs_list)):
            if logs_list[i] == logs_list[i - 1] + timedelta(days=1):
                current += 1
                longest = max(longest, current)
            else:
                current = 1

        return longest

    def get_completion_rate(self) -> float:
        """Calculate completion rate percentage."""
        today = date.today()
        days_active = (today - self.start_date).days + 1

        if days_active <= 0:
            return 0.0

        completed = HabitLog.objects.filter(habit=self, completed=True).count()

        return (completed / days_active) * 100


class HabitLog(models.Model):
    """Model for logging habit completions."""

    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="logs")
    date = models.DateField()
    completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("habit", "date")
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["habit", "date"]),
            models.Index(fields=["habit", "completed"]),
        ]

    def __str__(self):
        """Return log string representation."""
        status = "✓" if self.completed else "✗"
        return f"{self.habit.name} - {self.date} ({status})"
