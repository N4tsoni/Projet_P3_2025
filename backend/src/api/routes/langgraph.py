"""
LangGraph testing and visualization routes.
"""
from fastapi import APIRouter, Depends

from src.services.langgraph_service import LangGraphAgentService, get_langgraph_service

router = APIRouter(prefix="/api/langgraph", tags=["LangGraph"])


@router.get("/graph")
async def get_graph_visualization(
    service: LangGraphAgentService = Depends(get_langgraph_service)
):
    """
    Get ASCII visualization of the LangGraph workflow.

    Returns:
        Graph structure as text
    """
    return {
        "visualization": service.get_graph_visualization(),
        "description": "Jarvis LangGraph conversational workflow"
    }


@router.post("/test")
async def test_langgraph(
    message: str,
    service: LangGraphAgentService = Depends(get_langgraph_service)
):
    """
    Test LangGraph with a message and get full state.

    Args:
        message: Test message

    Returns:
        Full workflow state including response and metadata
    """
    result = await service.process_message_with_state(message)
    return result
