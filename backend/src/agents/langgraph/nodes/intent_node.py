"""
Intent detection node.
Analyzes user input to determine intent.
"""
from typing import Dict
from loguru import logger
from openai import AsyncOpenAI

from src.agents.langgraph.state.conversation_state import ConversationState
from src.core.config import get_settings


async def detect_intent(state: ConversationState) -> Dict:
    """
    Detect user intent from input.

    Possible intents:
    - query: User is asking a question
    - memorize: User wants to store information
    - task: User wants to create a task/reminder
    - general: General conversation
    - clarification: Answering a previous question

    Args:
        state: Current conversation state

    Returns:
        Updated state with detected intent
    """
    settings = get_settings()
    user_input = state["user_input"]

    logger.info(f"Detecting intent for: {user_input}")

    # Use LLM for intent detection
    client = AsyncOpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
    )

    prompt = f"""Analyze this user input and classify the intent.

User input: "{user_input}"

Classify as one of:
- query: User is asking a question about something
- memorize: User wants you to remember something
- task: User wants to create a task, reminder, or to-do
- general: General conversation, greeting, or chitchat

Return ONLY the intent word, nothing else."""

    try:
        response = await client.chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=10,
        )

        intent = response.choices[0].message.content.strip().lower()
        logger.info(f"Detected intent: {intent}")

        return {
            "intent": intent,
            "turn_count": state.get("turn_count", 0) + 1,
        }

    except Exception as e:
        logger.error(f"Intent detection failed: {e}")
        return {
            "intent": "general",
            "turn_count": state.get("turn_count", 0) + 1,
        }
