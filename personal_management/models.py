from __future__ import annotations

from django.contrib.auth import get_user_model
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
