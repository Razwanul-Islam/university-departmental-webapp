# Departmental Portal

Django REST API for users, subjects, classes, enrollments, exams, results, notices, and clubs.

## Demo accounts

| Role | Email | Password |
|---|---|---|
| Head | head@demo.edu | `CampusDemo!2026` |
| Teacher | teacher@demo.edu | `CampusDemo!2026` |
| Student | student@demo.edu | `CampusDemo!2026` |

These are the default accounts created by `seed.py`. Existing passwords are preserved when demo data is seeded again.

## Migrations and local check

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py check
```

Local portal: http://127.0.0.1:8000/

Local health check: http://127.0.0.1:8000/api/health/ — returns `{"status":"ok"}`.

## API documentation

Base URL: `http://127.0.0.1:8000/api/`. Use JSON request bodies and keep the trailing slash on endpoints.

### Authentication and users

Registration, login, refresh, and health checks are public. Other endpoints require an access token:

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

| Method | Endpoint | Request / purpose |
|---|---|---|
| POST | `/api/user/register/` | `name`, `email`, `password`, `password2`; creates a student |
| POST | `/api/user/login/` | `email`, `password`; returns tokens and user |
| POST | `/api/user/refresh/` | `refresh`; returns a new `access` token |
| POST | `/api/user/logout/` | `refresh`; invalidates the current user's refresh token |
| GET | `/api/user/userprofile/` | Current user's profile |
| PATCH | `/api/user/userprofile/` | Update `name` |
| POST | `/api/user/password/` | `old_password`, `password`, `password2` |
| GET | `/api/user/users/` | User directory, restricted by role |
| POST | `/api/user/users/` | Head creates a user: `name`, `email`, `password`, `user_type`, optional `is_active` |
| GET | `/api/user/users/{id}/` | Read a visible user |
| PUT, PATCH | `/api/user/users/{id}/` | Head updates a user; deactivate with `is_active: false` |
| GET | `/api/health/` | Server health |

Role values: `H` = Head, `T` = Teacher, `S` = Student. Users are deactivated through the API; user deletion is not supported.

Login example:

```json
{
  "email": "head@demo.edu",
  "password": "CampusDemo!2026"
}
```

Login and registration return:

```json
{
  "token": { "access": "<access_token>", "refresh": "<refresh_token>" },
  "user": {
    "id": 1,
    "email": "head@demo.edu",
    "name": "Dr. Ishak Ahmed",
    "user_type": "H",
    "is_active": true,
    "created_at": "<timestamp>"
  }
}
```

Password changes invalidate existing tokens; sign in again afterward.

### Academic resources

| Resource | Collection endpoint | Write fields | Record ID |
|---|---|---|---|
| Subjects | `/api/academic/subjects/` | `subject_name`, `subject_code`, `teacher_id` | `subject_id` |
| Classes | `/api/academic/classes/` | `class_name`, `semester`, `session`, `academic_year`, `class_teacher`, `subjects` (array of subject IDs) | `class_id` |
| Enrollments | `/api/academic/enrollments/` | `student`, `academic_class` | `id` |
| Exams | `/api/academic/exams/` | `exam_name`, `exam_date` (`YYYY-MM-DD`), `subject_id` | `exam_id` |
| Results | `/api/academic/results/` | `user_id` (student ID), `subject_id`, `exam_id`, `marks` | `result_id` |
| Notices | `/api/academic/notices/` | `notice_title`, `notice_description`, optional `subject_id` (`null` for department-wide notices) | `notice_id` |
| Clubs | `/api/academic/clubs/` | `club_name`, `club_description`, `user_id` (coordinator ID) | `club_id` |

Foreign-key values are numeric IDs. Response-only fields include readable names, calculated grades, counts, notice authors/dates, and enrollment timestamps.

