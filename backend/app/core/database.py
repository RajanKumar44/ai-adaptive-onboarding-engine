"""
Database connection and session management.
Uses SQLAlchemy ORM with PostgreSQL.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from app.core.config import get_settings

# Get database configuration
settings = get_settings()

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries if debug is enabled
    pool_pre_ping=True,  # Test connections before using them
    pool_size=10,
    max_overflow=20,
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for all ORM models
Base = declarative_base()


def get_db() -> Session:
    """
    Database session dependency for FastAPI.
    Yields a database session and closes it after request.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database by creating all tables.
    Should be called on application startup.
    """
    Base.metadata.create_all(bind=engine)
