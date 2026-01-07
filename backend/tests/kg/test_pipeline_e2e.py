"""
End-to-end test for KG pipeline.
Tests the complete flow from CSV to Neo4j.
"""
import pytest
from pathlib import Path
import asyncio

from src.kg.parsers.csv_parser import CSVParser
from src.kg.agents.entity_extractor_agent import EntityExtractorAgent
from src.kg.agents.relation_extractor_agent import RelationExtractorAgent
from src.kg.services.neo4j_service import Neo4jService
from src.kg.services.pipeline_orchestrator import PipelineOrchestrator
from src.kg.models.document import Document, DocumentFormat


class TestPipelineE2E:
    """End-to-end tests for the KG construction pipeline."""

    @pytest.fixture
    def csv_file(self):
        """Return path to test CSV file."""
        return Path("data/test_datasets/movies_sample.csv")

    @pytest.fixture
    def neo4j_service(self):
        """Create Neo4j service instance."""
        service = Neo4jService()
        service.connect()
        yield service
        service.close()

    def test_csv_parser(self, csv_file):
        """Test CSV parsing."""
        parser = CSVParser()
        df, metadata = parser.parse(csv_file)

        assert len(df) == 10, "Should parse 10 movies"
        assert len(df.columns) == 8, "Should have 8 columns"
        assert "title" in df.columns
        assert "director" in df.columns
        assert "actors" in df.columns

        # Check metadata
        assert metadata["filename"] == "movies_sample.csv"
        assert metadata["row_count"] == 10
        assert metadata["column_count"] == 8

    @pytest.mark.asyncio
    async def test_entity_extraction(self, csv_file):
        """Test entity extraction from CSV."""
        # Parse CSV
        parser = CSVParser()
        df, metadata = parser.parse(csv_file)
        records = parser.to_records(df)

        # Extract entities
        agent = EntityExtractorAgent()
        entities = await agent.extract_entities_batch(
            records=records[:5],  # Test with first 5 rows
            metadata=metadata,
            source_filename=csv_file.name
        )

        # Assertions
        assert len(entities) > 0, "Should extract at least some entities"

        # Check entity types
        entity_types = {e.type.value for e in entities}
        assert "Person" in entity_types or "Movie" in entity_types

        # Check entity structure
        for entity in entities:
            assert entity.name is not None
            assert entity.type is not None
            assert isinstance(entity.properties, dict)
            assert 0.0 <= entity.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_relation_extraction(self, csv_file):
        """Test relation extraction from CSV."""
        # Parse CSV
        parser = CSVParser()
        df, metadata = parser.parse(csv_file)
        records = parser.to_records(df)

        # Extract entities first
        entity_agent = EntityExtractorAgent()
        entities = await entity_agent.extract_entities_batch(
            records=records[:5],
            metadata=metadata,
            source_filename=csv_file.name
        )

        # Extract relations
        relation_agent = RelationExtractorAgent()
        relations = await relation_agent.extract_relations_batch(
            records=records[:5],
            entities=entities,
            metadata=metadata,
            source_filename=csv_file.name
        )

        # Assertions
        assert len(relations) > 0, "Should extract at least some relations"

        # Check relation structure
        for relation in relations:
            assert relation.from_entity is not None
            assert relation.to_entity is not None
            assert relation.type is not None
            assert 0.0 <= relation.confidence <= 1.0

    def test_neo4j_connection(self, neo4j_service):
        """Test Neo4j connection."""
        # Get initial stats
        stats = neo4j_service.get_graph_stats()

        assert "total_nodes" in stats
        assert "total_relationships" in stats
        assert isinstance(stats["total_nodes"], int)
        assert isinstance(stats["total_relationships"], int)

    @pytest.mark.asyncio
    async def test_full_pipeline(self, csv_file):
        """Test the complete pipeline end-to-end."""
        # Create document
        document = Document(
            filename=csv_file.name,
            format=DocumentFormat.CSV,
            size_bytes=csv_file.stat().st_size
        )

        # Run pipeline
        orchestrator = PipelineOrchestrator()

        try:
            result = await orchestrator.process_csv_file(csv_file, document)

            # Verify result structure
            assert result["status"] == "completed"
            assert "extraction" in result
            assert "storage" in result
            assert "graph_stats" in result

            # Verify extraction
            extraction = result["extraction"]
            assert extraction["entities_extracted"] > 0
            assert extraction["relations_extracted"] > 0

            # Verify storage
            storage = result["storage"]
            assert storage["entities_stored"] > 0
            assert storage["relations_stored"] > 0

            # Verify document status
            assert document.status.value == "completed"
            assert document.progress == 100.0
            assert document.entities_extracted > 0
            assert document.relations_extracted > 0

        except Exception as e:
            pytest.fail(f"Pipeline failed: {e}")


if __name__ == "__main__":
    """Run tests directly for development."""
    pytest.main([__file__, "-v", "-s"])
