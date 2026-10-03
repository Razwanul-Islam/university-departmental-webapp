# Departmental portal

A complete departmental app with Django REST Framework and React + TypeScript. It keeps the original account and academic models, adds the missing relationships, and uses shared viewsets, tables, and forms to keep the logic simple.

## Run locally (Windows / PowerShell)

Run these commands from the project directory:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py runserver
```

In a second terminal:

```powershell
cd frontend
npm.cmd ci
npm.cmd run dev
```

Open **http://127.0.0.1:5173/static/**. Vite forwards API requests to Django on port 8000. Node 20.19+ or 22.12+ and Python 3.12+ are recommended; this project was checked with Node 24 and Python 3.14.

Demo logins (all use **CampusDemo!2026**):

| Role | Email |
|---|---|
| Head | head@demo.edu |
| Teacher | teacher@demo.edu |
| Student | student@demo.edu |

The seed command is optional and repeatable. It adds six demo accounts, an enrolled class, three subjects, exams, results, notices, and clubs. It never resets existing passwords. To choose a different password for newly created accounts, use `seed_demo --password "your-password"`.

To create an administrator without demo data:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

Django admin is at **http://127.0.0.1:8000/admin/**. Head accounts created in the portal have portal access; only superusers have Django admin access.

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

Only one result is allowed per student and exam. The result subject must match the exam, and the student must be enrolled in a class offering that subject. Referenced records are protected from deletion. Classes and enrollments with results retain their academic links.

## Files to understand first

- `academic/models.py`: original entities plus class subjects, enrollment, club members, and grading.
- `academic/serializers.py`: form validation and readable names in API responses.
- `academic/views.py`: CRUD, role-specific record visibility, membership, and dashboard.
- `academic/permissions.py`: the two write-permission rules.
- `account/views.py` and `account/serializers.py`: authentication, profile, and user management.
- `frontend/src/resources.ts`: columns and fields for each screen.
- `frontend/src/App.tsx`: login state and navigation.
- `frontend/src/components/`: small screens plus the shared Editor and ResourcePage.
- `frontend/src/ui.tsx`: shared dialog, empty/error states, and formatting.
- `frontend/src/api.ts`: requests, session storage, automatic refresh, and error messages.
- `frontend/src/style.css`: responsive styling.

## API

Every academic endpoint requires a Bearer access token. Login and registration return `{token: {access, refresh}, user}`.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/user/register/ | Student registration: name, email, password, password2 |
| POST | /api/user/login/ | Email and password |
| POST | /api/user/refresh/ | Exchange refresh for access |
| POST | /api/user/logout/ | Blacklist the supplied refresh token |
| GET, PATCH | /api/user/userprofile/ | Read self or update name |
| POST | /api/user/password/ | old_password, password, password2 |
| GET, POST | /api/user/users/ | Scoped directory / head creates user |
| GET, PUT, PATCH | /api/user/users/{id}/ | Read / head edits user |
| GET | /api/academic/dashboard/ | Scoped counts, recent notices, upcoming exams |
| GET, POST | /api/academic/{resource}/ | List / create |
| GET, PUT, PATCH, DELETE | /api/academic/{resource}/{id}/ | Read / edit / delete |
| POST, DELETE | /api/academic/clubs/{id}/membership/ | Join / leave as current user |
| GET | /api/health/ | Health check |

Academic resources: `subjects`, `classes`, `enrollments`, `exams`, `results`, `notices`, `clubs`.
List responses are `{count, next, previous, results}`, with 20 records per page.
All lists support `?search=...`, `?page=...`, and ordering (e.g. exams: `?ordering=exam_date`).
Foreign-key filters are supported by each academic resource: subject teacher_id; exam/notice subject_id; class class_teacher; enrollment student/academic_class; result user_id/subject_id/exam_id. Users support user_type and is_active filters.

Write field names match the original models. Examples:

```json
{"subject_name":"Databases","subject_code":"CSE202","teacher_id":2}
{"class_name":"Year 2","semester":3,"session":2026,"academic_year":"2026","class_teacher":2,"subjects":[1]}
{"student":3,"academic_class":1}
{"exam_name":"Midterm","exam_date":"2026-11-01","subject_id":1}
{"user_id":3,"subject_id":1,"exam_id":1,"marks":85}
{"notice_title":"Welcome","notice_description":"Semester updates","subject_id":null}
{"club_name":"Coding Club","club_description":"Weekly projects","user_id":2}
```

Original subject/exam/result create, update, delete and retrieve paths are retained as aliases. The browsable API at `/api/academic/` lists resource routes.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
cd frontend
npm.cmd run build
npx.cmd playwright install chromium
npm.cmd test
```

Browser tests launch Django and Vite automatically on ports 8000 and 5173. Keep those ports free. They use a separate `.browser-test.sqlite3`, never your main database, and save desktop/mobile screenshots to `frontend/test-results/`.

## Built frontend and deployment

```powershell
cd frontend
npm.cmd run build
cd ..
.\.venv\Scripts\python.exe manage.py collectstatic --noinput
```

After building, Django serves the portal HTML at `/`. During development, `runserver` serves its assets at `/static/`. In production, configure your web server to serve `staticfiles/` under `/static/` and run Django through WSGI or ASGI. Do not use `runserver` for deployment.

Set a random SECRET_KEY, DJANGO_DEBUG=false, ALLOWED_HOSTS, and exact frontend CORS origins. Configure HTTPS; secure cookies, SSL redirect, and HSTS are enabled when debug is off. An example environment file is included. Set POSTGRES_DB and the other POSTGRES variables to use PostgreSQL; otherwise SQLite is used.

Tokens are stored per browser tab in sessionStorage. Logout blacklists refresh tokens; issued access tokens expire within ten minutes. Password changes invalidate existing tokens. Keep demo accounts confined to local development. Run `manage.py flushexpiredtokens` periodically to clean up expired token records.

The existing migration branches are joined by a new merge migration. Existing data is preserved; duplicate or out-of-range legacy results must be corrected before applying the new constraints. Existing classes need subjects and enrollments assigned through the portal, because those relationships were absent from the original design.
