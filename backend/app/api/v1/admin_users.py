"""Admin user management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_admin
from app.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.core.security import SecurityService

router = APIRouter()


class CreateUserRequest(BaseModel):
    """Request to create a new user"""

    email: EmailStr
    password: str
    full_name: str
    role: UserRole


class UserResponse(BaseModel):
    """User response model"""

    id: int
    email: str
    full_name: str | None
    role: str
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True


@router.post("/users/create", response_model=UserResponse)
async def create_user(
    request: CreateUserRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Create a new user (admin or staff only)"""

    user_repo = UserRepository(User, db)

    # Check if user already exists
    existing_user = await user_repo.get_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Validate password strength
    if len(request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long",
        )

    # Only admins can create other admins
    if request.role == UserRole.ADMIN and admin.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create admin accounts",
        )

    # Create the user
    hashed_password = SecurityService.hash_password(request.password)

    new_user = User(
        email=request.email,
        hashed_password=hashed_password,
        full_name=request.full_name,
        role=request.role,
        is_active=True,
        is_verified=True,  # Auto-verify staff/admin accounts
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.get("/users/staff", response_model=List[UserResponse])
async def list_staff_users(
    db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_admin)
):
    """List all staff and admin users"""

    user_repo = UserRepository(User, db)

    # Get all non-client users
    from sqlalchemy import select, or_

    query = select(User).where(
        or_(User.role == UserRole.ADMIN, User.role == UserRole.STAFF)
    )
    result = await db.execute(query)
    users = result.scalars().all()

    return users


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Delete a user account"""

    user_repo = UserRepository(User, db)
    user = await user_repo.get(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Prevent deleting yourself
    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    # Only admins can delete other admins
    if user.role == UserRole.ADMIN and admin.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete admin accounts",
        )

    await user_repo.delete(user_id)

    return {"message": "User deleted successfully", "user_id": user_id}


@router.put("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    new_password: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Reset a user's password"""

    user_repo = UserRepository(User, db)
    user = await user_repo.get(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long",
        )

    # Update password
    user.hashed_password = SecurityService.hash_password(new_password)
    await db.commit()

    return {"message": "Password reset successfully", "user_id": user_id}