| Method | Endpoint pattern | Action |
|---|---|---|
| GET | `/api/academic/{resource}/` | List visible records |
| POST | `/api/academic/{resource}/` | Create a record |
| GET | `/api/academic/{resource}/{id}/` | Read details |
| PUT, PATCH | `/api/academic/{resource}/{id}/` | Replace / partially update a record |
| DELETE | `/api/academic/{resource}/{id}/` | Delete a record |
| GET | `/api/academic/dashboard/` | Role-specific counts, average marks, recent notices, and upcoming exams |
| POST | `/api/academic/clubs/{id}/membership/` | Join as the current user; no body required |
| DELETE | `/api/academic/clubs/{id}/membership/` | Leave as the current user |

Heads manage academic resources. Teachers manage results for their assigned subjects and read relevant records. Students read enrolled subjects, related exams/notices, and their own results. All authenticated users can read clubs and join or leave them. General notices are visible to everyone signed in.

Result creation example (`POST /api/academic/results/`; use IDs from your database):

```json
{
  "user_id": 3,
  "subject_id": 1,
  "exam_id": 1,
  "marks": 85
}
```

Marks must be integers from 0 to 100; `grade` is calculated automatically. The exam must match the subject, the student must be enrolled in a class offering it, and only one result is allowed per student and exam. Deletions use CASCADE for linked records.

### Lists, filters, and responses

Lists contain 20 records per page:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [{ "subject_id": 1, "subject_name": "Databases", "subject_code": "CSE202", "teacher_id": 2, "teacher_name": "Teacher name" }]
}
```

All resource lists support `search`, `page`, and `ordering`. Examples: `/api/academic/subjects/?search=Databases` and `/api/academic/exams/?ordering=exam_date`.

| Resource | Additional filters |
|---|---|
| Users | `user_type`, `is_active` (`true` / `false`) |
| Subjects | `teacher_id` |
| Classes | `class_teacher` |
| Enrollments | `student`, `academic_class` |
| Exams, notices | `subject_id` |
| Results | `user_id`, `subject_id`, `exam_id` |

Ordering fields: academic resources use `pk`; exams also support `exam_date`, notices `notice_date`, and results `marks`. Users support `name`, `id`, and `created_at`. Prefix with `-` for descending order.

Status codes: `200` success, `201` created, `204` deleted/logged out, `400` invalid data, `401` missing/invalid authentication, `403` insufficient permission, `404` unavailable record/page, and `429` too many authentication requests. Validation errors return field messages or `non_field_errors`; other errors usually return `detail`.



## How the app works

1. A head creates teacher and student accounts in **People**.
2. The head creates subjects and assigns their teachers.
3. The head creates a class, assigns its subjects, and enrolls students.
4. The head schedules exams and posts subject-specific or department-wide notices.
5. Teachers enter marks for enrolled students in their own subjects. Grades are calculated automatically.
6. Students view their subjects, classes, exams, notices, and personal results.
7. All authenticated users can join or leave clubs and update their profiles.

Registration always creates a student. Heads create staff accounts or change roles in People. Accounts are deactivated rather than deleted. A head cannot deactivate or demote themselves. Roles with existing teaching or student records cannot be changed to an incompatible role.

| Action | Head | Teacher | Student |
|---|---|---|---|
| Manage people, subjects, classes, enrollment, exams, notices, clubs | Yes | No | No |
| Read subjects and exams | All | Assigned subjects | Enrolled subjects |
| Read classes and enrollments | All | Classes for assigned subjects (class teachers also see their classes) | Own |
| Manage results | All | Assigned subjects only | No |
| Read results | All | Assigned subjects only | Own |
| Read people | All | Self and students in assigned subjects | Self |
| Read notices | All | General + assigned subjects | General + enrolled subjects |
| Join / leave clubs | Self | Self | Self |
| Edit profile / password | Self | Self | Self |

Marks are integers from 0 to 100. Grade thresholds: A+ 80, A 75, A- 70, B+ 65, B 60, B- 55, C+ 50, C 45, D 40, F below 40. This default can be changed in `academic/models.py:grade_for`.

Only one result is allowed per student and exam. The result subject must match the exam, and the student must be enrolled in a class offering that subject. Foreign keys use CASCADE: deleting a subject also deletes its exams, notices, and results; deleting a class deletes its enrollments; deleting a user deletes records linked to that user. Updating an exam or class still checks that existing results keep consistent subject links.