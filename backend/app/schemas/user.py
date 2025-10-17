"""User schemas"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserOut(BaseModel):
    """User output schema"""

    id: int
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2
        # orm_mode = True  # Pydantic v1


class UserUpdate(BaseModel):
    """User update schema"""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
