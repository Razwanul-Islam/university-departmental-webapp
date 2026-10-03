from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

# Keep the original model/table names to preserve existing data and migrations.
class subject(models.Model):
    subject_id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=64)
    subject_code = models.CharField(max_length=15)
    teacher_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def __str__(self):
        return self.subject_name


class exam(models.Model):
    exam_id = models.AutoField(primary_key=True)
    exam_name = models.CharField(max_length=64)
    exam_date = models.DateField()
    subject_id = models.ForeignKey(subject, on_delete=models.PROTECT)

    def __str__(self):
        return self.exam_name


class notice(models.Model):
    notice_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    notice_title = models.CharField(max_length=64)
    notice_description = models.TextField()
    notice_date = models.DateField(auto_now=True)
    subject_id = models.ForeignKey(subject, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.notice_title


def grade_for(marks):
    for minimum, grade in [(80, 'A+'), (75, 'A'), (70, 'A-'), (65, 'B+'),
                           (60, 'B'), (55, 'B-'), (50, 'C+'), (45, 'C'), (40, 'D')]:
        if marks >= minimum:
            return grade
    return 'F'


class result(models.Model):
    result_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    subject_id = models.ForeignKey(subject, on_delete=models.PROTECT)
    exam_id = models.ForeignKey(exam, on_delete=models.PROTECT)
    marks = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    grade = models.CharField(max_length=2, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'exam_id'], name='one_result_per_student_exam'),
            models.CheckConstraint(condition=models.Q(marks__gte=0, marks__lte=100), name='marks_between_0_100'),
        ]

    def save(self, *args, **kwargs):
        self.grade = grade_for(self.marks)
        if kwargs.get('update_fields') is not None:
            kwargs['update_fields'] = set(kwargs['update_fields']) | {'grade'}
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user_id.name}: {self.marks} ({self.grade})'


class club(models.Model):
    club_id = models.AutoField(primary_key=True)
    club_name = models.CharField(max_length=64)
    club_description = models.TextField()
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='clubs')

    def __str__(self):
        return self.club_name


class Class(models.Model):
    class_id = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=64)
    semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    session = models.IntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2100)])
    academic_year = models.CharField(max_length=10)
    class_teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    subjects = models.ManyToManyField(subject, blank=True, related_name='classes')

    def __str__(self):
        return self.class_name


class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='enrollments')
    academic_class = models.ForeignKey(Class, on_delete=models.PROTECT, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['student', 'academic_class'], name='unique_class_enrollment')]

    def __str__(self):
        return f'{self.student.name} / {self.academic_class.class_name}'
