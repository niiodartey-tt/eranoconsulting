"""Enhanced Client model for comprehensive onboarding workflow"""
from sqlalchemy import (
    Column, String, Integer, ForeignKey, Index, 
    DateTime, Text, ARRAY, Boolean
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models.base import BaseModel
from app.models.enums import OnboardingStatus, ServiceType


class Client(BaseModel):
    """Client model with full onboarding workflow support"""

    __tablename__ = "clients"
    __table_args__ = (
        Index("ix_client_user", "user_id"),
        Index("ix_client_onboarding_status", "onboarding_status"),
        Index("ix_client_account_manager", "account_manager_id"),
    )

    # Link to user account
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        unique=True, 
        nullable=False
    )

    # Business Information (Step 1: Registration)
    business_name = Column(String(255), nullable=False)
    business_address = Column(Text, nullable=True)
    business_type = Column(String(100), nullable=True)  # e.g., "Limited Liability", "Sole Proprietor"
    registration_number = Column(String(100), nullable=True)  # RGD number
    
    # Contact Information
    contact_person = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=False)
    alternate_phone = Column(String(20), nullable=True)
    
    # Services Requested (Array of ServiceType enums)
    services_requested = Column(
        ARRAY(String), 
        nullable=True,
        default=[]
    )
    
    # Onboarding Workflow Status
    onboarding_status = Column(
        String(50),
        default=OnboardingStatus.PENDING_VERIFICATION.value,
        nullable=False,
        index=True
    )
    
    # Account Management
    account_manager_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Terms & Conditions
    terms_accepted = Column(Boolean, default=False, nullable=False)
    terms_accepted_at = Column(DateTime(timezone=True), nullable=True)
    privacy_policy_accepted = Column(Boolean, default=False, nullable=False)
    
    # Important Dates
    registration_date = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    verification_date = Column(DateTime(timezone=True), nullable=True)  # Admin verified
    activation_date = Column(DateTime(timezone=True), nullable=True)  # Fully active
    
    # Admin Notes
    admin_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Temporary Password (for Step 3)
    temp_password_sent = Column(Boolean, default=False, nullable=False)
    temp_password_sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="client")
    account_manager = relationship("User", foreign_keys=[account_manager_id])
    kyc_documents = relationship(
        "KYCDocument", 
        back_populates="client", 
        cascade="all, delete-orphan"
    )
    payments = relationship(
        "Payment", 
        back_populates="client", 
        cascade="all, delete-orphan"
    )
    engagement_letters = relationship(
        "EngagementLetter",
        back_populates="client",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Client(id={self.id}, business='{self.business_name}', status='{self.onboarding_status}')>"

    @property
    def is_pending_verification(self) -> bool:
        """Check if client is awaiting admin verification"""
        return self.onboarding_status == OnboardingStatus.PENDING_VERIFICATION.value

    @property
    def is_active(self) -> bool:
        """Check if client is fully active"""
        return self.onboarding_status == OnboardingStatus.ACTIVE.value

    @property
    def needs_kyc(self) -> bool:
        """Check if client needs to submit KYC documents"""
        return self.onboarding_status in [
            OnboardingStatus.PRE_ACTIVE.value,
            OnboardingStatus.KYC_SUBMISSION.value
        ]
