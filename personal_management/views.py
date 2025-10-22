from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.utils.text import slugify
from django.views import View
from django.views.generic import TemplateView

from . import models


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "personal_management/dashboard.html"
    default_microapps = [
        {
            "slug": "mission-control",
            "label": "Mission Control",
            "description": "Central command for aligning goals, habits, and tasks with your vision.",
        },
        {
            "slug": "operations",
            "label": "Operations",
            "description": "Keep the day-to-day business engine running smoothly.",
        },
        {
            "slug": "finance",
            "label": "Finance",
            "description": "Track money decisions, investments, and sustainability checkpoints.",
        },
        {
            "slug": "growth",
            "label": "Growth",
            "description": "Design experiments, learning plans, and development sprints.",
        },
        {
            "slug": "relationships",
            "label": "Relationships",
            "description": "Nurture the network that amplifies your personal and business impact.",
        },
        {
            "slug": "wellbeing",
            "label": "Wellbeing",
            "description": "Safeguard energy, health, and mindset so you can lead at your best.",
        },
        {
            "slug": "legacy",
            "label": "Legacy",
            "description": "Document big-picture wins and the story you are building over time.",
        },
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        life_areas = models.AreaOfLife.objects.filter(owner=user)
        microapps = [
            {
                "slug": slugify(area.name),
                "label": area.name,
                "description": area.description or "Define how this area supports your next leap.",
                "color": area.color,
            }
            for area in life_areas
        ]
        if not microapps:
            microapps = self.default_microapps

        active_slug = self.request.GET.get("app") or microapps[0]["slug"]
        active_microapp = next(
            (microapp for microapp in microapps if microapp["slug"] == active_slug), microapps[0]
        )

        context["life_areas"] = life_areas
        context["microapps"] = microapps
        context["active_microapp"] = active_microapp["slug"]
        context["active_microapp_label"] = active_microapp["label"]
        context["active_microapp_description"] = active_microapp["description"]
        context["tasks"] = models.Task.objects.filter(owner=user, completed=False)[:10]
        context["reflections"] = models.Reflection.objects.filter(owner=user)[:5]
        context["habits"] = models.Habit.objects.filter(area__owner=user, active=True)
        return context


class HomeView(View):
    template_name = "personal_management/home.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("personal_management:dashboard")
        return render(request, self.template_name)
