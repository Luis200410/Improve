from datetime import timedelta

import json

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.decorators.http import require_GET, require_POST
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

    @classmethod
    def build_dashboard_context(cls, request):
        user = request.user
        microapps = cls.default_microapps

        active_slug = request.GET.get("app") or microapps[0]["slug"]
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
        open_settings = request.GET.get("mode") == "settings"

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

        body_view = "overview"
        body_context = {
            "body_view": body_view,
            "body_today_sessions": [],
            "body_today_exercises": [],
            "body_today_meals": [],
            "body_next_session": None,
            "body_exercise_count": 0,
            "body_meal_count": 0,
            "body_session_count": 0,
            "body_exercises_page": None,
            "body_exercises_pagination": [],
            "body_meals_page": None,
            "body_meals_pagination": [],
            "body_sessions_full": None,
        }

        productivity_view = "overview"
        productivity_context = {
            "productivity_view": productivity_view,
            "pomodoro_defaults": {
                "focus_minutes": 25,
                "short_break_minutes": 5,
                "long_break_minutes": 15,
                "cycles_before_long_break": 4,
            },
            "weekly_reviews": [],
            "monthly_reviews": [],
            "big_four_goals": [],
            "productivity_habits": [],
            "backward_engineering_samples": [],
            "parkinson_prompts": [
                "What is the absolute latest this can be delivered?",
                "How can I compress the scope without sacrificing the outcome?",
                "What support do I need to hit an earlier deadline?",
            ],
        }

        if active_microapp["slug"] == "body":
            body_view = request.GET.get("body_view", "overview")
            exercises_qs = models.Exercise.objects.select_related("category").order_by("name")
            meals_qs = models.Meal.objects.select_related("category").order_by("name")
            sessions_qs = (
                models.WorkoutSession.objects.filter(owner=user)
                .prefetch_related("session_exercises__exercise")
                .order_by("-scheduled_for", "-updated_at")
            )

            sessions_list = list(sessions_qs)
            today_sessions = [s for s in sessions_list if s.scheduled_for == today]
            next_session = None
            if not today_sessions:
                next_session = next(
                    (
                        s
                        for s in sessions_list
                        if s.scheduled_for and s.scheduled_for >= today
                    ),
                    None,
                )
                if next_session is None and sessions_list:
                    next_session = sessions_list[0]

            seen_exercise_ids: set[int] = set()
            today_exercises: list[models.Exercise] = []
            for session in today_sessions:
                for section in session.session_exercises.all():
                    if section.exercise_id not in seen_exercise_ids:
                        seen_exercise_ids.add(section.exercise_id)
                        today_exercises.append(section.exercise)

            meals_for_today: list[models.Meal] = []
            if today_sessions:
                meals_for_today = list(meals_qs[:3])
            else:
                meals_for_today = list(meals_qs[:3])

            body_context.update(
                {
                    "body_view": body_view,
                    "body_today_sessions": today_sessions,
                    "body_today_exercises": today_exercises,
                    "body_today_meals": meals_for_today,
                    "body_next_session": next_session,
                    "body_exercise_count": exercises_qs.count(),
                    "body_meal_count": meals_qs.count(),
                    "body_session_count": len(sessions_list),
                }
            )

            if body_view == "exercises":
                page_number = request.GET.get("page", 1)
                paginator = Paginator(exercises_qs, 50)
                page_obj = paginator.get_page(page_number)
                body_context["body_exercises_page"] = page_obj
                body_context["body_exercises_pagination"] = DashboardView.pagination_window(page_obj)
            elif body_view == "meals":
                page_number = request.GET.get("page", 1)
                paginator = Paginator(meals_qs, 50)
                page_obj = paginator.get_page(page_number)
                body_context["body_meals_page"] = page_obj
                body_context["body_meals_pagination"] = DashboardView.pagination_window(page_obj)
            elif body_view == "sessions":
                body_context["body_sessions_full"] = sessions_list

        if active_microapp["slug"] == "productivity":
            productivity_view = request.GET.get("productivity_view", "overview")
            weekly_reviews = list(
                models.Reflection.objects.filter(owner=user, cadence=models.Reflection.WEEKLY)
                .order_by("-created_at")
            )
            monthly_reviews = list(
                models.Reflection.objects.filter(owner=user, cadence=models.Reflection.MONTHLY)
                .order_by("-created_at")
            )
            big_goals = list(
                models.Goal.objects.filter(area__owner=user)
                .order_by("target_date", "-start_date")[:4]
            )
            productivity_context.update(
                {
                    "productivity_view": productivity_view,
                    "weekly_reviews": weekly_reviews,
                    "monthly_reviews": monthly_reviews,
                    "big_four_goals": big_goals,
                    "productivity_habits": list(
                        models.Habit.objects.filter(area__owner=user)
                        .order_by("name")[:50]
                    ),
                    "backward_engineering_samples": [
                        {
                            "goal": goal.title,
                            "target_date": goal.target_date,
                            "start_date": goal.start_date,
                        }
                        for goal in big_goals
                    ],
                }
            )

        context = {
            "microapps": microapps,
            "sidebar_items": sidebar_items,
            "active_microapp": active_microapp["slug"],
            "active_microapp_label": active_microapp["label"],
            "active_microapp_description": active_microapp["description"],
            "active_microapp_tagline": active_microapp.get("tagline", ""),
            "active_microapp_data": active_microapp,
            "active_microapp_microcategories": active_microapp.get("microcategories", []),
            "active_microapp_setup_steps": active_microapp.get("setup_prompts", []),
            "show_setup_modal": (open_settings or not has_existing_data)
            and (active_microapp["slug"] != "today"),
            "first_time_onboarding": not has_existing_data and active_microapp["slug"] != "today",
            "active_dashboard_template": active_microapp.get(
                "dashboard_template", "personal_management/systems/second-brain/dashboard.html"
            ),
            "active_settings_template": active_microapp.get(
                "settings_template", "personal_management/systems/second-brain/settings.html"
            ),
            "active_microapp_slug": active_microapp["slug"],
            "tasks": models.Task.objects.filter(owner=user, completed=False)[:10],
            "reflections": models.Reflection.objects.filter(owner=user)[:5],
            "habits": models.Habit.objects.filter(area__owner=user, active=True),
            "life_areas": life_areas,
            "today_date": today,
            "tasks_today": tasks_today,
            "tasks_overdue": tasks_overdue,
            "tasks_upcoming": tasks_upcoming,
            "active_habits": active_habits,
            "latest_reflection": latest_reflection,
        }

        context.update(body_context)
        context.update(productivity_context)
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.build_dashboard_context(self.request))
        return context

    @staticmethod
    def pagination_window(page_obj, *, boundary=2, radius=1):
        pages = []
        total = page_obj.paginator.num_pages
        current = page_obj.number
        last = None
        for number in range(1, total + 1):
            in_boundary = number <= boundary or number > total - boundary
            near_current = abs(number - current) <= radius
            if in_boundary or near_current:
                pages.append(number)
                last = number
            else:
                if last is not None:
                    pages.append(None)
                    last = None
        return pages


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


