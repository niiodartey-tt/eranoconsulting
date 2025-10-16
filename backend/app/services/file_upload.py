# app/services/file_upload.py
import os
import hashlib
import aiofiles
import magic
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings
from app.models.uploaded_file import UploadedFile
from app.repositories.file import FileRepository
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

class FileUploadService:
    """Service for secure file uploads"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.file_repo = FileRepository(UploadedFile, db)
    
    async def upload_file(
        self,
        file: UploadFile,
        user_id: int,
        file_type: str = "document"
    ) -> UploadedFile:
        """Upload file with validation"""
        
        # Validate file size
        if file.size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE} bytes"
            )
        
        # Read file content
        content = await file.read()
        
        # Validate MIME type
        mime_type = magic.from_buffer(content, mime=True)
        if mime_type not in settings.ALLOWED_UPLOAD_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type {mime_type} not allowed"
            )
        
        # Generate secure filename
        file_hash = hashlib.sha256(content).hexdigest()
        extension = Path(file.filename).suffix
        secure_filename = f"{user_id}_{file_hash}{extension}"
        
        # Create upload directory if not exists
        upload_dir = Path(settings.UPLOAD_DIR) / str(user_id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = upload_dir / secure_filename
        
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save file"
            )
        
        # Save to database
        db_file = await self.file_repo.create(
            filename=file.filename,
            secure_filename=secure_filename,
            mime_type=mime_type,
            size=len(content),
            file_hash=file_hash,
            user_id=user_id,
            file_type=file_type
        )
        
        return db_file
    
    async def delete_file(self, file_id: int, user_id: int) -> bool:
        """Delete file"""
        file_obj = await self.file_repo.get(file_id)
        
        if not file_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        if file_obj.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this file"
            )
        
        # Delete physical file
        file_path = Path(settings.UPLOAD_DIR) / str(user_id) / file_obj.secure_filename
        
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
        
        # Delete from database
        return await self.file_repo.delete(file_id)
