# Automated Job Application Tracker

A production-oriented full-stack web application engineered for job seekers to manage job applications, monitor interview pipelines, organize tailored resumes, extract job posting details automatically, track deadlines, and analyze application velocity.

Built with Python 3.12+, Flask, PostgreSQL, SQLAlchemy 2.0, Alembic, Chart.js, and Lucide icons following clean architecture, strict security boundaries, and responsive design guidelines.

---

## 1. Project Overview

Finding and managing job opportunities across multiple platforms often results in disorganized spreadsheets, missed interview rounds, lost resume iterations, and fragmented notes. The **Automated Job Application Tracker** provides a centralized, private platform designed like a professional developer tool.

### Core Philosophy
- **Restrained, Engineered UI**: Designed with clean contrast, Inter typography, compact data tables, and zero decorative fluff or purple gradients.
- **Data Integrity**: True database relationships, parameterized queries, and real aggregations without fabricated statistics.
- **Robust Security**: Protection against CSRF, SSRF on URL parsers, CSV formula injection, path traversal on file uploads, and unauthorized cross-user access.

---

## 2. Key Features

- **Application Pipeline Management**: Track job opportunities through defined stages (`Saved`, `Applied`, `Assessment`, `Interview`, `Offer`, `Rejected`, `Withdrawn`) with search, filter, and pagination.
- **Interview Tracking**: Schedule multi-round interviews with timezone normalization, location/video links, notes, and chronological status updates.
- **Secure Resume Vault**: Store PDF and DOCX files in private storage (outside public static directories) with MIME verification and associate them with specific applications.
- **Automated Job Details Extraction**: Ingest job posting URLs, validate against private/internal IP ranges (SSRF defense), and extract Schema.org `JobPosting` structured metadata with fallback parsing.
- **Deadline Reminders**: In-app deadline alerts for upcoming application cutoff dates and scheduled interviews.
- **Application Analytics**: Visual distributions and velocity metrics powered by Chart.js calculated directly from authenticated user records.
- **Formula-Safe CSV Export**: Export application data with RFC 4180 escaping and spreadsheet formula injection defenses (`=`, `+`, `-`, `@`, `\t`, `\r`).

---

## 3. Technology Stack

- **Backend**: Python 3.12+, Flask 3.1, Flask-SQLAlchemy 3.1, SQLAlchemy 2.0, Flask-Migrate 4.1, Alembic 1.20, Flask-Login 0.6, Flask-WTF 1.3, Werkzeug.
- **Database**: PostgreSQL 15+ (production & dev), SQLite (isolated unit testing).
- **Driver**: `psycopg` 3.x (modern PostgreSQL DBAPI adapter).
- **Frontend**: Semantic HTML5, CSS3 with custom design tokens, Vanilla JavaScript (ES6+), Jinja2 templates, Lucide icons, Chart.js.
- **Job Extraction**: `requests`, `beautifulsoup4`, standard-library `urllib.parse` & `ipaddress`.
- **Testing & Quality Assurance**: `pytest`, `pytest-cov`, `ruff`.

---

## 4. Architecture

The application adopts a modular monolith structure utilizing Flask application factories and isolated Blueprints:

```text
automated-job-application-tracker/
├── app/
│   ├── __init__.py           # Flask application factory
│   ├── config.py             # Config profiles (Dev, Test, Prod)
│   ├── extensions.py         # DB, Migrate, Login, CSRF instances
│   ├── models/               # Domain ORM models (User, Application, Interview, Resume, Reminder, Activity)
│   ├── auth/                 # Authentication blueprint & session guards
│   ├── dashboard/            # Executive summary & metrics blueprint
│   ├── applications/         # Job applications CRUD & filtering
│   ├── extraction/           # SSRF-safe URL scraping & schema parsing
│   ├── resumes/              # Secure file storage & management
│   ├── reminders/            # Deadline & interview reminders
│   ├── analytics/            # Chart data & CSV export blueprint
│   ├── api/                  # RESTful endpoints
│   ├── templates/            # Jinja2 templates adhering to design tokens
│   └── static/               # CSS tokens, JS helpers, icons
├── migrations/               # Alembic database migration scripts
├── tests/                    # Pytest automated test suites
├── docs/                     # Architecture & database specifications
└── run.py                    # Application WSGI entrypoint
```

---

## 5. Prerequisites

- Python 3.12 or higher
- PostgreSQL 14+ (or Docker for running a local Postgres container)
- Git

---

## 6. Local Installation

### Clone the Repository
```bash
git clone https://github.com/your-username/automated-job-application-tracker.git
cd automated-job-application-tracker
```

### Create and Activate Virtual Environment

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 7. Environment Configuration

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Review and update variables:
```env
FLASK_APP=run.py
FLASK_DEBUG=0
SECRET_KEY=generate-a-secure-32-byte-hex-or-random-string
DATABASE_URL=postgresql+psycopg://app_user:app_password@localhost:5432/job_tracker
UPLOAD_FOLDER=instance/uploads
MAX_UPLOAD_SIZE_MB=10
APP_TIMEZONE=UTC
```

---

## 8. PostgreSQL Setup

1. Connect to your PostgreSQL instance:
```bash
psql -U postgres
```

2. Create user and database:
```sql
CREATE USER app_user WITH PASSWORD 'app_password';
CREATE DATABASE job_tracker OWNER app_user;
GRANT ALL PRIVILEGES ON DATABASE job_tracker TO app_user;
\q
```

---

## 9. Database Migrations

Apply Alembic migrations to initialize the schema:
```bash
flask db upgrade
```

To create a new migration after model modifications:
```bash
flask db migrate -m "Description of schema update"
flask db upgrade
```

---

## 10. Running the Application

Start the local development server:
```bash
flask run --port=5000
```
or
```bash
python run.py
```

Access the application in your browser at `http://127.0.0.1:5000`.

---

## 11. Running Tests and Linting

Run automated tests with coverage:
```bash
pytest --cov=app --cov-report=term-missing
```

Run Ruff code linting and formatting verification:
```bash
ruff check .
ruff format --check .
```

---

## 12. Security Considerations

- **Authentication**: Passwords hashed using Werkzeug `generate_password_hash` (scrypt / PBKDF2-HMAC-SHA256).
- **Session Security**: Cookies set with `HttpOnly`, `SameSite=Lax`, and `Secure` enabled in production.
- **CSRF Defense**: All mutating forms and AJAX requests require valid CSRF tokens via `Flask-WTF`.
- **SSRF Defense**: Extraction queries resolve DNS and reject private RFC 1918, loopback, link-local, and multicast IP ranges.
- **Private Storage**: Uploaded resumes are renamed with UUIDs, stored outside the web root (`instance/uploads/`), and served only to authorized owners with explicit `Content-Disposition`.
- **CSV Injection Prevention**: Export sanitizes field prefixes matching `=`, `+`, `-`, `@`, `\t`, `\r` by prepending a single quote.

---

## 13. License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
