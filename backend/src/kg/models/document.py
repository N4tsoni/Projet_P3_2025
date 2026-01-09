"""
Document models for Knowledge Graph pipeline.
Tracks source documents and processing status.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentFormat(str, Enum):
    """Supported document formats."""
    CSV = "csv"
    JSON = "json"
    PDF = "pdf"
    TXT = "txt"
    XML = "xml"
    XLSX = "xlsx"


class ProcessingStatus(str, Enum):
    """Document processing status."""
    PENDING = "pending"
    PARSING = "parsing"
    EXTRACTING_ENTITIES = "extracting_entities"
    EXTRACTING_RELATIONS = "extracting_relations"
    STORING = "storing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(BaseModel):
    """
    Represents a source document in the KG pipeline.

    Tracks the document through the pipeline stages.
    """

    # Core fields
    filename: str = Field(..., description="Original filename")
    format: DocumentFormat = Field(..., description="Document format")
    size_bytes: int = Field(..., description="File size in bytes")

    # Processing
    status: ProcessingStatus = Field(
        default=ProcessingStatus.PENDING,
        description="Current processing status"
    )
    progress: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Processing progress percentage"
    )

    # Metadata
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = Field(None, description="When processing completed")

    # Statistics
    entities_extracted: int = Field(default=0, description="Number of entities extracted")
    relations_extracted: int = Field(default=0, description="Number of relations extracted")

    # Error tracking
    error: Optional[str] = Field(None, description="Error message if failed")

    # Additional metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (encoding, columns, etc.)"
    )

    class Config:
        use_enum_values = True

    def mark_parsing(self):
        """Mark document as being parsed."""
        self.status = ProcessingStatus.PARSING
        self.progress = 10.0

    def mark_extracting_entities(self):
        """Mark document as extracting entities."""
        self.status = ProcessingStatus.EXTRACTING_ENTITIES
        self.progress = 30.0

    def mark_extracting_relations(self):
        """Mark document as extracting relations."""
        self.status = ProcessingStatus.EXTRACTING_RELATIONS
        self.progress = 60.0

    def mark_storing(self):
        """Mark document as storing to Neo4j."""
        self.status = ProcessingStatus.STORING
        self.progress = 80.0

    def mark_validating(self):
        """Mark document as validating."""
        self.status = ProcessingStatus.VALIDATING
        self.progress = 90.0

    def mark_completed(self, entities_count: int, relations_count: int):
        """Mark document as completed."""
        self.status = ProcessingStatus.COMPLETED
        self.progress = 100.0
        self.processed_at = datetime.utcnow()
        self.entities_extracted = entities_count
        self.relations_extracted = relations_count

    def mark_failed(self, error: str):
        """Mark document as failed."""
        self.status = ProcessingStatus.FAILED
        self.error = error
        self.processed_at = datetime.utcnow()


class DocumentUploadResponse(BaseModel):
    """Response after document upload."""
    document_id: str = Field(..., description="Unique document ID")
    filename: str = Field(..., description="Original filename")
    format: DocumentFormat = Field(..., description="Detected format")
    size_bytes: int = Field(..., description="File size")
    status: ProcessingStatus = Field(..., description="Initial status")


class DocumentStatusResponse(BaseModel):
    """Response for document processing status."""
    document_id: str = Field(..., description="Document ID")
    status: ProcessingStatus = Field(..., description="Current status")
    progress: float = Field(..., description="Progress percentage")
    entities_extracted: int = Field(..., description="Entities extracted so far")
    relations_extracted: int = Field(..., description="Relations extracted so far")
    error: Optional[str] = Field(None, description="Error if failed")
