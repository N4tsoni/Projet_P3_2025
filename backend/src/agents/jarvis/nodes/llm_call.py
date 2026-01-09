"""
Node 5: LLM Call
Calls Claude via OpenRouter with enriched context.
"""
import os
from typing import Any, Dict
from loguru import logger
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from ..state import AgentState
from ..prompts.system_prompts import get_system_prompt


async def llm_call_node(state: AgentState) -> Dict[str, Any]:
    """
    Call Claude via OpenRouter.

    Args:
        state: Current agent state

    Returns:
        Updated state with response and updated messages
    """
    logger.info("Node 5: LLM Call")

    # Initialize LLM
    llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        model=os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "500"))
    )

    # Build messages
    messages = [
        SystemMessage(content=get_system_prompt()),
        *state.get("messages", [])[-10:],  # Last 10 messages for context
    ]

    # Add KG context if available
    user_content = state["user_input"]
    formatted_context = state.get("formatted_context", "")

    if formatted_context:
        user_content = f"{formatted_context}\n\n**Message utilisateur:** {user_content}"
        logger.debug("Added KG context to user message")

    messages.append(HumanMessage(content=user_content))

    # Call LLM
    logger.debug("Calling LLM...")
    response = await llm.ainvoke(messages)
    assistant_response = response.content

    logger.info(f"LLM response: {assistant_response[:100]}...")

    # Build updated message history
    updated_messages = [
        *state.get("messages", []),
        HumanMessage(content=state["user_input"]),  # Store original user input
        AIMessage(content=assistant_response)
    ]

    return {
        "response": assistant_response,
        "messages": updated_messages,
        "metadata": state.get("metadata", {})
    }
