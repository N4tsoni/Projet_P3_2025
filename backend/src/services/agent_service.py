"""
Agent service for managing Jarvis conversational agent.
"""
from typing import Optional
from src.agents.jarvis_agent import JarvisAgent


class AgentService:
    """Service for managing Jarvis agent."""

    def __init__(self):
        """Initialize agent service."""
        self._agent: Optional[JarvisAgent] = None

    def get_agent(self) -> JarvisAgent:
        """
        Get or create Jarvis agent singleton.

        Returns:
            JarvisAgent instance
        """
        if self._agent is None:
            self._agent = JarvisAgent()

        return self._agent

    async def process_message(self, message: str) -> str:
        """
        Process a user message through the agent.

        Args:
            message: User message

        Returns:
            Agent response
        """
        agent = self.get_agent()
        return await agent.chat(message)

    def clear_history(self) -> None:
        """Clear conversation history."""
        if self._agent:
            self._agent.clear_history()


# Singleton instance
_agent_service: Optional[AgentService] = None


def get_agent_service() -> AgentService:
    """
    Get agent service singleton.

    Returns:
        AgentService instance
    """
    global _agent_service

    if _agent_service is None:
        _agent_service = AgentService()

    return _agent_service
