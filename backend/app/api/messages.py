# backend/app/api/messages.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import get_current_user
from app.db import get_db
from app import models, schemas, crud, utils

router = APIRouter(tags=["Messages"])


@router.post("/", response_model=schemas.MessageOut)
async def create_message(
    message_in: schemas.MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Send a message between users."""
    new_message = await crud.create_message(db, message_in, current_user.id)
    return new_message


@router.get("/", response_model=list[schemas.MessageOut])
async def get_messages(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Retrieve all messages related to the current user."""
    return await crud.get_user_messages(db, current_user.id)


@router.get("/{message_id}", response_model=schemas.MessageOut)
async def get_message_by_id(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a single message by ID if the user is authorized to see it."""
    msg = await crud.get_message_by_id(db, message_id)
    if not msg or (
        msg.sender_id != current_user.id and msg.receiver_id != current_user.id
    ):
        raise HTTPException(
            status_code=404, detail="Message not found or not accessible"
        )
    return msg
