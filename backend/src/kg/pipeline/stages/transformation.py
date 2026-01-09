"""
Transformation Stage: Transform and normalize extracted data.

Applies data transformations, normalization, and standardization.
"""

from typing import List, Dict, Any

from loguru import logger

from ..base import Stage, StageResult, StageStatus
from ..pipeline import PipelineContext


class TransformationStage(Stage):
    """
    Stage 6: Data Transformation

    Responsibilities:
    - Normalize entity names (e.g., "Tom Hanks" vs "Thomas Hanks")
    - Standardize property formats (dates, numbers, etc.)
    - Apply business rules and transformations
    - Clean and validate data
    - Merge duplicate entities

    Input:
        - context.entities
        - context.relations

    Output:
        - Transforms context.entities and context.relations in place
    """

    def __init__(self):
        super().__init__(name="TransformationStage")

    async def execute(self, context: PipelineContext) -> StageResult:
        """Transform and normalize extracted data."""
        logger.info("Transforming extracted entities and relations")

        try:
            entities_before = len(context.entities)
            relations_before = len(context.relations)

            # Transform entities
            context.entities = await self._transform_entities(context.entities)

            # Transform relations
            context.relations = await self._transform_relations(context.relations)

            entities_after = len(context.entities)
            relations_after = len(context.relations)

            logger.info(
                f"Transformation: entities {entities_before} -> {entities_after}, "
                f"relations {relations_before} -> {relations_after}"
            )

            return StageResult(
                stage_name=self.name,
                status=StageStatus.COMPLETED,
                duration_seconds=0.0,
                output_data={
                    "entities_before": entities_before,
                    "entities_after": entities_after,
                    "relations_before": relations_before,
                    "relations_after": relations_after
                }
            )

        except Exception as e:
            logger.error(f"Transformation failed: {e}")
            return StageResult(
                stage_name=self.name,
                status=StageStatus.FAILED,
                duration_seconds=0.0,
                error=str(e)
            )

    async def _transform_entities(self, entities: List[Any]) -> List[Any]:
        """
        Transform and normalize entities.

        TODO: Implement transformations:
        - Name normalization (lowercase, title case, etc.)
        - Property type conversion
        - Date parsing and standardization
        - Duplicate merging based on similarity
        """
        logger.warning("Entity transformation not fully implemented")
        return entities

    async def _transform_relations(self, relations: List[Any]) -> List[Any]:
        """
        Transform and normalize relations.

        TODO: Implement transformations:
        - Relation type standardization
        - Property normalization
        - Bidirectional relation handling
        """
        logger.warning("Relation transformation not fully implemented")
        return relations
