"""
Node 4: Context Building
Formats ranked KG results into context string for LLM.
"""
from typing import Any, Dict
from loguru import logger

from ..state import AgentState


async def context_building_node(state: AgentState) -> Dict[str, Any]:
    """
    Format ranked KG results into LLM context.

    Args:
        state: Current agent state

    Returns:
        Updated state with formatted_context populated
    """
    logger.info("Node 4: Context Building")

    ranked = state.get("ranked_context", [])

    if not ranked:
        logger.info("No context to build (empty ranked results)")
        return {
            "formatted_context": "",
            "metadata": state.get("metadata", {})
        }

    context_parts = ["**Contexte du Knowledge Graph:**\n"]

    for item in ranked:
        entity = item.get("entity", {})
        relationships = item.get("relationships", [])
        final_score = item.get("final_score", 0.0)

        name = entity.get("name", "Unknown")
        entity_type = entity.get("type", "Unknown")

        context_parts.append(
            f"\n- {name} ({entity_type}) [score: {final_score:.2f}]"
        )

        # Add relationships (limit to 3)
        for rel in relationships[:3]:
            rel_type = rel.get("type", "RELATED_TO")
            target_name = rel.get("target_name", "Unknown")
            context_parts.append(f"  → {rel_type} {target_name}")

    formatted_context = "\n".join(context_parts)

    logger.debug(f"Built context with {len(ranked)} entities")

    return {
        "formatted_context": formatted_context,
        "metadata": state.get("metadata", {})
    }
