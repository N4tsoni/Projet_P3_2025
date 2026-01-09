"""
Knowledge Graph Builder API routes.
Handles document upload, processing, and graph visualization.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
from typing import Dict, Any
from loguru import logger

from src.kg.services.pipeline_orchestrator import get_orchestrator
from src.kg.models.document import DocumentFormat


router = APIRouter(prefix="/api/kg", tags=["Knowledge Graph"])


# Temp directory for uploaded files
UPLOAD_DIR = Path("data/kg_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload a document for KG processing.

    Supported formats: CSV, JSON, PDF, TXT

    Returns:
        Upload confirmation and file info
    """
    try:
        # Validate file format
        file_extension = Path(file.filename).suffix.lower()
        format_mapping = {
            ".csv": DocumentFormat.CSV,
            ".json": DocumentFormat.JSON,
            ".pdf": DocumentFormat.PDF,
            ".txt": DocumentFormat.TXT,
            ".xlsx": DocumentFormat.XLSX,
            ".xml": DocumentFormat.XML
        }

        if file_extension not in format_mapping:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_extension}. "
                       f"Supported: {', '.join(format_mapping.keys())}"
            )

        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = file_path.stat().st_size
        logger.info(f"Uploaded file: {file.filename} ({file_size} bytes)")

        return {
            "status": "uploaded",
            "filename": file.filename,
            "format": format_mapping[file_extension],
            "size_bytes": file_size,
            "path": str(file_path)
        }

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process/{filename}")
async def process_document(filename: str) -> Dict[str, Any]:
    """
    Process an uploaded document through the KG pipeline.

    Stages:
    1. Parse document
    2. Extract entities (using Claude)
    3. Extract relations (using Claude)
    4. Store in Neo4j
    5. Validate

    Args:
        filename: Name of the uploaded file

    Returns:
        Processing results and statistics
    """
    try:
        # Find file
        file_path = UPLOAD_DIR / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")

        # Detect format
        file_extension = file_path.suffix.lower()
        format_mapping = {
            ".csv": DocumentFormat.CSV,
            ".json": DocumentFormat.JSON,
            ".pdf": DocumentFormat.PDF,
            ".txt": DocumentFormat.TXT
        }
        file_format = format_mapping.get(file_extension)

        if file_format is None:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format: {file_extension}"
            )

        # Process through pipeline
        logger.info(f"Processing {filename} through KG pipeline")
        orchestrator = get_orchestrator()
        result = await orchestrator.process_file(file_path, file_format)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-and-process")
async def upload_and_process(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload and immediately process a document in one call.

    Convenience endpoint that combines upload and process.

    Returns:
        Complete processing results
    """
    try:
        # Upload
        upload_result = await upload_document(file)
        filename = upload_result["filename"]

        # Process
        process_result = await process_document(filename)

        return {
            "upload": upload_result,
            "processing": process_result
        }

    except Exception as e:
        logger.error(f"Upload and process failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph/stats")
async def get_graph_statistics() -> Dict[str, Any]:
    """
    Get statistics about the knowledge graph.

    Returns:
        - Total nodes
        - Total relationships
        - Counts by node type
        - Counts by relationship type
    """
    try:
        orchestrator = get_orchestrator()
        stats = await orchestrator.get_graph_statistics()
        return stats

    except Exception as e:
        logger.error(f"Failed to get graph stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph/visualization")
async def get_graph_visualization(limit: int = 100) -> Dict[str, Any]:
    """
    Get graph data for visualization.

    Args:
        limit: Maximum number of nodes to return (default: 100)

    Returns:
        - nodes: List of node objects (id, label, properties)
        - edges: List of edge objects (id, from, to, type, properties)
    """
    try:
        if limit < 1 or limit > 1000:
            raise HTTPException(
                status_code=400,
                detail="Limit must be between 1 and 1000"
            )

        orchestrator = get_orchestrator()
        graph_data = await orchestrator.get_graph_visualization(limit)
        return graph_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get graph visualization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/graph/clear")
async def clear_graph() -> Dict[str, str]:
    """
    Clear all data from the knowledge graph.

    ⚠️ WARNING: This deletes ALL nodes and relationships!
    Use with caution, typically only for testing.

    Returns:
        Confirmation message
    """
    try:
        orchestrator = get_orchestrator()
        await orchestrator.clear_graph()

        return {
            "status": "cleared",
            "message": "All graph data has been deleted"
        }

    except Exception as e:
        logger.error(f"Failed to clear graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for KG service.

    Returns:
        Service status
    """
    try:
        # Test Neo4j connection
        orchestrator = get_orchestrator()
        stats = await orchestrator.get_graph_statistics()

        return {
            "status": "healthy",
            "neo4j": "connected",
            "total_nodes": str(stats.get("total_nodes", 0)),
            "total_relationships": str(stats.get("total_relationships", 0))
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.get("/uploaded-files")
async def list_uploaded_files() -> Dict[str, Any]:
    """
    List all uploaded files.

    Returns:
        List of uploaded file information
    """
    try:
        files = []
        for file_path in UPLOAD_DIR.glob("*"):
            if file_path.is_file():
                files.append({
                    "filename": file_path.name,
                    "size_bytes": file_path.stat().st_size,
                    "format": file_path.suffix.lower()
                })

        return {
            "count": len(files),
            "files": files
        }

    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        raise HTTPException(status_code=500, detail=str(e))
