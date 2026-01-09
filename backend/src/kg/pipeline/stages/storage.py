"""
Storage Stage: Store entities and relations in Neo4j.

Persists validated knowledge graph to database.
"""

from typing import List

from loguru import logger

from ..base import Stage, StageResult, StageStatus
from ..pipeline import PipelineContext
from ...services.neo4j_service import Neo4jService


class StorageStage(Stage):
    """
    Stage 9: Storage to Neo4j

    Responsibilities:
    - Connect to Neo4j database
    - Store entities as nodes
    - Store relations as edges
    - Batch operations for performance
    - Transaction management
    - Return storage IDs

    Input:
        - context.enriched_entities (or context.entities)
        - context.enriched_relations (or context.relations)

    Output:
        - context.storage_ids (Neo4j IDs for entities and relations)
    """

    def __init__(self):
        super().__init__(name="StorageStage")
        self.neo4j_service = None

    async def execute(self, context: PipelineContext) -> StageResult:
        """Store entities and relations in Neo4j."""
        logger.info("Storing entities and relations to Neo4j")

        try:
            # Use enriched data if available, otherwise use original
            entities = context.enriched_entities or context.entities
            relations = context.enriched_relations or context.relations

            if not entities and not relations:
                logger.warning("No entities or relations to store")
                return StageResult(
                    stage_name=self.name,
                    status=StageStatus.SKIPPED,
                    duration_seconds=0.0,
                    metadata={"reason": "No data to store"}
                )

            # Initialize Neo4j service and connect
            self.neo4j_service = Neo4jService()
            self.neo4j_service.connect()

            # Store entities
            logger.info(f"Storing {len(entities)} entities...")
            entity_ids = self.neo4j_service.create_entities_batch(entities)

            # Store relations
            logger.info(f"Storing {len(relations)} relations...")
            relation_ids = self.neo4j_service.create_relations_batch(relations)

            # Save IDs to context
            context.storage_ids = {
                "entity_ids": entity_ids,
                "relation_ids": relation_ids
            }

            logger.success(
                f"Stored {len(entity_ids)} entities and {len(relation_ids)} relations"
            )

            # Get graph stats for reporting
            stats = self.neo4j_service.get_graph_stats()

            return StageResult(
                stage_name=self.name,
                status=StageStatus.COMPLETED,
                duration_seconds=0.0,
                output_data={
                    "entities_stored": len(entity_ids),
                    "relations_stored": len(relation_ids),
                    "graph_stats": stats
                }
            )

        except Exception as e:
            logger.error(f"Storage failed: {e}")
            return StageResult(
                stage_name=self.name,
                status=StageStatus.FAILED,
                duration_seconds=0.0,
                error=str(e)
            )
        finally:
            # Clean up Neo4j connection
            if self.neo4j_service:
                self.neo4j_service.close()
