"""Refresh token repository for JWT token management"""
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import select, and_
from app.repositories.base import BaseRepository
from app.models.refresh_token import RefreshToken
import logging

logger = logging.getLogger(__name__)


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Repository for refresh token operations"""
    
    async def create_token(
        self,
        token: str,
        user_id: int,
        expires_at: datetime
    ) -> RefreshToken:
        """Create new refresh token"""
        refresh_token = RefreshToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at
        )
        
        self.db.add(refresh_token)
        await self.db.commit()
        await self.db.refresh(refresh_token)
        
        return refresh_token
    
    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """Get refresh token by token string"""
        query = select(RefreshToken).where(RefreshToken.token == token)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_valid_token(self, token: str) -> Optional[RefreshToken]:
        """Get valid (not revoked, not expired) refresh token"""
        now = datetime.now(timezone.utc)
        query = select(RefreshToken).where(
            and_(
                RefreshToken.token == token,
                RefreshToken.revoked == False,
                RefreshToken.expires_at > now
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def revoke_token(self, token: str) -> bool:
        """Revoke a refresh token"""
        token_obj = await self.get_by_token(token)
        
        if not token_obj:
            return False
        
        token_obj.revoked = True
        await self.db.commit()
        
        return True
    
    async def revoke_all_user_tokens(self, user_id: int) -> int:
        """Revoke all tokens for a user"""
        query = select(RefreshToken).where(
            and_(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked == False
            )
        )
        result = await self.db.execute(query)
        tokens = result.scalars().all()
        
        count = 0
        for token in tokens:
            token.revoked = True
            count += 1
        
        await self.db.commit()
        return count
