# Docker Quick Start Guide

**AI Adaptive Onboarding Engine - Phase 2 Complete**

## 1️⃣ Prerequisites

- Docker Desktop (or Docker Engine)
- Docker Compose v3.8+
- At least 4GB free disk space
- Ports 5432 and 8000 available

## 2️⃣ Start Everything with One Command

```bash
# Navigate to project root
cd ai-adaptive-onboarding-engine-main

# Start all services
docker-compose up -d

# Wait for services to start (10-15 seconds)
```

## 3️⃣ Verify Services are Running

```bash
# Check status
docker-compose ps

# Expected output:
# NAME                        STATUS              PORTS
# ai-onboarding-db           Up (healthy)        0.0.0.0:5432->5432/tcp
# ai-onboarding-app          Up (healthy)        0.0.0.0:8000->8000/tcp
```

## 4️⃣ Access Your Application

### Application APIs
```
Frontend: http://localhost:8000
API Docs: http://localhost:8000/docs (Swagger UI)
API Redoc: http://localhost:8000/redoc
```

### Database Admin (Development)
```bash
# Start with development profile
docker-compose --profile dev up -d

# Access Adminer UI
http://localhost:8080

# Login:
# Server: db
# Username: postgres
# Password: password (from .env)
# Database: ai_onboarding
```

## 5️⃣ View Logs

```bash
# All logs
docker-compose logs -f

# App logs only
docker-compose logs -f app

# Database logs only
docker-compose logs -f db

# Follow new logs only
docker-compose logs -f --tail=50
```

## 6️⃣ Database Backups

```bash
# Create a backup
docker-compose exec db bash /scripts/backup.sh /backups

# List backups
ls -lh backups/

# Restore from backup
docker-compose exec db bash /scripts/restore.sh /backups/db_backup_20240320_120000.sql.gz
```

## 7️⃣ Stop Services

```bash
# Stop all services (keeps data)
docker-compose down

# Stop and remove all volumes (deletes data!)
docker-compose down -v
```

## 8️⃣ Development Workflow

### Code Changes Auto-Reload

The app volume is mounted for auto-reload:
```bash
# Changes to /backend files trigger auto-reload
# Just save your file, app will restart automatically
```

### Update Dependencies

```bash
# Rebuild the app image after updating requirements.txt
docker-compose build app

# Or rebuild and restart
docker-compose up --build -d app
```

### Database Access

```bash
# Connect to database
docker-compose exec db psql -U postgres -d ai_onboarding

# Or use any PostgreSQL client
psql -h localhost -U postgres -d ai_onboarding
```

## 9️⃣ Common Tasks

### Check Database Health
```bash
docker-compose exec db psql -U postgres -d ai_onboarding -c "SELECT VERSION();"
```

### View Audit Logs
```bash
docker-compose exec db psql -U postgres -d ai_onboarding -c "SELECT id, action, table_name, timestamp FROM audit_logs LIMIT 10;"
```

### Create Admin User (via API)
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "name": "Admin User",
    "password": "securepassword",
    "role": "admin"
  }'
```

## 🔟 Troubleshooting

### Ports Already in Use

```bash
# Find what's using port 5432
lsof -i :5432

# Or use docker to find the container
docker ps | grep 5432

# Stop that container first
docker stop <container>

# Then start compose
docker-compose up -d
```

### Database Connection Error

```bash
# Check if database is healthy
docker-compose ps db

# Check database logs
docker-compose logs db

# Reset everything (careful!)
docker-compose down -v
docker-compose up -d
```

### Out of Memory

Increase Docker memory limit:
- **Windows/Mac:** Docker Desktop → Settings → Resources
- **Linux:** Modify docker-compose.yml resource limits

### Permission Denied Errors

```bash
# Fix script permissions
chmod +x backend/scripts/*.sh
chmod +x backend/entrypoint.sh
```

## 🎯 Next Steps

1. **Test the API:** Visit http://localhost:8000/docs
2. **Create a user account**
3. **Upload a resume and job description**
4. **Run an analysis**
5. **Check audit logs** to see what happened

## 📚 Documentation

- Full documentation: See `PHASE_2_DATABASE.md`
- API documentation: http://localhost:8000/docs
- Database queries: Connect via psql

## 🚀 Production Deployment

To deploy to production:

1. Update `.env` with production values
2. Set `APP_ENV=production` and `DEBUG=false`
3. Use a managed database (AWS RDS, Azure, etc.)
4. Configure TLS/SSL
5. Set up monitoring and backups
6. Deploy with Kubernetes or similar orchestration

---

**Everything is ready! Start with `docker-compose up -d`**
