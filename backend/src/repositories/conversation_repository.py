"""
Repository for conversation and message data access.
Handles all database operations for conversations.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from src.models.db_models import Conversation, Message


class ConversationRepository:
    """Repository for conversation CRUD operations."""

    def __init__(self, db: Session):
        self.db = db

    # ==================== Conversation Operations ====================

    def create_conversation(self, name: str) -> Conversation:
        """
        Create a new conversation.

        Args:
            name: Name/title for the conversation

        Returns:
            Created conversation
        """
        conversation = Conversation(name=name)
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a conversation by ID.

        Args:
            conversation_id: UUID of the conversation

        Returns:
            Conversation or None if not found
        """
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def list_conversations(self, limit: int = 50, offset: int = 0) -> List[Conversation]:
        """
        List all conversations, ordered by most recent first.

        Args:
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip

        Returns:
            List of conversations
        """
        return (
            self.db.query(Conversation)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def update_conversation_name(self, conversation_id: str, name: str) -> Optional[Conversation]:
        """
        Update conversation name.

        Args:
            conversation_id: UUID of the conversation
            name: New name for the conversation

        Returns:
            Updated conversation or None if not found
        """
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.name = name
            conversation.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(conversation)
        return conversation

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation and all its messages.

        Args:
            conversation_id: UUID of the conversation

        Returns:
            True if deleted, False if not found
        """
        conversation = self.get_conversation(conversation_id)
        if conversation:
            self.db.delete(conversation)
            self.db.commit()
            return True
        return False

    # ==================== Message Operations ====================

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        audio_url: Optional[str] = None,
    ) -> Message:
        """
        Add a message to a conversation.

        Args:
            conversation_id: UUID of the conversation
            role: "user" or "assistant"
            content: Message text (transcription or response)
            audio_url: Optional URL to audio file

        Returns:
            Created message
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            audio_url=audio_url,
        )
        self.db.add(message)

        # Update conversation's updated_at timestamp
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(message)
        return message

    def get_messages(self, conversation_id: str) -> List[Message]:
        """
        Get all messages for a conversation, ordered chronologically.

        Args:
            conversation_id: UUID of the conversation

        Returns:
            List of messages
        """
        return (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .all()
        )

    def get_conversation_with_messages(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a conversation with all its messages loaded.

        Args:
            conversation_id: UUID of the conversation

        Returns:
            Conversation with messages or None if not found
        """
        conversation = self.get_conversation(conversation_id)
        if conversation:
            # Messages are loaded automatically via relationship
            return conversation
        return None
