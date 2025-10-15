# backend/app/dependencies.py
from fastapi import Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .db import AsyncSessionLocal
from . import utils, crud
from jose import JWTError
from typing import Optional


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    auth = request.headers.get("authorization")
    if not auth:
        raise HTTPException(status_code=401, detail="Missing authorization header.")
    scheme, _, token = auth.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid auth header.")
    payload = utils.decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    try:
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token payload.")
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")
    return user


async def get_current_admin(user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required.")
    return user
