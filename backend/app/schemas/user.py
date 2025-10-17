# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr

class UserCreate(BaseModel):
    """User creation schema"""
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserOut(BaseModel):
    """User output schema"""
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """User update schema"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    
    class Config:
        from_attributes = True
