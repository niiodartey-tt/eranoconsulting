# backend/app/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(256), unique=True, nullable=False, index=True)
    hashed_password = Column(String(512), nullable=False)
    role = Column(String(50), default="client")  # 'client' | 'admin' | 'employee'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    client = relationship("Client", back_populates="user", uselist=False)
    files = relationship("FileRecord", back_populates="uploader")
    refresh_tokens = relationship(
        "RefreshToken", back_populates="user"
    )  # ✅ important line


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    company_name = Column(String(256))
    contact_name = Column(String(256))
    contact_phone = Column(String(100))
    contact_email = Column(String(256))
    status = Column(String(50), default="pending")  # pending | active | rejected
    kyc_uploaded = Column(Boolean, default=False)
    payment_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="client")


class FileRecord(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(512), nullable=False)
    path = Column(Text, nullable=False)
    file_type = Column(String(100))  # 'kyc' | 'receipt' | 'other'
    uploader_id = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    uploader = relationship("User", back_populates="files")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(512), nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False)

    user = relationship("User", back_populates="refresh_tokens")
