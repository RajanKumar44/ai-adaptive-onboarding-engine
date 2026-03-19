"""
User model for database persistence.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    """
    User model for storing user information.
    
    Attributes:
        id: Primary key
        email: User email address (unique)
        name: User full name
        created_at: Account creation timestamp
        analyses: Relationship to Analysis records
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to Analysis records
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
