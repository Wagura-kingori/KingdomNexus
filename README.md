# KingdomNexus

A comprehensive multi-tenant school management system built with Django and springboot featuring role-based access control, a REST API consumed by a Next.js frontend, and Celery-powered async timetable generation.

> **Django project package:** `rollover` | **Fees frontend:** [school-fees-management](../school-fees-management/README.md) | **Fees backend:** [fees-service](../fees-service/README.md) (Spring Boot)

---

## 🚀 Features

- **Multi-school / Multi-tenant** — Superadmin manages multiple schools; each school operates independently
- **Role-based Access Control** — Superadmin, School Admin, Teacher, Student, Parent, Payroll Manager, and Bursar roles with scoped permissions
- **Django REST Framework API** — Consumed by the Next.js 15 timetable frontend (JWT-authenticated)
- **Session-to-JWT bridge** — `/api/fees-token/` lets an already-logged-in (session-based) user obtain a short-lived JWT for calling independent microservices (currently: fees-service),(payrol: coming soon)
- **AJAX login endpoints** (`/api/csrf/`, `/api/login/`) — used by the fees dashboard's in-app login modal, no page navigation required
- **Event-driven sync to fees-service** — the `student_sync` app publishes student lifecycle events (enrolled/updated/withdrawn, term started) over Redis Streams, keeping the Spring Boot fees-service's local student data current without a synchronous call between services
- **Celery + Redis Async Tasks** — Automated timetable generation running as background tasks
- **WeasyPrint PDF Generation** — Report cards, payslips, and fee statements rendered to PDF
- **Force Password Change Middleware** — First-login password change enforcement
- **Django Signals** — Profile auto-creation on user registration (`profiles` app)

---

## 🛠️ Installation

### Prerequisites

