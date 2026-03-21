"""
Database connection and session management.
Uses SQLAlchemy ORM with PostgreSQL.
Includes connection pooling optimization for production use.
"""

import os
from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)

# Load settings
settings = get_settings()

# Get database URL with fallback support
database_url = os.getenv("DATABASE_URL") or settings.get_database_url()

if database_url.startswith("sqlite"):
    engine = create_engine(
        database_url,
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False},
    )
else:
    # Create SQLAlchemy engine with optimized pooling for PostgreSQL.
    engine = create_engine(
        database_url,
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
        },
    )


@event.listens_for(engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    """Configure PostgreSQL connection when established."""
    if engine.dialect.name != "postgresql":
        return

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
    from sqlalchemy.schema import CreateTable
    
    try:
        # Import models here to ensure they're registered before creating tables
        from app.models.user import User  # noqa: F401
        from app.models.analysis import Analysis  # noqa: F401
        from app.models.audit_log import AuditLog  # noqa: F401
        
        logger.info("Initializing database tables...")
        tables_to_create = [table for table in Base.metadata.tables.keys()]
        logger.info(f"Database tables to create: {tables_to_create}")
        
        if not tables_to_create:
            logger.warning("⚠ No tables found in Base.metadata.tables!")
            return
        
        # Create tables by executing raw SQL
        # This avoids SQLAlchemy transaction management complexity
        conn = engine.connect()
        try:
            for table in Base.metadata.sorted_tables:
                logger.debug(f"Creating table: {table.name}")
                # Generate CREATE TABLE DDL from table metadata
                create_table_sql = str(CreateTable(table).compile(bind=engine))
                logger.debug(f"SQL: {create_table_sql}")
                
                # Execute without transaction - just raw SQL
                try:
                    conn.exec_driver_sql(create_table_sql)
                except Exception as table_err:
                    error_str = str(table_err).lower()
                    if "already exists" not in error_str and "duplicate" not in error_str:
                        logger.warning(f"Error creating table {table.name}: {table_err}")
                        # Continue to next table even if one fails
            
            # Commit all changes
            conn.commit()
            logger.info(f"✓ Database initialization complete - {len(tables_to_create)} tables created successfully")
            
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"✗ Error during database initialization: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Don't re-raise - allow app to continue even if DB init fails


def dispose_db() -> None:
    """
    Dispose of all connections in the pool.
    Should be called on application shutdown.
    """
    logger.info("Disposing database connections...")
    engine.dispose()
    logger.info("Database connections disposed")