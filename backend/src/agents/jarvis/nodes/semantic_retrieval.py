"""
Node 2: Semantic Retrieval
Retrieves relevant entities from KG using semantic search.
"""
from typing import Any, Dict
from loguru import logger

from ..state import AgentState
from ..services.vector_store import get_vector_store


async def semantic_retrieval_node(state: AgentState) -> Dict[str, Any]:
    """
    Retrieve relevant entities from KG using semantic search.

    Args:
        state: Current agent state

    Returns:
        Updated state with kg_candidates populated
    """
    logger.info("Node 2: Semantic Retrieval")

    vector_store = get_vector_store()

    # Build query from user input + extracted entities
    query_parts = [state["user_input"]]
    for entity in state.get("extracted_entities", []):
        query_parts.append(entity["text"])
    query = " ".join(query_parts)

    logger.debug(f"Semantic search query: {query[:100]}...")

    # Semantic search
    candidates = await vector_store.semantic_search(
        query=query,
        top_k=20  # Retrieve more, rank later
    )

    logger.info(f"Retrieved {len(candidates)} candidates from vector store")

    return {
        "kg_candidates": candidates,
        "metadata": {
            **state.get("metadata", {}),
            "candidates_count": len(candidates)
        }
    }
