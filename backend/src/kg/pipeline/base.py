"""
Base classes for pipeline stages.

Defines the abstract base class for pipeline stages and common data structures.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class StageStatus(str, Enum):
    """Status of a pipeline stage execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StageResult:
    """Result of a pipeline stage execution."""

    stage_name: str
    status: StageStatus
    duration_seconds: float
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def is_success(self) -> bool:
        """Check if stage completed successfully."""
        return self.status == StageStatus.COMPLETED

    def is_failure(self) -> bool:
        """Check if stage failed."""
        return self.status == StageStatus.FAILED


class Stage(ABC):
    """
    Abstract base class for all pipeline stages.

    Each stage is responsible for a specific step in the document processing pipeline.
    Stages receive a PipelineContext, process it, and return a StageResult.
    """

    def __init__(self, name: Optional[str] = None):
        """
        Initialize stage.

        Args:
            name: Optional custom name for the stage. If not provided, uses class name.
        """
        self.name = name or self.__class__.__name__
        self.enabled = True

    @abstractmethod
    async def execute(self, context: "PipelineContext") -> StageResult:
        """
        Execute the stage logic.

        Args:
            context: Pipeline context containing shared data and state.

        Returns:
            StageResult with execution status and output data.

        Raises:
            Exception: If stage execution fails critically.
        """
        pass

    async def run(self, context: "PipelineContext") -> StageResult:
        """
        Run the stage with timing and error handling.

        Args:
            context: Pipeline context.

        Returns:
            StageResult with timing information.
        """
        if not self.enabled:
            return StageResult(
                stage_name=self.name,
                status=StageStatus.SKIPPED,
                duration_seconds=0.0,
                metadata={"reason": "Stage disabled"}
            )

        start_time = datetime.now()

        try:
            result = await self.execute(context)
            result.duration_seconds = (datetime.now() - start_time).total_seconds()
            return result

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return StageResult(
                stage_name=self.name,
                status=StageStatus.FAILED,
                duration_seconds=duration,
                error=str(e),
                metadata={"exception_type": type(e).__name__}
            )

    def enable(self):
        """Enable this stage."""
        self.enabled = True

    def disable(self):
        """Disable this stage (will be skipped)."""
        self.enabled = False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', enabled={self.enabled})>"
