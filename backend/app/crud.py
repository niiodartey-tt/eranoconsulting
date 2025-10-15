# backend/app/crud.py
from sqlalchemy.future import select
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from . import models, utils
from datetime import datetime
from .models import RefreshToken, User


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
    user = models.User(email=email, hashed_password=hashed, role=role)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


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
