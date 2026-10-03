from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ClassViewSet,
    ClubViewSet,
    EnrollmentViewSet,
    ExamViewSet,
    NoticeViewSet,
    ResultViewSet,
    SubjectViewSet,
    dashboard,
)

router = DefaultRouter()
for route, view in [
    ("subjects", SubjectViewSet),
    ("exams", ExamViewSet),
    ("notices", NoticeViewSet),
    ("results", ResultViewSet),
    ("classes", ClassViewSet),
    ("enrollments", EnrollmentViewSet),
    ("clubs", ClubViewSet),
]:
    router.register(route, view)

urlpatterns = [path("dashboard/", dashboard, name="dashboard")] + router.urls
