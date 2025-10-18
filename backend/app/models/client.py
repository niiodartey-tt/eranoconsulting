"""Client model for business client management"""
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Index, Enum
from sqlalchemy.orm import relationship
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
        Index("ix_client_status", "status"),
        {"extend_existing": True},
    )

    # Link to user
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    # Company information
    company_name = Column(String(256), nullable=True)
    contact_name = Column(String(256), nullable=True)
    contact_phone = Column(String(100), nullable=True)
    contact_email = Column(String(256), nullable=True)

    # Status tracking with proper enum
    status = Column(
        String(50),  # Keep as String for now, will migrate to Enum later
        default="pre_active",
        nullable=False,
    )

    # Onboarding progress tracking
    kyc_uploaded = Column(Boolean, default=False, nullable=False)
    payment_verified = Column(Boolean, default=False, nullable=False)
    onboarding_completed = Column(Boolean, default=False, nullable=False)
    engagement_letter_signed = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="client")

    # NOTE: We don't need kyc_documents relationship
    # Files are linked via UploadedFile.uploader_id -> User.id -> Client.user_id

    def __repr__(self):
        return f"<Client(id={self.id}, company='{self.company_name}', status='{self.status}')>"
