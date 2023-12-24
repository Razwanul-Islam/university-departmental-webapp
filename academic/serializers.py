from rest_framework import serializers
from .models import notice

class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = notice
        fields = ['notice_id', 'user_id', 'notice_title', 'notice_description', 'notice_date', 'subject_id']
