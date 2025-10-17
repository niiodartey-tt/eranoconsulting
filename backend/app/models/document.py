"""Document model for general client document storage"""
from sqlalchemy import Column, String, Integer, ForeignKey, Index, DateTime, Text, BigInteger, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models.base import BaseModel


class Document(BaseModel):
    """General document storage for clients"""

    __tablename__ = "documents"
    __table_args__ = (
        Index("ix_document_client", "client_id"),
        Index("ix_document_category", "category"),
        Index("ix_document_year_quarter", "year", "quarter"),
    )

    # Link to client
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Document information
    category = Column(String(50), nullable=False, index=True)  # bank_statements, tax_filings, etc.
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    
    # Organization
    year = Column(String(4), nullable=False, index=True)  # "2025"
    quarter = Column(String(20), nullable=False, index=True)  # "q1_jan_mar"
    document_date = Column(DateTime(timezone=True), nullable=True)  # Actual document date
    
    # Metadata
    description = Column(Text, nullable=True)
    tags = Column(ARRAY(String), nullable=True, default=[])
    
    # Upload tracking
    uploaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    uploaded_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    client = relationship("Client", foreign_keys=[client_id])
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])

    def __repr__(self):
        return f"<Document(id={self.id}, client_id={self.client_id}, category='{self.category}')>"
