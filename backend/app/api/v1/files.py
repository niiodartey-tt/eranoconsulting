"""File upload and download endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import os
from pathlib import Path
import uuid

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.uploaded_file import UploadedFile as FileModel
from app.schemas.file import FileOut, FileUploadResponse
from app.repositories.base import BaseRepository

router = APIRouter()

# Ensure upload directory exists
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = "other",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a file"""
    # Validate file type
    if file_type not in ["kyc", "receipt", "other"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Must be 'kyc', 'receipt', or 'other'"
        )
    
    # Validate file size
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE} bytes"
        )
    
    # Validate MIME type
    if file.content_type not in settings.ALLOWED_UPLOAD_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed: {file.content_type}"
        )
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{current_user.id}_{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Save to database
    file_repo = BaseRepository(FileModel, db)
    db_file = FileModel(
        filename=file.filename,
        path=str(file_path),
        file_type=file_type,
        uploader_id=current_user.id
    )
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)
    
    return FileUploadResponse(
        id=db_file.id,
        filename=db_file.filename,
        file_type=db_file.file_type,
        message="File uploaded successfully"
    )


@router.get("/", response_model=List[FileOut])
async def list_my_files(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List current user's files"""
    file_repo = BaseRepository(FileModel, db)
    files = await file_repo.list(
        skip=skip,
        limit=limit,
        filters={"uploader_id": current_user.id}
    )
    return files


@router.get("/{file_id}", response_model=FileOut)
async def get_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get file metadata"""
    file_repo = BaseRepository(FileModel, db)
    file = await file_repo.get(file_id)
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check ownership
    if file.uploader_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this file"
        )
    
    return file


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a file"""
    file_repo = BaseRepository(FileModel, db)
    file = await file_repo.get(file_id)
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check ownership
    if file.uploader_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this file"
        )
    
    # Delete physical file
    try:
        os.remove(file.path)
    except FileNotFoundError:
        pass  # File already deleted
    
    # Delete from database
    await file_repo.delete(file_id)
    return None
