"""Client model for business client management"""
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Index, Text, DateTime, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.models.base import BaseModel


class ClientStatus(str, enum.Enum):
    """Client status enumeration"""
    PRE_ACTIVE = "pre_active"  # Account created, awaiting onboarding
    PENDING_REVIEW = "pending_review"  # Documents submitted, awaiting admin review
    INACTIVE = "inactive"  # Reviewed but not yet fully activated
    ACTIVE = "active"  # Fully activated and operational
    REJECTED = "rejected"  # Application rejected
    SUSPENDED = "suspended"  # Account suspended


class Client(BaseModel):
    """Client model for business client information"""
    __tablename__ = "clients"
    __table_args__ = (
        Index("ix_client_user", "user_id"),
        Index("ix_client_onboarding_status", "onboarding_status"),
        Index("ix_client_account_manager", "account_manager_id"),
    )

    # Link to user
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    
    # Business information (matching database schema)
    business_name = Column(String(255), nullable=False)
    business_address = Column(Text, nullable=True)
    business_type = Column(String(100), nullable=True)
    registration_number = Column(String(100), nullable=True)
    
    # Contact information
    contact_person = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=False)
    alternate_phone = Column(String(20), nullable=True)
    
    # Services
    services_requested = Column(ARRAY(String), nullable=True)
    
    # Status tracking
    onboarding_status = Column(
        String(50), 
        default=ClientStatus.PRE_ACTIVE.value, 
        nullable=False,
        index=True
    )
    account_manager_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True,
        index=True
    )
    
    # Terms and policies
    terms_accepted = Column(Boolean, default=False, nullable=False)
    terms_accepted_at = Column(DateTime(timezone=True), nullable=True)
    privacy_policy_accepted = Column(Boolean, default=False, nullable=False)
    
    # Dates
    registration_date = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    verification_date = Column(DateTime(timezone=True), nullable=True)
    activation_date = Column(DateTime(timezone=True), nullable=True)
    
    # Admin fields
    admin_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    temp_password_sent = Column(Boolean, default=False, nullable=False)
    temp_password_sent_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="client")
    account_manager = relationship("User", foreign_keys=[account_manager_id])

    def __repr__(self):
        return f"<Client(id={self.id}, business='{self.business_name}', status='{self.onboarding_status}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if client is active"""
        return self.onboarding_status == ClientStatus.ACTIVE.value
    
    @property
    def is_pending(self) -> bool:
        """Check if client is pending review"""
        return self.onboarding_status == ClientStatus.PENDING_REVIEW.value
