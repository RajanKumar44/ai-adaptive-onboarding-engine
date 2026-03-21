# AI Adaptive Onboarding Engine

End-to-end AI onboarding project with:
- React frontend (Vite build served by Nginx)
- FastAPI backend
- PostgreSQL database

This README is aligned with the current, working Docker setup and is written for quick examiner verification from a GitHub link.

## 1. What Is Included

- Frontend: user registration/login, analysis flow, dashboards
- Backend: auth, analysis, admin, metrics, bulk, LLM-related routes
- Database: PostgreSQL persistence with SQLAlchemy models
- Dockerized stack: root compose for frontend + backend + db

## 2. Current Runtime URLs

After startup:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Swagger Docs: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## 3. Examiner Quick Start (Recommended)

Prerequisites:
- Docker Desktop installed and running

From project root:

```bash
docker compose --env-file .env.docker up --build -d
docker compose ps
```

Expected services:
- ai-onboarding-db (healthy)
- ai-onboarding-app (healthy)
- ai-onboarding-frontend (healthy)

Open in browser:
- http://localhost:3000
- http://localhost:8000/api/v1/docs

Stop stack:

```bash
docker compose down
```

## 4. Verification Commands

Health and docs:

```bash
curl -f http://localhost:8000/api/v1/docs
curl -f http://localhost:3000
```

Sample registration API check:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Examiner User",
    "email": "examiner.user@example.com",
    "password": "StrongPass123!",
    "confirm_password": "StrongPass123!"
  }'
```

## 5. Important Project Notes

- Adminer has been removed from the root stack by design.
- Root Docker stack is defined in docker-compose.yml.
- Default Docker env values are in .env.docker.
- Frontend API target in Docker is http://localhost:8000/api/v1.
- Backend docs endpoint is /api/v1/docs (not /docs).

## 6. Running on Another System

Option A: Build from source

```bash
docker compose --env-file .env.docker up --build -d
```

Option B: Pull pre-pushed images from Docker Hub

Published images:
- rajankumar44/ai-onboarding-app:latest
- rajankumar44/ai-onboarding-frontend:latest

Pull example:

```bash
docker pull rajankumar44/ai-onboarding-app:latest
docker pull rajankumar44/ai-onboarding-frontend:latest
docker pull postgres:15-alpine
```

Note on data migration:
- Docker images do not include live database volume data.
- Use pg_dump and restore if existing data must be moved.

## 7. Project Structure (High Level)

```text
.
├─ backend/
│  ├─ app/
│  ├─ Dockerfile
│  ├─ docker-compose.yml
│  └─ requirements.txt
├─ frontend/
│  ├─ src/
│  ├─ Dockerfile
│  ├─ nginx.conf
│  └─ package.json
├─ docker-compose.yml
├─ .env.docker
└─ README.md
```

## 8. Troubleshooting

If a service is not healthy yet, wait 20 to 40 seconds and re-check:

```bash
docker compose ps
docker compose logs app --tail 100
docker compose logs frontend --tail 100
```

If ports are occupied on host:
- Change APP_PORT, FRONTEND_PORT, POSTGRES_PORT in .env.docker
- Restart with the same up command

## 9. Documentation Pointers

- Full backend docs: backend/README.md
- API docs file: backend/API_DOCUMENTATION.md
- Docker guides: DOCKER_QUICKSTART.md and DOCKER_SETUP.md

---

If you are evaluating this project from GitHub, use Section 3 and Section 4 first. They are the shortest path to running and validating the system correctly.