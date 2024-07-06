from django.test import TestCase
from django.contrib.auth import get_user_model
from academic.models import subject, exam, notice, result, club, Class

class SubjectModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            name='Test User',
            password='testpass123'
        )

        self.subject = subject.objects.create(
            subject_name='Mathematics',
            subject_code='MATH101',
            teacher_id=self.user
        )

    def test_subject_creation(self):
        self.assertEqual(self.subject.subject_name, 'Mathematics')
        self.assertEqual(self.subject.subject_code, 'MATH101')
        self.assertEqual(self.subject.teacher_id, self.user)

    def test_subject_str(self):
        self.assertEqual(str(self.subject), 'Mathematics')

    def test_subject_primary_key(self):
        self.assertIsNotNone(self.subject.subject_id)

    def test_subject_teacher_fk(self):
        self.assertEqual(self.subject.teacher_id.email, 'testuser@example.com')


class ExamModelTest(TestCase):

    def setUp(self):
        self.subject = subject.objects.create(
            subject_name='Mathematics',
            subject_code='MATH101',
            teacher_id=get_user_model().objects.create_user(
                email='teacher@example.com',
                name='Teacher Name',
                password='testpass123'
            )
        )

        self.exam = exam.objects.create(
            exam_name='Midterm Exam',
            exam_date='2024-07-10',  # assuming this is the correct format
            subject_id=self.subject
        )

    def test_exam_creation(self):
        self.assertEqual(self.exam.exam_name, 'Midterm Exam')
        self.assertEqual(self.exam.exam_date, '2024-07-10')
        self.assertEqual(self.exam.subject_id, self.subject)

    def test_exam_str(self):
        self.assertEqual(str(self.exam), 'Midterm Exam')

    def test_exam_primary_key(self):
        self.assertIsNotNone(self.exam.exam_id)

    def test_exam_subject_fk(self):
        self.assertEqual(self.exam.subject_id.subject_name, 'Mathematics')


class NoticeModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='student@example.com',
            name='Student Name',
            password='testpass123'
        )

        self.subject = subject.objects.create(
            subject_name='Mathematics',
            subject_code='MATH101',
            teacher_id=get_user_model().objects.create_user(
                email='teacher@example.com',
                name='Teacher Name',
                password='testpass123'
            )
        )

        self.notice = notice.objects.create(
            user_id=self.user,
            notice_title='Exam Notice',
            notice_description='There will be an exam next week.',
            subject_id=self.subject
        )

    def test_notice_creation(self):
        self.assertEqual(self.notice.notice_title, 'Exam Notice')
        self.assertEqual(self.notice.notice_description, 'There will be an exam next week.')
        self.assertEqual(self.notice.user_id, self.user)
        self.assertEqual(self.notice.subject_id, self.subject)

    def test_notice_str(self):
        self.assertEqual(str(self.notice), 'Exam Notice')

    def test_notice_primary_key(self):
        self.assertIsNotNone(self.notice.notice_id)

    def test_notice_user_fk(self):
        self.assertEqual(self.notice.user_id.email, 'student@example.com')

    def test_notice_subject_fk(self):
        self.assertEqual(self.notice.subject_id.subject_name, 'Mathematics')


class ResultModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='student@example.com',
            name='Student Name',
            password='testpass123'
        )

        self.subject = subject.objects.create(
            subject_name='Mathematics',
            subject_code='MATH101',
            teacher_id=get_user_model().objects.create_user(
                email='teacher@example.com',
                name='Teacher Name',
                password='testpass123'
            )
        )

        self.exam = exam.objects.create(
            exam_name='Midterm Exam',
            exam_date='2024-07-10',
            subject_id=self.subject
        )

        self.result = result.objects.create(
            user_id=self.user,
            subject_id=self.subject,
            exam_id=self.exam,
            marks=85,
            grade='A'
        )

    def test_result_creation(self):
        self.assertEqual(self.result.user_id, self.user)
        self.assertEqual(self.result.subject_id, self.subject)
        self.assertEqual(self.result.exam_id, self.exam)
        self.assertEqual(self.result.marks, 85)
        self.assertEqual(self.result.grade, 'A')

    def test_result_str(self):
        self.assertEqual(str(self.result.result_id), str(self.result.result_id))

    def test_result_primary_key(self):
        self.assertIsNotNone(self.result.result_id)

    def test_result_user_fk(self):
        self.assertEqual(self.result.user_id.email, 'student@example.com')

    def test_result_subject_fk(self):
        self.assertEqual(self.result.subject_id.subject_name, 'Mathematics')

    def test_result_exam_fk(self):
        self.assertEqual(self.result.exam_id.exam_name, 'Midterm Exam')


class ClubModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='clubadmin@example.com',
            name='Club Admin',
            password='testpass123'
        )

        self.club = club.objects.create(
            club_name='Science Club',
            club_description='A club for science enthusiasts.',
            user_id=self.user
        )

    def test_club_creation(self):
        self.assertEqual(self.club.club_name, 'Science Club')
        self.assertEqual(self.club.club_description, 'A club for science enthusiasts.')
        self.assertEqual(self.club.user_id, self.user)

    def test_club_str(self):
        self.assertEqual(str(self.club), 'Science Club')

    def test_club_primary_key(self):
        self.assertIsNotNone(self.club.club_id)

    def test_club_user_fk(self):
        self.assertEqual(self.club.user_id.email, 'clubadmin@example.com')


class ClassModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='classteacher@example.com',
            name='Class Teacher',
            password='testpass123'
        )

        self.class_instance = Class.objects.create(
            class_name='Physics Class',
            semester=2,
            session=2024,
            academic_year='2023-2024',
            class_teacher=self.user
        )

    def test_class_creation(self):
        self.assertEqual(self.class_instance.class_name, 'Physics Class')
        self.assertEqual(self.class_instance.semester, 2)
        self.assertEqual(self.class_instance.session, 2024)
        self.assertEqual(self.class_instance.academic_year, '2023-2024')
        self.assertEqual(self.class_instance.class_teacher, self.user)

    def test_class_str(self):
        self.assertEqual(str(self.class_instance), 'Physics Class')

    def test_class_primary_key(self):
        self.assertIsNotNone(self.class_instance.class_id)

    def test_class_teacher_fk(self):
        self.assertEqual(self.class_instance.class_teacher.email, 'classteacher@example.com')
