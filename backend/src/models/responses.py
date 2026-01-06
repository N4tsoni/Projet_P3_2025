"""
Response models for API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    services: Optional[Dict[str, bool]] = Field(None, description="Sub-services status")


class VoiceProcessResponse(BaseModel):
    """Response from voice processing endpoint."""
    success: bool = Field(..., description="Whether processing succeeded")
    transcription: str = Field(..., description="Transcribed text from audio")
    response: str = Field(..., description="Agent's text response")
    audio_url: str = Field(..., description="URL to download response audio")


class ErrorResponse(BaseModel):
    """Error response."""
    error: str = Field(..., description="Error message")
    transcription: str = Field(default="", description="Partial transcription if available")
    response: str = Field(default="", description="Partial response if available")


class KnowledgeQueryResponse(BaseModel):
    """Response from knowledge graph query."""
    query: str = Field(..., description="Original query")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Query results")
    message: Optional[str] = Field(None, description="Additional message")


class KnowledgeAddResponse(BaseModel):
    """Response from knowledge addition."""
    success: bool = Field(..., description="Whether addition succeeded")
    message: str = Field(..., description="Response message")


class GraphNode(BaseModel):
    """Node in the knowledge graph."""
    id: str = Field(..., description="Node ID")
    label: str = Field(..., description="Node label")
    type: str = Field(..., description="Node type")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Node properties")


class GraphEdge(BaseModel):
    """Edge in the knowledge graph."""
    id: str = Field(..., description="Edge ID")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    type: str = Field(..., description="Edge type/relationship")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Edge properties")


class KnowledgeGraphResponse(BaseModel):
    """Response containing knowledge graph structure."""
    nodes: List[GraphNode] = Field(default_factory=list, description="Graph nodes")
    edges: List[GraphEdge] = Field(default_factory=list, description="Graph edges")
