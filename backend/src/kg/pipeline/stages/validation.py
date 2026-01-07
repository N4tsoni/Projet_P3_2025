"""
Validation Stage: Validate extracted and enriched data.

Ensures data quality and consistency before storage.
"""

from typing import Dict, Any, List

from loguru import logger

from ..base import Stage, StageResult, StageStatus
from ..pipeline import PipelineContext


class ValidationStage(Stage):
    """
    Stage 8: Data Validation

    Responsibilities:
    - Validate entity structure and properties
    - Validate relation references (entities exist)
    - Check data types and constraints
    - Identify and report data quality issues
    - Filter out invalid data

    Input:
        - context.enriched_entities (or context.entities)
        - context.enriched_relations (or context.relations)

    Output:
        - context.validation_results (validation report)
        - Filters context entities/relations (removes invalid ones)
    """

    def __init__(self, strict: bool = False):
        """
        Initialize validation stage.

        Args:
            strict: If True, fail on any validation error. If False, log warnings.
        """
        super().__init__(name="ValidationStage")
        self.strict = strict

    async def execute(self, context: PipelineContext) -> StageResult:
        """Validate entities and relations."""
        logger.info(f"Validating data (strict={self.strict})")

        try:
            # Use enriched data if available, otherwise use original
            entities = context.enriched_entities or context.entities
            relations = context.enriched_relations or context.relations

            # Validate entities
            entity_validation = await self._validate_entities(entities)

            # Validate relations
            relation_validation = await self._validate_relations(relations, entities)

            # Combine validation results
            validation_results = {
                "entities": entity_validation,
                "relations": relation_validation,
                "total_errors": entity_validation["errors"] + relation_validation["errors"],
                "total_warnings": entity_validation["warnings"] + relation_validation["warnings"]
            }

            context.validation_results = validation_results

            # Log results
            logger.info(
                f"Validation complete: "
                f"{validation_results['total_errors']} errors, "
                f"{validation_results['total_warnings']} warnings"
            )

            # Fail if strict mode and errors found
            if self.strict and validation_results["total_errors"] > 0:
                return StageResult(
                    stage_name=self.name,
                    status=StageStatus.FAILED,
                    duration_seconds=0.0,
                    error=f"Validation failed with {validation_results['total_errors']} errors",
                    output_data=validation_results
                )

            return StageResult(
                stage_name=self.name,
                status=StageStatus.COMPLETED,
                duration_seconds=0.0,
                output_data=validation_results
            )

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return StageResult(
                stage_name=self.name,
                status=StageStatus.FAILED,
                duration_seconds=0.0,
                error=str(e)
            )

    async def _validate_entities(self, entities: List[Any]) -> Dict[str, Any]:
        """
        Validate entities.

        TODO: Implement validation rules:
        - Required fields present (type, name)
        - Name not empty
        - Type is valid enum value
        - Properties are valid JSON
        - Confidence in valid range [0, 1]
        """
        logger.warning("Entity validation not fully implemented")

        return {
            "total": len(entities),
            "valid": len(entities),
            "invalid": 0,
            "errors": 0,
            "warnings": 0,
            "issues": []
        }

    async def _validate_relations(
        self,
        relations: List[Any],
        entities: List[Any]
    ) -> Dict[str, Any]:
        """
        Validate relations.

        TODO: Implement validation rules:
        - Required fields present (type, from_entity, to_entity)
        - Referenced entities exist
        - Relation type is valid enum value
        - No self-loops (if not allowed)
        - Properties are valid JSON
        """
        logger.warning("Relation validation not fully implemented")

        return {
            "total": len(relations),
            "valid": len(relations),
            "invalid": 0,
            "errors": 0,
            "warnings": 0,
            "issues": []
        }
