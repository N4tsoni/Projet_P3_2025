"""
Memory update node.
Stores new information in knowledge graph.
"""
from typing import Dict
from loguru import logger

from src.agents.langgraph.state.conversation_state import ConversationState
from src.services.knowledge_service import get_knowledge_service


async def update_memory(state: ConversationState) -> Dict:
    """
    Update knowledge graph with new information.

    Args:
        state: Current conversation state

    Returns:
        Updated state
    """
    intent = state.get("intent", "general")
    user_input = state["user_input"]
    assistant_response = state.get("assistant_response", "")

    logger.info(f"Checking if memory update needed for intent: {intent}")

    # Only store for memorize intent
    if intent != "memorize":
        logger.info("Intent doesn't require memory update")
        return {}

    try:
        # TODO: Implement actual knowledge extraction and storage
        knowledge_service = get_knowledge_service()

        # Extract entities and relationships from conversation
        data = {
            "type": "conversation",
            "user_input": user_input,
            "assistant_response": assistant_response,
        }

        await knowledge_service.add_knowledge(data)
        logger.info("Memory updated successfully")

        return {"knowledge_to_store": [data]}

    except Exception as e:
        logger.error(f"Memory update failed: {e}")
        return {}
