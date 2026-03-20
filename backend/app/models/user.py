"""
User model for database persistence.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    """
    User model for storing user information.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)

    # 🔐 For authentication (IMPORTANT)
    hashed_password = Column(String(255), nullable=True)

    # 🕒 Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 🟢 Soft delete / active user
    # NOTE:
    # - This column (and any future columns) will NOT be added automatically to an
    #   existing "users" table when using Base.metadata.create_all(...).
    # - When introducing this field into an already-deployed environment, you must
    #   either run a proper DB migration (e.g. via Alembic) or explicitly recreate
    #   the database/volume so that the column exists in the underlying schema.
    is_active = Column(Boolean, default=True, nullable=False)

    # 🔗 Relationship
    analyses = relationship(
        "Analysis",
        back_populates="user",
        cascade="all, delete-orphan"
    )