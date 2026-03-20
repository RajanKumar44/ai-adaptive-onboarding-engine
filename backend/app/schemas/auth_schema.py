"""
Pydantic schemas for authentication.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.user import UserRole


class TokenResponse(BaseModel):
    """Response for token generation."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")


class RegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr = Field(..., description="User email")
    name: str = Field(..., min_length=2, max_length=255, description="Full name")
    password: str = Field(..., min_length=8, description="Password")
    confirm_password: str = Field(..., description="Confirm password")
    
    def validate_passwords_match(self) -> bool:
        """Check if passwords match."""
        return self.password == self.confirm_password


class LoginRequest(BaseModel):
    """User login request."""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="Password")


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str = Field(..., description="Refresh token")


class ChangePasswordRequest(BaseModel):
    """Change password request."""
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")


class UpdateProfileRequest(BaseModel):
    """Update user profile request."""
    name: Optional[str] = Field(None, min_length=2, max_length=255, description="Full name")
    email: Optional[EmailStr] = Field(None, description="Email address")


class UserResponse(BaseModel):
    """User response (no password hash)."""
    id: int
    email: str
    name: Optional[str]
    role: UserRole
    is_active: bool
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """Detailed user response with additional metadata."""
    analyses_count: int = Field(default=0, description="Number of analyses by user")


class LogoutResponse(BaseModel):
    """Logout response."""
    message: str = Field(default="Successfully logged out")
    status: str = Field(default="success")
