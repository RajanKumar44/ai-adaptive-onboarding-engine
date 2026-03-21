# AI Adaptive Onboarding Engine

Production-ready onboarding platform with:
- FastAPI backend
- React frontend
- PostgreSQL persistence

## Repository Layout

- `backend/` - API, services, models, and tests
- `frontend/` - Vite React application
- `project_assets/` - project documentation, scripts, compose/env files, and reports

## Quick Start

From repository root, run:

```bash
cd project_assets
docker compose --env-file .env.docker up --build -d
```

Open:
- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/api/v1/docs

## Full Documentation

See:
- `project_assets/README.md`
- `project_assets/START_HERE.md`
- `backend/README.md`
