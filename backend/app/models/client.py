"""Client model for business client management"""
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Client(BaseModel):
    """Client model for business client information"""

    __tablename__ = "clients"
    __table_args__ = (
        Index("ix_client_user", "user_id"),
        Index("ix_client_status", "status"),
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

    # Status tracking
    status = Column(
        String(50), default="pending", nullable=False
    )  # 'pending', 'active', 'rejected', 'suspended'
    kyc_uploaded = Column(Boolean, default=False, nullable=False)
    payment_verified = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="client")

    def __repr__(self):
        return f"<Client(id={self.id}, company='{self.company_name}', status='{self.status}')>"
