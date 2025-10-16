from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas
from app.db import get_db
from app.utils import get_current_user

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post("/send", response_model=schemas.MessageOut)
async def send_message(
    msg: schemas.MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id == msg.receiver_id:
        raise HTTPException(status_code=400, detail="Cannot send message to yourself")

    message = await crud.create_message(
        db, current_user.id, msg.receiver_id, msg.content
    )
    return message


@router.get("/conversation/{user_id}", response_model=list[schemas.MessageOut])
async def get_conversation(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    messages = await crud.get_conversation(db, current_user.id, user_id)
    return messages
