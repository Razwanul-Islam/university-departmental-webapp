from rest_framework import serializers
from .models import notice,subject
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