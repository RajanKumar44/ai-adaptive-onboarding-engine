"""
AuditLog model for tracking all database changes.
Provides complete audit trail of who did what, when, and what changed.
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Index, ForeignKey
from datetime import datetime
from app.core.database import Base
import enum


class AuditAction(str, enum.Enum):
    """Types of audit actions."""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    RESTORE = "RESTORE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"


class AuditLog(Base):
    """
    Audit log model for tracking all changes to the system.
    
    Attributes:
        id: Primary key
        user_id: User who performed the action
        table_name: Which table was affected
        record_id: ID of the affected record
        action: Type of action (CREATE, UPDATE, DELETE, etc.)
        old_values: Previous values (JSON) - for updates and deletes
        new_values: New values (JSON) - for creates and updates
        changes: Summary of what changed (JSON) - for updates
        ip_address: IP address of the request
        user_agent: Browser/client information
        timestamp: When the action occurred
        description: Human-readable description
        
    Indexes:
        - user_id: Fast lookup by user
        - table_name + record_id: Fast lookup by entity
        - timestamp: Fast lookup by time range
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    table_name = Column(String(100), nullable=False, index=True)
    record_id = Column(Integer, nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    
    # Full values for tracking changes
    old_values = Column(JSON, nullable=True)  # Previous data
    new_values = Column(JSON, nullable=True)  # Updated data
    changes = Column(JSON, nullable=True)  # Only the fields that changed
    
    # Request context
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Indexes for common queries
    __table_args__ = (
        Index('ix_audit_logs_user_table_action', 'user_id', 'table_name', 'action'),
        Index('ix_audit_logs_table_record', 'table_name', 'record_id'),
        Index('ix_audit_logs_timestamp_range', 'timestamp'),
    )
