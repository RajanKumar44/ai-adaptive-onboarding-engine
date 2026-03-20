#!/bin/bash
# Database restore script
# Restores PostgreSQL database from backup file
# Usage: ./restore.sh <backup_file>

set -e

# Check for backup file argument
if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 db_backup_20240320_120000.sql.gz"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Database connection from environment or defaults
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-password}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:-ai_onboarding}"

echo "Starting database restore..."
echo "Database: $POSTGRES_DB"
echo "Host: $POSTGRES_HOST:$POSTGRES_PORT"
echo "Backup file: $BACKUP_FILE"
echo ""

# Ask for confirmation
read -p "This will overwrite the database. Are you sure? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Restore cancelled"
    exit 1
fi

# Set password for psql
export PGPASSWORD="$POSTGRES_PASSWORD"

# Decompress if needed
if [[ "$BACKUP_FILE" == *.gz ]]; then
    echo "Decompressing backup..."
    UNCOMPRESSED_FILE="${BACKUP_FILE%.gz}"
    gunzip -k "$BACKUP_FILE"
    RESTORE_FILE="$UNCOMPRESSED_FILE"
else
    RESTORE_FILE="$BACKUP_FILE"
fi

# Restore the database
echo "Restoring database..."
psql \
    -h "$POSTGRES_HOST" \
    -U "$POSTGRES_USER" \
    -p "$POSTGRES_PORT" \
    -f "$RESTORE_FILE"

echo "Database restore completed successfully!"
echo "Time: $(date)"

# Clean up decompressed file if we created it
if [[ "$BACKUP_FILE" == *.gz ]]; then
    rm -f "$RESTORE_FILE"
fi

# Unset password variable
unset PGPASSWORD
