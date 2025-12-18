"""
Knowledge retrieval node.
Retrieves relevant information from knowledge graph.
"""
from typing import Dict
from loguru import logger

from src.agents.langgraph.state.conversation_state import ConversationState
from src.services.knowledge_service import get_knowledge_service


async def retrieve_knowledge(state: ConversationState) -> Dict:
    """
    Retrieve relevant knowledge from Neo4j/Graphiti.

    Args:
        state: Current conversation state

    Returns:
        Updated state with retrieved knowledge
    """
    user_input = state["user_input"]
    intent = state.get("intent", "general")

    logger.info(f"Retrieving knowledge for intent: {intent}")

    # Only retrieve knowledge for queries
    if intent not in ["query"]:
        logger.info("Intent doesn't require knowledge retrieval")
        return {"retrieved_knowledge": []}

    try:
        # TODO: Implement actual GraphRAG retrieval
        knowledge_service = get_knowledge_service()
        result = await knowledge_service.query_knowledge(user_input)

        retrieved = result.get("results", [])
        logger.info(f"Retrieved {len(retrieved)} knowledge items")

        return {"retrieved_knowledge": retrieved}

    except Exception as e:
        logger.error(f"Knowledge retrieval failed: {e}")
        return {"retrieved_knowledge": []}
