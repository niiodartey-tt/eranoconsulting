# app/repositories/user.py
from typing import Optional, List
from sqlalchemy import select, and_, or_
from app.repositories.base import BaseRepository
from app.models.user import User, UserRole
from app.core.security import SecurityService
import logging

logger = logging.getLogger(__name__)

class UserRepository(BaseRepository[User]):
    """Repository for user operations"""
    
    async def create_user(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        role: UserRole = UserRole.CLIENT
    ) -> User:
        """Create new user with hashed password"""
        hashed_password = SecurityService.hash_password(password)
        
        return await self.create(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role
        )
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return await self.get_by(email=email.lower())
    
    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user"""
        user = await self.get_by_email(email)
        
        if not user:
            return None
        
        if user.failed_login_attempts >= 5:
            logger.warning(f"Account locked for user {email}")
            return None
        
        if not SecurityService.verify_password(password, user.hashed_password):
            await self.update(
                user.id,
                failed_login_attempts=user.failed_login_attempts + 1
            )
            return None
        
        # Reset failed attempts on successful login
        from datetime import datetime
        await self.update(
            user.id,
            failed_login_attempts=0,
            last_login=datetime.utcnow()
        )
        
        return user
    
    async def list_by_role(self, role: UserRole) -> List[User]:
        """List users by role"""
        return await self.list(filters={"role": role})
    
    async def search(self, query: str) -> List[User]:
        """Search users by email or name"""
        stmt = select(User).where(
            or_(
                User.email.ilike(f"%{query}%"),
                User.full_name.ilike(f"%{query}%")
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
