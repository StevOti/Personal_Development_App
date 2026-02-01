from django.contrib import admin

from .models import Habit, HabitLog


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "category", "frequency", "is_active")
    search_fields = ("name", "user__username")
    list_filter = ("category", "frequency", "is_active")


@admin.register(HabitLog)
class HabitLogAdmin(admin.ModelAdmin):
    list_display = ("id", "habit", "date", "completed", "created_at")
    search_fields = ("habit__name", "habit__user__username")
    list_filter = ("completed", "date")
