#!/bin/sh

# Entrypoint for AI Adaptive Onboarding Engine

set -e

echo "==============================================="
echo "AI Adaptive Onboarding Engine - Starting"
echo "==============================================="

# Default environment variables (fallbacks)

POSTGRES_HOST=${POSTGRES_HOST:-db}
POSTGRES_PORT=${POSTGRES_PORT:-5432}
POSTGRES_USER=${POSTGRES_USER:-admin}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-admin}
POSTGRES_DB=${POSTGRES_DB:-hackathon_db}

echo "Database Config:"
echo "Host: $POSTGRES_HOST"
echo "Port: $POSTGRES_PORT"
echo "DB: $POSTGRES_DB"
echo "User: $POSTGRES_USER"

# Wait for PostgreSQL

echo ""
echo "Waiting for PostgreSQL..."

max_attempts=30
attempt=1

while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
    if [ $attempt -ge $max_attempts ]; then
        echo "❌ PostgreSQL not reachable after $max_attempts attempts"
        exit 1
    fi
    
    echo "⏳ Attempt $attempt/$max_attempts: waiting..."
    attempt=$((attempt + 1))
    sleep 2
done

echo "✅ PostgreSQL is ready!"

# Optional: Initialize DB

if [ "$INIT_DB" = "true" ]; then
echo ""
echo "Initializing database..."
python -c "from app.models import User, Analysis, AuditLog; from app.core.database import init_db; init_db()"
echo "✅ Database initialized"
fi

# Optional: Run migrations

if [ "$ALEMBIC_UPGRADE" = "true" ]; then
echo ""
echo "Running migrations..."
alembic upgrade head
echo "✅ Migrations done"
fi

echo ""
echo "==============================================="
echo "Starting FastAPI server..."
echo "==============================================="
echo ""

# Start server

if [ "$APP_ENV" = "production" ]; then
    exec gunicorn app.main:app \
        --workers 4 \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:8000 \
        --access-logfile - \
        --error-logfile - \
        --log-level info
else
    exec uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000
fi
