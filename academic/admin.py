from django.contrib import admin

from .models import Class, Club, Enrollment, Exam, Notice, Result, Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("subject_id", "subject_name", "subject_code", "teacher_id")


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("exam_id", "exam_name", "exam_date", "subject_id")


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = (
        "notice_id",
        "user_id",
        "notice_title",
        "notice_description",
        "notice_date",
        "subject_id",
    )


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("result_id", "user_id", "subject_id", "exam_id", "marks", "grade")


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("club_id", "club_name", "club_description", "user_id")


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = (
        "class_id",
        "class_name",
        "semester",
        "session",
        "academic_year",
        "class_teacher",
    )


admin.site.register(Enrollment)
