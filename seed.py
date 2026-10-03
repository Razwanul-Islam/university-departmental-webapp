import argparse
import os
from datetime import timedelta

import django
from django.db import transaction
from django.utils import timezone


@transaction.atomic
def seed_demo(password):
    from django.contrib.auth import get_user_model

    from academic.models import Class, Club, Enrollment, Exam, Notice, Result, Subject

    User = get_user_model()
    people = []
    for email, name, role in [
        ("head@demo.edu", "Dr. Ishak Ahmed", "H"),
        ("teacher@demo.edu", "Farhana Rahman", "T"),
        ("teacher2@demo.edu", "Tanvir Hasan", "T"),
        ("student@demo.edu", "Ayesha Karim", "S"),
        ("student2@demo.edu", "Rafi Islam", "S"),
        ("student3@demo.edu", "Nadia Akter", "S"),
    ]:
        person, created = User.objects.get_or_create(
            email=email, defaults={"name": name, "user_type": role}
        )
        if created:
            person.set_password(password)
            person.save()
        people.append(person)
    head, teacher, teacher2, student, student2, student3 = people
    courses = []
    for name, code, lecturer in [
        ("Data Structures & Algorithms", "CSE 2201", teacher),
        ("Database Management Systems", "CSE 2203", teacher),
        ("Discrete Mathematics", "CSE 2205", teacher2),
    ]:
        course, _ = Subject.objects.get_or_create(
            subject_code=code,
            defaults={"subject_name": name, "teacher_id": lecturer},
        )
        courses.append(course)
    cohort, _ = Class.objects.get_or_create(
        class_name="Computer Science · Semester 3",
        defaults={
            "semester": 3,
            "session": timezone.localdate().year,
            "academic_year": str(timezone.localdate().year),
            "class_teacher": teacher,
        },
    )
    cohort.subjects.add(*courses)
    for person in [student, student2, student3]:
        Enrollment.objects.get_or_create(student=person, academic_class=cohort)
    for i, course in enumerate(courses):
        Exam.objects.get_or_create(
            exam_name="Midterm · " + course.subject_code,
            subject_id=course,
            defaults={"exam_date": timezone.localdate() + timedelta(days=7 + i * 3)},
        )
    completed, _ = Exam.objects.get_or_create(
        exam_name="Class assessment 01",
        subject_id=courses[0],
        defaults={"exam_date": timezone.localdate() - timedelta(days=5)},
    )
    for person, marks in [(student, 87), (student2, 76), (student3, 69)]:
        Result.objects.get_or_create(
            user_id=person,
            exam_id=completed,
            defaults={"subject_id": courses[0], "marks": marks},
        )
    for title, description, course in [
        (
            "Welcome to your departmental workspace",
            "Your subjects, exam schedules, results, and campus clubs now have a home. Explore the portal and keep your profile up to date.",
            None,
        ),
        (
            "Midterm examination schedule published",
            "The upcoming midterm dates are available on the Exams page. Check your subjects and start planning your revision.",
            None,
        ),
        (
            "Database lab preparation",
            "Please review relational models and SQL joins before the next laboratory session. Bring your own notes and questions.",
            courses[1],
        ),
    ]:
        Notice.objects.get_or_create(
            notice_title=title,
            defaults={
                "notice_description": description,
                "subject_id": course,
                "user_id": head,
            },
        )
    for name, description in [
        (
            "Programming Club",
            "Build, debug, and learn together. Weekly problem-solving sessions and student-led projects.",
        ),
        (
            "Debate Society",
            "Find your voice. Join thoughtful conversations, friendly debates, and interdepartmental competitions.",
        ),
        (
            "Photography Circle",
            "See campus through a new lens. Photo walks, creative workshops, and stories worth sharing.",
        ),
    ]:
        Club.objects.get_or_create(
            club_name=name,
            defaults={"club_description": description, "user_id": teacher},
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add repeatable local demo data.")
    parser.add_argument("--password", default="CampusDemo!2026")
    args = parser.parse_args()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "management.settings")
    django.setup()
    seed_demo(args.password)
    print("Demo ready: head@demo.edu, teacher@demo.edu, student@demo.edu")
