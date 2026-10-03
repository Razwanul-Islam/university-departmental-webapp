from django.db.models import Avg, Q
from django.utils import timezone
from rest_framework import filters, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Class, Club, Enrollment, Exam, Notice, Result, Subject
from .permissions import IsHeadAndTeacherUser, IsHeadUser, is_head
from .serializers import (
    ClassSerializer,
    ClubSerializer,
    EnrollmentSerializer,
    ExamSerializer,
    NoticeSerializer,
    ResultSerializer,
    SubjectSerializer,
)


def visible_subjects(user):
    courses = Subject.objects.select_related("teacher_id")
    if is_head(user):
        return courses
    if user.user_type == "T":
        return courses.filter(teacher_id=user)
    return courses.filter(classes__enrollments__student=user).distinct()


class AcademicViewSet(viewsets.ModelViewSet):
    permission_classes = [IsHeadUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering = ["pk"]
    ordering_fields = ["pk"]
    filter_fields = []

    def get_queryset(self):
        queryset = super().get_queryset()
        for field in self.filter_fields:
            value = self.request.query_params.get(field)
            if value:
                if not value.isdigit():
                    raise ValidationError({field: "Use a numeric ID."})
                queryset = queryset.filter(**{field: value})
        return queryset


class SubjectViewSet(AcademicViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    search_fields = ["subject_name", "subject_code", "teacher_id__name"]
    filter_fields = ["teacher_id"]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(pk__in=visible_subjects(self.request.user).values("pk"))
            .select_related("teacher_id")
        )


class ExamViewSet(AcademicViewSet):
    queryset = Exam.objects.select_related("subject_id")
    serializer_class = ExamSerializer
    search_fields = ["exam_name", "subject_id__subject_name"]
    ordering_fields = ["pk", "exam_date"]
    filter_fields = ["subject_id"]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(subject_id__in=visible_subjects(self.request.user))
        )


class NoticeViewSet(AcademicViewSet):
    queryset = Notice.objects.select_related("user_id", "subject_id")
    serializer_class = NoticeSerializer
    search_fields = ["notice_title", "notice_description"]
    ordering = ["-notice_date", "-pk"]
    ordering_fields = ["pk", "notice_date"]
    filter_fields = ["subject_id"]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                Q(subject_id__isnull=True)
                | Q(subject_id__in=visible_subjects(self.request.user))
            )
        )

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)


class ClassViewSet(AcademicViewSet):
    queryset = Class.objects.select_related("class_teacher").prefetch_related(
        "subjects", "enrollments"
    )
    serializer_class = ClassSerializer
    search_fields = ["class_name", "academic_year"]
    filter_fields = ["class_teacher"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if is_head(user):
            return queryset
        if user.user_type == "T":
            return queryset.filter(
                Q(class_teacher=user) | Q(subjects__teacher_id=user)
            ).distinct()
        return queryset.filter(enrollments__student=user)


class EnrollmentViewSet(AcademicViewSet):
    queryset = Enrollment.objects.select_related("student", "academic_class")
    serializer_class = EnrollmentSerializer
    search_fields = ["student__name", "student__email", "academic_class__class_name"]
    filter_fields = ["student", "academic_class"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if is_head(user):
            return queryset
        if user.user_type == "T":
            return queryset.filter(academic_class__subjects__teacher_id=user).distinct()
        return queryset.filter(student=user)


class ResultViewSet(AcademicViewSet):
    queryset = Result.objects.select_related("user_id", "subject_id", "exam_id")
    serializer_class = ResultSerializer
    permission_classes = [IsHeadAndTeacherUser]
    search_fields = ["user_id__name", "subject_id__subject_name", "exam_id__exam_name"]
    filter_fields = ["user_id", "subject_id", "exam_id"]
    ordering_fields = ["pk", "marks"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if is_head(user):
            return queryset
        if user.user_type == "T":
            return queryset.filter(subject_id__teacher_id=user)
        return queryset.filter(user_id=user)


class ClubViewSet(AcademicViewSet):
    queryset = Club.objects.select_related("user_id").prefetch_related("members")
    serializer_class = ClubSerializer
    search_fields = ["club_name", "club_description"]

    @action(
        detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated]
    )
    def membership(self, request, pk=None):
        item = self.get_object()
        if request.method == "POST":
            item.members.add(request.user)
        else:
            item.members.remove(request.user)
        return Response(self.get_serializer(item).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard(request):
    user = request.user
    courses = visible_subjects(user)
    assessments = Exam.objects.filter(subject_id__in=courses)
    announcements = Notice.objects.filter(
        Q(subject_id__isnull=True) | Q(subject_id__in=courses)
    ).select_related("user_id", "subject_id")
    scores = Result.objects.all()
    if not is_head(user):
        scores = (
            scores.filter(subject_id__teacher_id=user)
            if user.user_type == "T"
            else scores.filter(user_id=user)
        )
    upcoming = (
        assessments.filter(exam_date__gte=timezone.localdate())
        .select_related("subject_id")
        .order_by("exam_date", "pk")[:5]
    )
    context = {"request": request}
    return Response(
        {
            "subjects": courses.count(),
            "upcoming_exams": assessments.filter(
                exam_date__gte=timezone.localdate()
            ).count(),
            "results": scores.count(),
            "average_marks": scores.aggregate(value=Avg("marks"))["value"],
            "notices": announcements.count(),
            "clubs": Club.objects.count(),
            "recent_notices": NoticeSerializer(
                announcements.order_by("-notice_date", "-pk")[:4],
                many=True,
                context=context,
            ).data,
            "exam_schedule": ExamSerializer(upcoming, many=True, context=context).data,
        }
    )
