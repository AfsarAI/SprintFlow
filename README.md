# 🚀 SprintFlow — AI-Powered Team Project & Task Management

SprintFlow is a full-stack project and task management web application built with **React, TypeScript, and Vite** on the frontend, and **Python, FastAPI, PostgreSQL, SQLAlchemy, and Alembic** on the backend. It incorporates **Google Gemini Generative AI** to help software engineering teams break complex tasks into clear, actionable subtasks with interactive human-in-the-loop review.

---

## 📌 Project Status

**Current Stage:** Complete MVP (Submission-Ready)

- [x] Relational database schema with SQLAlchemy models & Alembic migrations.
- [x] Secure JWT-based authentication (registration, login, and `/auth/me`).
- [x] Strict user ownership and resource isolation (multi-tenant protection).
- [x] Full Project CRUD (`POST`, `GET`, `PATCH`, `DELETE`).
- [x] Full Task CRUD with status/priority/project query filters.
- [x] AI-powered subtask suggestion engine using Google Gemini.
- [x] Interactive frontend review & approval before subtasks are persisted.
- [x] Real-time workspace metrics (Total Projects, Total Tasks, Completed %, High Priority).
- [x] Comprehensive backend automated test suite (44 passing tests in pytest).
- [x] Zero TypeScript and Vite production bundling errors.

---

## 🛠️ Technology Stack

| Layer | Technology | Details |
| :--- | :--- | :--- |
| **Frontend** | React 19, TypeScript, Vite | Single-Page Application, custom modern CSS styling |
| **Backend** | Python 3.12, FastAPI | Asynchronous RESTful API, Pydantic validation |
| **Database** | PostgreSQL | Relational storage for users, projects, and tasks |
| **ORM & Migrations** | SQLAlchemy 2, Alembic | Declarative mapping, transactional DDL migrations |
| **Authentication** | PyJWT, bcrypt | Salted bcrypt password hashing & Bearer JWT tokens |
| **Generative AI** | Google Gemini (`google-genai`) | Structured JSON schema generation via `gemini-2.5-flash` |
| **Testing** | pytest, pytest-anyio | In-memory transactional database fixtures & mocks |

---

## 🏗️ System Architecture

```text
┌────────────────────────────────────────────────────────┐
│               Frontend (React + Vite)                  │
│   AuthView  │  Workspace  │  Projects  │  Tasks  │ AI  │
└──────────────────────────┬─────────────────────────────┘
                           │ HTTP REST (Bearer JWT)
┌──────────────────────────▼─────────────────────────────┐
│                 FastAPI Backend                        │
│   /auth     │     /projects     │     /tasks           │
│   (JWT)     │  (Owner Scoped)   │ (Owner Scoped + AI)  │
└──────────────┬─────────────────────────┬───────────────┘
               │                         │
               ▼                         ▼
┌───────────────────────────────┐ ┌──────────────────────┐
│     PostgreSQL Database       │ │   Google Gemini API  │
│  users │ projects │ tasks     │ │   (AI Subtask Engine)│
└───────────────────────────────┘ └──────────────────────┘
```

---

## 📂 Repository Structure

```text
SprintFlow/
├── backend/
│   ├── alembic/              # Database migration scripts & environment
│   ├── app/
│   │   ├── api/              # API route definitions (auth, projects, tasks)
│   │   │   ├── deps.py       # DB session and get_current_user dependencies
│   │   │   ├── auth.py       # Registration, login, profile endpoints
│   │   │   ├── projects.py   # Protected Project CRUD endpoints
│   │   │   └── tasks.py      # Protected Task CRUD & AI suggestion endpoints
│   │   ├── core/
│   │   │   ├── config.py     # Pydantic Settings & environment loader
│   │   │   └── security.py   # bcrypt password hashing & JWT token utils
│   │   ├── db/               # SQLAlchemy Base and SessionLocal engine
│   │   ├── models/           # User, Project, Task models & status enums
│   │   ├── schemas/          # Pydantic request/response models & validation
│   │   └── services/         # Gemini AI subtask prompt & validation service
│   ├── tests/                # Automated pytest test suite (44 tests)
│   ├── alembic.ini           # Alembic CLI configuration
│   ├── pyproject.toml        # Backend package configuration
│   ├── requirements.txt      # Pinned Python dependencies
│   └── .env.example          # Backend environment template
├── frontend/
│   ├── src/
│   │   ├── components/       # AuthView and Workspace components
│   │   ├── services/         # Centralized API service with auth interceptor
│   │   ├── types/            # TypeScript interfaces (auth, projects, tasks, AI)
│   │   ├── App.tsx           # Application root & session state management
│   │   └── App.css           # Modern custom workspace styles
│   ├── package.json          # Node dependencies & build scripts
│   └── .env.example          # Frontend environment template
├── .gitignore                # Strict secret and artifact exclusions
└── README.md                 # Project documentation
```

---

## ⚙️ Development Setup & Installation

### 1. Prerequisites
- **Python:** 3.12 or higher
- **Node.js:** 18 or higher (with `npm`)
- **PostgreSQL:** Running instance (local or container)

