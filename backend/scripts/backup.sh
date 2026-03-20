#!/bin/bash
# Database backup script
# Creates a full backup of PostgreSQL database with timestamp
# Usage: ./backup.sh [backup_dir]

set -e

# Configuration
BACKUP_DIR="${1:-.}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

# Database connection from environment or defaults
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-password}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:-ai_onboarding}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "Starting database backup..."
echo "Database: $POSTGRES_DB"
echo "Host: $POSTGRES_HOST:$POSTGRES_PORT"
echo "Output: $BACKUP_FILE"

# Set password for pg_dump
export PGPASSWORD="$POSTGRES_PASSWORD"

# Create backup
pg_dump \
    -h "$POSTGRES_HOST" \
    -U "$POSTGRES_USER" \
    -p "$POSTGRES_PORT" \
    -d "$POSTGRES_DB" \
    --verbose \
    --create \
    --clean \
    --if-exists \
    > "$BACKUP_FILE"

# Compress the backup
gzip "$BACKUP_FILE"
BACKUP_FILE="$BACKUP_FILE.gz"

# Get backup file size
SIZE=$(du -h "$BACKUP_FILE" | cut -f1)

echo "Backup completed successfully!"
echo "File: $BACKUP_FILE"
echo "Size: $SIZE"
echo "Time: $(date)"

# List recent backups
echo ""
echo "Recent backups:"
ls -lh "$BACKUP_DIR"/db_backup_*.sql.gz 2>/dev/null | tail -5

# Optional: Delete backups older than 30 days
echo ""
echo "Cleaning up old backups (older than 30 days)..."
find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -mtime +30 -delete
echo "Cleanup complete"

# Unset password variable
unset PGPASSWORD
