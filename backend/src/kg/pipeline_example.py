"""
Example usage of the modular KG pipeline.

This file demonstrates how to use the pipeline system for document processing.
"""

import asyncio
from pathlib import Path

from loguru import logger

from kg.pipeline import Pipeline, PipelineContext
from kg.pipeline.factory import PipelineFactory, create_pipeline
from kg.pipeline.stages import (
    ParsingStage,
    ChunkingStage,
    ExtractionStage,
    ValidationStage,
    StorageStage
)
from kg.models.document import Document


async def example_basic_usage():
    """Example 1: Basic pipeline usage with factory."""
    logger.info("=== Example 1: Basic Factory Usage ===")

    # Create pipeline using factory
    pipeline = PipelineFactory.create_csv_pipeline()

    # Print pipeline structure
    print(pipeline)

    # Execute pipeline
    file_path = Path("data/test_datasets/movies_sample.csv")
    document = Document(filename="movies_sample.csv", format="csv", size_bytes=1024)

    context = await pipeline.execute(
        file_path=file_path,
        filename="movies_sample.csv",
        file_format="csv",
        document=document
    )

    # Print results
    print("\n=== Pipeline Results ===")
    print(f"Success: {context.is_successful()}")
    print(f"Duration: {context.get_duration():.2f}s")
    print(f"Entities: {len(context.entities)}")
    print(f"Relations: {len(context.relations)}")
    print(f"Errors: {len(context.errors)}")

    # Print stage results
    print("\n=== Stage Results ===")
    for result in context.stage_results:
        status_emoji = "✅" if result.is_success() else "❌"
        print(f"{status_emoji} {result.stage_name}: {result.status.value} ({result.duration_seconds:.2f}s)")


async def example_custom_pipeline():
    """Example 2: Build custom pipeline manually."""
    logger.info("=== Example 2: Custom Pipeline ===")

    # Build pipeline manually
    pipeline = Pipeline(name="My Custom Pipeline")
    pipeline.add_stage(ParsingStage())
    pipeline.add_stage(ExtractionStage(batch_size=100))
    pipeline.add_stage(ValidationStage(strict=False))
    pipeline.add_stage(StorageStage())

    # Disable a stage dynamically
    validation_stage = pipeline.get_stage("ValidationStage")
    if validation_stage:
        validation_stage.disable()

    # Execute
    file_path = Path("data/test_datasets/movies_sample.csv")
    context = await pipeline.execute(
        file_path=file_path,
        filename="movies_sample.csv",
        file_format="csv"
    )

    print(f"Pipeline completed: {context.is_successful()}")


async def example_custom_factory():
    """Example 3: Use custom factory with options."""
    logger.info("=== Example 3: Custom Factory ===")

    # Create custom pipeline via factory
    pipeline = PipelineFactory.create_custom_pipeline(
        include_chunking=False,
        include_embedding=False,
        include_ner=False,
        include_transformation=True,
        include_enrichment=False,
        include_validation=True,
        strict_validation=False,
        batch_size=75
    )

    print(pipeline)


async def example_format_based():
    """Example 4: Auto-select pipeline based on file format."""
    logger.info("=== Example 4: Format-Based Pipeline ===")

    # Auto-select pipeline for CSV
    csv_pipeline = PipelineFactory.get_pipeline_for_format("csv")
    print("CSV Pipeline:")
    print(csv_pipeline)

    # Auto-select pipeline for PDF
    pdf_pipeline = PipelineFactory.get_pipeline_for_format("pdf")
    print("\nPDF Pipeline:")
    print(pdf_pipeline)


async def example_error_handling():
    """Example 5: Error handling and recovery."""
    logger.info("=== Example 5: Error Handling ===")

    pipeline = PipelineFactory.create_minimal_pipeline()

    # Try to process non-existent file
    try:
        context = await pipeline.execute(
            file_path=Path("non_existent_file.csv"),
            filename="non_existent_file.csv",
            file_format="csv"
        )

        if not context.is_successful():
            print("Pipeline failed:")
            for error in context.errors:
                print(f"  - {error}")

            # Print failed stages
            for result in context.stage_results:
                if result.is_failure():
                    print(f"\nFailed stage: {result.stage_name}")
                    print(f"Error: {result.error}")

    except Exception as e:
        logger.error(f"Pipeline exception: {e}")


async def example_context_inspection():
    """Example 6: Inspect pipeline context."""
    logger.info("=== Example 6: Context Inspection ===")

    pipeline = create_pipeline("csv")

    file_path = Path("data/test_datasets/movies_sample.csv")
    context = await pipeline.execute(
        file_path=file_path,
        filename="movies_sample.csv",
        file_format="csv"
    )

    # Convert context to dict
    context_dict = context.to_dict()

    print("\n=== Context Summary ===")
    print(f"Filename: {context_dict['filename']}")
    print(f"Format: {context_dict['file_format']}")
    print(f"Duration: {context_dict['duration_seconds']:.2f}s")
    print(f"Entities: {context_dict['entities_count']}")
    print(f"Relations: {context_dict['relations_count']}")
    print(f"Success: {context_dict['successful']}")

    print("\n=== Stages ===")
    for stage in context_dict['stages']:
        print(f"  {stage['name']}: {stage['status']} ({stage['duration']:.2f}s)")


async def main():
    """Run all examples."""
    examples = [
        # example_basic_usage,
        # example_custom_pipeline,
        example_custom_factory,
        example_format_based,
        # example_error_handling,
        # example_context_inspection,
    ]

    for example_func in examples:
        try:
            await example_func()
            print("\n" + "="*60 + "\n")
        except Exception as e:
            logger.error(f"Example failed: {e}")


if __name__ == "__main__":
    # Run examples
    asyncio.run(main())
