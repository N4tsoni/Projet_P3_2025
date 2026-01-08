"""
Jarvis conversational agent using OpenRouter.
"""
import os
from typing import List, Dict, Optional, Any
from loguru import logger
from openai import AsyncOpenAI

from src.kg.services.neo4j_service import Neo4jService


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

        # Knowledge Graph service (optional)
        self.kg_service: Optional[Neo4jService] = None
        self._init_kg_service()

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

    def _init_kg_service(self):
        """Initialize Knowledge Graph service if available."""
        try:
            self.kg_service = Neo4jService()
            self.kg_service.connect()
            logger.info("Knowledge Graph service initialized")
        except Exception as e:
            logger.warning(f"Knowledge Graph not available: {e}")
            self.kg_service = None

    def _get_kg_context(self, user_message: str) -> str:
        """
        Retrieve relevant context from Knowledge Graph.

        Args:
            user_message: User's message to extract context for

        Returns:
            Formatted context string from KG
        """
        if not self.kg_service:
            return ""

        try:
            # Extract potential entity names from message (simple word matching)
            words = user_message.split()
            entities_context = []

            # Try to find entities that match words in the message
            for word in words:
                if len(word) < 3:  # Skip short words
                    continue

                # Search for entities by name (case-insensitive partial match)
                entities = self.kg_service.search_entities_by_name(word.lower())

                for entity in entities[:3]:  # Limit to 3 entities per word
                    # Get entity with relationships
                    entity_with_rels = self.kg_service.get_entity_with_relationships(
                        entity.get('name')
                    )

                    if entity_with_rels:
                        entities_context.append(entity_with_rels)

            # Format context
            if not entities_context:
                return ""

            context_parts = ["**Contexte du Knowledge Graph:**\n"]

            for entity_data in entities_context[:5]:  # Limit to 5 entities
                entity = entity_data.get('entity', {})
                relationships = entity_data.get('relationships', [])

                name = entity.get('name', 'Unknown')
                entity_type = entity.get('type', 'Unknown')

                context_parts.append(f"\n- {name} ({entity_type})")

                # Add relationships
                for rel in relationships[:3]:  # Limit to 3 relationships per entity
                    rel_type = rel.get('type', 'RELATED_TO')
                    target = rel.get('target_name', 'Unknown')
                    context_parts.append(f"  → {rel_type} {target}")

            return "\n".join(context_parts)

        except Exception as e:
            logger.warning(f"Failed to get KG context: {e}")
            return ""

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

            # Get Knowledge Graph context
            kg_context = self._get_kg_context(user_message)

            # Build enriched user message
            enriched_message = user_message
            if kg_context:
                enriched_message = f"{kg_context}\n\n**Message utilisateur:** {user_message}"

            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_message,  # Store original message in history
            })

            # Build messages for API
            messages = [
                {"role": "system", "content": self.system_prompt},
                *self.conversation_history[-10:][:-1],  # Previous history
                {"role": "user", "content": enriched_message},  # Current message with KG context
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
