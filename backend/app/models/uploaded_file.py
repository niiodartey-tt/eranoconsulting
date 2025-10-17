"""Uploaded file model for document management"""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class UploadedFile(BaseModel):
    """Uploaded file model for document management"""

    __tablename__ = "files"
    __table_args__ = (
        Index("ix_file_uploader", "uploader_id"),
        Index("ix_file_type", "file_type"),
    )

    # File metadata
    filename = Column(String(512), nullable=False)
    path = Column(Text, nullable=False)
    file_type = Column(String(100), nullable=True)  # 'kyc', 'receipt', 'other'
    uploader_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    user = relationship("User", back_populates="uploaded_files")

    def __repr__(self):
        return f"<UploadedFile(id={self.id}, filename='{self.filename}', type='{self.file_type}')>"
