"""
Jarvis conversational agent - Legacy wrapper for backward compatibility.
Delegates to new LangGraph implementation.
"""
import os
from typing import List, Dict, Optional
from loguru import logger
from langchain_core.messages import HumanMessage, AIMessage

from src.agents.jarvis.graph import get_agent_graph


class JarvisAgent:
    """
    Conversational agent for Jarvis using OpenRouter.

    This is a legacy wrapper that maintains backward compatibility
    while delegating to the new LangGraph-based implementation.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
    ):
        """
        Initialize Jarvis agent.

        Args:
            api_key: OpenRouter API key (now read from env in graph)
            model: Model to use (now read from env in graph)
            temperature: Generation temperature (now read from env in graph)
        """
        # Validate API key
        api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found")

        # Get LangGraph implementation
        self.graph = get_agent_graph()

        # Conversation history (for backward compatibility)
        self.conversation_history: List[Dict[str, str]] = []

        logger.info("Initialized Jarvis agent (LangGraph-based)")

    async def chat(self, user_message: str, conversation_id: str = "default") -> str:
        """
        Process a user message and return response.

        Args:
            user_message: User's message
            conversation_id: Conversation ID for persistence

        Returns:
            Agent's response
        """
        try:
            logger.info(f"User: {user_message[:50]}...")

            # Convert history to LangChain messages
            messages = self._convert_history_to_messages()

            # Call graph
            response = await self.graph.chat(
                user_input=user_message,
                conversation_id=conversation_id,
                messages=messages
            )

            # Update legacy history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": response})

            logger.info(f"Jarvis: {response[:50]}...")

            return response

        except Exception as e:
            logger.error(f"Agent chat failed: {e}")
            raise

    def _convert_history_to_messages(self) -> List:
        """Convert legacy history format to LangChain messages."""
        messages = []
        for msg in self.conversation_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        return messages

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.conversation_history.copy()


# Singleton instance
_agent: Optional[JarvisAgent] = None


def get_agent() -> JarvisAgent:
    """
    Get or create Jarvis agent singleton.

    Returns:
        JarvisAgent instance
    """
    global _agent

    if _agent is None:
        _agent = JarvisAgent()

    return _agent
