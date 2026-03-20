#!/usr/bin/env python3
"""
Database utility script for Alembic migrations and database operations.
Usage: python db_utils.py <command> [args]

Commands:
    init-migrations    - Initialize Alembic migrations directory
    migrate           - Run pending migrations
    rollback          - Rollback last migration
    downgrade         - Downgrade to specific revision
    current           - Show current migration revision
    history           - Show migration history
    create-migration   - Create new migration (requires -m message)
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_command(cmd: list, description: str = "") -> bool:
    """Run a shell command and return success status."""
    if description:
        print(f"\n{'='*60}")
        print(f"Running: {description}")
        print(f"Command: {' '.join(cmd)}")
        print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True)
        if description:
            print(f"✓ {description} completed successfully\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Command failed: {e}\n")
        return False


def init_migrations() -> bool:
    """Initialize Alembic migrations directory."""
    migrations_dir = Path(__file__).parent.parent / "migrations"
    
    if migrations_dir.exists():
        print(f"Migrations directory already exists: {migrations_dir}")
        return True
    
    cmd = ["alembic", "init", str(migrations_dir)]
    return run_command(cmd, "Initializing Alembic migrations")


def migrate() -> bool:
    """Run pending migrations."""
    cmd = ["alembic", "upgrade", "head"]
    return run_command(cmd, "Running database migrations")


def rollback() -> bool:
    """Rollback the last migration."""
    cmd = ["alembic", "downgrade", "-1"]
    return run_command(cmd, "Rolling back last migration")


def downgrade(revision: str) -> bool:
    """Downgrade to a specific revision."""
    cmd = ["alembic", "downgrade", revision]
    return run_command(cmd, f"Downgrading to revision {revision}")


def current() -> bool:
    """Show current migration revision."""
    cmd = ["alembic", "current"]
    return run_command(cmd, "Showing current migration")


def history() -> bool:
    """Show migration history."""
    cmd = ["alembic", "history"]
    return run_command(cmd, "Showing migration history")


def create_migration(message: str) -> bool:
    """Create a new migration."""
    if not message:
        print("Error: Migration message is required. Use -m 'message'")
        return False
    
    cmd = ["alembic", "revision", "--autogenerate", "-m", message]
    return run_command(cmd, f"Creating migration: {message}")


def show_help() -> None:
    """Show help message."""
    help_text = """
Database Utility Script
======================

Usage: python db_utils.py <command> [options]

Commands:
    init-migrations     Initialize Alembic migrations directory
    migrate            Run pending migrations to latest version
    rollback           Rollback the last migration
    downgrade <rev>    Downgrade to a specific revision
    current            Show current migration revision
    history            Show migration history
    create-migration   Create a new migration (use -m 'message')
    help              Show this help message

Examples:
    python db_utils.py migrate
    python db_utils.py create-migration -m "Add user table"
    python db_utils.py downgrade ae1027a6acf
    python db_utils.py history
"""
    print(help_text)


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    # Handle commands
    if command == "init-migrations":
        success = init_migrations()
    
    elif command == "migrate":
        success = migrate()
    
    elif command == "rollback":
        success = rollback()
    
    elif command == "downgrade":
        if len(sys.argv) < 3:
            print("Error: Revision required. Usage: downgrade <revision>")
            sys.exit(1)
        success = downgrade(sys.argv[2])
    
    elif command == "current":
        success = current()
    
    elif command == "history":
        success = history()
    
    elif command == "create-migration":
        message = None
        if "-m" in sys.argv:
            idx = sys.argv.index("-m")
            if idx + 1 < len(sys.argv):
                message = sys.argv[idx + 1]
        success = create_migration(message)
    
    elif command == "help":
        show_help()
        success = True
    
    else:
        print(f"Unknown command: {command}")
        show_help()
        sys.exit(1)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
