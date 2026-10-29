# Architecture Documentation

## Overview

The **Automated Job Application Tracker** is designed following a modular monolith architecture using Python and Flask. The system prioritizes loose coupling, strong domain boundaries, strict security safeguards, and clear separation of concerns.

```
                              ┌─────────────────────────┐
                              │     Browser / Client    │
                              └────────────┬────────────┘
                                           │ HTTP/JSON
                                           ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                              Flask Application Shell                              │
│                                                                                   │
│  ┌────────────────────┐ ┌────────────────────┐ ┌────────────────────────────────┐ │
│  │   Authentication   │ │   Job Applications │ │      Interviews & Reminders    │ │
│  │   (Flask-Login,    │ │   (CRUD, Filters,  │ │      (Scheduling, APScheduler, │ │
│  │    Werkzeug Hash)  │ │    History, Audit) │ │       Timezone Normalization)  │ │
│  └────────────────────┘ └────────────────────┘ └────────────────────────────────┘ │
│  ┌────────────────────┐ ┌────────────────────┐ ┌────────────────────────────────┐ │
│  │ Job Info Extraction│ │ Resume Storage Mgr │ │       Analytics & Export       │ │
│  │ (SSRF-safe parser, │ │ (Private storage,  │ │       (Chart.js aggregations,  │ │
│  │  schema detection) │ │  MIME validation)  │ │        Injection-safe CSV)     │ │
│  └────────────────────┘ └────────────────────┘ └────────────────────────────────┘ │
│                                          │                                        │
│                                          ▼                                        │
│                           SQLAlchemy 2.0 ORM & Alembic                            │
└──────────────────────────────────────────┬────────────────────────────────────────┘
                                           │
                                           ▼
                              ┌─────────────────────────┐
                              │  PostgreSQL 15+ / SQLite│
                              └─────────────────────────┘
```

## Directory Structure

- `app/`: Primary application package.
  - `config.py`: Environment-aware configuration classes (Development, Testing, Production).
  - `extensions.py`: Centralized singleton initialization for SQLAlchemy, Migrate, LoginManager, and CSRFProtect.
  - `models/`: Domain models for Users, Applications, Interviews, Resumes, Reminders, and Activities.
  - `auth/`: Blueprint for user registration, authentication, sessions, and credential management.
  - `dashboard/`: Blueprint for the operational dashboard, metrics, and activity stream.
  - `applications/`: Blueprint for job application management, CRUD forms, pagination, and filtering.
  - `extraction/`: Blueprint and services for SSRF-protected URL fetching and JobPosting metadata parsing.
  - `resumes/`: Blueprint and services for authenticated file upload, MIME validation, and private document serving.
  - `reminders/`: Blueprint and background service for deadline tracking and alerts.
  - `analytics/`: Blueprint for status distribution metrics, timeline aggregations, and CSV exports.
  - `api/`: RESTful API endpoints.
  - `templates/`: Jinja2 templates adhering to design standards.
  - `static/`: Restrained CSS design tokens, Lucide icons, and vanilla JavaScript.
- `migrations/`: Alembic database version control and migration scripts.
- `tests/`: Automated unit, integration, and security test suites using pytest.
- `docs/`: Technical specifications and runbooks.

