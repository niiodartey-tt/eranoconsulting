# app/services/auth.py
from typing import Optional, Tuple
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user import UserRepository
from app.repositories.refresh_token import RefreshTokenRepository
from app.models.user import User, UserRole
from app.schemas.auth import TokenResponse, UserCreate
from app.core.security import SecurityService
from app.core.config import settings
import secrets
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """Service for authentication operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(User, db)
        self.token_repo = RefreshTokenRepository(RefreshToken, db)
    
    async def register(
        self,
        user_data: UserCreate,
        role: UserRole = UserRole.CLIENT
    ) -> User:
        """Register new user"""
        # Check if user exists
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Validate password strength
        self._validate_password_strength(user_data.password)
        
        # Create user
        user = await self.user_repo.create_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            role=role
        )
        
        # Send verification email (implement email service)
        # await self.email_service.send_verification_email(user)
        
        return user
    
    async def login(self, email: str, password: str) -> TokenResponse:
        """Login user and return tokens"""
        user = await self.user_repo.authenticate(email, password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Generate tokens
        access_token = SecurityService.create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value
            }
        )
        
        refresh_token = await self._create_refresh_token(user.id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token"""
        token_obj = await self.token_repo.get_valid_token(refresh_token)
        
        if not token_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user = await self.user_repo.get(token_obj.user_id)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not found or inactive"
            )
        
        # Revoke old token
        await self.token_repo.revoke_token(refresh_token)
        
        # Generate new tokens
        access_token = SecurityService.create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value
            }
        )
        
        new_refresh_token = await self._create_refresh_token(user.id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )
    
    async def _create_refresh_token(self, user_id: int) -> str:
        """Create refresh token"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        await self.token_repo.create(
            token=token,
            user_id=user_id,
            expires_at=expires_at
        )
        
        return token
    
    def _validate_password_strength(self, password: str):
        """Validate password meets security requirements"""
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters"
            )
        
        if not any(c.isupper() for c in password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one uppercase letter"
            )
        
        if not any(c.islower() for c in password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one lowercase letter"
            )
        
        if not any(c.isdigit() for c in password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one digit"
            )
