"""
Pipeline Factory: Pre-configured pipelines for common use cases.

Provides convenient builders for different types of document processing.
"""

from typing import List, Optional

from .pipeline import Pipeline
from .stages import (
    ParsingStage,
    ChunkingStage,
    EmbeddingStage,
    NERStage,
    ExtractionStage,
    TransformationStage,
    EnrichmentStage,
    ValidationStage,
    StorageStage
)


class PipelineFactory:
    """Factory for creating pre-configured pipelines."""

    @staticmethod
    def create_default_pipeline() -> Pipeline:
        """
        Create default full-featured pipeline.

        Stages:
        1. Parsing
        2. Chunking
        3. Embedding
        4. NER
        5. Extraction
        6. Transformation
        7. Enrichment
        8. Validation
        9. Storage
        """
        return Pipeline(name="Default KG Pipeline", stages=[
            ParsingStage(),
            ChunkingStage(chunk_size=1000, chunk_overlap=200),
            EmbeddingStage(model_name="all-MiniLM-L6-v2"),
            NERStage(model_name="en_core_web_sm"),
            ExtractionStage(batch_size=50),
            TransformationStage(),
            EnrichmentStage(),
            ValidationStage(strict=False),
            StorageStage()
        ])

    @staticmethod
    def create_csv_pipeline() -> Pipeline:
        """
        Create pipeline optimized for CSV files.

        For structured CSV data, we skip chunking, embedding, and NER
        since data is already structured.

        Stages:
        1. Parsing (CSV)
        2. Extraction (LLM)
        3. Transformation
        4. Validation
        5. Storage
        """
        return Pipeline(name="CSV KG Pipeline", stages=[
            ParsingStage(),
            ExtractionStage(batch_size=50),
            TransformationStage(),
            ValidationStage(strict=False),
            StorageStage()
        ])

    @staticmethod
    def create_text_pipeline() -> Pipeline:
        """
        Create pipeline optimized for unstructured text (PDF, TXT).

        Includes full text processing: chunking, embedding, NER.

        Stages:
        1. Parsing
        2. Chunking
        3. Embedding
        4. NER
        5. Extraction
        6. Transformation
        7. Enrichment
        8. Validation
        9. Storage
        """
        return Pipeline(name="Text KG Pipeline", stages=[
            ParsingStage(),
            ChunkingStage(chunk_size=1000, chunk_overlap=200),
            EmbeddingStage(model_name="all-MiniLM-L6-v2"),
            NERStage(model_name="en_core_web_sm"),
            ExtractionStage(batch_size=50),
            TransformationStage(),
            EnrichmentStage(),
            ValidationStage(strict=False),
            StorageStage()
        ])

    @staticmethod
    def create_minimal_pipeline() -> Pipeline:
        """
        Create minimal pipeline (parsing + extraction + storage only).

        Fast pipeline for quick testing or simple use cases.

        Stages:
        1. Parsing
        2. Extraction
        3. Storage
        """
        return Pipeline(name="Minimal KG Pipeline", stages=[
            ParsingStage(),
            ExtractionStage(batch_size=100),
            StorageStage()
        ])

    @staticmethod
    def create_custom_pipeline(
        include_chunking: bool = True,
        include_embedding: bool = True,
        include_ner: bool = True,
        include_transformation: bool = True,
        include_enrichment: bool = True,
        include_validation: bool = True,
        strict_validation: bool = False,
        batch_size: int = 50
    ) -> Pipeline:
        """
        Create custom pipeline with optional stages.

        Args:
            include_chunking: Include chunking stage.
            include_embedding: Include embedding stage.
            include_ner: Include NER stage.
            include_transformation: Include transformation stage.
            include_enrichment: Include enrichment stage.
            include_validation: Include validation stage.
            strict_validation: Use strict validation (fail on errors).
            batch_size: Batch size for extraction.

        Returns:
            Configured pipeline.
        """
        stages = [ParsingStage()]

        if include_chunking:
            stages.append(ChunkingStage())

        if include_embedding:
            stages.append(EmbeddingStage())

        if include_ner:
            stages.append(NERStage())

        stages.append(ExtractionStage(batch_size=batch_size))

        if include_transformation:
            stages.append(TransformationStage())

        if include_enrichment:
            stages.append(EnrichmentStage())

        if include_validation:
            stages.append(ValidationStage(strict=strict_validation))

        stages.append(StorageStage())

        return Pipeline(name="Custom KG Pipeline", stages=stages)

    @staticmethod
    def get_pipeline_for_format(file_format: str) -> Pipeline:
        """
        Get recommended pipeline for a file format.

        Args:
            file_format: File format (csv, json, pdf, txt, etc.)

        Returns:
            Appropriate pipeline for the format.
        """
        format_lower = file_format.lower()

        if format_lower == "csv":
            return PipelineFactory.create_csv_pipeline()
        elif format_lower in ["pdf", "txt", "docx"]:
            return PipelineFactory.create_text_pipeline()
        elif format_lower == "json":
            # JSON could be structured or unstructured
            return PipelineFactory.create_default_pipeline()
        else:
            # Default fallback
            return PipelineFactory.create_default_pipeline()


# Convenience function
def create_pipeline(pipeline_type: str = "default", **kwargs) -> Pipeline:
    """
    Create a pipeline by type name.

    Args:
        pipeline_type: Type of pipeline ("default", "csv", "text", "minimal", "custom")
        **kwargs: Additional arguments for custom pipeline.

    Returns:
        Configured pipeline.
    """
    factory_map = {
        "default": PipelineFactory.create_default_pipeline,
        "csv": PipelineFactory.create_csv_pipeline,
        "text": PipelineFactory.create_text_pipeline,
        "minimal": PipelineFactory.create_minimal_pipeline,
        "custom": lambda: PipelineFactory.create_custom_pipeline(**kwargs)
    }

    factory = factory_map.get(pipeline_type, PipelineFactory.create_default_pipeline)
    return factory()
