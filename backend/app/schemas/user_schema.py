"""
User Pydantic schemas for validation and serialization.
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    pass


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    created_at: datetime
    
    class Config:
        """Pydantic config."""
        from_attributes = True


class UserInDB(UserResponse):
    """Schema for user in database."""
    pass
