# IMPROVE Personal Growth OS

IMPROVE is an opinionated Django starter kit that unifies proven personal growth and management practices into a single product. It combines strategic planning, habit tracking, task execution, and reflective journaling so you can run your life with the same rigor you bring to high-performing teams.

## What's in this starter
- Django project `rebolution` with admin, auth, and base configuration
- Core app `personal_management` with models for areas of life, goals, milestones, habits, tasks, and reflections
- Admin dashboards for every model so you can curate data immediately
- Admin access is locked to superusers so you can keep staff-only views in future
- Public marketing pages plus authenticated dashboard and login flow
- Default Today app summarizing tasks, habits, reflections, and arenas for the current day
- Business OS shell (sidebar + workspace) ready for wiring the eight microapps after login
- Each microapp ships with a dashboard view plus a settings popup for system configuration
- Dedicated template folders per arena so you can expand each microapp independently
- Dark grid aesthetic inspired by modern productivity suites
- Templates and forms structured for rapid iteration

## Quick start
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # create your first account
python manage.py runserver
```

Then visit `http://127.0.0.1:8000/` for the public home page or `http://127.0.0.1:8000/admin/` to seed your personal operating system.

## Project structure
```
Improve/
├─ manage.py
├─ rebolution/                # Django project settings, URLs, WSGI/ASGI entrypoints
├─ personal_management/       # Core app with models, admin, views, and templates
│  └─ templates/personal_management/systems/  # Per-arena dashboards & setup popups
├─ templates/registration/    # Built-in auth templates (login, password flows)
├─ static/                    # Global static assets placeholder
└─ requirements.txt
```

## Next ideas
1. Build user-facing CRUD views for goals, habits, and reflections with inline forms.
2. Add analytics (progress charts, streaks, habit completion heatmaps).
3. Layer in accountability features such as weekly review prompts or coach check-ins.
4. Integrate external data sources (calendar, wearables, task managers) via Celery.

Let me know what module you want to tackle next and we can continue shaping the product.
