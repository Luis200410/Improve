from datetime import timedelta

from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from . import models


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "personal_management/dashboard.html"
    default_microapps = [
        {
            "slug": "today",
            "label": "Today",
            "description": "All time-sensitive priorities, rituals, and insights synced for the current day.",
            "tagline": "Lead the day with intention.",
            "dashboard_template": "personal_management/systems/today/dashboard.html",
            "settings_template": "personal_management/systems/today/settings.html",
        },
        {
            "slug": "second-brain",
            "label": "Second Brain",
            "description": "Engineered knowledge OS to capture, organize, and resurface insights effortlessly.",
            "tagline": "Turn ideas into creative momentum.",
            "microcategories": [
                "Capture Inboxes",
                "Projects & Pillars",
                "Knowledge Library",
                "Review Rituals",
            ],
            "setup_prompts": [
                "Define your core knowledge pillars.",
                "List the inboxes you use to capture ideas.",
                "Decide the cadence for linking, reviewing, and archiving notes.",
            ],
            "dashboard_template": "personal_management/systems/second-brain/dashboard.html",
            "settings_template": "personal_management/systems/second-brain/settings.html",
        },
        {
            "slug": "body",
            "label": "Body",
            "description": "Optimize energy with unified protocols for training, nutrition, and recovery.",
            "tagline": "Keep energy, strength, and recovery in sync.",
            "microcategories": [
                "Training Cycles",
                "Nutrition Playbooks",
                "Recovery Protocols",
                "Vitals Dashboard",
            ],
            "setup_prompts": [
                "Document your current training split and intensity.",
                "Capture nutrition rules, macros, or restrictions.",
                "List recovery staples such as sleep targets, mobility, and supplementation.",
            ],
            "dashboard_template": "personal_management/systems/body/dashboard.html",
            "settings_template": "personal_management/systems/body/settings.html",
        },
        {
            "slug": "productivity",
            "label": "Productivity",
            "description": "Operational layer for planning, prioritization, and execution rhythms.",
            "tagline": "Plan with intention. Finish with focus.",
            "microcategories": [
                "Weekly Intentions",
                "Priority Pipeline",
                "Focus Sprints",
                "Retrospectives",
            ],
            "setup_prompts": [
                "Clarify your planning cadence (daily/weekly/monthly).",
                "Define criteria for prioritizing incoming work.",
                "Describe how you close loops and review progress at each checkpoint.",
            ],
            "dashboard_template": "personal_management/systems/productivity/dashboard.html",
            "settings_template": "personal_management/systems/productivity/settings.html",
        },
        {
            "slug": "money",
            "label": "Money",
            "description": "Bring finances, investments, and cashflow under one proactive command center.",
            "tagline": "Make confident money moves on purpose.",
            "microcategories": [
                "Cashflow Tracking",
                "Investments & Assets",
                "Spending Rules",
                "Financial Reviews",
            ],
            "setup_prompts": [
                "Map your income and recurring expense streams.",
                "List investment accounts and key metrics to monitor.",
                "Establish review checkpoints for money decisions.",
            ],
            "dashboard_template": "personal_management/systems/money/dashboard.html",
            "settings_template": "personal_management/systems/money/settings.html",
        },
        {
            "slug": "relationships",
            "label": "Relationships",
            "description": "Curate the ecosystem of people who fuel your life, work, and collaboration.",
            "tagline": "Nurture the people who elevate your mission.",
            "microcategories": [
                "Inner Circle",
                "Partners & Collaborators",
                "Community Touchpoints",
                "Celebrations & Support",
            ],
            "setup_prompts": [
                "Identify your key relationship categories.",
                "Define how often you want to reconnect with each group.",
                "Capture rituals that help you show up for people intentionally.",
            ],
            "dashboard_template": "personal_management/systems/relationships/dashboard.html",
            "settings_template": "personal_management/systems/relationships/settings.html",
        },
        {
            "slug": "mind-emotions",
            "label": "Mind & Emotions",
            "description": "Systems for mental clarity, emotional regulation, and reflective growth.",
            "tagline": "Protect your focus and emotional range.",
            "microcategories": [
                "Mindfulness Stack",
                "Journaling & Reflection",
                "Emotional Check-ins",
                "Support Resources",
            ],
            "setup_prompts": [
                "Choose the mental fitness tools that keep you grounded.",
                "Outline when and how you journal or reflect.",
                "Note escalation paths or support when stress or overwhelm hits.",
            ],
            "dashboard_template": "personal_management/systems/mind-emotions/dashboard.html",
            "settings_template": "personal_management/systems/mind-emotions/settings.html",
        },
        {
            "slug": "work",
            "label": "Work",
            "description": "Bridge long-range vision with concrete execution across teams and products.",
            "tagline": "Align vision, teams, and delivery.",
            "microcategories": [
                "Vision & Roadmaps",
                "Active Initiatives",
                "Team Rituals",
                "Delivery Metrics",
            ],
            "setup_prompts": [
                "Document the north star metrics or mission for your work.",
                "List current initiatives and their owners.",
                "Capture rituals that keep execution aligned and on track.",
            ],
            "dashboard_template": "personal_management/systems/work/dashboard.html",
            "settings_template": "personal_management/systems/work/settings.html",
        },
        {
            "slug": "legacy-fun",
            "label": "Legacy & Fun",
            "description": "Design intentional experiences, memories, and impact that outlast today.",
            "tagline": "Engineer unforgettable memories and impact.",
            "microcategories": [
                "Signature Moments",
                "Giving & Contributions",
                "Adventures",
                "Story Archive",
            ],
            "setup_prompts": [
                "Write down the legacy themes you care about.",
                "List experiences you want to design this year.",
                "Outline how you record milestones and memories.",
            ],
            "dashboard_template": "personal_management/systems/legacy-fun/dashboard.html",
            "settings_template": "personal_management/systems/legacy-fun/settings.html",
        },
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        microapps = self.default_microapps

        active_slug = self.request.GET.get("app") or microapps[0]["slug"]
        active_microapp = next(
            (microapp for microapp in microapps if microapp["slug"] == active_slug), microapps[0]
        )

        today = timezone.localdate()
        tomorrow = today + timedelta(days=1)
        end_week = today + timedelta(days=7)

        life_areas = models.AreaOfLife.objects.filter(owner=user).order_by("name")
        has_existing_data = (
            life_areas.exists()
            or models.Task.objects.filter(owner=user).exists()
            or models.Habit.objects.filter(area__owner=user).exists()
            or models.Reflection.objects.filter(owner=user).exists()
        )
        open_settings = self.request.GET.get("mode") == "settings"

        dashboard_url = reverse("personal_management:dashboard")
        sidebar_items = []
        for microapp in microapps:
            href = dashboard_url if microapp["slug"] == "today" else f"{dashboard_url}?app={microapp['slug']}"
            sidebar_items.append(
                {
                    "slug": microapp["slug"],
                    "label": microapp["label"],
                    "tagline": microapp.get("tagline"),
                    "href": href,
                    "active": microapp["slug"] == active_microapp["slug"],
                }
            )

        tasks_today = models.Task.objects.filter(
            owner=user, due_date=today, completed=False
        ).order_by("due_date", "title")
        tasks_overdue = models.Task.objects.filter(
            owner=user, completed=False, due_date__lt=today
        ).order_by("due_date")
        tasks_upcoming = models.Task.objects.filter(
            owner=user, completed=False, due_date__gte=tomorrow, due_date__lte=end_week
        ).order_by("due_date")
        active_habits = models.Habit.objects.filter(area__owner=user, active=True).order_by("name")
        latest_reflection = (
            models.Reflection.objects.filter(owner=user).order_by("-created_at").first()
        )

        context["microapps"] = microapps
        context["sidebar_items"] = sidebar_items
        context["active_microapp"] = active_microapp["slug"]
        context["active_microapp_label"] = active_microapp["label"]
        context["active_microapp_description"] = active_microapp["description"]
        context["active_microapp_tagline"] = active_microapp.get("tagline", "")
        context["active_microapp_data"] = active_microapp
        context["active_microapp_microcategories"] = active_microapp.get("microcategories", [])
        context["active_microapp_setup_steps"] = active_microapp.get("setup_prompts", [])
        context["show_setup_modal"] = (open_settings or not has_existing_data) and (
            active_microapp["slug"] != "today"
        )
        context["first_time_onboarding"] = (
            not has_existing_data and active_microapp["slug"] != "today"
        )
        context["active_dashboard_template"] = active_microapp.get(
            "dashboard_template", "personal_management/systems/second-brain/dashboard.html"
        )
        context["active_settings_template"] = active_microapp.get(
            "settings_template", "personal_management/systems/second-brain/settings.html"
        )
        context["active_microapp_slug"] = active_microapp["slug"]
        context["tasks"] = models.Task.objects.filter(owner=user, completed=False)[:10]
        context["reflections"] = models.Reflection.objects.filter(owner=user)[:5]
        context["habits"] = models.Habit.objects.filter(area__owner=user, active=True)
        context["life_areas"] = life_areas
        context["today_date"] = today
        context["tasks_today"] = tasks_today
        context["tasks_overdue"] = tasks_overdue
        context["tasks_upcoming"] = tasks_upcoming
        context["active_habits"] = active_habits
        context["latest_reflection"] = latest_reflection
        return context


class HomeView(View):
    template_name = "personal_management/home.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("personal_management:dashboard")
        return render(request, self.template_name)

def logout_view(request):
    logout(request)
    return redirect("personal_management:home")


def today_redirect(request):
    dashboard_url = reverse("personal_management:dashboard")
    return redirect(f"{dashboard_url}?app=today")
