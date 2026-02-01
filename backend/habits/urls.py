"""
URL routing for habits app.
Week 2: CRUD endpoints for habits and habit logs.
Week 4.1: Analytics endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from habits.views import HabitViewSet, HabitLogViewSet
from habits.analytics import analytics_overview, analytics_weekly, analytics_monthly

app_name = "habits"

router = DefaultRouter()
router.register(r"", HabitViewSet, basename="habit")
router.register(r"logs", HabitLogViewSet, basename="habitlog")

urlpatterns = [
    path("analytics/overview/", analytics_overview, name="analytics-overview"),
    path("analytics/weekly/", analytics_weekly, name="analytics-weekly"),
    path("analytics/monthly/", analytics_monthly, name="analytics-monthly"),
    path("", include(router.urls)),
]
