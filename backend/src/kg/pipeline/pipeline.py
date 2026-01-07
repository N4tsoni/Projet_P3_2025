"""
Main Pipeline orchestrator for Knowledge Graph construction.

The Pipeline class coordinates execution of multiple stages in sequence,
managing shared context and collecting results.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from loguru import logger

from .base import Stage, StageResult, StageStatus
from ..models.document import Document, ProcessingStatus


@dataclass
class PipelineContext:
    """
    Shared context passed between pipeline stages.

    This context accumulates data as it flows through the pipeline.
    Each stage can read from and write to the context.
    """

    # Input
    file_path: Path
    filename: str
    file_format: str
    document: Optional[Document] = None

    # Stage outputs (populated as pipeline progresses)
    raw_data: Optional[Any] = None  # Parsed raw data (DataFrame, dict, etc.)
    metadata: Dict[str, Any] = field(default_factory=dict)  # File metadata
    chunks: Optional[List[Dict[str, Any]]] = None  # Text chunks
    embeddings: Optional[List[List[float]]] = None  # Embeddings for chunks
    entities: List[Any] = field(default_factory=list)  # Extracted entities
    relations: List[Any] = field(default_factory=list)  # Extracted relations
    enriched_entities: List[Any] = field(default_factory=list)  # Enriched entities
    enriched_relations: List[Any] = field(default_factory=list)  # Enriched relations
    validation_results: Dict[str, Any] = field(default_factory=dict)  # Validation info
    storage_ids: Dict[str, List[str]] = field(default_factory=dict)  # Neo4j IDs

    # Pipeline execution tracking
    start_time: datetime = field(default_factory=datetime.now)
    stage_results: List[StageResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def add_error(self, error: str):
        """Add an error message to context."""
        self.errors.append(error)
        logger.error(f"Pipeline error: {error}")

    def get_duration(self) -> float:
        """Get total pipeline duration in seconds."""
        return (datetime.now() - self.start_time).total_seconds()

    def is_successful(self) -> bool:
        """Check if all executed stages succeeded."""
        if not self.stage_results:
            return False
        return all(r.is_success() or r.status == StageStatus.SKIPPED for r in self.stage_results)

    def get_stage_result(self, stage_name: str) -> Optional[StageResult]:
        """Get result for a specific stage by name."""
        for result in self.stage_results:
            if result.stage_name == stage_name:
                return result
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for serialization."""
        return {
            "filename": self.filename,
            "file_format": self.file_format,
            "duration_seconds": self.get_duration(),
            "entities_count": len(self.entities),
            "relations_count": len(self.relations),
            "chunks_count": len(self.chunks) if self.chunks else 0,
            "errors": self.errors,
            "successful": self.is_successful(),
            "stages": [
                {
                    "name": r.stage_name,
                    "status": r.status.value,
                    "duration": r.duration_seconds,
                    "error": r.error
                }
                for r in self.stage_results
            ]
        }


class Pipeline:
    """
    Main pipeline orchestrator.

    Executes a sequence of stages in order, managing context and error handling.
    """

    def __init__(self, stages: Optional[List[Stage]] = None, name: str = "KG Pipeline"):
        """
        Initialize pipeline.

        Args:
            stages: List of stages to execute in order.
            name: Name of the pipeline.
        """
        self.name = name
        self.stages: List[Stage] = stages or []

    def add_stage(self, stage: Stage) -> "Pipeline":
        """
        Add a stage to the pipeline.

        Args:
            stage: Stage to add.

        Returns:
            Self for method chaining.
        """
        self.stages.append(stage)
        return self

    def remove_stage(self, stage_name: str) -> "Pipeline":
        """
        Remove a stage by name.

        Args:
            stage_name: Name of stage to remove.

        Returns:
            Self for method chaining.
        """
        self.stages = [s for s in self.stages if s.name != stage_name]
        return self

    def get_stage(self, stage_name: str) -> Optional[Stage]:
        """Get a stage by name."""
        for stage in self.stages:
            if stage.name == stage_name:
                return stage
        return None

    async def execute(
        self,
        file_path: Path,
        filename: str,
        file_format: str,
        document: Optional[Document] = None
    ) -> PipelineContext:
        """
        Execute the pipeline.

        Args:
            file_path: Path to input file.
            filename: Name of file.
            file_format: Format of file (csv, json, pdf, etc.).
            document: Optional document tracking object.

        Returns:
            PipelineContext with execution results.
        """
        logger.info(f"Starting {self.name} for file: {filename}")

        # Initialize context
        context = PipelineContext(
            file_path=file_path,
            filename=filename,
            file_format=file_format,
            document=document
        )

        # Execute stages in sequence
        for i, stage in enumerate(self.stages, 1):
            logger.info(f"Executing stage {i}/{len(self.stages)}: {stage.name}")

            # Update document status if available
            if document:
                await self._update_document_status(document, stage.name, i, len(self.stages))

            # Run stage
            result = await stage.run(context)
            context.stage_results.append(result)

            # Log result
            if result.is_success():
                logger.success(f"Stage '{stage.name}' completed in {result.duration_seconds:.2f}s")
            elif result.status == StageStatus.SKIPPED:
                logger.info(f"Stage '{stage.name}' skipped")
            else:
                logger.error(f"Stage '{stage.name}' failed: {result.error}")
                context.add_error(f"{stage.name}: {result.error}")

            # Stop pipeline on failure (optional: could make this configurable)
            if result.is_failure():
                logger.error(f"Pipeline stopped due to stage failure: {stage.name}")
                if document:
                    document.mark_failed(result.error or "Stage failed")
                break

        # Final status
        if context.is_successful():
            logger.success(f"Pipeline completed successfully in {context.get_duration():.2f}s")
            if document:
                # Get entity and relation counts from context
                entities = context.enriched_entities or context.entities or []
                relations = context.enriched_relations or context.relations or []
                document.mark_completed(len(entities), len(relations))
        else:
            logger.error(f"Pipeline failed after {context.get_duration():.2f}s")

        return context

    async def _update_document_status(
        self,
        document: Document,
        stage_name: str,
        current_stage: int,
        total_stages: int
    ):
        """Update document status based on current stage."""
        progress = (current_stage / total_stages) * 100

        # Map stage names to document statuses
        status_mapping = {
            "ParsingStage": ProcessingStatus.PARSING,
            "ChunkingStage": ProcessingStatus.PARSING,
            "EmbeddingStage": ProcessingStatus.EXTRACTING_ENTITIES,
            "NERStage": ProcessingStatus.EXTRACTING_ENTITIES,
            "ExtractionStage": ProcessingStatus.EXTRACTING_RELATIONS,
            "TransformationStage": ProcessingStatus.EXTRACTING_RELATIONS,
            "EnrichmentStage": ProcessingStatus.STORING,
            "ValidationStage": ProcessingStatus.VALIDATING,
            "StorageStage": ProcessingStatus.STORING,
        }

        status = status_mapping.get(stage_name, ProcessingStatus.PARSING)
        document.status = status
        document.progress = progress

    def __repr__(self) -> str:
        return f"<Pipeline(name='{self.name}', stages={len(self.stages)})>"

    def __str__(self) -> str:
        stages_str = "\n".join(f"  {i+1}. {s.name}" for i, s in enumerate(self.stages))
        return f"{self.name}:\n{stages_str}"
