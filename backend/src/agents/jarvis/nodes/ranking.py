"""
Node 3: Result Ranking
Ranks and filters KG retrieval results using multiple factors.
"""
from typing import Any, Dict
from loguru import logger

from ..state import AgentState


async def ranking_node(state: AgentState) -> Dict[str, Any]:
    """
    Rank and filter KG retrieval results.

    Ranking factors:
    1. Semantic similarity score (from vector search)
    2. Entity type match (from NER)
    3. Graph centrality (number of relationships)

    Args:
        state: Current agent state

    Returns:
        Updated state with ranked_context populated
    """
    logger.info("Node 3: Result Ranking")

    candidates = state.get("kg_candidates", [])

    if not candidates:
        logger.info("No candidates to rank")
        return {
            "ranked_context": [],
            "metadata": state.get("metadata", {})
        }

    extracted_entities = state.get("extracted_entities", [])
    ranked = []

    for candidate in candidates:
        score = 0.0

        # Factor 1: Semantic similarity (already in candidate)
        similarity_score = candidate.get("similarity_score", 0.0)
        score += similarity_score * 0.5

        # Factor 2: Entity type match
        candidate_type = candidate.get("entity", {}).get("type", "").upper()
        for extracted_ent in extracted_entities:
            extracted_label = extracted_ent.get("label", "").upper()
            # Match entity types (PERSON, ORG, GPE, etc.)
            if extracted_label in candidate_type or candidate_type in extracted_label:
                score += 0.2
                break

        # Factor 3: Graph centrality (relationship count)
        rel_count = candidate.get("relationship_count", 0)
        # Normalize to max 0.3 (10+ relationships = max score)
        score += min(rel_count / 10.0, 0.3)

        candidate["final_score"] = score
        ranked.append(candidate)

    # Sort by final score (descending) and take top 5
    ranked.sort(key=lambda x: x.get("final_score", 0.0), reverse=True)
    top_ranked = ranked[:5]

    scores_str = ", ".join([f"{c['final_score']:.2f}" for c in top_ranked])
    logger.info(
        f"Ranked {len(ranked)} candidates, selected top {len(top_ranked)} "
        f"(scores: [{scores_str}])"
    )

    return {
        "ranked_context": top_ranked,
        "metadata": {
            **state.get("metadata", {}),
            "ranked_count": len(top_ranked)
        }
    }
