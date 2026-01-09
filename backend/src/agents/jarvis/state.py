"""
Agent state definition for Jarvis LangGraph agent.
State is shared across all nodes in the graph.
"""
from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """Shared state for Jarvis agent graph.

    This state is passed through all nodes in the graph, with each node
    reading from and writing to specific fields.
    """

    # Input
    conversation_id: str
    user_input: str

    # History
    messages: List[BaseMessage]  # Full conversation history

    # NER results
    extracted_entities: List[Dict[str, Any]]  # Entities extracted from user message

    # Retrieval results
    kg_candidates: List[Dict[str, Any]]  # Retrieved from vector search
    ranked_context: List[Dict[str, Any]]  # After ranking

    # Context
    formatted_context: str  # String context formatted for LLM

    # Output
    response: str  # Final assistant response

    # Metadata
    metadata: Dict[str, Any]  # Timing, scores, debug info, etc.
