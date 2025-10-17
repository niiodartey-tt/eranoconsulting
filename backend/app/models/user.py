"""User model with authentication and authorization"""
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Enum,
    Index,
    Integer,
    DateTime,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import relationship, validates
import enum
import re
from app.models.base import BaseModel


class UserRole(str, enum.Enum):
    """User role enumeration"""

    ADMIN = "admin"
    STAFF = "staff"
    CLIENT = "client"


class User(BaseModel):
    """User model for authentication and authorization"""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_user_email"),
        Index("ix_user_email_active", "email", "is_active"),
        Index("ix_user_role", "role"),
        CheckConstraint(
            "email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$'",
            name="check_email_format",
        ),
        {"extend_existing": True},
    )

    # Core fields
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.CLIENT, nullable=False, index=True)

    # Status fields
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)

    # Audit fields
    last_login = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    uploaded_files = relationship(
        "UploadedFile", back_populates="user", cascade="all, delete-orphan"
    )
    sent_messages = relationship(
        "Message", foreign_keys="Message.sender_id", back_populates="sender"
    )
    received_messages = relationship(
        "Message", foreign_keys="Message.receiver_id", back_populates="receiver"
    )
    client = relationship(
        "Client", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    @validates("email")
    def validate_email(self, key, email):
        """Validate and normalize email"""
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            raise ValueError("Invalid email format")
        return email.lower()

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role.value}')>"
