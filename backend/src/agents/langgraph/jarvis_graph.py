"""
Main LangGraph workflow for Jarvis.
"""
from typing import Literal
from langgraph.graph import StateGraph, END
from loguru import logger

from src.agents.langgraph.state.conversation_state import ConversationState
from src.agents.langgraph.nodes.intent_node import detect_intent
from src.agents.langgraph.nodes.knowledge_node import retrieve_knowledge
from src.agents.langgraph.nodes.response_node import generate_response
from src.agents.langgraph.nodes.memory_node import update_memory


def should_retrieve_knowledge(state: ConversationState) -> Literal["retrieve", "skip"]:
    """
    Conditional routing: should we retrieve knowledge?

    Args:
        state: Current state

    Returns:
        "retrieve" if we should query knowledge graph, "skip" otherwise
    """
    intent = state.get("intent", "general")

    # Retrieve knowledge for queries
    if intent in ["query"]:
        logger.info("Routing to knowledge retrieval")
        return "retrieve"

    logger.info("Skipping knowledge retrieval")
    return "skip"


def should_update_memory(state: ConversationState) -> Literal["update", "skip"]:
    """
    Conditional routing: should we update memory?

    Args:
        state: Current state

    Returns:
        "update" if we should store knowledge, "skip" otherwise
    """
    intent = state.get("intent", "general")

    # Update memory for memorize and task intents
    if intent in ["memorize", "task"]:
        logger.info("Routing to memory update")
        return "update"

    logger.info("Skipping memory update")
    return "skip"


def create_jarvis_graph() -> StateGraph:
    """
    Create the Jarvis conversational graph.

    Workflow:
    START → Intent Detection → [Conditional] Knowledge Retrieval →
    Response Generation → [Conditional] Memory Update → END

    Returns:
        Compiled StateGraph
    """
    # Create graph
    workflow = StateGraph(ConversationState)

    # Add nodes
    workflow.add_node("detect_intent", detect_intent)
    workflow.add_node("retrieve_knowledge", retrieve_knowledge)
    workflow.add_node("generate_response", generate_response)
    workflow.add_node("update_memory", update_memory)

    # Define edges
    # Start → Intent Detection
    workflow.set_entry_point("detect_intent")

    # Intent Detection → Conditional Knowledge Retrieval
    workflow.add_conditional_edges(
        "detect_intent",
        should_retrieve_knowledge,
        {
            "retrieve": "retrieve_knowledge",
            "skip": "generate_response",
        }
    )

    # Knowledge Retrieval → Response Generation
    workflow.add_edge("retrieve_knowledge", "generate_response")

    # Response Generation → Conditional Memory Update
    workflow.add_conditional_edges(
        "generate_response",
        should_update_memory,
        {
            "update": "update_memory",
            "skip": END,
        }
    )

    # Memory Update → END
    workflow.add_edge("update_memory", END)

    # Compile graph
    graph = workflow.compile()

    logger.info("Jarvis LangGraph workflow created successfully")

    return graph


# Create graph instance (singleton)
jarvis_graph = create_jarvis_graph()
