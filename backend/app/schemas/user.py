"""
User schemas for API request and response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    """
    Schema for creating a new user.
    """
    email: EmailStr = Field(..., example="user@example.com")
    username: str = Field(..., min_length=3, max_length=50, example="johndoe")
    full_name: Optional[str] = Field(None, example="John Doe")


class UserUpdate(BaseModel):
    """
    Schema for updating user information.
    """
    full_name: Optional[str] = Field(None, example="John Doe")
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """
    Schema for user information response.
    """
    id: str
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    total_documents_processed: int
    last_activity_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
