"""
Graphiti client initialization and configuration.
"""
import os
from typing import Optional
from loguru import logger
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodicNode
from graphiti_core.edges import EpisodicEdge
from graphiti_core.llm_client import LLMClient
from graphiti_core.embedder import EmbedderClient


class GraphitiClient:
    """
    Wrapper class for Graphiti initialization and management.
    """

    def __init__(
        self,
        neo4j_uri: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_password: Optional[str] = None,
        neo4j_database: str = "neo4j",
    ):
        """
        Initialize Graphiti client with Neo4j backend.

        Args:
            neo4j_uri: Neo4j connection URI (bolt://...)
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
            neo4j_database: Neo4j database name (default: "neo4j")
        """
        self.neo4j_uri = neo4j_uri or os.getenv("NEO4J_URI", "bolt://neo4j:7687")
        self.neo4j_user = neo4j_user or os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = neo4j_password or os.getenv("NEO4J_PASSWORD")
        self.neo4j_database = neo4j_database

        self.graphiti: Optional[Graphiti] = None
        self._initialize_graphiti()

    def _initialize_graphiti(self):
        """Initialize Graphiti with Neo4j connection."""
        try:
            logger.info(f"Initializing Graphiti with Neo4j at {self.neo4j_uri}")

            # Initialize Graphiti directly with connection parameters
            # Note: LLM client and embedder will use default OpenAI configuration
            # from OPENAI_API_KEY environment variable
            self.graphiti = Graphiti(
                uri=self.neo4j_uri,
                user=self.neo4j_user,
                password=self.neo4j_password,
            )

            logger.info("Graphiti initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Graphiti: {e}")
            raise

    async def add_episode(
        self,
        name: str,
        content: str,
        source_description: str,
        reference_time: Optional[str] = None,
    ) -> list[EpisodicNode]:
        """
        Add an episode (document/transaction) to the knowledge graph.

        Args:
            name: Name/identifier for the episode
            content: The actual content to process
            source_description: Description of the source
            reference_time: Optional timestamp for the episode

        Returns:
            List of created episodic nodes
        """
        if not self.graphiti:
            raise RuntimeError("Graphiti not initialized")

        try:
            logger.info(f"Adding episode: {name}")

            # Add episode to knowledge graph
            result = await self.graphiti.add_episode(
                name=name,
                episode_body=content,
                source_description=source_description,
                reference_time=reference_time,
            )

            logger.info(f"Episode added successfully: {len(result)} nodes created")
            return result

        except Exception as e:
            logger.error(f"Failed to add episode: {e}")
            raise

    async def search(
        self,
        query: str,
        num_results: int = 10,
    ) -> list:
        """
        Search the knowledge graph using semantic search.

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            List of search results
        """
        if not self.graphiti:
            raise RuntimeError("Graphiti not initialized")

        try:
            logger.info(f"Searching for: {query}")

            results = await self.graphiti.search(
                query=query,
                num_results=num_results,
            )

            logger.info(f"Found {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    async def close(self):
        """Close Graphiti connection."""
        if self.graphiti:
            try:
                # Close the Graphiti connection
                if hasattr(self.graphiti, 'close'):
                    await self.graphiti.close()
                logger.info("Graphiti connection closed")
            except Exception as e:
                logger.error(f"Error closing Graphiti: {e}")


# Singleton instance
_graphiti_client: Optional[GraphitiClient] = None


def get_graphiti_client() -> GraphitiClient:
    """
    Get or create the Graphiti client singleton.

    Returns:
        GraphitiClient instance
    """
    global _graphiti_client

    if _graphiti_client is None:
        _graphiti_client = GraphitiClient()

    return _graphiti_client
