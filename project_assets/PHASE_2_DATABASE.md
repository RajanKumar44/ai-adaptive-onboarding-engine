# PHASE 2: Database & Persistence Layer

This document covers the complete database setup for the AI Adaptive Onboarding Engine, including Alembic migrations, audit logging, soft deletes, and Docker containerization.

## Overview

PHASE 2 implements enterprise-grade database capabilities:

- ✅ **Alembic Migrations** - Version control for database schema changes
- ✅ **Audit Logging** - Track who did what, when, and what changed
- ✅ **Soft Deletes** - Mark data as deleted without removing it
- ✅ **Database Indexes** - Optimized queries on frequently accessed fields
- ✅ **Connection Pooling** - Optimized for production use
- ✅ **Backup/Restore** - Automated database backup scripts
- ✅ **Docker Container** - Complete containerized deployment

---

## Project Structure

```
backend/
├── app/
│   ├── models/
│   │   ├── base.py              # AuditedBase mixin for audit fields
│   │   ├── user.py              # User model with RBAC
│   │   ├── analysis.py          # Analysis model
│   │   └── audit_log.py         # AuditLog model
│   ├── core/
│   │   └── database.py          # Enhanced connection pooling
│   ├── services/
│   │   └── audit_service.py     # Audit logging service
│   └── main.py
├── scripts/
│   ├── backup.sh                # Database backup script
│   ├── restore.sh               # Database restore script
│   ├── db_utils.py              # Python database utilities
│   └── init-db.sql              # Database initialization
├── Dockerfile                   # Multi-stage Docker image
├── entrypoint.sh               # Container entrypoint script
├── requirements.txt            # Python dependencies
└── .dockerignore               # Docker build ignore file

root/
└── docker-compose.yml          # Docker Compose orchestration
```

---

## Database Features

### 1. Audit Logging

Every change to the database is tracked in the `audit_logs` table.

**Tracked Information:**
- Who made the change (user_id)
- What table and record was affected
- Type of action (CREATE, UPDATE, DELETE, RESTORE)
- Old and new values (JSON)
- What specifically changed
- When it happened (timestamp)
- Request metadata (IP address, user agent)

**Usage:**

```python
from app.services.audit_service import AuditLogger

# Log a create action
AuditLogger.log_create(
    db=db,
    user_id=current_user.id,
    table_name="users",
    record_id=new_user.id,
    new_values=user_dict,
    ip_address=request.client.host,
    user_agent=request.headers.get("user-agent")
)

# Get audit history for a record
history = AuditLogger.get_record_history(db, "users", user_id)

# Get all actions by a user
user_actions = AuditLogger.get_user_activity(db, user_id)
```

### 2. Soft Deletes

Records are marked as deleted instead of being removed, preserving data.

**Usage:**

```python
from app.models.user import User

# Soft delete
user.soft_delete(user_id=admin_id)
db.add(user)
db.commit()

# Query active records only
active_users = db.query(User).filter(User.deleted_at == None).all()

# Restore soft-deleted record
user.restore(user_id=admin_id)
db.add(user)
db.commit()
```

### 3. Database Indexes

Optimized indexes for frequently queried fields:

**User table:**
- `ix_users_email_not_deleted` - email lookup excluding deleted
- `ix_users_active_deleted` - active user filtering
- `ix_users_created_at` - time-range queries
- `ix_users_role` - role-based filtering

**Analysis table:**
- `ix_analyses_user_id_not_deleted` - user analysis lookup
- `ix_analyses_created_at` - time-range queries
- `ix_analyses_user_created` - user-specific analysis timeline

**AuditLog table:**
- `ix_audit_logs_user_table_action` - user action history
- `ix_audit_logs_table_record` - record history
- `ix_audit_logs_timestamp_range` - time-range audit queries

### 4. Connection Pooling

Optimized SQLAlchemy connection pooling for production:

```python
# Configuration in app/core/database.py
pool_size=20                # Maintain 20 connections
max_overflow=40            # Up to 40 additional connections
pool_pre_ping=True         # Verify connections before use
pool_recycle=3600          # Recycle connections after 1 hour
```

---

## Docker Deployment

### Quick Start

1. **Build and start all services:**

```bash
docker-compose up -d
```

2. **View logs:**

```bash
docker-compose logs -f app
docker-compose logs -f db
```

3. **Watch application startup:**

```bash
docker-compose logs -f app | grep "Starting FastAPI"
```

4. **Access the application:**

```
http://localhost:8000
```

5. **Access database admin UI (development):**

```bash
docker-compose --profile dev up -d adminer
# Then visit http://localhost:8080
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (careful - deletes data!)
docker-compose down -v
```

### Environment Variables

Create a `.env` file in the project root:

```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=ai_onboarding

# App
APP_ENV=production
DEBUG=false
APP_PORT=8000

# LLM
OPENAI_API_KEY=your-key
```

### Docker Compose Services

#### PostgreSQL Database
- **Container:** ai-onboarding-db
- **Image:** postgres:15-alpine
- **Port:** 5432 (configurable)
- **Volume:** postgres_data (named volume for persistence)
- **Health Check:** Automatic verification

#### FastAPI Application
- **Container:** ai-onboarding-app
- **Build:** Multi-stage Dockerfile
- **Port:** 8000 (configurable)
- **Volumes:** Code mount for development, logs, uploads
- **Depends On:** Database health check
- **Resource Limits:** 2 CPU, 2GB RAM

#### Adminer (Optional)
- **Profile:** dev (only starts with `--profile dev`)
- **Port:** 8080
- **Database Admin UI:** http://localhost:8080

