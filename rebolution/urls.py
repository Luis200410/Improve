from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("personal_management.urls")),
    path(
        "about/",
        TemplateView.as_view(template_name="personal_management/about.html"),
        name="about",
    ),
]
