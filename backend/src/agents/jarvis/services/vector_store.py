"""
Vector store service for semantic search using Neo4j vector index.
"""
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
from loguru import logger
import numpy as np

from src.kg.services.neo4j_service import Neo4jService


class VectorStore:
    """Service for embedding-based semantic search using Neo4j vector index."""

    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize vector store with Neo4j.

        Args:
            embedding_model: Sentence-transformers model name
        """
        self.embedding_model_name = embedding_model
        self.model = SentenceTransformer(embedding_model)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

        # Neo4j service
        self.neo4j = Neo4jService()
        try:
            self.neo4j.connect()
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

        logger.info(f"Vector store initialized with model: {embedding_model} (dim: {self.embedding_dim})")

        # Create vector index if it does not exist
        self._ensure_vector_index()

    def _ensure_vector_index(self):
        """Create Neo4j vector index if it does not exist."""
        try:
            with self.neo4j.driver.session() as session:
                # Check if index exists
                result = session.run("SHOW INDEXES")
                indexes = [record["name"] for record in result]

                if "entity_embedding_index" not in indexes:
                    # Create vector index
                    session.run(f"""
                        CREATE VECTOR INDEX entity_embedding_index IF NOT EXISTS
                        FOR (n:Entity)
                        ON n.embedding
                        OPTIONS {{
                            indexConfig: {{
                                `vector.dimensions`: {self.embedding_dim},
                                `vector.similarity_function`: 'cosine'
                            }}
                        }}
                    """)
                    logger.info("Created Neo4j vector index: entity_embedding_index")
                else:
                    logger.info("Vector index already exists")
        except Exception as e:
            logger.warning(f"Could not create vector index (might already exist): {e}")

    async def build_index_from_kg(self):
        """
        Build vector embeddings for all entities in Neo4j.
        Adds embedding property to each node.
        """
        logger.info("Building embeddings for Neo4j entities...")

        with self.neo4j.driver.session() as session:
            # Fetch all entities
            result = session.run("""
                MATCH (n)
                WHERE n.name IS NOT NULL
                RETURN elementId(n) as id, n.name as name, labels(n) as labels, properties(n) as properties
            """)

            entities = list(result)

            if not entities:
                logger.warning("No entities found in Neo4j to index")
                return

            logger.info(f"Generating embeddings for {len(entities)} entities...")

            # Generate embeddings in batch
            texts = []
            for record in entities:
                name = record.get("name", "Unknown")
                properties = dict(record["properties"])

                # Build text for embedding: name + properties
                text_parts = [name]
                for key, value in properties.items():
                    if key != "name" and key != "embedding" and value:
                        text_parts.append(f"{key}: {value}")
                text = " | ".join(text_parts)
                texts.append(text)

            # Generate all embeddings at once
            embeddings = self.model.encode(texts, show_progress_bar=True)

            # Update Neo4j nodes with embeddings
            for record, embedding in zip(entities, embeddings):
                entity_id = record["id"]
                session.run("""
                    MATCH (n)
                    WHERE elementId(n) = $id
                    SET n.embedding = $embedding
                """, id=entity_id, embedding=embedding.tolist())

            logger.info(f"Successfully added embeddings to {len(entities)} entities")

    async def add_entities(self, entities: List[Dict[str, Any]]):
        """
        Add embeddings to new entities.

        Args:
            entities: List of entity dicts with name, type, properties
        """
        if not entities:
            return

        texts = []
        entity_names = []

        for entity in entities:
            # Build text for embedding
            text_parts = [entity.get("name", "Unknown")]
            properties = entity.get("properties", {})
            for key, value in properties.items():
                if key != "name" and key != "embedding" and value:
                    text_parts.append(f"{key}: {value}")
            text = " | ".join(text_parts)

            texts.append(text)
            entity_names.append(entity.get("name"))

        # Generate embeddings
        embeddings = self.model.encode(texts)

        # Update entities in Neo4j
        with self.neo4j.driver.session() as session:
            for name, embedding in zip(entity_names, embeddings):
                session.run("""
                    MATCH (n {name: $name})
                    SET n.embedding = $embedding
                """, name=name, embedding=embedding.tolist())

        logger.info(f"Added embeddings to {len(entities)} entities")

    async def semantic_search(
        self,
        query: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search using Neo4j vector index.

        Args:
            query: Search query text
            top_k: Number of results to return

        Returns:
            List of dicts with entity info and similarity scores
        """
        # Generate query embedding
        query_embedding = self.model.encode(query)

        # Search using Neo4j vector index
        with self.neo4j.driver.session() as session:
            result = session.run("""
                CALL db.index.vector.queryNodes(
                    'entity_embedding_index',
                    $top_k,
                    $query_embedding
                )
                YIELD node, score
                OPTIONAL MATCH (node)-[r]->(m)
                RETURN 
                    node.name as name,
                    labels(node)[0] as type,
                    properties(node) as properties,
                    score,
                    collect({
                        type: type(r),
                        target_name: m.name,
                        target_type: labels(m)[0],
                        properties: properties(r)
                    }) as relationships
            """, top_k=top_k, query_embedding=query_embedding.tolist())

            candidates = []
            for record in result:
                name = record["name"]
                entity_type = record["type"]
                properties = dict(record["properties"])
                similarity_score = record["score"]
                relationships = [
                    rel for rel in record["relationships"]
                    if rel.get("target_name")  # Filter out None relationships
                ]

                # Remove embedding from properties (large array)
                if 'embedding' in properties:
                    del properties['embedding']

                candidates.append({
                    "entity": {
                        "name": name,
                        "type": entity_type,
                        "properties": properties
                    },
                    "relationships": relationships[:10],  # Limit relationships
                    "relationship_count": len(relationships),
                    "similarity_score": float(similarity_score)
                })

        logger.debug(f"Found {len(candidates)} candidates for query: {query[:50]}...")
        return candidates

    def get_count(self) -> int:
        """Get number of entities with embeddings."""
        with self.neo4j.driver.session() as session:
            result = session.run("""
                MATCH (n)
                WHERE n.embedding IS NOT NULL
                RETURN count(n) as count
            """)
            return result.single()["count"]

    def clear(self):
        """Remove all embeddings from entities."""
        with self.neo4j.driver.session() as session:
            session.run("""
                MATCH (n)
                WHERE n.embedding IS NOT NULL
                REMOVE n.embedding
            """)
        logger.warning("All embeddings removed from entities")


# Singleton instance
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """
    Get or create vector store singleton.

    Returns:
        VectorStore instance
    """
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
