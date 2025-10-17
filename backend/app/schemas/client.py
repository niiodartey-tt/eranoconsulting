"""Client schemas"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class ClientRegister(BaseModel):
    """Client registration schema"""
    email: EmailStr
    password: str
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None


class ClientOut(BaseModel):
    """Client output schema"""
    id: int
    user_id: int
    company_name: Optional[str]
    contact_email: Optional[EmailStr]
    status: str
    kyc_uploaded: bool
    payment_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True
