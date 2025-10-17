"""Authentication schemas"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class Token(BaseModel):
    """Access token response"""
    access_token: str
    token_type: str = "bearer"


class TokenResponse(BaseModel):
    """Token response with refresh token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


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
