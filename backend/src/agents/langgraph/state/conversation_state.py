"""
Conversation state model for LangGraph.
"""
from typing import TypedDict, List, Dict, Optional, Annotated
from operator import add


class Message(TypedDict):
    """Message structure in conversation."""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: Optional[str]


class ConversationState(TypedDict):
    """
    State for the Jarvis conversational agent.

    This state is passed between all nodes in the LangGraph workflow.
    """

    # Input/Output
    user_input: str  # Current user input (text)
    assistant_response: str  # Generated response

    # Conversation History
    messages: Annotated[List[Message], add]  # Full conversation history

    # Intent & Context
    intent: Optional[str]  # Detected intent (query, memorize, task, etc.)
    entities: Dict[str, any]  # Extracted entities
    context: Dict[str, any]  # Additional context

    # Knowledge Graph
    retrieved_knowledge: List[Dict[str, any]]  # Retrieved from Neo4j
    knowledge_to_store: List[Dict[str, any]]  # New knowledge to add

    # Metadata
    session_id: Optional[str]  # Session identifier
    turn_count: int  # Number of turns in conversation
    needs_clarification: bool  # If true, ask user for more info
    clarification_question: Optional[str]  # Question to ask user

    # Error handling
    error: Optional[str]  # Error message if any


def create_initial_state(user_input: str, session_id: Optional[str] = None) -> ConversationState:
    """
    Create initial conversation state.

    Args:
        user_input: User's input text
        session_id: Optional session identifier

    Returns:
        Initial ConversationState
    """
    return ConversationState(
        user_input=user_input,
        assistant_response="",
        messages=[],
        intent=None,
        entities={},
        context={},
        retrieved_knowledge=[],
        knowledge_to_store=[],
        session_id=session_id,
        turn_count=0,
        needs_clarification=False,
        clarification_question=None,
        error=None,
    )
