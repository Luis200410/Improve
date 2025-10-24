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
- Exercise and meal libraries plus a workout session builder in the Body arena
- Productivity arena with a backend-backed Pomodoro timer, blocking lists, reviews, habit tracker, and timeboxing tools
- Management command `python manage.py seed_body_library --count 3000 --meal-count 10000` to bulk-generate media-ready exercises and 10,000 diet-specific meals
- Dedicated template folders per arena so you can expand each microapp independently
- Dark grid aesthetic inspired by modern productivity suites
- Templates and forms structured for rapid iteration

## Quick start
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DJANGO_DB_NAME=Improve          # optional if you want to override defaults
export DJANGO_DB_USER=postgres
export DJANGO_DB_PASSWORD=2004
export DJANGO_DB_HOST=localhost
export DJANGO_DB_PORT=5432
python manage.py migrate
python manage.py createsuperuser  # create your first account
python manage.py runserver

# populate the Body libraries with media-ready seed data (optional)
python manage.py seed_body_library --count 3000 --meal-count 10000
```

Then visit `http://127.0.0.1:8000/` for the public home page or `http://127.0.0.1:8000/admin/` to seed your personal operating system.

## Database configuration
- Default connection targets PostgreSQL 17 (as managed by pgAdmin 4) with:
  - database: `Improve`
  - user: `postgres`
  - password: `2004`
  - host: `localhost`
  - port: `5432`
- Override any value by exporting the matching `DJANGO_DB_*` environment variable before running the app.
- After adding or editing models run `python manage.py makemigrations` followed by `python manage.py migrate` to sync schema changes.

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
4. Extend the Body arena with workout builders or meal planning workflows tied to the new libraries.
5. Integrate external data sources (calendar, wearables, task managers) via Celery.

Let me know what module you want to tackle next and we can continue shaping the product.