---

## Alembic Migrations (Advanced)

Currently, migrations are in manual mode. To set up Alembic for automatic migrations:

### Initialize Alembic

```bash
# Inside container
docker-compose exec app python scripts/db_utils.py init-migrations

# Or locally
python backend/scripts/db_utils.py init-migrations
```

### Create a Migration

```bash
# Automatically detect model changes
docker-compose exec app python scripts/db_utils.py create-migration -m "Add new field to users"

# Or locally
python backend/scripts/db_utils.py create-migration -m "Add new field to users"
```

### Run Migrations

```bash
# Inside container
docker-compose exec app python scripts/db_utils.py migrate

# Or enable auto-migration on startup
export ALEMBIC_UPGRADE=true
docker-compose up -d
```

### Migration Commands

```bash
# View current migration
python backend/scripts/db_utils.py current

# View all migrations
python backend/scripts/db_utils.py history

# Rollback last migration
python backend/scripts/db_utils.py rollback

# Downgrade to specific revision
python backend/scripts/db_utils.py downgrade ae1027a6acf
```

---

## Backup & Restore

### Automated Backups

Create backups with a single command:

```bash
# Inside container
docker-compose exec db bash /scripts/backup.sh /backups

# Or locally (requires PostgreSQL client)
./backend/scripts/backup.sh ./backups
```

Output:
- `db_backup_20240320_120000.sql.gz` (compressed SQL dump)
- Automatic cleanup of backups older than 30 days
- Logs all backup details

### Restore from Backup

```bash
# List available backups
ls -lh backups/

# Restore from backup
docker-compose exec db bash /scripts/restore.sh /backups/db_backup_20240320_120000.sql.gz
```

**Warning:** This will overwrite the current database!

### Backup Scheduling (Linux/Mac)

Add to crontab for automatic daily backups:

```bash
# Daily backup at 2 AM
0 2 * * * cd /path/to/project && docker-compose exec -T db bash /scripts/backup.sh /backups >> /var/log/db-backup.log 2>&1
```

---

## Database Initialization

On first startup, the application automatically:

1. Waits for PostgreSQL to be ready (with retries)
2. Creates PostgreSQL extensions (UUID, pg_trgm, pgcrypto)
3. Initializes all tables via SQLAlchemy ORM
4. Creates all indexes
5. Sets up helper functions

Optional: Set `ALEMBIC_UPGRADE=true` to run migrations instead.

---

## Monitoring & Debugging

### View Database Logs

```bash
docker-compose logs db
```

### Connect to Database Directly

```bash
# Using psql in container
docker-compose exec db psql -U postgres -d ai_onboarding

# Or remotely
psql -h localhost -U postgres -d ai_onboarding
```

### Check Database Size

```sql
-- Inside psql
SELECT pg_database.datname,
       pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
ORDER BY pg_database_size(pg_database.datname) DESC;
```

### View Active Connections

```sql
SELECT datname, count(*) as connections
FROM pg_stat_activity
GROUP BY datname;
```

### View Audit Trail

```sql
-- Recent audit logs
SELECT id, timestamp, action, table_name, record_id, user_id 
FROM audit_logs 
ORDER BY timestamp DESC 
LIMIT 20;

-- Audit history for a specific record
SELECT * FROM audit_logs 
WHERE table_name = 'users' AND record_id = 1
ORDER BY timestamp DESC;
```

---

## Performance Optimization

### Connection Pool Tuning

Adjust in `app/core/database.py`:

```python
pool_size=20           # Start with (CPU cores × 2)
max_overflow=40        # Or (pool_size × 2)
pool_recycle=3600      # Adjust based on database timeout settings
```

### Query Optimization

1. Use indexes created automatically on model fields
2. Avoid N+1 queries with proper relationships
3. Use pagination for large result sets
4. Filter on indexed columns first

### Monitoring Performance

```sql
-- Slow queries
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;

-- Missing indexes
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE idx_scan = 0;
```

---

## Troubleshooting

### Database Connection Issues

```bash
# Check if database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Try connecting directly
docker-compose exec db psql -U postgres -d ai_onboarding -c "SELECT VERSION();"
```

### Migration Issues

```bash
# If stuck in migration
docker-compose down -v  # Remove everything
docker-compose up -d    # Start fresh
```

### Permission Issues

```bash
# Fix script permissions
chmod +x backend/scripts/*.sh
chmod +x backend/entrypoint.sh
```

### Out of Memory

Increase Docker resource limits in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      memory: 4G  # Increase as needed
```

---

## Production Checklist

- [ ] Set `APP_ENV=production` in environment
- [ ] Set `DEBUG=false`
- [ ] Change `JWT_SECRET_KEY` to random value
- [ ] Change `POSTGRES_PASSWORD` to strong password
- [ ] Enable TLS for PostgreSQL connections
- [ ] Set up automated backups
- [ ] Configure monitoring/alerting
- [ ] Set resource limits appropriately
- [ ] Use managed PostgreSQL (AWS RDS, Azure Database, etc.)
- [ ] Enable connection pooling with PgBouncer for large deployments

---

## Next Steps (PHASE 3)

PHASE 3 will add:
- Advanced authentication & authorization
- Rate limiting
- Request logging & monitoring
- Error tracking (Sentry)
- Prometheus metrics
- Structured logging with JSON output

---

## References

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Performance Tuning](https://www.postgresql.org/docs/current/performance.html)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Database Documentation](https://fastapi.tiangolo.com/advanced/sql-databases/)

---

**Last Updated:** March 20, 2024
**PHASE 2 Status:** ✅ COMPLETE
