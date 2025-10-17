"""File schemas"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FileOut(BaseModel):
    """File output schema"""

    id: int
    filename: str
    file_type: Optional[str]
    created_at: datetime
    uploader_id: Optional[int]

    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    """File upload response"""

    id: int
    filename: str
    file_type: str
    message: str
