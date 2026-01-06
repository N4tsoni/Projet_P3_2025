"""
Service for conversation management.
Business logic for creating, retrieving, and managing conversations.
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime

from src.repositories.conversation_repository import ConversationRepository
from src.models.db_models import Conversation, Message


class ConversationService:
    """Service for managing conversations and messages."""

    def __init__(self, db: Session):
        self.repository = ConversationRepository(db)

    # ==================== Conversation Management ====================

    def create_conversation(self, name: Optional[str] = None) -> Conversation:
        """
        Create a new conversation.

        Args:
            name: Optional name for the conversation.
                  If not provided, will be auto-generated from first message.

        Returns:
            Created conversation
        """
        if not name:
            name = f"Conversation {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"

        return self.repository.create_conversation(name)

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a conversation by ID.

        Args:
            conversation_id: UUID of the conversation

        Returns:
            Conversation or None if not found
        """
        return self.repository.get_conversation(conversation_id)

    def list_conversations(self, limit: int = 50, offset: int = 0) -> List[Conversation]:
        """
        List all conversations.

        Args:
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip (for pagination)

        Returns:
            List of conversations, ordered by most recent first
        """
        return self.repository.list_conversations(limit=limit, offset=offset)

    def rename_conversation(self, conversation_id: str, name: str) -> Optional[Conversation]:
        """
        Rename a conversation.

        Args:
            conversation_id: UUID of the conversation
            name: New name for the conversation

        Returns:
            Updated conversation or None if not found
        """
        return self.repository.update_conversation_name(conversation_id, name)

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation and all its messages.

        Args:
            conversation_id: UUID of the conversation

        Returns:
            True if deleted, False if not found
        """
        return self.repository.delete_conversation(conversation_id)

    # ==================== Message Management ====================

    def add_user_message(self, conversation_id: str, transcription: str) -> Message:
        """
        Add a user message (from voice transcription) to a conversation.

        Args:
            conversation_id: UUID of the conversation
            transcription: Transcribed user speech

        Returns:
            Created message
        """
        return self.repository.add_message(
            conversation_id=conversation_id,
            role="user",
            content=transcription,
            audio_url=None,
        )

    def add_assistant_message(
        self, conversation_id: str, response: str, audio_url: str
    ) -> Message:
        """
        Add an assistant message (LLM response) to a conversation.

        Args:
            conversation_id: UUID of the conversation
            response: Assistant's text response
            audio_url: URL to the TTS audio file

        Returns:
            Created message
        """
        return self.repository.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=response,
            audio_url=audio_url,
        )

    def add_interaction(
        self, conversation_id: str, transcription: str, response: str, audio_url: str
    ) -> Tuple[Message, Message]:
        """
        Add a complete interaction (user message + assistant response).

        This is a convenience method for the voice pipeline which processes
        a complete turn (user speaks → assistant responds).

        Args:
            conversation_id: UUID of the conversation
            transcription: User's transcribed speech
            response: Assistant's text response
            audio_url: URL to the TTS audio file

        Returns:
            Tuple of (user_message, assistant_message)
        """
        user_msg = self.add_user_message(conversation_id, transcription)
        assistant_msg = self.add_assistant_message(conversation_id, response, audio_url)
        return user_msg, assistant_msg

    def get_conversation_history(self, conversation_id: str) -> List[Message]:
        """
        Get all messages in a conversation.

        Args:
            conversation_id: UUID of the conversation

        Returns:
            List of messages, ordered chronologically
        """
        return self.repository.get_messages(conversation_id)

    def auto_name_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Auto-generate a conversation name from the first user message.

        Args:
            conversation_id: UUID of the conversation

        Returns:
            Updated conversation or None if not found
        """
        messages = self.get_conversation_history(conversation_id)
        if not messages:
            return None

        # Find first user message
        first_user_message = next((m for m in messages if m.role == "user"), None)
        if not first_user_message:
            return None

        # Generate name from first 50 characters of first message
        name = first_user_message.content[:50]
        if len(first_user_message.content) > 50:
            name += "..."

        return self.rename_conversation(conversation_id, name)


def get_conversation_service(db: Session) -> ConversationService:
    """
    Factory function to get conversation service instance.

    Args:
        db: Database session

    Returns:
        ConversationService instance
    """
    return ConversationService(db)
