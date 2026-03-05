# Task Management System

A production-ready, distributed Task Management System built for the **Distributed Systems** coursework at WIUT. The application is fully containerised with Docker and served through an Nginx reverse proxy backed by a PostgreSQL database.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Database Schema](#database-schema)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start (Docker)](#quick-start-docker)
- [Environment Variables](#environment-variables)
- [Running Migrations](#running-migrations)
- [Running Tests](#running-tests)
- [URL Reference](#url-reference)
- [Multi-Stage Docker Build](#multi-stage-docker-build)

---

## Architecture Overview

```
Browser
   │
   ▼
┌─────────────────────────────────────────────┐
│              Nginx  (port 80)               │
│  • Serves /static/ and /media/ directly     │
│  • Proxies all other requests → Gunicorn    │
└────────────────────┬────────────────────────┘
                     │ HTTP (internal)
                     ▼
┌─────────────────────────────────────────────┐
│          Django + Gunicorn  (port 8000)     │
│  • 3 worker processes                       │
│  • Reads config from environment variables  │
└────────────────────┬────────────────────────┘
                     │ psycopg2
                     ▼
┌─────────────────────────────────────────────┐
│          PostgreSQL 15  (port 5432)         │
│  • Persistent volume: postgres_data         │
└─────────────────────────────────────────────┘
```

All three services are orchestrated with **Docker Compose** and communicate over an internal Docker network — nothing except port 80 is exposed to the host.

---

## Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| Backend | Django 4.2 (Python) | Batteries-included, secure, mature ORM |
| Database | PostgreSQL 15 | Industry-standard relational DB, cloud-ready |
| Web Server | Nginx 1.25 | High-performance reverse proxy & static file serving |
| App Server | Gunicorn | Production-grade WSGI server for Django |
| Containerisation | Docker + Docker Compose | Reproducible environments, easy deployment |
| Auth | Django built-in auth | Proven, secure session-based authentication |

---

## Database Schema

```
auth_user  (Django built-in)
    │
    │ 1 ── ∞
    ▼
 Project
 ─────────
 id          BigAutoField  PK
 name        CharField(200)
 description TextField
 owner       ForeignKey → auth_user   (Many-to-One)
 created_at  DateTimeField
 updated_at  DateTimeField
    │
    │ 1 ── ∞
    ▼
  Task
  ────────────────────────────────────
  id          BigAutoField  PK
  title       CharField(200)
  description TextField
  status      CharField  [TODO | IN_PROGRESS | DONE]
  priority    CharField  [LOW | MEDIUM | HIGH]
  due_date    DateField (nullable)
  project     ForeignKey → Project    (Many-to-One)
  tags        ManyToManyField → Tag   (Many-to-Many)
  created_at  DateTimeField
  updated_at  DateTimeField
    │
    │ ∞ ── ∞  (join table: tasks_task_tags)
    ▼
  Tag
  ────────
  id   BigAutoField  PK
  name CharField(50) unique
```

**Key relationships:**
- `Project` → `User` : Many-to-One (a user owns many projects)
- `Task` → `Project` : Many-to-One (a project contains many tasks)
- `Task` ↔ `Tag` : Many-to-Many (a task can have many tags; a tag can label many tasks)

---

## Project Structure

```
task-management/
├── Dockerfile               # Multi-stage build (builder → production)
├── docker-compose.yml       # Orchestrates db, app, nginx
├── .env                     # Local secrets (never commit this)
├── .env.example             # Template — copy to .env and fill in
├── .dockerignore
├── .gitignore
├── nginx/
│   └── default.conf         # Nginx reverse proxy config
└── taskmanager/             # Django project root
    ├── manage.py
    ├── requirements.txt
    ├── config/
    │   ├── settings.py      # All secrets loaded from environment
    │   ├── urls.py
    │   └── wsgi.py
    ├── static/
    │   └── css/style.css
    └── tasks/               # Main Django app
        ├── models.py        # Project, Task, Tag models
        ├── admin.py         # Customised Django admin
        ├── views.py         # Auth + CRUD views
        ├── urls.py          # URL routing
        ├── forms.py         # Bootstrap-styled forms
        ├── tests.py         # 10 unit & integration tests
        ├── migrations/
        │   ├── __init__.py
        │   └── 0001_initial.py
        └── templates/
            ├── registration/
            │   ├── login.html
            │   └── register.html
            └── tasks/
                ├── task_list.html
                ├── task_detail.html
                ├── task_form.html
                ├── task_confirm_delete.html
                ├── project_list.html
                ├── project_form.html
                ├── project_confirm_delete.html
                ├── tag_list.html
                ├── tag_form.html
                └── tag_confirm_delete.html
```

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)
- Git

That's it — Python and PostgreSQL do **not** need to be installed locally.

---

## Quick Start (Docker)

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd task-management
```

### 2. Create your environment file

```bash
cp .env.example .env
```

Edit `.env` and set a strong `DJANGO_SECRET_KEY` and your preferred database credentials.

### 3. Build and start all services

```bash
docker compose up --build
```

This single command will:
1. Pull `postgres:15-alpine` and `nginx:1.25-alpine`
2. Build the Django image using the multi-stage Dockerfile
3. Start the `db` container and wait for it to pass the health check
4. Run `python manage.py migrate` automatically
5. Collect static files
6. Start Gunicorn with 3 workers
7. Start Nginx on port 80

### 4. Create a superuser (optional, for Django Admin)

```bash
docker compose exec app python manage.py createsuperuser
```

### 5. Open the application

| URL | Description |
|---|---|
| `http://localhost` | Main application |
| `http://localhost/admin/` | Django Admin panel |

### 6. Stop the application

```bash
docker compose down          # stops containers, keeps volumes
docker compose down -v       # stops containers AND deletes database volume
```

---

## Environment Variables

All secrets are managed through environment variables — nothing is hard-coded.

Copy `.env.example` to `.env` and fill in the values:

```env
# Django
DJANGO_SECRET_KEY=your-long-random-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost,https://yourdomain.com

# PostgreSQL
POSTGRES_DB=taskmanager
POSTGRES_USER=taskuser
POSTGRES_PASSWORD=a-strong-password-here
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

> **Never commit `.env` to version control.** It is listed in `.gitignore`.

---

## Running Migrations

Migrations run automatically on startup via the `docker-compose.yml` command. To run them manually:

```bash
# Apply all migrations
docker compose run --rm app python manage.py migrate

# Create new migrations after changing models.py
docker compose run --rm app python manage.py makemigrations
```

---

## Running Tests

The test suite covers model relationships and view authentication/permissions:

```bash
docker compose run --rm app python manage.py test tasks
```

Tests included:

| Test | What it verifies |
|---|---|
| `test_project_str` | `__str__` on Project model |
| `test_task_str` | `__str__` on Task model |
| `test_tag_str` | `__str__` on Tag model |
| `test_task_project_relationship` | Task's Many-to-One with Project |
| `test_task_tag_many_to_many` | Task's Many-to-Many with Tag |
| `test_login_required_redirect` | Unauthenticated users are redirected |
| `test_task_list_authenticated` | Authenticated users reach the task list |
| `test_register_view` | Register page returns 200 |
| `test_project_create` | POST creates a project in the DB |
| `test_task_create` | POST creates a task in the DB |

---

## URL Reference

| Method | URL | Description |
|---|---|---|
| GET | `/` | Task list (dashboard) |
| GET/POST | `/register/` | User registration |
| GET/POST | `/login/` | User login |
| POST | `/logout/` | User logout |
| GET/POST | `/tasks/new/` | Create task |
| GET | `/tasks/<id>/` | Task detail |
| GET/POST | `/tasks/<id>/edit/` | Edit task |
| POST | `/tasks/<id>/delete/` | Delete task |
| GET | `/projects/` | Project list |
| GET/POST | `/projects/new/` | Create project |
| GET/POST | `/projects/<id>/edit/` | Edit project |
| POST | `/projects/<id>/delete/` | Delete project |
| GET | `/tags/` | Tag list |
| GET/POST | `/tags/new/` | Create tag |
| POST | `/tags/<id>/delete/` | Delete tag |
| GET | `/admin/` | Django Admin |

---

## Multi-Stage Docker Build

The Dockerfile uses a two-stage build to produce a minimal, secure production image:

```dockerfile
# Stage 1 — Builder
# Installs all Python dependencies into an isolated /install prefix.
# This stage is discarded after the build; it never ships to production.
FROM python:3.12-slim AS builder
...
RUN pip install --prefix=/install -r requirements.txt

# Stage 2 — Production
# Copies only the pre-built packages from Stage 1.
# Runs as a non-root system user (app) for security.
FROM python:3.12-slim AS production
COPY --from=builder /install /usr/local
...
USER app
```

**Why multi-stage?**
- The final image contains **no build tools, no pip cache, no compiler** — only what is needed to run the app.
- Running as a **non-root user** limits the blast radius of any container escape.
- Image size stays well under 200 MB.
 




