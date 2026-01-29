"""
URL routing for habits app.
Week 2: CRUD endpoints for habits and habit logs.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from habits.views import HabitViewSet, HabitLogViewSet

app_name = "habits"

router = DefaultRouter()
router.register(r"", HabitViewSet, basename="habit")
router.register(r"logs", HabitLogViewSet, basename="habitlog")

urlpatterns = [
    path("", include(router.urls)),
]
