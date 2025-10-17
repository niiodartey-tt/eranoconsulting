# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.auth import AuthService
from app.schemas.auth import UserCreate, TokenResponse
from app.schemas.user import UserOut
from app.models.user import UserRole
from app.core.rate_limit import rate_limit
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", response_model=UserOut)
@rate_limit(requests=5, period=3600)  # 5 requests per hour
async def register(
    user_data: UserCreate, request: Request, db: AsyncSession = Depends(get_db)
):
    """Register new user"""
    service = AuthService(db)
    user = await service.register(user_data)
    return UserOut.from_orm(user)


@router.post("/login", response_model=TokenResponse)
@rate_limit(requests=10, period=60)  # 10 requests per minute
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    response: Response = None,
    db: AsyncSession = Depends(get_db),
):
    """Login user"""
    service = AuthService(db)
    tokens = await service.login(form_data.username, form_data.password)

    # Set refresh token as httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=30 * 24 * 60 * 60,  # 30 days
    )

    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request, response: Response, db: AsyncSession = Depends(get_db)
):
    """Refresh access token"""
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found"
        )

    service = AuthService(db)
    tokens = await service.refresh_token(refresh_token)

    # Update refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=30 * 24 * 60 * 60,
    )

    return tokens


@router.post("/logout")
async def logout(
    request: Request, response: Response, db: AsyncSession = Depends(get_db)
):
    """Logout user"""
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:
        # Revoke token in database
        service = AuthService(db)
        await service.revoke_token(refresh_token)

    # Clear cookie
    response.delete_cookie("refresh_token")

    return {"message": "Logged out successfully"}
