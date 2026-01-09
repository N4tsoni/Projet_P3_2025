"""
Entity models for Knowledge Graph.
Represents nodes in the graph.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Literal
from enum import Enum


class EntityType(str, Enum):
    """Supported entity types."""
    PERSON = "Person"
    MOVIE = "Movie"
    STUDIO = "Studio"
    ORGANIZATION = "Organization"
    LOCATION = "Location"
    CONCEPT = "Concept"
    GENERIC = "Generic"


class Entity(BaseModel):
    """
    Represents an entity (node) in the knowledge graph.

    Examples:
        - Person: {type: "Person", name: "Tom Hanks", birth_year: 1956}
        - Movie: {type: "Movie", title: "Forrest Gump", year: 1994, genre: "Drama"}
    """

    # Core fields
    type: EntityType = Field(..., description="Type of entity (Person, Movie, etc.)")
    name: str = Field(..., description="Primary identifier/name of the entity")

    # Properties (flexible key-value storage)
    properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional properties specific to entity type"
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
        Convert to Neo4j node properties.
        Flattens properties dict into root level.
        """
        props = {
            "name": self.name,
            **self.properties,
            "confidence": self.confidence
        }
        if self.source:
            props["source"] = self.source
        return props

    def get_label(self) -> str:
        """Get Neo4j label (entity type)."""
        return self.type.value if isinstance(self.type, Enum) else self.type


class EntityBatch(BaseModel):
    """Batch of entities for bulk operations."""
    entities: List[Entity] = Field(..., description="List of entities")
    total: int = Field(..., description="Total number of entities")
    document_source: Optional[str] = Field(None, description="Source document")


# Example entity schemas for common types
class PersonEntity(Entity):
    """Person entity with typed properties."""
    type: Literal[EntityType.PERSON] = EntityType.PERSON

    @property
    def birth_year(self) -> Optional[int]:
        return self.properties.get("birth_year")

    @property
    def nationality(self) -> Optional[str]:
        return self.properties.get("nationality")


class MovieEntity(Entity):
    """Movie entity with typed properties."""
    type: Literal[EntityType.MOVIE] = EntityType.MOVIE

    @property
    def year(self) -> Optional[int]:
        return self.properties.get("year")

    @property
    def genre(self) -> Optional[str]:
        return self.properties.get("genre")

    @property
    def rating(self) -> Optional[float]:
        return self.properties.get("rating")


class StudioEntity(Entity):
    """Studio/Organization entity with typed properties."""
    type: Literal[EntityType.STUDIO] = EntityType.STUDIO

    @property
    def country(self) -> Optional[str]:
        return self.properties.get("country")

    @property
    def founded_year(self) -> Optional[int]:
        return self.properties.get("founded_year")
