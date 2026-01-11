"""
User Pydantic schemas for request/response validation.

This module defines all Pydantic models for user-related API endpoints,
including request validation and response serialization.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=100, description="Username")
    full_name: str | None = Field(None, max_length=255, description="Full name")


class UserCreate(UserBase):
    """Schema for user creation request."""

    password: str = Field(..., min_length=8, max_length=100, description="User password")


class UserUpdate(BaseModel):
    """Schema for user update request."""

    email: EmailStr | None = Field(None, description="User email address")
    full_name: str | None = Field(None, max_length=255, description="Full name")
    is_active: bool | None = Field(None, description="User active status")


class UserResponse(UserBase):
    """Schema for user response."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="User ID")
    is_active: bool = Field(..., description="User active status")
    is_superuser: bool = Field(..., description="Superuser status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UserLogin(BaseModel):
    """Schema for user login request."""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")


class Token(BaseModel):
    """Schema for authentication token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """Schema for token payload data."""

    user_id: int | None = Field(None, description="User ID from token")
    username: str | None = Field(None, description="Username from token")
