"""Authentication schemas"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class Token(BaseModel):
    """Access token response"""

    access_token: str
    token_type: str = "bearer"


class TokenResponse(BaseModel):
    """Token response with refresh token"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# Add this class
class UserResponse(BaseModel):
    """User response schema for registration"""

    id: int
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2
        # orm_mode = True  # Pydantic v1


class UserCreate(BaseModel):
    """User registration schema"""

    email: EmailStr
    password: str
    full_name: Optional[str] = None


class TokenPayload(BaseModel):
    """JWT token payload"""

    sub: Optional[int] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = "client"
