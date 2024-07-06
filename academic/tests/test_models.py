from django.test import TestCase
from  academic.models import subject,exam

class TestSubject(TestCase):

    def test_subject(self):
        subject_id=101
        subject_name="CSE"
        subject_code="CSE-101"
        teacher_id=1

        #user=subject.objects.create_object(subject_id=subject_id,subject_name=subject_name,subject_code=subject_code,teacher_id=teacher_id)
        self.assertEqual(subject.subject_id,subject_id)
        self.assertEqual(subject.subject_name,subject_name)
        self.assertEqual(subject.subject_code,subject_code)
        self.assertEqual(subject.teacher_id,teacher_id)