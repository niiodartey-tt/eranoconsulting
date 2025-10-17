# backend/app/crud.py
from sqlalchemy.future import select
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from . import models, utils
from .models import Message
from datetime import datetime
from .models import RefreshToken, User
from app.utils import verify_password


async def get_user_by_id(db: AsyncSession, user_id: int):
    return await db.get(User, user_id)


async def get_user_by_email(db: AsyncSession, email: str):
    q = select(models.User).where(models.User.email == email)
    res = await db.execute(q)
    return res.scalars().first()


async def create_refresh_token(
    db: AsyncSession, user_id: int, token: str, expires_at: datetime
):
    rt = RefreshToken(token=token, user_id=user_id, expires_at=expires_at)
    db.add(rt)
    await db.commit()
    await db.refresh(rt)
    return rt


async def get_refresh_token(db: AsyncSession, token: str):
    q = select(RefreshToken).where(RefreshToken.token == token)
    res = await db.execute(q)
    return res.scalars().first()


async def revoke_refresh_token(db: AsyncSession, token: str):
    rt = await get_refresh_token(db, token)
    if not rt:
        return None
    rt.revoked = True
    await db.commit()
    await db.refresh(rt)
    return rt


async def create_user(
    db: AsyncSession, email: str, password: str, role: str = "client"
):
    hashed = utils.hash_password(password)
    user = models.User(email=user.email, hashed_password=hashed, role=role)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return new_user


async def create_client_for_user(
    db: AsyncSession,
    user_id: int,
    company_name=None,
    contact_name=None,
    contact_phone=None,
):
    client = models.Client(
        user_id=user_id,
        company_name=company_name,
        contact_name=contact_name,
        contact_phone=contact_phone,
        contact_email=None,
    )
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client


async def list_clients(db: AsyncSession, limit: int = 100):
    q = select(models.Client).order_by(models.Client.created_at.desc()).limit(limit)
    res = await db.execute(q)
    return res.scalars().all()


async def mark_kyc_uploaded(db: AsyncSession, client_id: int):
    q = await db.get(models.Client, client_id)
    if not q:
        return None
    q.kyc_uploaded = True
    await db.commit()
    await db.refresh(q)
    return q


async def save_file_record(
    db: AsyncSession, filename: str, path: str, file_type: str, uploader_id: int
):
    rec = models.FileRecord(
        filename=filename, path=path, file_type=file_type, uploader_id=uploader_id
    )
    db.add(rec)
    await db.commit()
    await db.refresh(rec)
    return rec


async def create_message(db, sender_id: int, receiver_id: int, content: str):
    msg = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


async def get_conversation(db, user_a: int, user_b: int):
    q = (
        select(Message)
        .where(
            ((Message.sender_id == user_a) & (Message.receiver_id == user_b))
            | ((Message.sender_id == user_b) & (Message.receiver_id == user_a))
        )
        .order_by(Message.timestamp.asc())
    )
    res = await db.execute(q)
    return res.scalars().all()


async def authenticate_user(db, email: str, password: str):
    """Authenticate user by email and password"""
    from app.models import User

    q = select(User).where(User.email == email)
    result = await db.execute(q)
    user = result.scalar_one_or_none()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


# backend/app/crud.py (add these near the end)

from sqlalchemy import select
from app import models, schemas


async def create_message(db, message_in: schemas.MessageCreate, sender_id: int):
    new_message = models.Message(
        sender_id=sender_id,
        receiver_id=message_in.receiver_id,
        content=message_in.content,
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message


async def get_user_messages(db, user_id: int):
    result = await db.execute(
        select(models.Message).where(
            (models.Message.sender_id == user_id)
            | (models.Message.receiver_id == user_id)
        )
    )
    return result.scalars().all()


async def get_message_by_id(db, message_id: int):
    result = await db.execute(
        select(models.Message).where(models.Message.id == message_id)
    )
    return result.scalar_one_or_none()
