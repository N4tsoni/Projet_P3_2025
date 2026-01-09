"""
Main LangGraph orchestrator for Jarvis agent.
"""
from typing import Optional, List
from loguru import logger
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage

from .state import AgentState
from .nodes import (
    ner_extraction_node,
    semantic_retrieval_node,
    ranking_node,
    context_building_node,
    llm_call_node,
    memory_persist_node,
)


class JarvisAgentGraph:
    """LangGraph-based Jarvis agent with modular node architecture."""

    def __init__(self):
        """Initialize the agent graph."""
        self.graph = self._build_graph()
        logger.info("Jarvis agent graph initialized")

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow.

        Flow: NER → Retrieval → Ranking → Context → LLM → Memory → END
        """
        graph = StateGraph(AgentState)

        # Add nodes
        graph.add_node("ner_extraction", ner_extraction_node)
        graph.add_node("semantic_retrieval", semantic_retrieval_node)
        graph.add_node("ranking", ranking_node)
        graph.add_node("context_building", context_building_node)
        graph.add_node("llm_call", llm_call_node)
        graph.add_node("memory_persist", memory_persist_node)

        # Define linear flow
        graph.set_entry_point("ner_extraction")
        graph.add_edge("ner_extraction", "semantic_retrieval")
        graph.add_edge("semantic_retrieval", "ranking")
        graph.add_edge("ranking", "context_building")
        graph.add_edge("context_building", "llm_call")
        graph.add_edge("llm_call", "memory_persist")
        graph.add_edge("memory_persist", END)

        return graph.compile()

    async def chat(
        self,
        user_input: str,
        conversation_id: str,
        messages: Optional[List[BaseMessage]] = None
    ) -> str:
        """
        Main chat interface - compatible with VoiceService.

        Args:
            user_input: User's message
            conversation_id: Conversation ID for persistence
            messages: Previous message history (LangChain messages)

        Returns:
            Assistant's response string
        """
        logger.info(f"Processing user input: {user_input[:50]}...")

        # Initialize state
        state: AgentState = {
            "conversation_id": conversation_id,
            "user_input": user_input,
            "messages": messages or [],
            "extracted_entities": [],
            "kg_candidates": [],
            "ranked_context": [],
            "formatted_context": "",
            "response": "",
            "metadata": {}
        }

        # Execute graph
        try:
            final_state = await self.graph.ainvoke(state)
            response = final_state.get("response", "")

            # Log metadata
            metadata = final_state.get("metadata", {})
            logger.info(
                f"Graph execution completed. "
                f"NER: {metadata.get('ner_count', 0)} entities, "
                f"Candidates: {metadata.get('candidates_count', 0)}, "
                f"Ranked: {metadata.get('ranked_count', 0)}"
            )

            return response

        except Exception as e:
            logger.error(f"Graph execution failed: {e}")
            raise


# Singleton
_agent_graph: Optional[JarvisAgentGraph] = None


def get_agent_graph() -> JarvisAgentGraph:
    """
    Get or create agent graph singleton.

    Returns:
        JarvisAgentGraph instance
    """
    global _agent_graph
    if _agent_graph is None:
        _agent_graph = JarvisAgentGraph()
    return _agent_graph
