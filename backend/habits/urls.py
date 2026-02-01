"""
URL routing for habits app.
Week 2: CRUD endpoints for habits and habit logs.
Week 4.1: Analytics endpoints.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from habits.analytics import (analytics_monthly, analytics_overview,
                              analytics_weekly)
from habits.export import export_csv, export_json
from habits.views import HabitLogViewSet, HabitViewSet

app_name = "habits"

router = DefaultRouter()
router.register(r"", HabitViewSet, basename="habit")
router.register(r"logs", HabitLogViewSet, basename="habitlog")

urlpatterns = [
    path("analytics/overview/", analytics_overview, name="analytics-overview"),
    path("analytics/weekly/", analytics_weekly, name="analytics-weekly"),
    path("analytics/monthly/", analytics_monthly, name="analytics-monthly"),
    path("export/csv/", export_csv, name="export-csv"),
    path("export/json/", export_json, name="export-json"),
    path("", include(router.urls)),
]
