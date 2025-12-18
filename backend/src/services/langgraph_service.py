"""
LangGraph agent service for managing Jarvis conversational workflow.
"""
from typing import Optional, Dict, Any
from loguru import logger

from src.agents.langgraph.jarvis_graph import jarvis_graph
from src.agents.langgraph.state.conversation_state import create_initial_state


class LangGraphAgentService:
    """Service for managing LangGraph-based Jarvis agent."""

    def __init__(self):
        """Initialize LangGraph agent service."""
        self.graph = jarvis_graph
        logger.info("LangGraph Agent Service initialized")

    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None
    ) -> str:
        """
        Process a user message through the LangGraph workflow.

        Args:
            message: User message
            session_id: Optional session identifier for persistence

        Returns:
            Assistant response
        """
        try:
            logger.info(f"Processing message: {message}")

            # Create initial state
            initial_state = create_initial_state(
                user_input=message,
                session_id=session_id
            )

            # Run graph
            result = await self.graph.ainvoke(initial_state)

            # Extract response
            response = result.get("assistant_response", "")

            logger.info(f"LangGraph response: {response[:100]}...")

            # Log workflow metadata
            intent = result.get("intent")
            retrieved_count = len(result.get("retrieved_knowledge", []))
            stored_count = len(result.get("knowledge_to_store", []))

            logger.info(
                f"Workflow completed - Intent: {intent}, "
                f"Retrieved: {retrieved_count}, Stored: {stored_count}"
            )

            return response

        except Exception as e:
            logger.exception(f"LangGraph processing failed: {e}")
            return "Désolé, j'ai rencontré une erreur lors du traitement de votre message."

    async def process_message_with_state(
        self,
        message: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and return full state.

        Args:
            message: User message
            session_id: Optional session identifier

        Returns:
            Full conversation state including response and metadata
        """
        try:
            logger.info(f"Processing message with state: {message}")

            # Create initial state
            initial_state = create_initial_state(
                user_input=message,
                session_id=session_id
            )

            # Run graph
            result = await self.graph.ainvoke(initial_state)

            logger.info("LangGraph workflow completed successfully")

            return {
                "response": result.get("assistant_response", ""),
                "intent": result.get("intent"),
                "retrieved_knowledge": result.get("retrieved_knowledge", []),
                "knowledge_stored": result.get("knowledge_to_store", []),
                "turn_count": result.get("turn_count", 0),
                "needs_clarification": result.get("needs_clarification", False),
                "error": result.get("error"),
            }

        except Exception as e:
            logger.exception(f"LangGraph processing failed: {e}")
            return {
                "response": "Désolé, j'ai rencontré une erreur lors du traitement de votre message.",
                "error": str(e),
            }

    def get_graph_visualization(self) -> str:
        """
        Get ASCII visualization of the graph.

        Returns:
            Graph structure as string
        """
        # TODO: Implement graph visualization
        return """
Jarvis LangGraph Workflow:

START
  ↓
detect_intent
  ↓
[Conditional: should_retrieve_knowledge?]
  ├─ retrieve → retrieve_knowledge → generate_response
  └─ skip → generate_response
      ↓
generate_response
  ↓
[Conditional: should_update_memory?]
  ├─ update → update_memory → END
  └─ skip → END
"""


# Singleton instance
_langgraph_service: Optional[LangGraphAgentService] = None


def get_langgraph_service() -> LangGraphAgentService:
    """
    Get LangGraph agent service singleton.

    Returns:
        LangGraphAgentService instance
    """
    global _langgraph_service

    if _langgraph_service is None:
        _langgraph_service = LangGraphAgentService()

    return _langgraph_service
