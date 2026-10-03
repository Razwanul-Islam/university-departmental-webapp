import pytest
from rest_framework.test import APIClient

from academic.models import (
    Class,
    Club,
    Enrollment,
    Exam,
    Notice,
    Result,
    Subject,
)
from account.models import User

pytestmark = pytest.mark.django_db
PASSWORD = "AstrongCampus!4628"


@pytest.fixture
def setup(settings):
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
    users = [
        User.objects.create_user(
            f"{role.lower()}{i}@example.edu", f"Person {i}", PASSWORD, user_type=role
        )
        for i, role in enumerate(["H", "T", "T", "S", "S"])
    ]
    head, teacher, other_teacher, student, other_student = users
    course = Subject.objects.create(
        subject_name="Algorithms", subject_code="CSE201", teacher_id=teacher
    )
    other_course = Subject.objects.create(
        subject_name="Networks", subject_code="CSE301", teacher_id=other_teacher
    )
    cohort = Class.objects.create(
        class_name="Year 2",
        semester=3,
        session=2026,
        academic_year="2026",
        class_teacher=teacher,
    )
    cohort.subjects.add(course)
    enrollment = Enrollment.objects.create(student=student, academic_class=cohort)
    assessment = Exam.objects.create(
        exam_name="Midterm", exam_date="2026-11-10", subject_id=course
    )
    return dict(
        zip(["head", "teacher", "other_teacher", "student", "other_student"], users),
        course=course,
        other_course=other_course,
        cohort=cohort,
        enrollment=enrollment,
        assessment=assessment,
    )


def client(user=None):
    api = APIClient()
    if user:
        api.force_authenticate(user)
    return api


def payload(data, **updates):
    return dict(
        user_id=data["student"].pk,
        subject_id=data["course"].pk,
        exam_id=data["assessment"].pk,
        marks=85,
        **updates,
    )


def test_complete_head_teacher_student_workflow(setup):
    head = client(setup["head"])
    course = head.post(
        "/api/academic/subjects/",
        {
            "subject_name": "Databases",
            "subject_code": "CSE202",
            "teacher_id": setup["teacher"].pk,
        },
    )
    assert course.status_code == 201
    cohort = head.post(
        "/api/academic/classes/",
        {
            "class_name": "New cohort",
            "semester": 4,
            "session": 2026,
            "academic_year": "2026",
            "class_teacher": setup["teacher"].pk,
            "subjects": [course.data["subject_id"]],
        },
        format="json",
    )
    assert cohort.status_code == 201
    enrollment = head.post(
        "/api/academic/enrollments/",
        {"student": setup["student"].pk, "academic_class": cohort.data["class_id"]},
    )
    assert enrollment.status_code == 201
    assessment = head.post(
        "/api/academic/exams/",
        {
            "exam_name": "Final",
            "exam_date": "2026-12-01",
            "subject_id": course.data["subject_id"],
        },
    )
    assert assessment.status_code == 201
    teacher = client(setup["teacher"])
    created = teacher.post(
        "/api/academic/results/",
        {
            "user_id": setup["student"].pk,
            "subject_id": course.data["subject_id"],
            "exam_id": assessment.data["exam_id"],
            "marks": 87,
            "grade": "F",
        },
    )
    assert created.status_code == 201 and created.data["grade"] == "A+"
    updated = teacher.patch(
        f"/api/academic/results/{created.data['result_id']}/", {"marks": 74}
    )
    assert updated.status_code == 200 and updated.data["grade"] == "A-"
    student = client(setup["student"])
    assert student.get("/api/academic/results/").data["count"] == 1
    assert student.get("/api/academic/dashboard/").data["subjects"] == 2
    assert (
        client(setup["other_student"])
        .get(f"/api/academic/results/{created.data['result_id']}/")
        .status_code
        == 404
    )


@pytest.mark.parametrize(
    "resource",
    ["subjects", "exams", "notices", "classes", "enrollments", "results", "clubs"],
)
def test_anonymous_access_is_denied(resource):
    assert client().get(f"/api/academic/{resource}/").status_code == 401


@pytest.mark.parametrize(
    "resource", ["subjects", "exams", "notices", "classes", "enrollments", "clubs"]
)
def test_teacher_and_student_cannot_manage_head_resources(setup, resource):
    for role in ["teacher", "student"]:
        assert (
            client(setup[role])
            .post(f"/api/academic/{resource}/", {}, format="json")
            .status_code
            == 403
        )


