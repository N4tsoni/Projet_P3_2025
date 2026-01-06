"""
Database models for conversation persistence.
Similar to ChatGPT/Claude web interfaces - conversations contain messages.
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4

from src.core.database import Base


class Conversation(Base):
    """
    Conversation entity - represents a chat session.

    Similar to ChatGPT conversations - each has a name and contains multiple messages.
    """

    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship to messages
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, name={self.name})>"


class Message(Base):
    """
    Message entity - represents a single message in a conversation.

    Stores both user input (transcription) and assistant response,
    along with the audio URL for TTS output.
    """

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)  # Transcription (user) or response text (assistant)
    audio_url = Column(String(512), nullable=True)  # URL to audio file (for assistant messages)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship to conversation
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role}, conversation_id={self.conversation_id})>"
