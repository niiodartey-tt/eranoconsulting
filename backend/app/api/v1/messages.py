# app/api/v1/messages.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.message import Message

router = APIRouter()

# Schemas
class MessageCreate(BaseModel):
    receiver_id: int
    content: str

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime
    sender_name: Optional[str] = None
    receiver_name: Optional[str] = None
    is_read: bool = False
    
    class Config:
        from_attributes = True


@router.post("/send", response_model=MessageResponse)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message to another user"""
    
    # Verify receiver exists
    receiver = await db.get(User, message_data.receiver_id)
    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receiver not found"
        )
    
    # Create message
    new_message = Message(
        sender_id=current_user.id,
        receiver_id=message_data.receiver_id,
        content=message_data.content,
        timestamp=datetime.utcnow()
    )
    
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    
    return MessageResponse(
        id=new_message.id,
        sender_id=new_message.sender_id,
        receiver_id=new_message.receiver_id,
        content=new_message.content,
        timestamp=new_message.timestamp,
        sender_name=current_user.full_name or current_user.email,
        receiver_name=receiver.full_name or receiver.email
    )


@router.get("/conversations", response_model=List[dict])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of conversations with latest message"""
    
    # Get all users the current user has messaged with
    stmt = select(Message).where(
        or_(
            Message.sender_id == current_user.id,
            Message.receiver_id == current_user.id
        )
    ).order_by(Message.timestamp.desc())
    
    result = await db.execute(stmt)
    messages = result.scalars().all()
    
    # Group by conversation partner
    conversations = {}
    for msg in messages:
        partner_id = msg.receiver_id if msg.sender_id == current_user.id else msg.sender_id
        
        if partner_id not in conversations:
            partner = await db.get(User, partner_id)
            conversations[partner_id] = {
                "partner_id": partner_id,
                "partner_name": partner.full_name or partner.email,
                "partner_email": partner.email,
                "last_message": msg.content,
                "last_message_time": msg.timestamp,
                "unread_count": 0
            }
    
    # Count unread messages
    for partner_id in conversations:
        unread_stmt = select(func.count()).select_from(Message).where(
            and_(
                Message.sender_id == partner_id,
                Message.receiver_id == current_user.id,
                Message.is_read == False
            )
        )
        unread_result = await db.execute(unread_stmt)
        conversations[partner_id]["unread_count"] = unread_result.scalar()
    
    return list(conversations.values())


@router.get("/with/{user_id}", response_model=List[MessageResponse])
async def get_messages_with_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all messages with a specific user"""
    
    stmt = select(Message).where(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == user_id),
            and_(Message.sender_id == user_id, Message.receiver_id == current_user.id)
        )
    ).order_by(Message.timestamp.asc())
    
    result = await db.execute(stmt)
    messages = result.scalars().all()
    
    # Mark messages as read
    for msg in messages:
        if msg.receiver_id == current_user.id and not msg.is_read:
            msg.is_read = True
    
    await db.commit()
    
    # Get sender and receiver info
    partner = await db.get(User, user_id)
    
    return [
        MessageResponse(
            id=msg.id,
            sender_id=msg.sender_id,
            receiver_id=msg.receiver_id,
            content=msg.content,
            timestamp=msg.timestamp,
            sender_name=current_user.full_name if msg.sender_id == current_user.id else (partner.full_name or partner.email),
            receiver_name=partner.full_name if msg.receiver_id == user_id else (current_user.full_name or current_user.email),
            is_read=msg.is_read
        )
        for msg in messages
    ]


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get count of unread messages"""
    
    stmt = select(func.count()).select_from(Message).where(
        and_(
            Message.receiver_id == current_user.id,
            Message.is_read == False
        )
    )
    
    result = await db.execute(stmt)
    count = result.scalar()
    
    return {"unread_count": count}


@router.delete("/{message_id}")
async def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a message"""
    
    message = await db.get(Message, message_id)
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Only sender can delete
    if message.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own messages"
        )
    
    await db.delete(message)
    await db.commit()
    
    return {"message": "Message deleted successfully"}
