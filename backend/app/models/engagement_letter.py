"""Engagement Letter model for client agreements"""
from sqlalchemy import (
    Column, String, Integer, ForeignKey, Index, 
    DateTime, Text, ARRAY
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models.base import BaseModel


class EngagementLetter(BaseModel):
    """Engagement letter generation and signature tracking"""

    __tablename__ = "engagement_letters"
    __table_args__ = (
        Index("ix_engagement_client", "client_id"),
        Index("ix_engagement_status", "status"),
    )

    # Link to client
    client_id = Column(
        Integer,
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Letter Content
    services_included = Column(
        ARRAY(String),
        nullable=False
    )  # List of services covered
    
    scope_of_work = Column(Text, nullable=False)  # Detailed scope
    
    fee_structure = Column(Text, nullable=False)  # Fee details
    
    terms_and_conditions = Column(Text, nullable=False)  # T&Cs
    
    duration = Column(String(100), nullable=True)  # e.g., "12 months"
    
    commencement_date = Column(DateTime(timezone=True), nullable=True)
    
    # Document Information
    document_path = Column(String(500), nullable=True)  # PDF file path
    document_version = Column(Integer, default=1, nullable=False)
    
    # Generation Information
    generated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    generated_by_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Signature Information
    status = Column(
        String(50),
        default="draft",
        nullable=False,
        index=True
    )  # "draft", "sent", "signed", "expired"
    
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    signature_data = Column(Text, nullable=True)  # Base64 signature image
    signed_at = Column(DateTime(timezone=True), nullable=True)
    signed_ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    
    # Electronic Signature Consent
    client_consent = Column(Integer, default=False, nullable=False)  # Boolean as int
    consent_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Admin Notes
    notes = Column(Text, nullable=True)

    # Relationships
    client = relationship("Client", back_populates="engagement_letters")
    generated_by = relationship("User", foreign_keys=[generated_by_id])

    def __repr__(self):
        return (
            f"<EngagementLetter(id={self.id}, client_id={self.client_id}, "
            f"status='{self.status}', signed={self.is_signed})>"
        )

    @property
    def is_signed(self) -> bool:
        """Check if engagement letter is signed"""
        return self.status == "signed" and self.signed_at is not None

    @property
    def is_expired(self) -> bool:
        """Check if engagement letter has expired"""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_pending_signature(self) -> bool:
        """Check if awaiting client signature"""
        return self.status == "sent" and not self.is_signed and not self.is_expired
