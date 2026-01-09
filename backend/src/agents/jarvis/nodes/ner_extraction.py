"""
Node 1: NER Extraction
Extracts named entities from user input using spaCy.
"""
from typing import Any, Dict
from loguru import logger

from ..state import AgentState
from ..services.ner_service import get_ner_service


async def ner_extraction_node(state: AgentState) -> Dict[str, Any]:
    """
    Extract entities from user input.

    Args:
        state: Current agent state

    Returns:
        Updated state with extracted_entities populated
    """
    logger.info("Node 1: NER Extraction")

    ner_service = get_ner_service()
    entities = ner_service.extract_entities(state["user_input"])

    logger.info(f"Extracted {len(entities)} entities: {[e['text'] for e in entities]}")

    return {
        "extracted_entities": entities,
        "metadata": {
            **state.get("metadata", {}),
            "ner_count": len(entities)
        }
    }