def test_result_scope_and_validation(setup):
    teacher = client(setup["teacher"])
    data = payload(setup)
    assert (
        client(setup["other_teacher"]).post("/api/academic/results/", data).status_code
        == 400
    )
    assert (
        client(setup["student"]).post("/api/academic/results/", data).status_code == 403
    )
    for invalid in [-1, 101]:
        assert (
            teacher.post(
                "/api/academic/results/", {**data, "marks": invalid}
            ).status_code
            == 400
        )
    assert (
        teacher.post(
            "/api/academic/results/", {**data, "user_id": setup["other_student"].pk}
        ).status_code
        == 400
    )
    assert (
        teacher.post(
            "/api/academic/results/", {**data, "subject_id": setup["other_course"].pk}
        ).status_code
        == 400
    )
    created = teacher.post("/api/academic/results/", data)
    assert created.status_code == 201
    assert teacher.post("/api/academic/results/", data).status_code == 400
    assert (
        client(setup["other_teacher"])
        .patch(f"/api/academic/results/{created.data['result_id']}/", {"marks": 5})
        .status_code
        == 404
    )


def test_enrollment_and_role_integrity(setup):
    api = client(setup["head"])
    assert (
        api.post(
            "/api/academic/enrollments/",
            {"student": setup["student"].pk, "academic_class": setup["cohort"].pk},
        ).status_code
        == 400
    )
    assert (
        api.post(
            "/api/academic/enrollments/",
            {"student": setup["teacher"].pk, "academic_class": setup["cohort"].pk},
        ).status_code
        == 400
    )
    assert (
        api.post(
            "/api/academic/subjects/",
            {
                "subject_name": "Bad",
                "subject_code": "BAD",
                "teacher_id": setup["student"].pk,
            },
        ).status_code
        == 400
    )
    assert (
        api.patch(
            f"/api/user/users/{setup['head'].pk}/", {"user_type": "S"}
        ).status_code
        == 400
    )
    assert (
        api.patch(
            f"/api/user/users/{setup['teacher'].pk}/", {"user_type": "S"}
        ).status_code
        == 400
    )
    assert (
        api.patch(
            f"/api/user/users/{setup['student'].pk}/", {"user_type": "T"}
        ).status_code
        == 400
    )


def test_subject_notice_and_people_visibility(setup):
    Notice.objects.create(
        notice_title="Everyone", notice_description="General", user_id=setup["head"]
    )
    Notice.objects.create(
        notice_title="Private course",
        notice_description="Scoped",
        user_id=setup["head"],
        subject_id=setup["other_course"],
    )
    student = client(setup["student"])
    assert student.get("/api/academic/subjects/").data["count"] == 1
    assert student.get("/api/academic/notices/").data["count"] == 1
    assert student.get("/api/user/users/").data["count"] == 1
    teacher = client(setup["teacher"])
    assert teacher.get("/api/user/users/").data["count"] == 2
    assert teacher.post("/api/user/users/", {}).status_code == 403
    assert (
        student.patch(
            "/api/user/userprofile/", {"name": "Updated", "user_type": "H"}
        ).data["user_type"]
        == "S"
    )


def test_results_keep_consistent_subject_links(setup):
    Result.objects.create(
        user_id=setup["student"],
        subject_id=setup["course"],
        exam_id=setup["assessment"],
        marks=85,
    )
    api = client(setup["head"])
    assert (
        api.patch(
            f"/api/academic/exams/{setup['assessment'].pk}/",
            {"subject_id": setup["other_course"].pk},
        ).status_code
        == 400
    )
    assert (
        api.patch(
            f"/api/academic/classes/{setup['cohort'].pk}/",
            {"subjects": []},
            format="json",
        ).status_code
        == 400
    )
    assert (
        api.patch(
            f"/api/academic/classes/{setup['cohort'].pk}/",
            {"subjects": [setup["course"].pk, setup["other_course"].pk]},
            format="json",
        ).status_code
        == 200
    )


