# backend/app/api/admin.py
import os
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import AsyncSessionLocal
from .. import crud
from jose import jwt
from dotenv import load_dotenv
from ..schemas import ClientOut
from typing import List
from ..dependencies import get_current_admin, get_db

load_dotenv()
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change_me_in_prod")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

router = APIRouter(prefix="/admin", tags=["admin"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# simple admin dependency:
async def admin_required(request: Request, db: AsyncSession = Depends(get_db)):
    auth = request.headers.get("authorization")
    if not auth:
        raise HTTPException(status_code=401, detail="Missing auth header.")
    scheme, _, token = auth.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid auth header.")
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        role = payload.get("role", "client")
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token.")
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required.")
    # optionally return the admin user record
    q = await db.execute(
        __import__("sqlalchemy")
        .select(__import__("..models", fromlist=["models"]).models.User)
        .where(__import__("..models", fromlist=["models"]).models.User.id == user_id)
    )
    user = q.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="Admin user not found.")
    return user


@router.get("/clients", response_model=List[ClientOut])
async def list_clients(
    db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)
):
    clients = await crud.list_clients(db)
    return clients


@router.post("/clients/{client_id}/status")
async def set_client_status(
    client_id: int,
    status: str,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    if status not in ("pending", "active", "rejected"):
        raise HTTPException(status_code=400, detail="Invalid status.")
    client = await db.get(
        __import__("..models", fromlist=["models"]).models.Client, client_id
    )
    if not client:
        raise HTTPException(status_code=404, detail="Client not found.")
    client.status = status
    await db.commit()
    await db.refresh(client)
    return {"detail": "updated", "client_id": client_id, "status": status}
