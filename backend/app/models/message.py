"""Message model for user-to-user communication"""
from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models.base import BaseModel


class Message(BaseModel):
    """Message model for user-to-user communication"""

    __tablename__ = "messages"
    __table_args__ = (
        Index("ix_message_sender", "sender_id"),
        Index("ix_message_receiver", "receiver_id"),
        Index("ix_message_timestamp", "timestamp"),
    )

    # Message data
    sender_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    receiver_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content = Column(Text, nullable=False)
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    sender = relationship(
        "User", foreign_keys=[sender_id], back_populates="sent_messages"
    )
    receiver = relationship(
        "User", foreign_keys=[receiver_id], back_populates="received_messages"
    )

    def __repr__(self):
        return f"<Message(id={self.id}, from={self.sender_id}, to={self.receiver_id})>"
