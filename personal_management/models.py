from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

User = get_user_model()


class AreaOfLife(models.Model):
    """High-level life domain used to group goals and habits."""

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="life_areas")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=7,
        default="#4f46e5",
        help_text="Hex color used to represent the area in the UI.",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Area of Life"
        verbose_name_plural = "Areas of Life"
        unique_together = ("owner", "name")

    def __str__(self) -> str:
        return f"{self.name} ({self.owner})"


class Goal(models.Model):
    """Longer-term desired outcome tracked through milestones."""

    area = models.ForeignKey(AreaOfLife, on_delete=models.CASCADE, related_name="goals")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField(default=timezone.now)
    target_date = models.DateField(null=True, blank=True)
    success_criteria = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date", "title"]

    def __str__(self) -> str:
        return self.title

    @property
    def milestones_completed(self) -> int:
        return self.milestones.filter(done=True).count()

    @property
    def milestones_total(self) -> int:
        return self.milestones.count()

    def completion_ratio(self) -> float:
        total = self.milestones_total
        return self.milestones_completed / total if total else 0.0


class Milestone(models.Model):
    """Concrete checkpoints that indicate progress toward a goal."""

    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name="milestones")
    title = models.CharField(max_length=200)
    due_date = models.DateField(null=True, blank=True)
    done = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["done", "due_date", "title"]

    def __str__(self) -> str:
        return f"{self.goal.title}: {self.title}"


class Habit(models.Model):
    """Recurring practice tracked by frequency and streak."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

    FREQUENCY_CHOICES = [
        (DAILY, "Daily"),
        (WEEKLY, "Weekly"),
        (MONTHLY, "Monthly"),
        (CUSTOM, "Custom"),
    ]

    area = models.ForeignKey(AreaOfLife, on_delete=models.CASCADE, related_name="habits")
    name = models.CharField(max_length=120)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default=DAILY)
    target_per_period = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("area", "name")

    def __str__(self) -> str:
        return self.name

    def latest_check_in(self) -> "HabitCheckIn | None":
        return self.checkins.order_by("-timestamp").first()


class HabitCheckIn(models.Model):
    """Atomic record of a user completing a habit repetition."""

    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="checkins")
    timestamp = models.DateTimeField(default=timezone.now)
    note = models.CharField(max_length=240, blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"{self.habit.name} @ {self.timestamp:%Y-%m-%d %H:%M}"


class Task(models.Model):
    """Actionable item that can be tied to goals or tracked independently."""

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    goal = models.ForeignKey(
        Goal, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ["completed", "due_date", "-pk"]

    def __str__(self) -> str:
        return self.title


class Reflection(models.Model):
    """Structured journaling tool for reviewing progress and insights."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

    CADENCE_CHOICES = [
        (DAILY, "Daily"),
        (WEEKLY, "Weekly"),
        (MONTHLY, "Monthly"),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reflections")
    created_at = models.DateTimeField(auto_now_add=True)
    cadence = models.CharField(max_length=20, choices=CADENCE_CHOICES, default=DAILY)
    highlights = models.TextField(blank=True)
    lessons = models.TextField(blank=True)
    next_steps = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.owner} reflection ({self.created_at:%Y-%m-%d})"


class ExerciseCategory(models.Model):
    """High-level grouping used to organize exercises (e.g., Strength, Mobility)."""

    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Exercise Category"

    def __str__(self) -> str:
        return self.name


