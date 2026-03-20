#!/bin/bash
# Application entrypoint script
# Handles database initialization and starts the application

set -e

echo "================================================"
echo "AI Adaptive Onboarding Engine - Starting"
echo "================================================"

# Database configuration
export POSTGRES_USER="${POSTGRES_USER:-postgres}"
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-password}"
export POSTGRES_HOST="${POSTGRES_HOST:-db}"
export POSTGRES_PORT="${POSTGRES_PORT:-5432}"
export POSTGRES_DB="${POSTGRES_DB:-ai_onboarding}"

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if nc -z "$POSTGRES_HOST" "$POSTGRES_PORT" 2>/dev/null; then
        echo "✓ PostgreSQL is ready!"
        break
    fi
    
    echo "  Attempt $attempt/$max_attempts: PostgreSQL not ready yet..."
    sleep 2
    attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
    echo "✗ Failed to connect to PostgreSQL after $max_attempts attempts"
    exit 1
fi

# Run migrations if ALEMBIC_UPGRADE is set
if [ "${ALEMBIC_UPGRADE}" = "true" ]; then
    echo ""
    echo "Running database migrations..."
    cd /app
    python -m alembic upgrade head
    echo "✓ Migrations completed"
fi

# Initialize database if needed
if [ "${INIT_DB}" = "true" ]; then
    echo ""
    echo "Initializing database..."
    cd /app
    python -c "from app.core.database import init_db; init_db()"
    echo "✓ Database initialized"
fi

# Start the application
echo ""
echo "================================================"
echo "Starting FastAPI application..."
echo "Host: 0.0.0.0"
echo "Port: 8000"
echo "="================================================"
echo ""

# Use gunicorn in production with uvicorn workers, or uvicorn in development
if [ "${APP_ENV}" = "production" ]; then
    exec gunicorn app.main:app \
        --workers 4 \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:8000 \
        --access-logfile - \
        --error-logfile - \
        --log-level info
else
    # Development mode with auto-reload
    exec uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload
fi
