from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (SubjectViewSet, ExamViewSet, NoticeViewSet, ResultViewSet,
                    ClassViewSet, EnrollmentViewSet, ClubViewSet, dashboard)

router = DefaultRouter()
for route, view in [('subjects', SubjectViewSet), ('exams', ExamViewSet), ('notices', NoticeViewSet),
                    ('results', ResultViewSet), ('classes', ClassViewSet),
                    ('enrollments', EnrollmentViewSet), ('clubs', ClubViewSet)]:
    router.register(route, view)

# Preserve old API paths while the frontend uses the consistent resource routes.
urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('subjects/create/', SubjectViewSet.as_view({'post': 'create'}), name='subject-create'),
    path('subjects/update/<int:pk>/', SubjectViewSet.as_view({'put': 'update', 'patch': 'partial_update'}), name='subject-update'),
    path('subjects/delete/<int:pk>/', SubjectViewSet.as_view({'delete': 'destroy'}), name='subject-delete'),
]
for prefix, view in [('exam', ExamViewSet), ('result', ResultViewSet)]:
    urlpatterns += [
        path(f'{prefix}/create/', view.as_view({'post': 'create'}), name=f'{prefix}-create'),
        path(f'{prefix}/update/<int:pk>/', view.as_view({'put': 'update', 'patch': 'partial_update'}), name=f'{prefix}-update'),
        path(f'{prefix}/delete/<int:pk>/', view.as_view({'delete': 'destroy'}), name=f'{prefix}-delete'),
        path(f'{prefix}/<int:pk>/', view.as_view({'get': 'retrieve'}), name=f'{prefix}-retrieve'),
    ]
urlpatterns += router.urls
