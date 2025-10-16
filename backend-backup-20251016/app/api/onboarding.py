# backend/app/api/onboarding.py

import os
from pathlib import Path
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException,
    status,
    Request,
)
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import AsyncSessionLocal
from app.models import User
from app.utils import JWT_SECRET_KEY, JWT_ALGORITHM
from app import crud

# Optional: if using .env
from dotenv import load_dotenv

load_dotenv()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


# --- Database session dependency ---
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# --- Auth helper (get current user) ---
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    auth = request.headers.get("authorization")
    if not auth:
        raise HTTPException(status_code=401, detail="Missing auth header.")

    scheme, _, token = auth.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid auth header.")

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    return user


# --- File upload route ---
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Handles client KYC or document uploads."""
    upload_dir = Path(UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)

    file_path = upload_dir / f"{current_user.id}_{file.filename}"

    try:
        # Save file
        with open(file_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Optionally: store in DB
    if hasattr(crud, "save_file_record"):
        try:
            await crud.save_file_record(
                db,
                filename=file.filename,
                path=str(file_path),
                file_type="kyc",
                uploader_id=current_user.id,
            )
        except Exception as e:
            print("DB record save failed:", e)

    return {"message": "✅ File uploaded successfully", "file": file.filename}
