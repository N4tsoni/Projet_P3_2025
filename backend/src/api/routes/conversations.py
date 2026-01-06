"""
Conversation management endpoints.
Provides CRUD operations for conversations similar to ChatGPT/Claude interfaces.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.core.database import get_db
from src.services.conversation_service import get_conversation_service, ConversationService
from src.models.requests import ConversationCreateRequest, ConversationRenameRequest
from src.models.responses import (
    ConversationResponse,
    ConversationListResponse,
    ConversationCreateResponse,
    MessageResponse,
)
from loguru import logger

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])


# ==================== Conversation Endpoints ====================


@router.post("", response_model=ConversationCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    request: ConversationCreateRequest,
    db: Session = Depends(get_db),
):
    """
    Create a new conversation.

    - **name**: Optional name for the conversation (auto-generated if not provided)
    """
    try:
        service = get_conversation_service(db)
        conversation = service.create_conversation(name=request.name)

        return ConversationCreateResponse(
            success=True,
            conversation=ConversationResponse(
                id=conversation.id,
                name=conversation.name,
                created_at=conversation.created_at.isoformat(),
                updated_at=conversation.updated_at.isoformat(),
                messages=None,
            ),
        )
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create conversation: {str(e)}",
        )


@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    List all conversations.

    - **limit**: Maximum number of conversations to return (default: 50)
    - **offset**: Number of conversations to skip for pagination (default: 0)
    """
    try:
        service = get_conversation_service(db)
        conversations = service.list_conversations(limit=limit, offset=offset)

        return ConversationListResponse(
            conversations=[
                ConversationResponse(
                    id=conv.id,
                    name=conv.name,
                    created_at=conv.created_at.isoformat(),
                    updated_at=conv.updated_at.isoformat(),
                    messages=None,
                )
                for conv in conversations
            ],
            total=len(conversations),
        )
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list conversations: {str(e)}",
        )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    include_messages: bool = True,
    db: Session = Depends(get_db),
):
    """
    Get a specific conversation by ID.

    - **conversation_id**: UUID of the conversation
    - **include_messages**: Whether to include messages (default: true)
    """
    try:
        service = get_conversation_service(db)
        conversation = service.get_conversation(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found",
            )

        messages = None
        if include_messages:
            messages = [
                MessageResponse(
                    id=msg.id,
                    role=msg.role,
                    content=msg.content,
                    audio_url=msg.audio_url,
                    created_at=msg.created_at.isoformat(),
                )
                for msg in conversation.messages
            ]

        return ConversationResponse(
            id=conversation.id,
            name=conversation.name,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            messages=messages,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation: {str(e)}",
        )


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def rename_conversation(
    conversation_id: str,
    request: ConversationRenameRequest,
    db: Session = Depends(get_db),
):
    """
    Rename a conversation.

    - **conversation_id**: UUID of the conversation
    - **name**: New name for the conversation
    """
    try:
        service = get_conversation_service(db)
        conversation = service.rename_conversation(conversation_id, request.name)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found",
            )

        return ConversationResponse(
            id=conversation.id,
            name=conversation.name,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            messages=None,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error renaming conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rename conversation: {str(e)}",
        )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
):
    """
    Delete a conversation and all its messages.

    - **conversation_id**: UUID of the conversation
    """
    try:
        service = get_conversation_service(db)
        deleted = service.delete_conversation(conversation_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found",
            )

        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete conversation: {str(e)}",
        )


# ==================== Message Endpoints ====================


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    db: Session = Depends(get_db),
):
    """
    Get all messages in a conversation.

    - **conversation_id**: UUID of the conversation
    """
    try:
        service = get_conversation_service(db)

        # Verify conversation exists
        conversation = service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found",
            )

        messages = service.get_conversation_history(conversation_id)

        return [
            MessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                audio_url=msg.audio_url,
                created_at=msg.created_at.isoformat(),
            )
            for msg in messages
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get messages: {str(e)}",
        )
