"""
Response generation node.
Generates assistant response using LLM with context.
"""
from typing import Dict
from loguru import logger
from openai import AsyncOpenAI

from src.agents.langgraph.state.conversation_state import ConversationState
from src.core.config import get_settings


async def generate_response(state: ConversationState) -> Dict:
    """
    Generate response using LLM with full context.

    Args:
        state: Current conversation state

    Returns:
        Updated state with generated response
    """
    settings = get_settings()
    user_input = state["user_input"]
    intent = state.get("intent", "general")
    retrieved_knowledge = state.get("retrieved_knowledge", [])
    messages = state.get("messages", [])

    logger.info(f"Generating response for intent: {intent}")

    # Build context
    context_parts = []

    if retrieved_knowledge:
        context_parts.append("Retrieved knowledge:")
        for item in retrieved_knowledge[:3]:  # Top 3 items
            context_parts.append(f"- {item}")

    # Build system prompt
    system_prompt = """Tu es Jarvis, un assistant personnel vocal intelligent et serviable.

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
- Évite les listes à puces dans tes réponses vocales, privilégie le texte fluide"""

    if context_parts:
        system_prompt += "\n\n" + "\n".join(context_parts)

    # Build message history
    conversation_messages = [{"role": "system", "content": system_prompt}]

    # Add recent conversation history
    for msg in messages[-6:]:  # Last 6 messages (3 turns)
        conversation_messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Add current user input
    conversation_messages.append({
        "role": "user",
        "content": user_input
    })

    # Call LLM
    try:
        client = AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )

        response = await client.chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=conversation_messages,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )

        assistant_response = response.choices[0].message.content.strip()
        logger.info(f"Generated response: {assistant_response[:100]}...")

        # Add messages to history
        new_messages = [
            {
                "role": "user",
                "content": user_input,
                "timestamp": None
            },
            {
                "role": "assistant",
                "content": assistant_response,
                "timestamp": None
            }
        ]

        return {
            "assistant_response": assistant_response,
            "messages": new_messages,
        }

    except Exception as e:
        logger.error(f"Response generation failed: {e}")
        return {
            "assistant_response": "Désolé, j'ai rencontré une erreur lors du traitement de votre demande.",
            "error": str(e),
        }
