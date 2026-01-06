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


# ==================== Conversation Models ====================

class MessageResponse(BaseModel):
    """Single message in a conversation."""
    id: int = Field(..., description="Message ID")
    role: str = Field(..., description="Message role (user or assistant)")
    content: str = Field(..., description="Message text content")
    audio_url: Optional[str] = Field(None, description="URL to audio file (for assistant messages)")
    created_at: str = Field(..., description="Message creation timestamp")

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Conversation with optional messages."""
    id: str = Field(..., description="Conversation ID")
    name: str = Field(..., description="Conversation name/title")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    messages: Optional[List[MessageResponse]] = Field(None, description="Messages in conversation")

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """List of conversations."""
    conversations: List[ConversationResponse] = Field(..., description="List of conversations")
    total: int = Field(..., description="Total number of conversations")


class ConversationCreateResponse(BaseModel):
    """Response after creating a conversation."""
    success: bool = Field(..., description="Whether creation succeeded")
    conversation: ConversationResponse = Field(..., description="Created conversation")
