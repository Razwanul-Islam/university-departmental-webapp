# import pytest
# from datetime import date
# from django.contrib.auth import get_user_model
# from academic.models import notice, subject  # Import your models from academic
# from academic.serializers import NoticeSerializer,SubjectSerializer,

# @pytest.mark.django_db
# class TestNoticeSerializer:
    
#     def test_notice_serializer(self):
#         user = get_user_model().objects.create(email='test@example.com', name='Test User', password='testpassword')
#         subject_obj = subject.objects.create(subject_name='Mathematics', subject_code='MATH101', teacher_id=user)
        
#         notice_data = {
#             'notice_id': 1,
#             'user_id': user.id,
#             'notice_title': 'Important Notice',
#             'notice_description': 'This is a notice description.',
#             'notice_date': date.today(),
#             'subject_id': subject_obj.pk  # Accessing the primary key of subject_obj
#         }
        
#         serializer = NoticeSerializer(data=notice_data)
#         assert serializer.is_valid()
        
#         instance = serializer.save()
#         assert instance.notice_id == 1
#         assert instance.user_id.id == user.id
#         assert instance.notice_title == 'Important Notice'
#         assert instance.notice_description == 'This is a notice description.'
#         assert instance.notice_date == date.today()
#         assert instance.subject_id.pk == subject_obj.pk  # Ensure subject_id primary keys match




# Test User Serializatin with empty instance
# import pytest
# from django.contrib.auth import get_user_model
# from academic.serializers import UserSerializer  # Import your UserSerializer

# @pytest.mark.django_db
# class TestUserSerializer:
    
#     def test_user_serializer_with_empty_instance(self):
#         # Create an empty instance or provide an empty dictionary
#         serializer = UserSerializer(data={})
        
#         assert not serializer.is_valid(), serializer.errors



# Test Subject Serializer
import pytest
from django.contrib.auth import get_user_model
from academic.models import subject
from academic.serializers import SubjectSerializer

@pytest.mark.django_db
class TestSubjectSerializer:
    
    def test_subject_serializer(self):
        user = get_user_model().objects.create(email='teacher@example.com', name='Teacher', password='testpassword')
        
        subject_data = {
            'subject_id': 1,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'teacher_id': user.id
        }
        
        serializer = SubjectSerializer(data=subject_data)
        assert serializer.is_valid()
        
        instance = serializer.save()
        assert instance.subject_id == 1
        assert instance.subject_name == 'Mathematics'
        assert instance.subject_code == 'MATH101'
        assert instance.teacher_id.id == user.id
        
    def test_subject_serializer_invalid_data(self):
        invalid_subject_data = {
            'subject_id': 1,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'teacher_id': 999  # Invalid teacher ID
        }
        
        serializer = SubjectSerializer(data=invalid_subject_data)
        assert not serializer.is_valid()
