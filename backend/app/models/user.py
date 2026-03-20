"""
User model for database persistence.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
from app.models.base import AuditedBase
import enum


class UserRole(str, enum.Enum):
    """
    User roles for role-based access control (RBAC).
    """
    ADMIN = "admin"           # Full system access
    USER = "user"             # Regular user access to own analyses
    GUEST = "guest"           # Read-only access


class User(Base, AuditedBase):
    """
    User model for storing user information.
    
    Attributes:
        id: Primary key
        email: User email address (unique)
        name: User full name
        password_hash: Bcrypt hashed password
        role: User's role for access control (admin, user, guest)
        is_active: Whether the user account is active
        created_at: Account creation timestamp
        created_by: User ID who created this account
        updated_at: Last profile update timestamp
        updated_by: User ID who last updated this account
        deleted_at: When account was soft deleted (NULL if active)
        analyses: Relationship to Analysis records
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationship to Analysis records
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes for frequently queried fields
    __table_args__ = (
        Index('ix_users_email_not_deleted', 'email', 'deleted_at'),
        Index('ix_users_active_deleted', 'is_active', 'deleted_at'),
        Index('ix_users_created_at', 'created_at'),
        Index('ix_users_role', 'role'),
    )
    
    @property
    def is_deleted(self) -> bool:
        """Check if user is soft deleted."""
        return self.deleted_at is not None
