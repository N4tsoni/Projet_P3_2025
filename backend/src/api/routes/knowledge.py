"""
Knowledge graph routes.
"""
from fastapi import APIRouter, HTTPException
from loguru import logger

from src.models.requests import KnowledgeAddRequest
from src.models.responses import (
    KnowledgeQueryResponse,
    KnowledgeAddResponse,
    KnowledgeGraphResponse
)
from src.services.graph_service import get_graph_service

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.get("/query", response_model=KnowledgeQueryResponse)
async def query_knowledge(q: str):
    """
    Query the knowledge graph.

    Args:
        q: Query string

    Returns:
        Query results from the knowledge graph
    """
    try:
        graph_service = get_graph_service()
        results = await graph_service.query_knowledge(q)

        return KnowledgeQueryResponse(
            query=q,
            results=results,
            message="GraphRAG query à implémenter" if not results else None
        )

    except Exception as e:
        logger.error(f"Error querying knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add", response_model=KnowledgeAddResponse)
async def add_knowledge(data: KnowledgeAddRequest):
    """
    Manually add knowledge to the graph.

    Args:
        data: Knowledge data to add

    Returns:
        Success status
    """
    try:
        graph_service = get_graph_service()
        success = await graph_service.add_knowledge(
            content=data.content,
            source=data.source,
            metadata=data.metadata
        )

        return KnowledgeAddResponse(
            success=success,
            message="Knowledge added successfully" if success else "Failed to add knowledge"
        )

    except Exception as e:
        logger.error(f"Error adding knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph", response_model=KnowledgeGraphResponse)
async def get_knowledge_graph():
    """
    Get the knowledge graph structure.

    Returns:
        Graph nodes and edges
    """
    try:
        graph_service = get_graph_service()
        nodes, edges = await graph_service.get_graph_structure()

        return KnowledgeGraphResponse(nodes=nodes, edges=edges)

    except Exception as e:
        logger.error(f"Error getting knowledge graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))
