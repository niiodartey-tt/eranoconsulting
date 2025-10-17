"""Admin panel endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_admin
from app.models.user import User, UserRole
from app.models.client import Client
from app.schemas.user import UserOut
from app.schemas.client import ClientOut
from app.repositories.user import UserRepository
from app.repositories.base import BaseRepository

router = APIRouter()


@router.get("/users", response_model=List[UserOut])
async def list_all_users(
    skip: int = 0,
    limit: int = 100,
    role: UserRole = None,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin)
):
    """List all users with optional role filter"""
    user_repo = UserRepository(User, db)
    
    if role:
        users = await user_repo.list_by_role(role)
    else:
        users = await user_repo.list(skip=skip, limit=limit)
    
    return users


@router.get("/clients", response_model=List[ClientOut])
async def list_all_clients(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin)
):
    """List all clients with optional status filter"""
    client_repo = BaseRepository(Client, db)
    
    filters = {}
    if status_filter:
        filters["status"] = status_filter
    
    clients = await client_repo.list(skip=skip, limit=limit, filters=filters)
    return clients


@router.put("/clients/{client_id}/status")
async def update_client_status(
    client_id: int,
    new_status: str,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin)
):
    """Update client status (pending/active/rejected/suspended)"""
    valid_statuses = ["pending", "active", "rejected", "suspended"]
    
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    client_repo = BaseRepository(Client, db)
    client = await client_repo.get(client_id)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    client.status = new_status
    await db.commit()
    await db.refresh(client)
    
    return {
        "message": "Client status updated",
        "client_id": client_id,
        "new_status": new_status
    }


@router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin)
):
    """Activate a user account"""
    user_repo = UserRepository(User, db)
    user = await user_repo.get(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    user.failed_login_attempts = 0  # Reset failed attempts
    await db.commit()
    
    return {"message": "User activated", "user_id": user_id}


@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin)
):
    """Deactivate a user account"""
    user_repo = UserRepository(User, db)
    user = await user_repo.get(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Don't allow deactivating yourself
    if user.id == _admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user.is_active = False
    await db.commit()
    
    return {"message": "User deactivated", "user_id": user_id}


@router.get("/stats")
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin)
):
    """Get admin dashboard statistics"""
    # Count users by role
    query = select(User.role, db.func.count(User.id)).group_by(User.role)
    result = await db.execute(query)
    user_counts = dict(result.all())
    
    # Count clients by status
    query = select(Client.status, db.func.count(Client.id)).group_by(Client.status)
    result = await db.execute(query)
    client_counts = dict(result.all())
    
    return {
        "users": user_counts,
        "clients": client_counts,
        "total_users": sum(user_counts.values()),
        "total_clients": sum(client_counts.values())
    }
