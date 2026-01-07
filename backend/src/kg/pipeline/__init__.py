"""
Pipeline module for Knowledge Graph construction.

This module provides a modular pipeline architecture for processing documents
and building knowledge graphs. The pipeline is composed of discrete stages,
each with a specific responsibility.
"""

from .pipeline import Pipeline, PipelineContext
from .base import Stage, StageResult

__all__ = ["Pipeline", "PipelineContext", "Stage", "StageResult"]
