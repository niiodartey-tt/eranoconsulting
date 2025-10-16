# backend/app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


# Auth
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[int] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = "client"


# User / Register
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


# Client registration payload
class ClientRegister(BaseModel):
    email: EmailStr
    password: str
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None


# Client summary
class ClientOut(BaseModel):
    id: int
    user_id: int
    company_name: Optional[str]
    contact_email: Optional[EmailStr]
    status: str
    kyc_uploaded: bool
    payment_verified: bool
    created_at: datetime

    class Config:
        orm_mode = True


class TokenWithRefresh(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class MessageBase(BaseModel):
    content: str
    receiver_id: int


class MessageCreate(MessageBase):
    pass


class MessageOut(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime

    class Config:
        orm_mode = True