### 2. Database Provisioning
Create a dedicated database and user in your PostgreSQL instance:
```sql
CREATE DATABASE sprintflow;
CREATE USER sprintflow WITH PASSWORD 'sprintflow_password';
GRANT ALL PRIVILEGES ON DATABASE sprintflow TO sprintflow;
ALTER DATABASE sprintflow OWNER TO sprintflow;
```

### 3. Backend Setup
1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   *(Optionally add your `GEMINI_API_KEY` for live AI generation)*
5. Run database migrations:
   ```bash
   alembic upgrade head
   ```
6. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   *The interactive API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).*

### 4. Frontend Setup
1. Navigate to the `frontend/` directory in a new terminal:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
4. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *Open your browser to [http://localhost:5173](http://localhost:5173).*

---

## 🔐 Environment Variables Reference

### Backend (`backend/.env`)
| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `PROJECT_NAME` | Name of the application | `SprintFlow` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg://sprintflow:sprintflow_password@localhost:5432/sprintflow` |
| `JWT_SECRET_KEY` | Secret key for signing JWT tokens | *(32+ character secure secret)* |
| `JWT_ALGORITHM` | Algorithm for token signing | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token validity duration | `60` |
| `GEMINI_API_KEY` | Google Gemini API key for AI subtasks | `your_gemini_api_key_here` |

### Frontend (`frontend/.env`)
| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | Base URL of the backend API | `http://localhost:8000` |

---

## 📡 API Endpoints Reference

### Health
- `GET /health` — Public health check (`{"status": "ok", "project": "SprintFlow"}`).

### Authentication
- `POST /auth/register` — Register a new account (`email`, `password` ≥ 6 chars). Returns safe user object (HTTP 201).
- `POST /auth/login` — Sign in with `email` and `password`. Returns Bearer `access_token` (HTTP 200).
- `GET /auth/me` — Retrieve profile of the currently authenticated user (HTTP 200).

### Projects (Owner Scoped)
- `POST /projects` — Create a project owned by `current_user.id` (HTTP 201).
- `GET /projects` — List all projects owned by `current_user.id` (HTTP 200).
- `GET /projects/{project_id}` — View single project details. Returns HTTP 403 if owned by another user.
- `PATCH /projects/{project_id}` — Update project name or description (HTTP 200).
- `DELETE /projects/{project_id}` — Delete project and cascade-delete all its child tasks (HTTP 204).

### Tasks (Owner Scoped)
- `POST /tasks` — Create a task within a project owned by the user (HTTP 201).
- `POST /tasks/batch` — Batch create multiple approved tasks/subtasks into a project (HTTP 201).
- `GET /tasks` — List user tasks with optional query filters:
  - `?project_id=1`
  - `?status=todo|in_progress|done`
  - `?priority=low|medium|high`
- `GET /tasks/{task_id}` — Get single task details (HTTP 200).
- `PATCH /tasks/{task_id}` — Update title, description, status, priority, or due date (HTTP 200).
- `DELETE /tasks/{task_id}` — Delete task (HTTP 204).

### AI Subtask Suggestions
- `POST /tasks/{task_id}/suggest-subtasks` — Generates 2–6 structured subtask suggestions using Google Gemini based on task context.
  - **Human-in-the-Loop:** Suggestions are strictly **not** auto-saved into the database.
  - Returns `{"task_id": ..., "task_title": ..., "subtasks": [{"title": "...", "description": "..."}]}`.

---

## 🧪 Automated Testing

The backend includes a comprehensive test suite utilizing an isolated in-memory transactional database (`sqlite:///:memory:`) with enforced foreign keys:

```bash
cd backend
PYTHONPATH=. .venv/bin/pytest -v
```

### Test Coverage Highlights (44 Tests):
1. **Health Check:** `test_health.py` validates system status.
2. **Authentication:** `test_auth.py` validates registration, duplicate email rejection, short passwords, login, incorrect passwords, expired tokens, and `/auth/me`.
3. **Strict Ownership Isolation:** `test_ownership.py` validates that User B cannot read, update, delete, or request AI suggestions on User A's projects and tasks.
4. **Project CRUD:** `test_projects.py` validates project creation, validation errors, listing, updating, deleting, and cascade-deletion of child tasks.
5. **Task CRUD & Filtering:** `test_tasks.py` validates task creation, validation, filtering by project/status/priority, updating, and deleting.
6. **AI Subtasks & Batch Approval:** `test_ai.py` validates structured output parsing, error handling when unconfigured, rejection of malformed outputs, confirmation that suggestions are not auto-persisted, and batch creation upon user approval.

### Frontend Production Build Check:
```bash
cd frontend
npm run build
```
Ensures zero TypeScript compilation warnings and produces optimized production assets with Vite.

---

## 🔒 Security & Architecture Principles

- **Credential Safety:** Passwords are encrypted with individual salts using bcrypt before reaching storage. Raw passwords and password hashes are excluded from all schemas and responses.
- **Resource Authorization:** Task and project endpoints verify ownership against `current_user.id`, preventing horizontal privilege escalation (IDOR attacks).
- **Graceful AI Degredation:** When the Gemini API key is missing or network limits occur, the API returns a clear `503 Service Unavailable` with setup guidance rather than crashing.
- **Human-in-the-Loop AI:** AI suggestions must be reviewed, edited (if desired), and approved by the user before being committed to the database.
