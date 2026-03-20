"""
User model for database persistence.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    """
    User roles for role-based access control (RBAC).
    """
    ADMIN = "admin"           # Full system access
    USER = "user"             # Regular user access to own analyses
    GUEST = "guest"           # Read-only access


class User(Base):
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
        updated_at: Last profile update timestamp
        analyses: Relationship to Analysis records
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to Analysis records
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
