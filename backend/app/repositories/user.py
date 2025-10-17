"""User repository for database operations"""
from typing import Optional, List
from sqlalchemy import select
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
        
        user = User(
            email=email.lower(),
            hashed_password=hashed_password,
            full_name=full_name,
            role=role
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        query = select(User).where(User.email == email.lower())
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password"""
        user = await self.get_by_email(email)
        
        if not user:
            return None
        
        # Check for account lockout
        if user.failed_login_attempts >= 5:
            logger.warning(f"Account locked for user {email}")
            return None
        
        # Verify password
        if not SecurityService.verify_password(password, user.hashed_password):
            # Increment failed attempts
            user.failed_login_attempts += 1
            await self.db.commit()
            return None
        
        # Reset failed attempts on successful login
        from datetime import datetime, timezone as tz
        user.failed_login_attempts = 0
        user.last_login = datetime.now(tz.utc)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def list_by_role(self, role: UserRole) -> List[User]:
        """List users by role"""
        query = select(User).where(User.role == role)
        result = await self.db.execute(query)
        return result.scalars().all()
