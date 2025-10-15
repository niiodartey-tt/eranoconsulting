# backend/app/api/onboarding.py
import os
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import AsyncSessionLocal
from .. import crud, utils
from jose import jwt
from dotenv import load_dotenv

load_dotenv()
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# helper to extract current user from Authorization header
from fastapi import Request
from jose import JWTError
from ..utils import JWT_SECRET_KEY, JWT_ALGORITHM


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
        raise HTTPException(status_code=401, detail="Invalid token.")
    user = await db.get(
        crud.__import__("..models", fromlist=["models"]).models.User, user_id
    )  # safer to use get_user_by_email; but we can fetch
    if not user:
        # fallback: query
        q = await db.execute(
            __import__("sqlalchemy")
            .select(__import__("..models", fromlist=["models"]).models.User)
            .where(
                __import__("..models", fromlist=["models"]).models.User.id == user_id
            )
        )
        user = q.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")
    return user


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = Form(...),  # e.g. 'kyc' or 'payment_receipt'
    db: AsyncSession = Depends(get_db),
    request=Depends(get_current_user),
):
    user = request
    # Validate file type
    if file_type not in ("kyc", "payment_receipt", "other"):
        raise HTTPException(status_code=400, detail="Invalid file_type.")
    # Secure filename handling
    import uuid, pathlib

    ext = pathlib.Path(file.filename).suffix
    safe_name = f"{uuid.uuid4().hex}{ext}"
    dest_path = os.path.join(UPLOAD_DIR, safe_name)

    # Save file to disk (async)
    import aiofiles

    try:
        async with aiofiles.open(dest_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save error: {e}")

    # Store metadata in DB
    rec = await crud.save_file_record(
        db,
        filename=file.filename,
        path=dest_path,
        file_type=file_type,
        uploader_id=user.id,
    )

    # If this file is a KYC for a client's account, mark kyc_uploaded
    if file_type == "kyc":
        # fetch client by user_id
        q = await db.execute(
            __import__("sqlalchemy")
            .select(__import__("..models", fromlist=["models"]).models.Client)
            .where(
                __import__("..models", fromlist=["models"]).models.Client.user_id
                == user.id
            )
        )
        client = q.scalars().first()
        if client:
            client.kyc_uploaded = True
            await db.commit()
            await db.refresh(client)

    return {"detail": "uploaded", "file_id": rec.id}
