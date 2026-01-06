"""
Request models for API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class KnowledgeAddRequest(BaseModel):
    """Request to add knowledge to the graph."""
    content: str = Field(..., description="Content to add to knowledge graph", min_length=1)
    source: Optional[str] = Field(None, description="Source of the knowledge")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class KnowledgeQueryRequest(BaseModel):
    """Request to query the knowledge graph."""
    query: str = Field(..., description="Query string", min_length=1)
    num_results: int = Field(default=10, description="Number of results to return", ge=1, le=100)
