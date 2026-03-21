# AI Adaptive Onboarding Engine

Production-ready AI onboarding platform that analyzes candidate profiles against role requirements, identifies skill gaps, and generates adaptive learning recommendations.

Built with:
- FastAPI backend
- React frontend (Vite + Nginx)
- PostgreSQL for persistence
- Docker Compose for reproducible local setup

## Demo Video

<video controls width="100%" src="https://drive.google.com/uc?export=download&id=1Xsc2-iNr4ekyOFj4X9IFPzxEQ4TTVt_D">
  Your browser does not support embedded video playback.
</video>

Direct link: https://drive.google.com/file/d/1Xsc2-iNr4ekyOFj4X9IFPzxEQ4TTVt_D/view?usp=drivesdk

## Why This Project Matters

Traditional onboarding is static and role-agnostic. This project makes onboarding:
- Personalized: based on actual resume and JD skill delta
- Measurable: track progress, completion patterns, and skill trends
- Actionable: generate structured learning paths from detected gaps

## Core Capabilities

- Secure auth flows: registration, login, profile, password management
- Resume + JD analysis pipeline with persisted results
- Skill gap detection and adaptive recommendations
- Role-aware dashboards (admin vs regular users)
- User management for admins
- Analytics views derived from database-backed data (not mock-only UI)

## Architecture At A Glance

```text
Frontend (React)
    |
    | HTTP (JWT)
    v
Backend API (FastAPI)
    |
    | SQLAlchemy ORM
    v
PostgreSQL
```

## Repository Structure

```text
.
├─ backend/           # FastAPI app, business logic, routes, models, tests
├─ frontend/          # React app, components, pages, API client
├─ project_assets/    # Compose/env files, scripts, reports, extended docs
├─ .gitignore
└─ README.md
```

## Quick Start (Evaluator Friendly)

Prerequisite:
- Docker Desktop running

From repository root:

```bash
cd project_assets
docker compose --env-file .env.docker up --build -d
docker compose ps
```

Expected healthy services:
- ai-onboarding-db
- ai-onboarding-app
- ai-onboarding-frontend

Open:
- Frontend: http://localhost:3000
- Backend API docs (Swagger): http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

Stop:

```bash
docker compose down
```

## Fast Validation Checklist

1. Frontend loads at http://localhost:3000
2. API docs load at http://localhost:8000/api/v1/docs
3. Register a user from UI
4. Login and navigate Dashboard, Analytics, Programs
5. Verify data appears from database-backed endpoints

## API Surface (Selected)

Auth:
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- GET /api/v1/auth/me

Analysis:
- POST /api/v1/analyze
- GET /api/v1/analysis/{analysis_id}
- GET /api/v1/users/{user_id}/analyses

Admin:
- GET /api/v1/admin/users
- PUT /api/v1/admin/users/{user_id}/role
- PUT /api/v1/admin/users/{user_id}/activate
- PUT /api/v1/admin/users/{user_id}/deactivate

System:
- GET /api/v1/metrics/health

## What Makes It Hackathon-Ready

- End-to-end functionality across frontend, backend, and DB
- Clean role-based access control behavior
- Real data integration in UI with graceful fallbacks
- Containerized deployment path for fast judging
- Well-documented flows for rapid verification

## Common Issues And Fixes

- Ports already in use:
  - Update values in project_assets/.env.docker and restart
- Slow first startup:
  - Initial image builds can take a few minutes
- No data visible in charts:
  - Run at least one analysis flow after login

## Extended Documentation

- project_assets/README.md
- project_assets/START_HERE.md
- backend/README.md
- backend/API_DOCUMENTATION.md

## Future Improvements

- Production CI/CD pipeline with automated quality gates
- Expanded model explainability and recommendation confidence scoring
- Advanced cohort analytics and trend segmentation
- Managed cloud deployment templates

---

If you are evaluating this project in a hackathon setting, the fastest path is:
1. Run the stack using the Quick Start section
2. Validate via Swagger + UI flow
3. Review role-based behavior and analytics pages