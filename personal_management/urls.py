from django.urls import path

from . import views

app_name = "personal_management"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("today/", views.today_redirect, name="today"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("api/pomodoro/summary/", views.pomodoro_summary, name="pomodoro_summary"),
    path("api/pomodoro/start/", views.pomodoro_start, name="pomodoro_start"),
    path("api/pomodoro/complete/", views.pomodoro_complete, name="pomodoro_complete"),
    path("api/pomodoro/cancel/", views.pomodoro_cancel, name="pomodoro_cancel"),
]
