"""File upload and download endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import os
from pathlib import Path
import secrets
import aiofiles
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.uploaded_file import UploadedFile

router = APIRouter()

# Ensure upload directory exists
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed MIME types
ALLOWED_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a file"""
    
    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not allowed"
        )
    
    # Validate file size (read in chunks)
    file_size = 0
    chunk_size = 1024 * 1024  # 1MB chunks
    chunks = []
    
    while chunk := await file.read(chunk_size):
        file_size += len(chunk)
        chunks.append(chunk)
        
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
            )
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{secrets.token_urlsafe(16)}{file_extension}"
    
    # Create user-specific directory
    user_dir = UPLOAD_DIR / str(current_user.id)
    user_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = user_dir / unique_filename
    
    # Save file
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            for chunk in chunks:
                await f.write(chunk)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Save to database
    db_file = UploadedFile(
        filename=file.filename,
        path=str(file_path),
        file_type=file.content_type,
        uploader_id=current_user.id
    )
    
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)
    
    return {
        "id": db_file.id,
        "filename": db_file.filename,
        "file_type": db_file.file_type,
        "uploaded_at": db_file.created_at,
        "message": "File uploaded successfully"
    }


@router.get("/my-files")
async def get_my_files(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all files uploaded by current user"""
    
    stmt = select(UploadedFile).where(UploadedFile.uploader_id == current_user.id).order_by(UploadedFile.created_at.desc())
    result = await db.execute(stmt)
    files = result.scalars().all()
    
    return [
        {
            "id": f.id,
            "filename": f.filename,
            "file_type": f.file_type,
            "uploaded_at": f.created_at,
            "size_mb": round(os.path.getsize(f.path) / 1024 / 1024, 2) if os.path.exists(f.path) else 0
        }
        for f in files
    ]


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a file"""
    
    stmt = select(UploadedFile).where(
        UploadedFile.id == file_id,
        UploadedFile.uploader_id == current_user.id
    )
    result = await db.execute(stmt)
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Delete physical file
    try:
        if os.path.exists(file.path):
            os.remove(file.path)
    except Exception as e:
        print(f"Error deleting file: {e}")
    
    # Delete from database
    await db.delete(file)
    await db.commit()
    
    return {"message": "File deleted successfully"}
