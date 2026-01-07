"""
Relation models for Knowledge Graph.
Represents edges/relationships between entities.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Literal
from enum import Enum


class RelationType(str, Enum):
    """Supported relation types."""
    ACTED_IN = "ACTED_IN"
    DIRECTED = "DIRECTED"
    PRODUCED_BY = "PRODUCED_BY"
    WORKS_AT = "WORKS_AT"
    KNOWS = "KNOWS"
    RELATED_TO = "RELATED_TO"
    LOCATED_IN = "LOCATED_IN"
    PART_OF = "PART_OF"


class Relation(BaseModel):
    """
    Represents a relationship (edge) in the knowledge graph.

    Examples:
        - Actor → Movie: {
            type: "ACTED_IN",
            from_entity: "Tom Hanks",
            to_entity: "Forrest Gump",
            properties: {role: "Forrest Gump"}
          }
    """

    # Core fields
    type: RelationType = Field(..., description="Type of relationship")
    from_entity: str = Field(..., description="Source entity name")
    to_entity: str = Field(..., description="Target entity name")

    # Optional: Entity types for validation
    from_entity_type: Optional[str] = Field(None, description="Type of source entity")
    to_entity_type: Optional[str] = Field(None, description="Type of target entity")

    # Properties (flexible key-value storage)
    properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional properties specific to relation (e.g., role, year)"
    )

    # Metadata
    source: Optional[str] = Field(None, description="Source document/file")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Extraction confidence score")

    # Neo4j ID (set after creation)
    neo4j_id: Optional[str] = Field(None, description="Neo4j internal ID")

    class Config:
        use_enum_values = True

    def to_neo4j_props(self) -> Dict[str, Any]:
        """
        Convert to Neo4j relationship properties.
        """
        props = {
            **self.properties,
            "confidence": self.confidence
        }
        if self.source:
            props["source"] = self.source
        return props

    def get_type(self) -> str:
        """Get Neo4j relationship type."""
        return self.type.value if isinstance(self.type, Enum) else self.type


class RelationBatch(BaseModel):
    """Batch of relations for bulk operations."""
    relations: List[Relation] = Field(..., description="List of relations")
    total: int = Field(..., description="Total number of relations")
    document_source: Optional[str] = Field(None, description="Source document")


# Typed relation examples
class ActedInRelation(Relation):
    """Person ACTED_IN Movie relationship."""
    type: Literal[RelationType.ACTED_IN] = RelationType.ACTED_IN
    from_entity_type: Literal["Person"] = "Person"
    to_entity_type: Literal["Movie"] = "Movie"

    @property
    def role(self) -> Optional[str]:
        """Character name/role in the movie."""
        return self.properties.get("role")


class DirectedRelation(Relation):
    """Person DIRECTED Movie relationship."""
    type: Literal[RelationType.DIRECTED] = RelationType.DIRECTED
    from_entity_type: Literal["Person"] = "Person"
    to_entity_type: Literal["Movie"] = "Movie"


class ProducedByRelation(Relation):
    """Movie PRODUCED_BY Studio relationship."""
    type: Literal[RelationType.PRODUCED_BY] = RelationType.PRODUCED_BY
    from_entity_type: Literal["Movie"] = "Movie"
    to_entity_type: Literal["Studio"] = "Studio"

    @property
    def budget(self) -> Optional[float]:
        """Production budget."""
        return self.properties.get("budget")
