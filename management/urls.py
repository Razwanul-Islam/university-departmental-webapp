from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", lambda request: JsonResponse({"status": "ok"})),
    path("api/user/", include("account.urls")),
    path("api/academic/", include("academic.urls")),
    path("", TemplateView.as_view(template_name="index.html"), name="portal"),
]
