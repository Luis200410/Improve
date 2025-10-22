from django.urls import path

from . import views

app_name = "personal_management"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("today/", views.today_redirect, name="today"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
]
