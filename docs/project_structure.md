# Project Structure

This document explains the **project structure** for the Intilaq AI backend codebase.  
It outlines how the codebase is organized into folders and modules, and how responsibility is divided among them.

> This file describes the physical folder/file structure.  
> For clean architecture layers (e.g. services, repositories, DI), refer to `architecture.md`.

---

## 1. `backend/`

The main source code lives here. This is where all services, APIs, business logic, data access, and utilities are defined.

---

### 1.1 `api/`

Defines all **FastAPI route handlers**, grouped by domain:

- `auth_api/`: Handles user and HR authentication routes.
- `cv_api/`: Handles CV builder operations (experience, education, etc.).
- `home_api/`: Handles home dashboard and statistics for users.
- `hr_interview_api/`: Handles HR-side interview flows (create/send/manage).
- `interview_api/`: Handles candidate-side interviews (question/answer/feedback).

---

### 1.2 `core/`

Contains shared infrastructure and helper layers:

- `email/`: Email rendering and delivery services.
- `job_runners/`: Background job definitions (e.g. video/audio processing).
- `job_triggers/`: Enqueues jobs (e.g. using RQ).
- `middlewares/`: Custom FastAPI middleware (logging, auth tracking).
- `providers/`: Dependency Injection setup for services.
- `base_service.py`: Common base class for business logic services.
- `config.py`: Environment and settings configuration.
- `logger.py`, `trace_logger.py`: Unified logging across modules.

---

### 1.3 `data_access/`

Responsible for data access logic and repository patterns:

- `mongo/`: MongoDB-based access layers (sessions, answers, etc).
- `postgres/`: PostgreSQL access layers (users, HR data).
- `redis/`: Redis access logic (session, token storage).

---

### 1.4 `database/`

Holds **SQLAlchemy models** and PostgreSQL initialization:

- `models/`: Pydantic + SQLAlchemy models used by PostgreSQL.

---

### 1.5 `domain_services/`

This is where all **business logic** lives, grouped by features/domains:

- `ai_services/`: Whisper, Gemini, transcription, similarity scoring.
- `auth_services/`: All logic related to user/HR login, password, etc.
- `cv_services/`: One service per CV section (awards, education, etc).
- `doc_services/`: Resume export: HTML rendering, PDF, DOCX generators.
- `home_services/`: Stats and dashboard logic.
- `hr_services/`: Divided into:
  - `auth_services/`: HR-specific login/register logic.
  - `client_interview_services/`: Candidate responses handler.
  - `create_interview_services/`: Question creation & invitation logic.
  - `home/`: Summary and scoring view for HR.
- `interview_services/`: Session flow, scoring, feedback.
- `token_services/`: JWT access/refresh token services.

---

### 1.6 `job_worker/`

- `worker.py`: Entrypoint for the background worker using Redis Queue (RQ).
- Used to run background jobs in Docker container.

---

### 1.7 `schemas/`

All **Pydantic models** for validating request/response payloads:

- `auth_schema.py`: Auth-related schemas.
- `cv_schema.py`: CV fields (experience, education).
- `hr_schema.py`: HR-related schemas (e.g., interview setup).
- `interview_schema.py`: Candidate interview session schemas.

---

### 1.8 `utils/`

Reusable utility functions:

- `date_utils.py`: Time/date formatting.
- `jwt_utils.py`: Token decoding.
- `email_utils.py`: Email parsing helpers.
- `exception_handlers.py`: Global FastAPI exception handlers.
- `response_schemas.py`: `success_response()` and `error_response()` helpers.
- `status_utils.py`: Enum-style centralized status codes.
- `string_utils.py`: Generic string cleaning.

---

### 1.9 `tests/`

Reserved for automated tests and validation (in progress).

---

## 2. Root-Level Files and Folders

These files exist at the root of the project:

- `main.py`: The FastAPI server entry point.
- `docker-compose.yml`: Defines the full container stack (FastAPI, Whisper, Redis, Nginx, etc.).
- `Dockerfile.fastapi`: Builds the FastAPI app container.
- `Dockerfile.whisper`: Builds the Whisper service container.
- `nginx/`: Contains NGINX config files for reverse proxy and SSL.
- `certs/`: Mounted SSL certificates.
- `static/`, `templates/`: Used for frontend HTML and email rendering.
- `.env`, `env/`: Environment secrets and settings.
- `alembic.ini`: Alembic migrations for PostgreSQL.
- `logs/`: Logging output.
- `migrations/`: Alembic migration scripts.
- `speech_to_text_service/`: A separate audio microservice (Whisper-based).
- `prometheus/`: Monitoring configuration (Prometheus/Grafana).
- `scripts/`: Internal helper scripts (if added).

---

## 3. Notes

- **Modular and Scalable**: Each feature (CV, Interview, HR) is isolated and extendable.
- **Separation of Concerns**: Business logic is decoupled from routing and DB layers.
- **Infrastructure-Ready**: Ready for background jobs, monitoring, and production deployment.

---

For architectural flow, dependency injection patterns, and separation of domains → check [`architecture.md`](architecture.md)

