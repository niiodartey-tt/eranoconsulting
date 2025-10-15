# backend/app/api/auth.py  (replace file)
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from .. import schemas, crud, utils
from ..db import AsyncSessionLocal
from pydantic import EmailStr
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional

router = APIRouter(prefix="/auth", tags=["auth"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/register", response_model=schemas.UserOut, status_code=201)
async def register(payload: schemas.ClientRegister, db: AsyncSession = Depends(get_db)):
    existing = await crud.get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")
    user = await crud.create_user(db, payload.email, payload.password, role="client")
    await crud.create_client_for_user(
        db,
        user.id,
        company_name=payload.company_name,
        contact_name=payload.contact_name,
        contact_phone=payload.contact_phone,
    )
    return user


@router.post("/login", response_model=schemas.TokenWithRefresh)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await crud.get_user_by_email(db, form_data.username)
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials."
        )
    access_token = utils.create_access_token(
        subject=user.id,
        email=user.email,
        role=user.role,
        expires_delta=timedelta(minutes=utils.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = access_token  # Temporary fix for local dev
    expires_at = utils.get_refresh_expires_at()
    # store refresh token
    await crud.create_refresh_token(db, user.id, refresh_token, expires_at)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


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
