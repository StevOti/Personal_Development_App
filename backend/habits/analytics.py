"""
Analytics views for habit tracking.
Week 4.1: Statistical endpoints for user insights.
"""

import logging
from datetime import date, timedelta

from django.db.models import Count, Max, Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from habits.models import Habit, HabitLog

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics_overview(request):
    """
    Get overview analytics for the authenticated user.

    Returns:
        - total_habits: Total number of habits
        - active_habits: Number of active habits
        - total_completions: Total habit logs completed
        - current_streak: Longest current streak across all habits
        - longest_streak: All-time longest streak
        - completion_rate: Overall completion rate (percentage)
        - category_breakdown: List of categories with stats
    """
    user = request.user
    habits = Habit.objects.filter(user=user)

    # Basic counts
    total_habits = habits.count()
    active_habits = habits.filter(is_active=True).count()
    total_completions = HabitLog.objects.filter(
        habit__user=user, completed=True
    ).count()

    # Calculate streaks
    current_streak = 0
    longest_streak = 0

    for habit in habits.filter(is_active=True, frequency="daily"):
        habit_current = habit.calculate_current_streak()
        habit_longest = habit.get_longest_streak()

        if habit_current > current_streak:
            current_streak = habit_current
        if habit_longest > longest_streak:
            longest_streak = habit_longest

    # Calculate completion rate
    # Get all active daily habits and check completion rate for last 30 days
    thirty_days_ago = date.today() - timedelta(days=30)
    active_daily_habits = habits.filter(is_active=True, frequency="daily")

    if active_daily_habits.exists():
        expected_logs = 0
        actual_logs = 0

        for habit in active_daily_habits:
            # Calculate days since start (or 30 days ago, whichever is more recent)
            start = max(habit.start_date, thirty_days_ago)
            days_active = (date.today() - start).days + 1
            expected_logs += days_active

            # Count actual completions
            actual_logs += HabitLog.objects.filter(
                habit=habit, date__gte=start, completed=True
            ).count()

        completion_rate = (
            round((actual_logs / expected_logs * 100), 1) if expected_logs > 0 else 0
        )
    else:
        completion_rate = 0

    # Category breakdown
    from habits.models import HabitCategory

    category_breakdown = []

    for category_value, category_label in HabitCategory.choices:
        category_habits = habits.filter(category=category_value)
        habit_count = category_habits.count()

        if habit_count > 0:
            category_completions = HabitLog.objects.filter(
                habit__in=category_habits, completed=True
            ).count()

            category_breakdown.append(
                {
                    "category": category_value,
                    "category_label": category_label,
                    "habit_count": habit_count,
                    "total_completions": category_completions,
                }
            )

    logger.info(
        f"Analytics overview requested: user={user.id}, total_habits={total_habits}, completion_rate={completion_rate}%"
    )

    return Response(
        {
            "total_habits": total_habits,
            "active_habits": active_habits,
            "total_completions": total_completions,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "completion_rate": completion_rate,
            "category_breakdown": category_breakdown,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics_weekly(request):
    """
    Get weekly analytics (last 7 days).

    Returns daily breakdown for the last 7 days:
        - date: Date string
        - completions: Number of completed logs
        - total_habits: Number of active habits
        - completion_rate: Completion rate for that day
    """
    user = request.user
    today = date.today()
    daily_data = []

    # Get all active daily habits
    active_habits = Habit.objects.filter(user=user, is_active=True, frequency="daily")
    total_active = active_habits.count()

    for i in range(7):
        check_date = today - timedelta(days=i)

        # Count completions for this date
        completions = HabitLog.objects.filter(
            habit__user=user, date=check_date, completed=True
        ).count()

        # Calculate rate
        if total_active > 0:
            rate = round((completions / total_active * 100), 1)
        else:
            rate = 0

        daily_data.append(
            {
                "date": str(check_date),
                "completions": completions,
                "total_habits": total_active,
                "completion_rate": rate,
            }
        )

    logger.info(f"Analytics weekly requested: user={user.id}, days={len(daily_data)}")

    return Response({"daily_data": daily_data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics_monthly(request):
    """
    Get monthly analytics for the current month.

    Returns:
        - month: Current month (1-12)
        - year: Current year
        - total_completions: Total completions this month
        - total_habits: Number of active habits
        - completion_rate: Completion rate for the month
        - category_breakdown: Completions by category
    """
    user = request.user
    today = date.today()
    month_start = today.replace(day=1)

    # Get active habits
    active_habits = Habit.objects.filter(user=user, is_active=True)
    total_active = active_habits.count()

    # Count completions this month
    total_completions = HabitLog.objects.filter(
        habit__user=user, date__gte=month_start, completed=True
    ).count()

    # Calculate expected completions (only for daily habits)
    active_daily = active_habits.filter(frequency="daily")
    days_in_month = today.day  # Days elapsed so far
    expected_completions = active_daily.count() * days_in_month

    completion_rate = 0
    if expected_completions > 0:
        completion_rate = round((total_completions / expected_completions * 100), 1)

    # Category breakdown for this month
    from habits.models import HabitCategory

    category_breakdown = []

    for category_value, category_label in HabitCategory.choices:
        category_habits = active_habits.filter(category=category_value)

        if category_habits.exists():
            category_completions = HabitLog.objects.filter(
                habit__in=category_habits, date__gte=month_start, completed=True
            ).count()

            if category_completions > 0:
                category_breakdown.append(
                    {
                        "category": category_value,
                        "category_label": category_label,
                        "completions": category_completions,
                    }
                )

    logger.info(
        f"Analytics monthly requested: user={user.id}, month={today.month}/{today.year}, completions={total_completions}"
    )

    return Response(
        {
            "month": today.month,
            "year": today.year,
            "total_completions": total_completions,
            "total_habits": total_active,
            "completion_rate": completion_rate,
            "category_breakdown": category_breakdown,
        }
    )
