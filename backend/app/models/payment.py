"""Payment model for client payment tracking"""
from sqlalchemy import (
    Column, String, Integer, ForeignKey, Index, 
    DateTime, Text, Numeric, BigInteger
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from decimal import Decimal
from app.models.base import BaseModel
from app.models.enums import VerificationStatus


class Payment(BaseModel):
    """Payment records and verification tracking"""

    __tablename__ = "payments"
    __table_args__ = (
        Index("ix_payment_client", "client_id"),
        Index("ix_payment_verification_status", "verification_status"),
        Index("ix_payment_date", "payment_date"),
    )

    # Link to client
    client_id = Column(
        Integer,
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Payment Details
    amount = Column(
        Numeric(10, 2),
        nullable=False
    )  # e.g., 5150.00 GHS
    
    currency = Column(
        String(3),
        default="GHS",
        nullable=False
    )  # ISO currency code
    
    payment_reference = Column(
        String(100),
        nullable=True
    )  # Bank transaction reference
    
    payment_method = Column(
        String(50),
        default="bank_transfer",
        nullable=False
    )  # "bank_transfer", "mobile_money", "cash", etc.
    
    payment_date = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )  # Date payment was made (from receipt)
    
    # Receipt Upload
    receipt_file_path = Column(String(500), nullable=True)
    receipt_filename = Column(String(255), nullable=True)
    receipt_file_size = Column(BigInteger, nullable=True)
    receipt_mime_type = Column(String(100), nullable=True)
    
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
    admin_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Bank Reconciliation
    bank_statement_matched = Column(Integer, default=False, nullable=False)  # Boolean as int
    bank_statement_reference = Column(String(100), nullable=True)
    
    # Payment Type
    payment_type = Column(
        String(50),
        default="initial_deposit",
        nullable=False
    )  # "initial_deposit", "engagement_fee", "service_fee", etc.
    
    description = Column(Text, nullable=True)  # Additional notes

    # Relationships
# FIXED: # FIXED:     client = relationship("Client", back_populates="payments")
    verified_by = relationship("User", foreign_keys=[verified_by_id])

    def __repr__(self):
        return (
            f"<Payment(id={self.id}, client_id={self.client_id}, "
            f"amount={self.amount} {self.currency}, status='{self.verification_status}')>"
        )

    @property
    def is_approved(self) -> bool:
        """Check if payment is approved"""
        return self.verification_status == VerificationStatus.APPROVED.value

    @property
    def is_pending(self) -> bool:
        """Check if payment is pending review"""
        return self.verification_status == VerificationStatus.PENDING.value

    @property
    def amount_formatted(self) -> str:
        """Format amount with currency"""
        return f"{self.currency} {self.amount:,.2f}"
