"""Pydantic schemas for authentication."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class PasswordResetRequest(BaseModel):
    """Schema for requesting a password reset email."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for confirming a password reset with token."""
    token: str
    new_password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    """Schema for changing password while logged in."""
    current_password: str
    new_password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    """Schema for user data in responses."""
    id: UUID
    email: str
    username: str
    is_approved: bool
    is_league_admin: bool
    is_owner: bool
    is_primary_owner: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)

