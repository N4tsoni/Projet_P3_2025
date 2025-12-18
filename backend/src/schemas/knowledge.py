"""
Knowledge graph schemas.
"""
from pydantic import BaseModel
from typing import List, Dict, Any


class KnowledgeNode(BaseModel):
    """Knowledge graph node."""

    id: str
    label: str
    type: str
    properties: Dict[str, Any]


class KnowledgeEdge(BaseModel):
    """Knowledge graph edge."""

    id: str
    source: str
    target: str
    type: str
    properties: Dict[str, Any]


class KnowledgeGraphResponse(BaseModel):
    """Knowledge graph response."""

    nodes: List[KnowledgeNode]
    edges: List[KnowledgeEdge]


class KnowledgeQueryResponse(BaseModel):
    """Knowledge query response."""

    query: str
    results: List[Dict[str, Any]]
    message: str


class KnowledgeAddRequest(BaseModel):
    """Request to add knowledge."""

    data: Dict[str, Any]


class KnowledgeAddResponse(BaseModel):
    """Response after adding knowledge."""

    success: bool
    message: str
