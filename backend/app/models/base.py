"""
Base model with common audit fields for all database entities.
Provides soft delete functionality and audit tracking.
"""

from sqlalchemy import Column, Integer, DateTime, String, Boolean, Index
from sqlalchemy.orm import declarative_mixin
from datetime import datetime
from app.core.database import Base


@declarative_mixin
class AuditedBase:
    """
    Mixin class that adds audit fields to all models.
    
    Attributes:
        created_at: When the record was created
        created_by: User ID who created the record
        updated_at: When the record was last updated
        updated_by: User ID who last updated the record
        deleted_at: When the record was soft deleted (NULL if not deleted)
    """
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_by = Column(Integer, nullable=True)  # User ID
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    updated_by = Column(Integer, nullable=True)  # User ID
    deleted_at = Column(DateTime, nullable=True, index=True)  # Soft delete
    
    @property
    def is_deleted(self) -> bool:
        """Check if record is soft deleted."""
        return self.deleted_at is not None
    
    def soft_delete(self, user_id: int = None) -> None:
        """Mark record as deleted without removing it."""
        self.deleted_at = datetime.utcnow()
        self.updated_by = user_id
    
    def restore(self, user_id: int = None) -> None:
        """Restore a soft-deleted record."""
        self.deleted_at = None
        self.updated_by = user_id
