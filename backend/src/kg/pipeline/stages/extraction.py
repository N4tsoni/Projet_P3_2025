"""
Extraction Stage: Extract entities and relations using LLM agents.

Uses Claude or other LLMs to extract structured knowledge from data.
"""

from typing import List

from loguru import logger

from ..base import Stage, StageResult, StageStatus
from ..pipeline import PipelineContext
from ...agents.entity_extractor_agent import EntityExtractorAgent
from ...agents.relation_extractor_agent import RelationExtractorAgent


class ExtractionStage(Stage):
    """
    Stage 5: Entity and Relation Extraction

    Responsibilities:
    - Use LLM agents (Claude) to extract entities
    - Use LLM agents to extract relations between entities
    - Batch processing for efficiency
    - Deduplication of entities and relations

    Input:
        - context.raw_data (or context.chunks)
        - context.metadata

    Output:
        - context.entities (extracted entities)
        - context.relations (extracted relations)
    """

    def __init__(self, batch_size: int = 50):
        """
        Initialize extraction stage.

        Args:
            batch_size: Number of records to process per batch.
        """
        super().__init__(name="ExtractionStage")
        self.batch_size = batch_size
        self.entity_agent = EntityExtractorAgent()
        self.relation_agent = RelationExtractorAgent()

    async def execute(self, context: PipelineContext) -> StageResult:
        """Extract entities and relations using LLM agents."""
        logger.info(f"Extracting entities and relations with batch_size={self.batch_size}")

        try:
            if not context.raw_data:
                raise ValueError("No raw data available for extraction")

            # Extract entities
            logger.info("Extracting entities...")
            entities = await self.entity_agent.extract_entities_batch(
                records=context.raw_data,
                metadata=context.metadata,
                source_filename=context.filename,
                batch_size=self.batch_size
            )
            context.entities = entities

            logger.info(f"Extracted {len(entities)} entities")

            # Extract relations
            logger.info("Extracting relations...")
            relations = await self.relation_agent.extract_relations_batch(
                records=context.raw_data,
                entities=entities,
                metadata=context.metadata,
                source_filename=context.filename,
                batch_size=self.batch_size
            )
            context.relations = relations

            logger.info(f"Extracted {len(relations)} relations")

            return StageResult(
                stage_name=self.name,
                status=StageStatus.COMPLETED,
                duration_seconds=0.0,
                output_data={
                    "entities_count": len(entities),
                    "relations_count": len(relations)
                }
            )

        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return StageResult(
                stage_name=self.name,
                status=StageStatus.FAILED,
                duration_seconds=0.0,
                error=str(e)
            )