def get_pomodoro_profile(user):
    profile, _ = models.PomodoroProfile.objects.get_or_create(user=user)
    return profile


def _forest_payload(profile: models.PomodoroProfile) -> list[dict]:
    trees = []
    for tree in profile.forest.order_by("-planted_at")[:18]:
        trees.append(
            {
                "tree_type": tree.tree_type,
                "focus_minutes": tree.focus_minutes,
                "planted_at": timezone.localtime(tree.planted_at).strftime("%b %d"),
            }
        )
    return trees


def _pomodoro_summary_payload(profile: models.PomodoroProfile) -> dict:
    return {
        "profile": profile.to_summary(),
        "forest": _forest_payload(profile),
    }


@login_required
@require_GET
def pomodoro_summary(request):
    profile = get_pomodoro_profile(request.user)
    payload = _pomodoro_summary_payload(profile)
    active_session = (
        profile.sessions.filter(status=models.PomodoroSession.RUNNING).order_by("-started_at").first()
    )
    if active_session:
        payload["active_session"] = {
            "id": active_session.id,
            "focus_minutes": active_session.focus_minutes,
            "current_cycle": active_session.current_cycle,
            "started_at": active_session.started_at.isoformat(),
            "elapsed_seconds": active_session.elapsed_seconds,
        }
    else:
        payload["active_session"] = None
    return JsonResponse(payload)


@login_required
@require_POST
def pomodoro_start(request):
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON payload")

    focus_minutes = max(1, int(data.get("focus_minutes", 25)))
    short_break = max(1, int(data.get("short_break_minutes", 5)))
    long_break = max(1, int(data.get("long_break_minutes", 15)))
    cycles = max(1, int(data.get("cycles_before_long_break", 4)))

    profile = get_pomodoro_profile(request.user)
    profile.sessions.filter(status=models.PomodoroSession.RUNNING).update(status=models.PomodoroSession.CANCELLED)

    session = models.PomodoroSession.objects.create(
        profile=profile,
        focus_minutes=focus_minutes,
        short_break_minutes=short_break,
        long_break_minutes=long_break,
        cycles_before_long_break=cycles,
    )

    return JsonResponse({"session": session.to_dict()})


@login_required
@require_POST
def pomodoro_complete(request):
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON payload")

    session_id = data.get("session_id")
    if not session_id:
        return HttpResponseBadRequest("session_id is required")

    session = get_object_or_404(
        models.PomodoroSession,
        pk=session_id,
        profile__user=request.user,
    )

    if session.status != models.PomodoroSession.RUNNING:
        return HttpResponseBadRequest("Session is not running")

    completed_minutes = max(1, int(data.get("completed_minutes", session.focus_minutes)))
    profile = session.profile
    xp_gained, tree_type = profile.add_focus_minutes(completed_minutes)
    session.status = models.PomodoroSession.COMPLETED
    session.completed_focus_minutes = completed_minutes
    session.tree_type = tree_type
    session.save(update_fields=["status", "completed_focus_minutes", "tree_type", "updated_at"])
    models.PomodoroTree.objects.create(
        profile=profile,
        tree_type=tree_type,
        focus_minutes=completed_minutes,
    )
    payload = _pomodoro_summary_payload(profile)
    payload["xp_gained"] = xp_gained
    payload["tree_type"] = tree_type
    return JsonResponse({"summary": payload})


@login_required
@require_POST
def pomodoro_cancel(request):
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON payload")

    session_id = data.get("session_id")
    if not session_id:
        return HttpResponseBadRequest("session_id is required")

    session = get_object_or_404(
        models.PomodoroSession,
        pk=session_id,
        profile__user=request.user,
    )
    session.status = models.PomodoroSession.CANCELLED
    session.save(update_fields=["status", "updated_at"])
    return JsonResponse({"ok": True})
