"""Message schemas"""
from pydantic import BaseModel
from datetime import datetime


class MessageBase(BaseModel):
    """Base message schema"""
    receiver_id: int
    content: str


class MessageCreate(MessageBase):
    """Message creation schema"""
    pass


class MessageOut(BaseModel):
    """Message output schema"""
    id: int
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True
