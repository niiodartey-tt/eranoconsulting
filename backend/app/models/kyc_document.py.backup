"""KYC Document model for client verification"""
from sqlalchemy import (
    Column, String, Integer, ForeignKey, Index, 
    DateTime, Text, BigInteger
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models.base import BaseModel
from app.models.enums import DocumentType, VerificationStatus


class KYCDocument(BaseModel):
    """KYC document uploads and verification tracking"""

    __tablename__ = "kyc_documents"
    __table_args__ = (
        Index("ix_kyc_client", "client_id"),
        Index("ix_kyc_verification_status", "verification_status"),
        Index("ix_kyc_document_type", "document_type"),
    )

    # Link to client
    client_id = Column(
        Integer,
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Document Information
    document_type = Column(
        String(50),
        nullable=False,
        index=True
    )  # Uses DocumentType enum values
    
    document_name = Column(String(255), nullable=False)  # Original filename
    file_path = Column(String(500), nullable=False)  # Relative path in storage
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    mime_type = Column(String(100), nullable=False)  # e.g., "application/pdf"
    
    # Upload Information
    uploaded_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Verification Status
    verification_status = Column(
        String(50),
        default=VerificationStatus.PENDING.value,
        nullable=False,
        index=True
    )
    
    # Admin Review
    verified_by_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    verification_date = Column(DateTime(timezone=True), nullable=True)
    admin_comments = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Resubmission Tracking
    is_resubmission = Column(Integer, default=False, nullable=False)  # Boolean stored as int
    resubmission_count = Column(Integer, default=0, nullable=False)
    previous_document_id = Column(
        Integer,
        ForeignKey("kyc_documents.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships
    client = relationship("Client", back_populates="kyc_documents")
    verified_by = relationship("User", foreign_keys=[verified_by_id])
    previous_document = relationship(
        "KYCDocument",
        remote_side="KYCDocument.id",
        foreign_keys=[previous_document_id]
    )

    def __repr__(self):
        return (
            f"<KYCDocument(id={self.id}, client_id={self.client_id}, "
            f"type='{self.document_type}', status='{self.verification_status}')>"
        )

    @property
    def is_approved(self) -> bool:
        """Check if document is approved"""
        return self.verification_status == VerificationStatus.APPROVED.value

    @property
    def is_pending(self) -> bool:
        """Check if document is pending review"""
        return self.verification_status == VerificationStatus.PENDING.value

    @property
    def needs_resubmission(self) -> bool:
        """Check if document needs to be resubmitted"""
        return self.verification_status == VerificationStatus.RESUBMISSION_REQUIRED.value
