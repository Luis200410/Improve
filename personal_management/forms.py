from django import forms

from . import models


class TaskForm(forms.ModelForm):
    class Meta:
        model = models.Task
        fields = ["title", "description", "goal", "due_date", "completed"]


class ReflectionForm(forms.ModelForm):
    class Meta:
        model = models.Reflection
        fields = ["cadence", "highlights", "lessons", "next_steps"]
