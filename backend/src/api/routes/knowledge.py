"""
Knowledge graph routes.
"""
from fastapi import APIRouter, Depends, HTTPException

from src.schemas.knowledge import (
    KnowledgeGraphResponse,
    KnowledgeQueryResponse,
    KnowledgeAddRequest,
    KnowledgeAddResponse,
)
from src.controllers.knowledge_controller import (
    KnowledgeController,
    get_knowledge_controller,
)

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge"])


@router.get("/query", response_model=KnowledgeQueryResponse)
async def query_knowledge(
    q: str,
    controller: KnowledgeController = Depends(get_knowledge_controller)
):
    """
    Query the knowledge graph.

    Args:
        q: Query string

    Returns:
        Query results from knowledge graph

    Raises:
        HTTPException: If query fails
    """
    try:
        return await controller.query_knowledge(q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add", response_model=KnowledgeAddResponse)
async def add_knowledge(
    request: KnowledgeAddRequest,
    controller: KnowledgeController = Depends(get_knowledge_controller)
):
    """
    Manually add knowledge to the graph.

    Args:
        request: Knowledge data to add

    Returns:
        Success status

    Raises:
        HTTPException: If addition fails
    """
    try:
        return await controller.add_knowledge(request.data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph", response_model=KnowledgeGraphResponse)
async def get_knowledge_graph(
    controller: KnowledgeController = Depends(get_knowledge_controller)
):
    """
    Get the knowledge graph structure.

    Returns:
        Graph nodes and edges

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        return await controller.get_knowledge_graph()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
