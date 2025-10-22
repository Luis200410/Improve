from django.contrib import admin

from . import models


@admin.register(models.AreaOfLife)
class AreaOfLifeAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "color")
    search_fields = ("name", "owner__username")
    list_filter = ("owner",)


class MilestoneInline(admin.TabularInline):
    model = models.Milestone
    extra = 1


@admin.register(models.Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("title", "area", "start_date", "target_date", "completion_ratio")
    search_fields = ("title", "area__name")
    list_filter = ("area__owner", "area")
    inlines = [MilestoneInline]


@admin.register(models.Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ("name", "area", "frequency", "target_per_period", "active")
    list_filter = ("frequency", "active", "area__owner")
    search_fields = ("name", "area__name")


@admin.register(models.HabitCheckIn)
class HabitCheckInAdmin(admin.ModelAdmin):
    list_display = ("habit", "timestamp", "note")
    list_filter = ("habit__area__owner", "habit")
    search_fields = ("habit__name", "note")
    date_hierarchy = "timestamp"


@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "goal", "due_date", "completed")
    list_filter = ("completed", "due_date", "owner")
    search_fields = ("title", "goal__title", "owner__username")


@admin.register(models.Reflection)
class ReflectionAdmin(admin.ModelAdmin):
    list_display = ("owner", "cadence", "created_at")
    list_filter = ("cadence", "owner")
    search_fields = ("owner__username", "highlights", "lessons")


def _superuser_only_admin(request):
    return request.user.is_active and request.user.is_superuser


admin.site.has_permission = _superuser_only_admin
