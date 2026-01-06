"""
Jarvis conversational agent using OpenRouter.
"""
import os
from typing import List, Dict, Optional
from loguru import logger
from openai import AsyncOpenAI


class JarvisAgent:
    """
    Conversational agent for Jarvis using OpenRouter.
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
            api_key: OpenRouter API key
            model: Model to use (e.g., 'anthropic/claude-3.5-sonnet')
            temperature: Generation temperature
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found")

        self.model = model or os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
        self.temperature = temperature

        # OpenRouter uses OpenAI SDK with custom base URL
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
        )

        # Conversation history
        self.conversation_history: List[Dict[str, str]] = []

        # System prompt
        self.system_prompt = self._build_system_prompt()

        logger.info(f"Initialized Jarvis agent with model: {self.model}")

    def _build_system_prompt(self) -> str:
        """Build the system prompt for Jarvis."""
        return """Tu es Jarvis, un assistant personnel vocal intelligent et serviable.

Ton rôle:
- Aider l'utilisateur avec ses questions et tâches quotidiennes
- Mémoriser les informations importantes que l'utilisateur partage
- Être concis et naturel dans tes réponses (adapté pour la synthèse vocale)
- Être amical, professionnel et efficace

Consignes importantes:
- Réponds de manière concise (2-3 phrases maximum sauf si détails demandés)
- Utilise un ton conversationnel et naturel
- Si l'utilisateur te donne une information à retenir, confirme que tu l'as mémorisée
- Si tu ne sais pas quelque chose, dis-le honnêtement
- Évite les listes à puces dans tes réponses vocales, privilégie le texte fluide

Tu es actuellement en phase de test et ton knowledge graph se construit progressivement."""

    async def chat(self, user_message: str) -> str:
        """
        Process a user message and return response.

        Args:
            user_message: User's message

        Returns:
            Agent's response
        """
        try:
            logger.info(f"User: {user_message}")

            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_message,
            })

            # Build messages for API
            messages = [
                {"role": "system", "content": self.system_prompt},
                *self.conversation_history[-10:],  # Keep last 10 messages for context
            ]

            # Call OpenRouter
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=int(os.getenv("LLM_MAX_TOKENS", "500")),
            )

            assistant_message = response.choices[0].message.content.strip()

            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message,
            })

            logger.info(f"Jarvis: {assistant_message}")

            return assistant_message

        except Exception as e:
            logger.error(f"Agent chat failed: {e}")
            raise

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
