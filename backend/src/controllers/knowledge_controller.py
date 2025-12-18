"""
Knowledge controller for knowledge graph operations.
"""
from typing import Dict, Any
from loguru import logger

from src.schemas.knowledge import (
    KnowledgeGraphResponse,
    KnowledgeQueryResponse,
    KnowledgeAddResponse,
)
from src.services.knowledge_service import get_knowledge_service


class KnowledgeController:
    """Controller for knowledge graph operations."""

    def __init__(self):
        """Initialize knowledge controller."""
        self.knowledge_service = get_knowledge_service()

    async def query_knowledge(self, query: str) -> KnowledgeQueryResponse:
        """
        Query the knowledge graph.

        Args:
            query: Query string

        Returns:
            KnowledgeQueryResponse with results
        """
        logger.info(f"Querying knowledge graph: {query}")

        result = await self.knowledge_service.query_knowledge(query)

        return KnowledgeQueryResponse(**result)

    async def add_knowledge(self, data: Dict[str, Any]) -> KnowledgeAddResponse:
        """
        Add knowledge to the graph.

        Args:
            data: Knowledge data to add

        Returns:
            KnowledgeAddResponse with success status
        """
        logger.info(f"Adding knowledge to graph: {data}")

        result = await self.knowledge_service.add_knowledge(data)

        return KnowledgeAddResponse(**result)

    async def get_knowledge_graph(self) -> KnowledgeGraphResponse:
        """
        Get the knowledge graph structure.

        Returns:
            KnowledgeGraphResponse with nodes and edges
        """
        logger.info("Retrieving knowledge graph structure")

        result = await self.knowledge_service.get_knowledge_graph()

        return KnowledgeGraphResponse(**result)


# Singleton instance
_knowledge_controller: "KnowledgeController" = None


def get_knowledge_controller() -> KnowledgeController:
    """
    Get knowledge controller singleton.

    Returns:
        KnowledgeController instance
    """
    global _knowledge_controller

    if _knowledge_controller is None:
        _knowledge_controller = KnowledgeController()

    return _knowledge_controller
