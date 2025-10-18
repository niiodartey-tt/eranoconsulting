# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Response, Form
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.auth import TokenResponse, UserCreate
from app.services.auth import AuthService
from app.core.rate_limit import rate_limit

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/login", response_model=TokenResponse)
# @rate_limit(requests=10, period=60)
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Login user"""
    service = AuthService(db)
    tokens = await service.login(username, password)

    return tokens


@router.post("/register")
# @rate_limit(requests=5, period=60)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register new user"""
    service = AuthService(db)
    user = await service.register(user_data)

    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "message": "User created successfully",
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token"""
    service = AuthService(db)
    tokens = await service.refresh_token(refresh_token)

    return tokens


@router.post("/logout")
async def logout(
    current_user: dict = Depends(oauth2_scheme),
):
    """Logout user"""
    return {"message": "Logged out successfully"}