def test_club_membership_is_self_service_and_idempotent(setup):
    item = Club.objects.create(
        club_name="Coding", club_description="Projects", user_id=setup["teacher"]
    )
    api = client(setup["student"])
    url = f"/api/academic/clubs/{item.pk}/membership/"
    for _ in range(2):
        response = api.post(url, {"user_id": setup["other_student"].pk})
        assert response.status_code == 200 and response.data["member_count"] == 1
    assert item.members.filter(pk=setup["student"].pk).exists()
    assert not item.members.filter(pk=setup["other_student"].pk).exists()
    assert api.delete(url).data["member_count"] == 0


def test_registration_login_refresh_logout_and_password(setup):
    api = client()
    registration = api.post(
        "/api/user/register/",
        {
            "name": "New Student",
            "email": "NEW@example.edu",
            "password": PASSWORD,
            "password2": PASSWORD,
            "user_type": "H",
        },
    )
    assert (
        registration.status_code == 201
        and registration.data["user"]["user_type"] == "S"
    )
    assert registration.data["user"]["email"] == "new@example.edu"
    login = api.post(
        "/api/user/login/", {"email": "NEW@example.edu", "password": PASSWORD}
    )
    assert login.status_code == 200
    tokens = login.data["token"]
    assert (
        api.post("/api/user/refresh/", {"refresh": tokens["refresh"]}).status_code
        == 200
    )
    api.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access"])
    assert api.get("/api/user/userprofile/").status_code == 200
    assert (
        api.post("/api/user/logout/", {"refresh": tokens["refresh"]}).status_code == 204
    )
    api.credentials()
    assert (
        api.post("/api/user/refresh/", {"refresh": tokens["refresh"]}).status_code
        == 401
    )
    tokens = api.post(
        "/api/user/login/", {"email": "new@example.edu", "password": PASSWORD}
    ).data["token"]
    api.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access"])
    assert (
        api.post(
            "/api/user/password/",
            {
                "old_password": "wrong",
                "password": "AnotherSecure!123",
                "password2": "AnotherSecure!123",
            },
        ).status_code
        == 400
    )
    assert (
        api.post(
            "/api/user/password/",
            {
                "old_password": PASSWORD,
                "password": "AnotherSecure!123",
                "password2": "AnotherSecure!123",
            },
        ).status_code
        == 200
    )
    assert api.get("/api/user/userprofile/").status_code == 401
    api.credentials()
    assert (
        api.post("/api/user/refresh/", {"refresh": tokens["refresh"]}).status_code
        == 401
    )


def test_inactive_user_cannot_authenticate_or_refresh(setup):
    api = client()
    tokens = api.post(
        "/api/user/login/", {"email": setup["student"].email, "password": PASSWORD}
    ).data["token"]
    setup["student"].is_active = False
    setup["student"].save()
    assert (
        api.post(
            "/api/user/login/", {"email": setup["student"].email, "password": PASSWORD}
        ).status_code
        == 401
    )
    assert (
        api.post("/api/user/refresh/", {"refresh": tokens["refresh"]}).status_code
        == 401
    )


@pytest.mark.parametrize("target", ["course", "teacher"])
def test_parent_deletions_cascade_to_dependents(setup, target):
    score = Result.objects.create(
        user_id=setup["student"],
        subject_id=setup["course"],
        exam_id=setup["assessment"],
        marks=85,
    )
    announcement = Notice.objects.create(
        notice_title="Course update",
        notice_description="Details",
        user_id=setup["head"],
        subject_id=setup["course"],
    )
    item = Club.objects.create(
        club_name="Coding", club_description="Projects", user_id=setup["teacher"]
    )
    item.members.add(setup["student"])
    parent = setup[target]
    if target == "course":
        url = f"/api/academic/subjects/{parent.pk}/"
        assert client(setup["student"]).delete(url).status_code == 403
        assert client(setup["head"]).delete(url).status_code == 204
    else:
        parent.delete()

    assert not Result.objects.filter(pk=score.pk).exists()
    assert not Notice.objects.filter(pk=announcement.pk).exists()
    assert Enrollment.objects.filter(pk=setup["enrollment"].pk).exists() == (
        target == "course"
    )
    assert Club.objects.filter(pk=item.pk).exists() == (target == "course")
    assert Subject.objects.filter(pk=setup["other_course"].pk).exists()
    assert User.objects.filter(pk=setup["student"].pk).exists()