- Python 3.13+
- PostgreSQL (or SQLite for development)
- Redis / [Memurai](https://www.memurai.com/) (Windows) for Celery broker **and** student_sync event publishing
- WeasyPrint (for PDF generation)

### Setup

1. **Clone the repository and create a virtual environment:**
   ```bash
   git clone <repo-url>
   cd rollover
   python -m venv venv
   source venv/bin/activate        # Linux/macOS
   venv\Scripts\activate           # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables** — copy and edit `.env`:
   ```env
   SECRET_KEY=generate-your-new-secret-key
   DEBUG=False 
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database
   DB_NAME=kingdomnexus(just a placeholder)
   DB_USER=postgres
   DB_PASSWORD=password
   DB_HOST=localhost
   DB_PORT=5432

   # Celery / Redis
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0

   # CORS (Next.js frontends — timetable + fees dashboard)
   CORS_ALLOWED_ORIGINS=http://localhost:4028
   CSRF_TRUSTED_ORIGINS=http://localhost:4028
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Seed initial data (optional):**
   ```bash
   python manage.py seed_data
   ```

7. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

8. **Start the Celery worker** (separate terminal):
   ```bash
   celery -A rollover worker --loglevel=info
   ```

9. **(Optional) Start fees-service** — see [fees-service/README.md](../fees-service/README.md).
   Django works fine without it running; only the fees dashboard needs
   it. Set `FEES_EVENTS_ENABLED=true` there once ready to receive
   student sync events from this project.

---

## 🧩 Apps Overview
## some apps are still in development 
| App | Purpose |
|---|---|
| `users` | Custom user model, role management, middleware, force-password-change flow, session-to-JWT bridge endpoints |
| `student_sync` | Publishes student lifecycle events (Redis Streams) consumed by the separate `fees-service` microservice — does not affect this app's own behavior if Redis is down |
| `profiles` | Auto-created profiles for Teachers, Students, and Parents via signals |
| `schools` | School registration and school-level dashboard |
| `academics` | Subjects, classrooms, class grades, sections, and enrollments |
| `students` | Student records, admission numbers, and classroom assignments |
| `teachers` | Teacher records, `TeacherSubjectAssignment` model, subject-teacher linking |
| `timetable` | Timetable entries, periods, breaks, generation config, Celery tasks, solver engine |
| `attendance` | Attendance records with serializers for API consumption |
| `exams` | Exam types, exams, and student results with class ranking |
| `fees` | Django-native fee structures/payments (legacy — being superseded by the separate `fees-service` Spring Boot microservice for the bursar-facing dashboard; not the same thing) |
| `grading` | Grade boundaries and grading scale configuration |
| `payroll` | Staff payroll, payslip generation, payroll periods, and PDF payslips (a Spring Boot `payroll-service`, following the same pattern as `fees-service`, is planned) |
| `reports` | Report cards and PDF report generation (WeasyPrint) |
| `messaging` | Internal notices and messages between users |
| `library` | Book catalog, borrowing, fines, and overdue management |
| `hostell` | Hostel rooms, boarder assignments, and hostel management |
| `transport` | Routes, vehicles, student transport assignments, and transport fees |
| `assets` | School asset inventory, categories, and issue tracking |
| `attendance` | Class and school-wide attendance tracking |
| `parent` | Parent portal — view children's results, attendance, and fees |
| `events` | School event management |
| `communication` | School-wide communication and announcements |
| `canteen` | Canteen management (in development) |
| `staff` | Non-teaching staff records |
| `accounts` | Supporting authentication utilities |
| `made_aesy` | Public-facing pages — school showcase, church/ministry site, sermons, projects |

---

## 📁 Project Structure

```
rollover/                          # Root directory
├── manage.py
├── .env                           # Environment variables
├── rollover/                      # Django project package
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py                  # Celery app configuration
│   ├── asgi.py
│   └── wsgi.py
│
├── users/                         # Custom user model + RBAC + JWT bridge + AJAX login
├── student_sync/                  # Publishes student events to fees-service via Redis Streams
├── profiles/                      # Auto-created role profiles (signals)
├── schools/                       # Multi-school management
├── academics/                     # Subjects, classrooms, enrollments
├── students/                      # Student records
├── teachers/                      # Teacher records + subject assignments
├── timetable/                     # Timetable engine (Celery + solver)
│   ├── tasks.py                   # Celery async generation task
│   ├── solver.py                  # Constraint-based timetable solver
│   └── serializers.py             # DRF serializers for API
├── attendance/                    # Attendance tracking
├── exams/                         # Exams, results, class rankings
├── fees/                          # Django-native fees app (legacy, see fees-service)
├── grading/                       # Grading scale configuration
├── payroll/                       # Staff payroll and payslips
├── reports/                       # Report cards (WeasyPrint PDF)
├── messaging/                     # Internal notices and messages
├── library/                       # Book catalog and borrowing
├── hostell/                       # Hostel and boarder management
├── transport/                     # Routes, vehicles, transport fees
├── assets/                        # Asset inventory and issue tracking
├── parent/                        # Parent portal
├── events/                        # School events
├── communication/                 # Announcements
├── canteen/                       # Canteen (in development)
├── staff/                         # Non-teaching staff
├── accounts/                      # Auth utilities
├── made_aesy/                     # Public-facing / church site
│   ├── management/commands/
│   │   └── seed_data.py           # Initial data seeder
│   ├── static/images/
│   └── templates/
│
├── templates/                     # Global Django templates
│   ├── base.html
│   ├── dashboard/                 # Role-specific dashboards
│   ├── timetable/                 # Timetable setup, view, conflicts
│   └── ...                        # Per-app template directories
│
├── static/                        # Global static files
│   ├── css/style.css
│   └── timetable/
│       ├── css/setup.css
│       └── js/setup.js
└── media/                         # User-uploaded files (PDFs, etc.)
```

---

## 🔐 Authentication & Roles

Authentication is dual-mode:

- **Session auth** — Django templates (admin dashboard, teacher/student/parent portals). Login is handled by `RoleBasedLoginView`, which routes each role to its destination via a shared `role_redirect_url()` function — also used by `force_password_change` after a first-login password reset, so a newly created user lands in the right place immediately rather than a generic home page.
- **JWT auth** — DRF API consumed by Next.js frontends (`djangorestframework-simplejwt`). No dedicated JWT login endpoint exists for end users; instead, `GET /api/fees-token/` bridges an existing Django session into a short-lived JWT on demand, carrying the user's `role` as a token claim. `POST /api/login/` (paired with `GET /api/csrf/`) additionally supports logging into Django itself via AJAX, from a separate frontend, without a page navigation.

### Roles

| Role | Scope |
|---|---|
| Superadmin | Full access; no school assigned by default — selects school explicitly in UI |
| School Admin | Manages a single school's data |
| Teacher | Accesses own subjects, classes, attendance, and results entry |
| Student | Views own timetable, results, fees, and attendance |
| Parent | Views children's results, attendance, fees, and notices |
| Payroll Manager | Manages staff payroll |
| Bursar | Manages school fees via the separate fees-service dashboard |

> First-time login forces a password change via the `users` middleware before any other page is accessible.

### Withdrawal (not deletion)

`User.status` (`active` / `withdrawn`) tracks whether someone is still
active in the system, separate from whether their account still
exists. Withdrawing someone (any role) sets this flag, deactivates
their login (`is_active = False`), and — for students specifically —
publishes a `student.withdrawn` event so fees-service marks them
accordingly without ever touching their payment history. This is
intentionally distinct from actually deleting a `User`, which remains
permanent and irreversible.

---

## ⚙️ Timetable Generation

The timetable engine runs as an async Celery task:

1. Admin configures `TimetableGenerationConfig` (periods, breaks, subject loads) in the UI.
2. A POST request triggers `timetable/tasks.py` via Celery.
3. `solver.py` runs constraint-based slot allocation across classrooms, subjects, and teachers.
4. Completed entries are saved as `TimetableEntry` records.
5. The frontend polls the task status endpoint until completion.

> **Troubleshooting 0 entries:** Ensure `TeacherSubjectAssignment` records exist, all subjects are linked to a classroom, and `Period` records are configured for the target school before triggering generation.

---

## 📦 Key Dependencies

```
Django
djangorestframework
djangorestframework-simplejwt
django-cors-headers
celery
redis
WeasyPrint
Pillow
python-decouple / python-dotenv
```

> Full list in `requirements.txt`.

---

## 🗄️ Database

- **Development:** SQLite (`db.sqlite3`) — included in root for local dev
- **Production:** PostgreSQL (recommended)

Run migrations after any model change:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🧪 Management Commands

| Command | Description |
|---|---|
| `python manage.py seed_data` | Seeds initial schools, subjects, and demo users |
| `python manage.py create_roles` | Creates default payroll roles |

---

## 📱 Deployment

For production, use Gunicorn + NGINX:

```bash
gunicorn rollover.wsgi:application --bind 0.0.0.0:8000
```

A `Dockerfile.weasyprint` is included in the `rollover/` package directory for containerised PDF generation.

Static files:
```bash
python manage.py collectstatic
```

---

## 🔗 Related

- [school-fees-management (Next.js fees dashboard)](../school-fees-management/README.md)
- [fees-service (Spring Boot fees backend)](../fees-service/README.md)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery Docs](https://docs.celeryq.dev/)
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/)
- [WeasyPrint](https://doc.courtbouillon.org/weasyprint/)
