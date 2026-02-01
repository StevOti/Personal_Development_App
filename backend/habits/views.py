"""
API views for habit tracking endpoints.
Provides CRUD operations for habits and habit logging.
"""

import logging

from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from habits.models import Habit, HabitLog
from habits.serializers import (HabitListSerializer, HabitLogSerializer,
                                HabitSerializer)

logger = logging.getLogger(__name__)


class HabitViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Habit CRUD operations.
    - List: GET /api/habits/ (user's habits only)
    - Create: POST /api/habits/
    - Retrieve: GET /api/habits/{id}/
    - Update: PUT/PATCH /api/habits/{id}/
    - Delete: DELETE /api/habits/{id}/
    - Log: POST /api/habits/{id}/log/
    - Stats: GET /api/habits/{id}/stats/
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only the current user's habits."""
        return Habit.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """Use list serializer for list view, full serializer for detail views."""
        if self.action == "list":
            return HabitListSerializer
        return HabitSerializer

    def perform_create(self, serializer):
        """Set the user when creating a habit."""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def log(self, request, pk=None):
        """
        Log a habit completion.
        POST /api/habits/{id}/log/

        Request body:
        {
            "date": "2024-01-15",
            "completed": true,
            "notes": "Optional notes"
        }
        """
        habit = self.get_object()
        serializer = HabitLogSerializer(data=request.data)

        if serializer.is_valid():
            try:
                log = serializer.save(habit=habit)
                logger.info(
                    f"Habit log created: user={request.user.id}, "
                    f"habit={habit.id}, date={log.date}, completed={log.completed}"
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                logger.warning(
                    f"Duplicate log attempt: user={request.user.id}, "
                    f"habit={habit.id}, date={request.data.get('date')}"
                )
                return Response(
                    {"detail": "A log for this habit already exists for this date."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def stats(self, request, pk=None):
        """
        Get habit statistics.
        GET /api/habits/{id}/stats/

        Returns:
        {
            "current_streak": 3,
            "longest_streak": 5,
            "completion_rate": 0.65,
            "total_logs": 13,
            "completed_logs": 8
        }
        """
        habit = self.get_object()

        stats_data = {
            "current_streak": habit.calculate_current_streak(),
            "longest_streak": habit.get_longest_streak(),
            "completion_rate": habit.get_completion_rate(),
            "total_logs": habit.logs.count(),
            "completed_logs": habit.logs.filter(completed=True).count(),
        }

        return Response(stats_data)


class HabitLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for HabitLog CRUD operations.
    - List: GET /api/habit-logs/ (user's logs only)
    - Create: POST /api/habit-logs/
    - Retrieve: GET /api/habit-logs/{id}/
    - Update: PUT/PATCH /api/habit-logs/{id}/
    - Delete: DELETE /api/habit-logs/{id}/
    """

    permission_classes = [IsAuthenticated]
    serializer_class = HabitLogSerializer

    def get_queryset(self):
        """Return only logs for the current user's habits."""
        return HabitLog.objects.filter(habit__user=self.request.user)