class Exercise(models.Model):
    """Reference library entry for an exercise including technique guidance."""

    BODYWEIGHT = "bodyweight"
    DUMBBELL = "dumbbell"
    BARBELL = "barbell"
    MACHINE = "machine"
    KETTLEBELL = "kettlebell"
    BAND = "band"
    OTHER = "other"

    EQUIPMENT_CHOICES = [
        (BODYWEIGHT, "Bodyweight"),
        (DUMBBELL, "Dumbbell"),
        (BARBELL, "Barbell"),
        (MACHINE, "Machine"),
        (KETTLEBELL, "Kettlebell"),
        (BAND, "Resistance Band"),
        (OTHER, "Other"),
    ]

    MUSCLE_GROUP_CHOICES = [
        ("Abdominals", "Abdominals"),
        ("Obliques", "Obliques"),
        ("Lower Back", "Lower Back"),
        ("Upper Back", "Upper Back"),
        ("Chest", "Chest"),
        ("Shoulders", "Shoulders"),
        ("Biceps", "Biceps"),
        ("Triceps", "Triceps"),
        ("Forearms", "Forearms"),
        ("Quadriceps", "Quadriceps"),
        ("Hamstrings", "Hamstrings"),
        ("Glutes", "Glutes"),
        ("Calves", "Calves"),
        ("Hip Flexors", "Hip Flexors"),
        ("Adductors", "Adductors"),
        ("Rotator Cuff", "Rotator Cuff"),
        ("Cardiovascular System", "Cardiovascular System"),
        ("Neck", "Neck"),
        ("Grip", "Grip"),
    ]

    name = models.CharField(max_length=160)
    category = models.ForeignKey(
        ExerciseCategory, on_delete=models.CASCADE, related_name="exercises"
    )
    equipment = models.CharField(
        max_length=32, choices=EQUIPMENT_CHOICES, default=BODYWEIGHT
    )
    primary_muscles = ArrayField(
        base_field=models.CharField(max_length=32, choices=MUSCLE_GROUP_CHOICES),
        default=list,
        help_text="Select the main muscle groups activated by this movement.",
        size=6,
    )
    secondary_muscles = ArrayField(
        base_field=models.CharField(max_length=32, choices=MUSCLE_GROUP_CHOICES),
        default=list,
        blank=True,
        help_text="Select supporting muscle groups (optional).",
        size=6,
    )
    description = models.TextField(
        blank=True, help_text="Explain the purpose or intent of this movement."
    )
    coaching_cues = models.TextField(
        blank=True, help_text="Bulleted cues or reminders for proper execution."
    )
    image_url = models.URLField(
        blank=True,
        help_text="Link to a reference image or GIF that demonstrates the movement.",
    )
    video_url = models.URLField(
        blank=True,
        help_text="Link to a demo video (YouTube, Loom, MP4, etc.).",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("name", "category", "equipment")

    def __str__(self) -> str:
        return self.name

    @property
    def primary_muscles_display(self) -> str:
        return ", ".join(self.primary_muscles)

    @property
    def secondary_muscles_display(self) -> str:
        return ", ".join(self.secondary_muscles)


class MealCategory(models.Model):
    """Categories to group meals (e.g., Breakfast, Post-Workout, Plant-Based)."""

    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Meal Category"

    def __str__(self) -> str:
        return self.name


class Meal(models.Model):
    """Reference entry for meals with macro breakdown."""

    name = models.CharField(max_length=160)
    category = models.ForeignKey(
        MealCategory, on_delete=models.CASCADE, related_name="meals"
    )
    summary = models.CharField(
        max_length=200,
        blank=True,
        help_text="Headline to describe the meal intent (e.g., High-protein breakfast).",
    )
    ingredients = models.TextField(
        blank=True, help_text="List ingredients and quantities (newline separated)."
    )
    instructions = models.TextField(blank=True)
    servings = models.PositiveSmallIntegerField(default=1)
    calories = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True, help_text="kcal per serving."
    )
    protein = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="grams per serving."
    )
    carbohydrates = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="grams per serving."
    )
    fats = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="grams per serving."
    )
    prep_time_minutes = models.PositiveIntegerField(
        null=True, blank=True, help_text="Estimated prep time per meal."
    )
    image_url = models.URLField(
        blank=True,
        help_text="Link to a reference image for the meal.",
    )
    recipe_url = models.URLField(
        blank=True,
        help_text="Link to a full recipe or video walkthrough.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("name", "category")

    def __str__(self) -> str:
        return self.name


class PomodoroProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="pomodoro_profile")
    total_focus_minutes = models.PositiveIntegerField(default=0)
    total_sessions = models.PositiveIntegerField(default=0)
    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    coins = models.PositiveIntegerField(default=0)
    streak_count = models.PositiveIntegerField(default=0)
    best_streak = models.PositiveIntegerField(default=0)
    last_completed_date = models.DateField(null=True, blank=True)

    TREE_THRESHOLDS = [
        (25, "Sprout"),
        (35, "Sapling"),
        (50, "Grove"),
        (65, "Blossom"),
        (90, "Ancient"),
    ]

    XP_PER_MINUTE = 10
    XP_PER_LEVEL = 500

    def __str__(self) -> str:
        return f"Pomodoro profile for {self.user}"

    def add_focus_minutes(self, minutes: int) -> tuple[int, str]:
        minutes = max(1, minutes)
        self.total_focus_minutes += minutes
        self.total_sessions += 1
        gained_xp = minutes * self.XP_PER_MINUTE
        self.xp += gained_xp
        self.coins += minutes // 5

        today = timezone.localdate()
        if self.last_completed_date:
            if today == self.last_completed_date:
                pass
            elif today == self.last_completed_date + timedelta(days=1):
                self.streak_count += 1
            else:
                self.streak_count = 1
        else:
            self.streak_count = 1
        self.best_streak = max(self.best_streak, self.streak_count)
        self.last_completed_date = today

        self.level = max(1, (self.xp // self.XP_PER_LEVEL) + 1)
        tree_type = self._tree_for_minutes(minutes)
        self.save()
        return gained_xp, tree_type

    def _tree_for_minutes(self, minutes: int) -> str:
        for threshold, name in self.TREE_THRESHOLDS:
            if minutes <= threshold:
                return name
        return self.TREE_THRESHOLDS[-1][1]

    def xp_needed_for_next(self) -> int:
        return self.level * self.XP_PER_LEVEL

    def xp_progress(self) -> int:
        base = (self.level - 1) * self.XP_PER_LEVEL
        return self.xp - base

    def to_summary(self) -> dict:
        return {
            "level": self.level,
            "xp": self.xp,
            "xp_for_next_level": self.xp_needed_for_next(),
            "xp_progress": self.xp_progress(),
            "xp_needed_for_next": self.XP_PER_LEVEL,
            "total_focus_minutes": self.total_focus_minutes,
            "total_sessions": self.total_sessions,
            "streak_count": self.streak_count,
            "best_streak": self.best_streak,
            "coins": self.coins,
        }


class PomodoroSession(models.Model):
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (RUNNING, "Running"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]

    profile = models.ForeignKey(PomodoroProfile, on_delete=models.CASCADE, related_name="sessions")
    focus_minutes = models.PositiveIntegerField()
    short_break_minutes = models.PositiveIntegerField(default=5)
    long_break_minutes = models.PositiveIntegerField(default=15)
    cycles_before_long_break = models.PositiveIntegerField(default=4)
    current_cycle = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=RUNNING)
    started_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    completed_focus_minutes = models.PositiveIntegerField(default=0)
    tree_type = models.CharField(max_length=32, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"Pomodoro session for {self.profile.user} ({self.status})"

    @property
    def elapsed_seconds(self) -> int:
        return max(0, int((timezone.now() - self.started_at).total_seconds()) + self.completed_focus_minutes * 60)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "focus_minutes": self.focus_minutes,
            "short_break_minutes": self.short_break_minutes,
            "long_break_minutes": self.long_break_minutes,
            "cycles_before_long_break": self.cycles_before_long_break,
            "current_cycle": self.current_cycle,
            "status": self.status,
            "started_at": self.started_at.isoformat(),
        }


class PomodoroTree(models.Model):
    profile = models.ForeignKey(PomodoroProfile, on_delete=models.CASCADE, related_name="forest")
    tree_type = models.CharField(max_length=32)
    focus_minutes = models.PositiveIntegerField()
    planted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-planted_at"]

    def __str__(self) -> str:
        return f"{self.tree_type} ({self.focus_minutes} min)"


class WorkoutSession(models.Model):
    """Structured training session composed of multiple exercises."""

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="workout_sessions")
    title = models.CharField(max_length=160)
    scheduled_for = models.DateField(null=True, blank=True)
    focus = models.CharField(
        max_length=120,
        blank=True,
        help_text="High-level intent (e.g., Lower Body Strength, Mobility Reset).",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_for", "-created_at"]

    def __str__(self) -> str:
        return self.title


class SessionExercise(models.Model):
    """Join model describing how an exercise is performed inside a session."""

    session = models.ForeignKey(
        WorkoutSession, on_delete=models.CASCADE, related_name="session_exercises"
    )
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="session_uses")
    order = models.PositiveIntegerField(default=1)
    sets = models.PositiveSmallIntegerField(default=3)
    reps = models.CharField(
        max_length=40, default="10", help_text="Reps or time (e.g., 8-10, 45s)."
    )
    tempo = models.CharField(max_length=40, blank=True, help_text="Tempo (e.g., 3010).")
    rest_seconds = models.PositiveIntegerField(
        null=True, blank=True, help_text="Rest after this exercise in seconds."
    )
    notes = models.TextField(blank=True, help_text="Coaching cues or progressions.")

    class Meta:
        ordering = ["order"]
        unique_together = ("session", "order")

    def __str__(self) -> str:
        return f"{self.session.title} · {self.exercise.name}"
