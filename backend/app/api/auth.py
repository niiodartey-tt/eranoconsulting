from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app import schemas, crud, utils
from app.db import get_db


router = APIRouter()


@router.post("/register")
async def register_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = await crud.create_user(db, user)
    return {"msg": "User registered successfully", "user": new_user.email}


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    access_token = utils.create_access_token(user.id, user.email, user.role)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=schemas.Token)
async def refresh(
    refresh_token: Optional[str] = None, db: AsyncSession = Depends(get_db)
):
    """
    Exchange a valid refresh_token for a new access token.
    For production, you should pass refresh token via secure httpOnly cookie.
    Here we accept it in JSON or form (client should POST {"refresh_token": "..."}).
    """
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Missing refresh_token.")
    rt = await crud.get_refresh_token(db, refresh_token)
    if not rt or rt.revoked:
        raise HTTPException(status_code=401, detail="Invalid refresh token.")
    from datetime import datetime, timezone

    if rt.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired.")
    user = await crud.get_user_by_id(db, rt.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")
    access_token = utils.create_access_token(
        subject=user.id, email=user.email, role=user.role
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/revoke_refresh")
async def revoke_refresh(
    refresh_token: Optional[str] = None, db: AsyncSession = Depends(get_db)
):
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Missing refresh_token.")
    rt = await crud.revoke_refresh_token(db, refresh_token)
    if not rt:
        raise HTTPException(status_code=404, detail="Refresh token not found.")
    return {"detail": "revoked"}
