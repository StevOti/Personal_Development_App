"""
Export endpoints for habits data.
Week 4.4: CSV and JSON export functionality.
"""

import csv
import json
from datetime import datetime
from io import StringIO

from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from habits.models import Habit, HabitLog


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_csv(request):
    """
    Export user's habits and logs as CSV.
    
    GET /api/habits/export/csv/
    
    Returns:
        CSV file with all user's habits and logs
        Columns: Habit, Category, Frequency, Goal, Date Logged, Completed
    """
    user = request.user
    habits = Habit.objects.filter(user=user)
    
    # Create CSV response
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Habit Name',
        'Category',
        'Frequency',
        'Goal Count',
        'Start Date',
        'Date Logged',
        'Completed'
    ])
    
    # Write habit data with logs
    for habit in habits:
        logs = HabitLog.objects.filter(habit=habit).order_by('date')
        
        if logs.exists():
            # One row per log entry
            for log in logs:
                writer.writerow([
                    habit.name,
                    habit.category,
                    habit.frequency,
                    habit.goal_count,
                    habit.start_date.isoformat(),
                    log.date.isoformat(),
                    'Yes' if log.completed else 'No'
                ])
        else:
            # If no logs, still write habit with empty log fields
            writer.writerow([
                habit.name,
                habit.category,
                habit.frequency,
                habit.goal_count,
                habit.start_date.isoformat(),
                '',
                ''
            ])
    
    # Prepare response
    response = HttpResponse(
        output.getvalue(),
        content_type='text/csv'
    )
    response['Content-Disposition'] = (
        f'attachment; filename="habits_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    )
    
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_json(request):
    """
    Export user's habits and logs as JSON.
    
    GET /api/habits/export/json/
    
    Returns:
        JSON file with all user's habits and logs
        Structure:
        {
            "user": "username",
            "export_date": "ISO date",
            "habits": [
                {
                    "name": "...",
                    "category": "...",
                    "frequency": "...",
                    "goal_count": N,
                    "start_date": "...",
                    "streak_count": N,
                    "longest_streak": N,
                    "logs": [
                        {
                            "date": "...",
                            "completed": true/false
                        }
                    ]
                }
            ]
        }
    """
    user = request.user
    habits = Habit.objects.filter(user=user)
    
    habits_data = []
    
    for habit in habits:
        logs = HabitLog.objects.filter(habit=habit).order_by('date')
        
        habit_dict = {
            'name': habit.name,
            'category': habit.category,
            'frequency': habit.frequency,
            'goal_count': habit.goal_count,
            'start_date': habit.start_date.isoformat(),
                'streak_count': habit.calculate_current_streak(),
                'longest_streak': habit.get_longest_streak(),
            'logs': [
                {
                    'date': log.date.isoformat(),
                    'completed': log.completed
                }
                for log in logs
            ]
        }
        habits_data.append(habit_dict)
    
    export_data = {
        'user': user.username,
        'export_date': datetime.now().isoformat(),
        'habits': habits_data
    }
    
    # Prepare response
    response = HttpResponse(
        json.dumps(export_data, indent=2),
        content_type='application/json'
    )
    response['Content-Disposition'] = (
        f'attachment; filename="habits_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
    )
    
    return response
