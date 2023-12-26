from rest_framework import serializers
from .models import notice, exam,subject,result
from django.contrib.auth import get_user_model


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = notice
        fields = ['notice_id', 'user_id', 'notice_title', 'notice_description', 'notice_date', 'subject_id']




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id','name','email']



class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = subject
        fields = ['subject_id', 'subject_name', 'subject_code', 'teacher_id']
        


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = exam
        fields = ['exam_id', 'exam_name', 'exam_date', 'subject_id']
        
        
        



class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = result
        fields = ['result_id', 'user_id', 'subject_id', 'exam_id', 'marks', 'grade']

