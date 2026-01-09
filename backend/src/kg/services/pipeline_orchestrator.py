"""
Pipeline Orchestrator for Knowledge Graph construction.
Coordinates all agents and services to process documents into KG.

REFACTORED to use new modular Pipeline architecture.
"""
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

from src.kg.pipeline.factory import PipelineFactory
from src.kg.pipeline.pipeline import Pipeline, PipelineContext
from src.kg.services.neo4j_service import Neo4jService, get_neo4j_service
from src.kg.models.document import Document, DocumentFormat, ProcessingStatus


class PipelineOrchestrator:
    """
    Orchestrates the entire KG construction pipeline.

    This orchestrator now uses the modular Pipeline architecture
    with configurable stages for maximum flexibility.
    """

    def __init__(self):
        """Initialize the pipeline orchestrator."""
        self.neo4j_service: Optional[Neo4jService] = None
        # Pipelines are created on-demand based on file format
        self._pipelines: Dict[str, Pipeline] = {}

    def _get_pipeline(self, file_format: str) -> Pipeline:
        """
        Get or create pipeline for a specific file format.

        Args:
            file_format: File format (csv, json, pdf, txt, etc.)

        Returns:
            Configured pipeline for the format
        """
        format_lower = file_format.lower()

        if format_lower not in self._pipelines:
            self._pipelines[format_lower] = PipelineFactory.get_pipeline_for_format(format_lower)

        return self._pipelines[format_lower]

    async def process_csv_file(
        self,
        file_path: Path,
        document: Document
    ) -> Dict[str, Any]:
        """
        Process a CSV file through the complete KG pipeline.

        Uses the new modular Pipeline architecture.

        Args:
            file_path: Path to CSV file
            document: Document tracking object

        Returns:
            Processing statistics
        """
        logger.info(f"Starting CSV pipeline for {file_path.name}")

        try:
            # Initialize Neo4j service
            self.neo4j_service = get_neo4j_service()

            # Get CSV-optimized pipeline
            pipeline = self._get_pipeline("csv")

            # Execute pipeline
            context = await pipeline.execute(
                file_path=file_path,
                filename=file_path.name,
                file_format="csv",
                document=document
            )

            # Build result from context
            result = self._build_result_from_context(context, document)

            if context.is_successful():
                logger.success(f"Pipeline completed successfully for {file_path.name}")

                # Auto-index entities in vector store
                await self._auto_index_entities(context)
            else:
                logger.error(f"Pipeline completed with errors for {file_path.name}")

            return result

        except Exception as e:
            logger.error(f"Pipeline failed for {file_path.name}: {e}")
            document.mark_failed(str(e))
            raise

    def _build_result_from_context(
        self,
        context: PipelineContext,
        document: Document
    ) -> Dict[str, Any]:
        """
        Build result dictionary from pipeline context.

        Args:
            context: Pipeline execution context
            document: Document tracking object

        Returns:
            Standardized result dictionary
        """
        # Get storage result if available
        storage_result = context.get_stage_result("StorageStage")
        storage_data = storage_result.output_data if (storage_result and storage_result.output_data) else {}

        # Get extraction counts
        entities = context.enriched_entities or context.entities
        relations = context.enriched_relations or context.relations

        result = {
            "status": "completed" if context.is_successful() else "failed",
            "document": {
                "filename": document.filename,
                "format": document.format,
                "status": document.status,
                "progress": document.progress
            },
            "extraction": {
                "entities_extracted": len(entities),
                "relations_extracted": len(relations),
                "entities_by_type": self._count_by_type(entities),
                "relations_by_type": self._count_by_type(relations)
            },
            "storage": {
                "entities_stored": storage_data.get("entities_stored", 0),
                "relations_stored": storage_data.get("relations_stored", 0)
            },
            "graph_stats": storage_data.get("graph_stats", {}),
            "pipeline": {
                "duration_seconds": context.get_duration(),
                "stages": [
                    {
                        "name": r.stage_name,
                        "status": r.status.value,
                        "duration": r.duration_seconds,
                        "error": r.error
                    }
                    for r in context.stage_results
                ],
                "errors": context.errors
            }
        }

        return result

    def _count_by_type(self, items) -> Dict[str, int]:
        """
        Count items by their type attribute.

        Args:
            items: List of entities or relations

        Returns:
            Dict mapping type to count
        """
        counts = {}
        for item in items:
            # Handle both Entity objects and dicts
            if isinstance(item, dict):
                item_type = str(item.get('type', 'Unknown'))
            elif hasattr(item, 'type'):
                # Handle Enum or string type
                item_type = item.type.value if hasattr(item.type, 'value') else str(item.type)
            else:
                item_type = 'Unknown'

            counts[item_type] = counts.get(item_type, 0) + 1
        return counts

    async def _auto_index_entities(self, context: PipelineContext):
        """
        Automatically index entities in vector store after successful pipeline execution.

        Args:
            context: Pipeline execution context with entities
        """
        try:
            from src.agents.jarvis.services.vector_store import get_vector_store

            # Get entities from context (use enriched if available)
            entities_to_index = context.enriched_entities or context.entities

            if not entities_to_index:
                logger.debug("No entities to index")
                return

            logger.info(f"Auto-indexing {len(entities_to_index)} entities in vector store...")

            # Get vector store
            vector_store = get_vector_store()

            # Convert entities to dicts if needed
            entity_dicts = []
            for entity in entities_to_index:
                if hasattr(entity, 'to_neo4j_props'):
                    # Entity object
                    entity_dict = {
                        "name": entity.name,
                        "type": entity.type.value if hasattr(entity.type, 'value') else str(entity.type),
                        "properties": entity.to_neo4j_props()
                    }
                elif isinstance(entity, dict):
                    entity_dict = entity
                else:
                    continue

                entity_dicts.append(entity_dict)

            # Add to vector store
            await vector_store.add_entities(entity_dicts)

            logger.success(f"✓ Auto-indexed {len(entity_dicts)} entities in vector store")

        except Exception as e:
            # Don't fail the pipeline if indexing fails
            logger.warning(f"Failed to auto-index entities: {e}")

    async def process_file(
        self,
        file_path: Path,
        file_format: DocumentFormat
    ) -> Dict[str, Any]:
        """
        Process any supported file format using modular pipeline.

        Args:
            file_path: Path to the file
            file_format: Document format

        Returns:
            Processing statistics
        """
        # Create document tracking object
        document = Document(
            filename=file_path.name,
            format=file_format,
            size_bytes=file_path.stat().st_size
        )

        # Initialize Neo4j service
        if self.neo4j_service is None:
            self.neo4j_service = get_neo4j_service()

        try:
            # Get appropriate pipeline for format
            pipeline = self._get_pipeline(file_format.value)

            # Execute pipeline
            logger.info(f"Processing {file_path.name} with {pipeline.name}")
            context = await pipeline.execute(
                file_path=file_path,
                filename=file_path.name,
                file_format=file_format.value,
                document=document
            )

            # Build result
            result = self._build_result_from_context(context, document)

            # Auto-index entities if successful
            if context.is_successful():
                await self._auto_index_entities(context)

            return result

        except Exception as e:
            logger.error(f"Pipeline failed for {file_path.name}: {e}")
            document.mark_failed(str(e))
            raise

    async def get_graph_visualization(self, limit: int = 100) -> Dict[str, Any]:
        """
        Get graph data for visualization.

        Args:
            limit: Maximum nodes to return

        Returns:
            Graph data with nodes and edges
        """
        if self.neo4j_service is None:
            self.neo4j_service = get_neo4j_service()

        return self.neo4j_service.get_graph_data(limit)

    async def get_graph_statistics(self) -> Dict[str, Any]:
        """
        Get graph statistics.

        Returns:
            Statistics about the graph
        """
        if self.neo4j_service is None:
            self.neo4j_service = get_neo4j_service()

        return self.neo4j_service.get_graph_stats()

    async def clear_graph(self):
        """Clear all data from the graph (use with caution!)."""
        if self.neo4j_service is None:
            self.neo4j_service = get_neo4j_service()

        self.neo4j_service.clear_graph()
        logger.warning("Graph cleared")


# Singleton instance
_orchestrator: Optional[PipelineOrchestrator] = None


def get_orchestrator() -> PipelineOrchestrator:
    """
    Get or create pipeline orchestrator singleton.

    Returns:
        PipelineOrchestrator instance
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = PipelineOrchestrator()
    return _orchestrator
