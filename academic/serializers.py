from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import subject, exam, notice, result, club, Class, Enrollment
from .permissions import is_head

User = get_user_model()


def require_teacher(user):
    if user.user_type not in ('H', 'T') or not user.is_active:
        raise serializers.ValidationError('Choose an active teacher or head.')
    return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email']


class SubjectSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher_id.name', read_only=True)

    class Meta:
        model = subject
        fields = ['subject_id', 'subject_name', 'subject_code', 'teacher_id', 'teacher_name']

    validate_teacher_id = staticmethod(require_teacher)


class ExamSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject_id.subject_name', read_only=True)

    class Meta:
        model = exam
        fields = ['exam_id', 'exam_name', 'exam_date', 'subject_id', 'subject_name']

    def validate(self, attrs):
        if self.instance and attrs.get('subject_id', self.instance.subject_id) != self.instance.subject_id and self.instance.result_set.exists():
            raise serializers.ValidationError('An exam with results cannot change subjects.')
        return attrs


class NoticeSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='user_id.name', read_only=True)
    subject_name = serializers.CharField(source='subject_id.subject_name', read_only=True, default=None)

    class Meta:
        model = notice
        fields = ['notice_id', 'user_id', 'author_name', 'notice_title', 'notice_description', 'notice_date', 'subject_id', 'subject_name']
        read_only_fields = ['user_id', 'notice_date']


class ClassSerializer(serializers.ModelSerializer):
    subject_names = serializers.SlugRelatedField(source='subjects', slug_field='subject_name', many=True, read_only=True)
    teacher_name = serializers.CharField(source='class_teacher.name', read_only=True)
    student_count = serializers.IntegerField(source='enrollments.count', read_only=True)

    class Meta:
        model = Class
        fields = ['class_id', 'class_name', 'semester', 'session', 'academic_year', 'class_teacher', 'teacher_name', 'subjects', 'subject_names', 'student_count']

    validate_class_teacher = staticmethod(require_teacher)

    def validate(self, attrs):
        if self.instance and 'subjects' in attrs:
            removed = self.instance.subjects.exclude(pk__in=[s.pk for s in attrs['subjects']])
            if result.objects.filter(subject_id__in=removed, user_id__enrollments__academic_class=self.instance).exists():
                raise serializers.ValidationError('Subjects with recorded student results cannot be removed.')
        return attrs


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    class_name = serializers.CharField(source='academic_class.class_name', read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'student_name', 'academic_class', 'class_name', 'enrolled_at']
        read_only_fields = ['enrolled_at']

    def validate_student(self, user):
        if user.user_type != 'S' or not user.is_active:
            raise serializers.ValidationError('Choose an active student.')
        return user

    def validate(self, attrs):
        if self.instance and (attrs.get('student', self.instance.student) != self.instance.student or attrs.get('academic_class', self.instance.academic_class) != self.instance.academic_class):
            if result.objects.filter(user_id=self.instance.student, subject_id__classes=self.instance.academic_class).exists():
                raise serializers.ValidationError('This enrollment has results. Preserve it and create a new enrollment.')
        return attrs


class ResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='user_id.name', read_only=True)
    subject_name = serializers.CharField(source='subject_id.subject_name', read_only=True)
    exam_name = serializers.CharField(source='exam_id.exam_name', read_only=True)

    class Meta:
        model = result
        fields = ['result_id', 'user_id', 'student_name', 'subject_id', 'subject_name', 'exam_id', 'exam_name', 'marks', 'grade']
        read_only_fields = ['grade']

    def validate(self, attrs):
        def value(key):
            return attrs.get(key, getattr(self.instance, key, None))
        student, course, assessment = value('user_id'), value('subject_id'), value('exam_id')
        if student.user_type != 'S' or not student.is_active:
            raise serializers.ValidationError({'user_id': 'Choose an active student.'})
        if assessment.subject_id_id != course.pk:
            raise serializers.ValidationError({'exam_id': 'The exam must belong to this subject.'})
        if not Enrollment.objects.filter(student=student, academic_class__subjects=course).exists():
            raise serializers.ValidationError({'user_id': 'The student must be enrolled in a class offering this subject.'})
        request = self.context.get('request')
        if request and not is_head(request.user) and course.teacher_id_id != request.user.pk:
            raise serializers.ValidationError({'subject_id': 'You can only record results for your assigned subjects.'})
        return attrs


class ClubSerializer(serializers.ModelSerializer):
    coordinator_name = serializers.CharField(source='user_id.name', read_only=True)
    member_count = serializers.IntegerField(source='members.count', read_only=True)
    is_member = serializers.SerializerMethodField()

    class Meta:
        model = club
        fields = ['club_id', 'club_name', 'club_description', 'user_id', 'coordinator_name', 'member_count', 'is_member']

    def validate_user_id(self, user):
        if not user.is_active:
            raise serializers.ValidationError('Choose an active coordinator.')
        return user

    def get_is_member(self, obj):
        request = self.context.get('request')
        return bool(request and obj.members.filter(pk=request.user.pk).exists())
