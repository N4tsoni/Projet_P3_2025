"""
Node 6: Memory Persistence
Persists conversation to PostgreSQL database.
"""
from typing import Any, Dict
from loguru import logger

from ..state import AgentState


async def memory_persist_node(state: AgentState) -> Dict[str, Any]:
    """
    Persist conversation to PostgreSQL.

    Note: This node is kept minimal as the VoiceService already handles
    conversation persistence. This is a placeholder for future enhancements
    like storing metadata or conversation summaries.

    Args:
        state: Current agent state

    Returns:
        Updated state (unchanged)
    """
    logger.info("Node 6: Memory Persistence")

    # For now, just log the conversation details
    # Actual persistence is handled by VoiceService
    logger.debug(
        f"Conversation {state.get('conversation_id')} - "
        f"User: {state.get('user_input', '')[:50]}... "
        f"Response: {state.get('response', '')[:50]}..."
    )

    return {
        "metadata": state.get("metadata", {})
    }
