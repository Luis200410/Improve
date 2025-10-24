from django import forms
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


@admin.register(models.ExerciseCategory)
class ExerciseCategoryAdmin(admin.ModelAdmin):
    search_fields = ("name",)

class ExerciseForm(forms.ModelForm):
    primary_muscles = forms.MultipleChoiceField(
        choices=models.Exercise.MUSCLE_GROUP_CHOICES,
        widget=forms.SelectMultiple,
        label="Primary muscles",
    )
    secondary_muscles = forms.MultipleChoiceField(
        choices=models.Exercise.MUSCLE_GROUP_CHOICES,
        widget=forms.SelectMultiple,
        required=False,
        label="Secondary muscles",
    )

    class Meta:
        model = models.Exercise
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["primary_muscles"].initial = self.instance.primary_muscles
            self.fields["secondary_muscles"].initial = self.instance.secondary_muscles

    def clean_primary_muscles(self):
        return self.cleaned_data["primary_muscles"] or []

    def clean_secondary_muscles(self):
        return self.cleaned_data["secondary_muscles"] or []


@admin.register(models.Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "equipment", "has_media")
    list_filter = ("category", "equipment")
    search_fields = ("name", "primary_muscles", "secondary_muscles")
    form = ExerciseForm

    @admin.display(boolean=True, description="Media")
    def has_media(self, obj):
        return bool(obj.image_url or obj.video_url)


@admin.register(models.MealCategory)
class MealCategoryAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(models.Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "calories", "protein", "carbohydrates", "fats", "has_media")
    list_filter = ("category",)
    search_fields = ("name", "summary", "ingredients")

    @admin.display(boolean=True, description="Media")
    def has_media(self, obj):
        return bool(obj.image_url or obj.recipe_url)


@admin.register(models.PomodoroProfile)
class PomodoroProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "level",
        "total_focus_minutes",
        "total_sessions",
        "streak_count",
        "best_streak",
        "coins",
    )
    search_fields = ("user__username", "user__email")


@admin.register(models.PomodoroSession)
class PomodoroSessionAdmin(admin.ModelAdmin):
    list_display = (
        "profile",
        "status",
        "focus_minutes",
        "current_cycle",
        "started_at",
        "completed_focus_minutes",
    )
    list_filter = ("status", "focus_minutes")
    search_fields = ("profile__user__username",)


@admin.register(models.PomodoroTree)
class PomodoroTreeAdmin(admin.ModelAdmin):
    list_display = ("profile", "tree_type", "focus_minutes", "planted_at")
    list_filter = ("tree_type",)


class SessionExerciseInline(admin.TabularInline):
    model = models.SessionExercise
    extra = 1
    autocomplete_fields = ("exercise",)


@admin.register(models.WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "scheduled_for", "focus", "updated_at")
    list_filter = ("owner", "scheduled_for")
    search_fields = ("title", "focus", "notes", "owner__username")
    inlines = [SessionExerciseInline]
    autocomplete_fields = ("owner",)


def _superuser_only_admin(request):
    return request.user.is_active and request.user.is_superuser


admin.site.has_permission = _superuser_only_admin
