"""
Database connection and session management.
Uses SQLAlchemy ORM with PostgreSQL.
Includes connection pooling optimization for production use.
"""

from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)

# Load settings
settings = get_settings()

# Create SQLAlchemy engine with optimized pooling
engine = create_engine(
    settings.DATABASE_URL,
    # Connection pooling configuration
    poolclass=pool.QueuePool,
    pool_size=20,           # Number of connections to maintain in pool
    max_overflow=40,        # Additional connections beyond pool_size
    pool_pre_ping=True,     # Verify connections before use
    pool_recycle=3600,      # Recycle connections after 1 hour
    
    # Performance settings
    echo=settings.DEBUG,
    connect_args={
        "connect_timeout": 10,
        "statement_timeout": 30000,  # 30 seconds for queries
    },
)


@event.listens_for(engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    """Configure PostgreSQL connection when established."""
    cursor = dbapi_connection.cursor()
    
    # Enable UUID support
    try:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    except Exception:
        pass  # Extension might already exist
    
    # Set reasonable search_path
    cursor.execute("SET search_path TO public")
    dbapi_connection.commit()
    cursor.close()


@event.listens_for(engine, "engine_disposed")
def receive_engine_disposed(engine):
    """Log when engine connection pool is disposed."""
    logger.info("Database engine connection pool disposed")


@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log successful connection."""
    logger.debug("New database connection established")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log connection checkout."""
    logger.debug("Database connection checked out from pool")


# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,  # Don't expire objects after commit
)

# Base class
Base = declarative_base()


def get_db() -> Session:
    """
    FastAPI dependency for DB session.
    Provides a database session for each request.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database (create tables).
    Should be called once at application startup.
    """
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialization complete")


def dispose_db() -> None:
    """
    Dispose of all connections in the pool.
    Should be called on application shutdown.
    """
    logger.info("Disposing database connections...")
    engine.dispose()
    logger.info("Database connections disposed")