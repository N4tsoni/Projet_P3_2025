"""
Script to test Neo4j and Graphiti connection.
"""
import asyncio
import os
from loguru import logger
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


async def test_neo4j_connection():
    """Test basic Neo4j connection."""
    uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")

    logger.info(f"Testing Neo4j connection to {uri}")

    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        logger.info("✅ Neo4j connection successful")

        # Run a simple query
        with driver.session() as session:
            result = session.run("RETURN 'Hello, Neo4j!' AS message")
            message = result.single()["message"]
            logger.info(f"✅ Query executed: {message}")

        driver.close()
        return True

    except Exception as e:
        logger.error(f"❌ Neo4j connection failed: {e}")
        return False


async def test_graphiti_initialization():
    """Test Graphiti initialization."""
    logger.info("Testing Graphiti initialization")

    try:
        from src.graph.graphiti_client import GraphitiClient

        client = GraphitiClient()
        logger.info("✅ Graphiti initialized successfully")

        # Test adding a simple episode
        logger.info("Testing episode addition...")
        nodes = await client.add_episode(
            name="test_episode",
            content="This is a test transaction of 100 EUR for office supplies.",
            source_description="Test data",
        )
        logger.info(f"✅ Episode added: {len(nodes)} nodes created")

        # Test search
        logger.info("Testing search...")
        results = await client.search(query="office supplies", num_results=5)
        logger.info(f"✅ Search completed: {len(results)} results found")

        await client.close()
        return True

    except Exception as e:
        logger.error(f"❌ Graphiti initialization failed: {e}")
        logger.exception(e)
        return False


async def main():
    """Run all connection tests."""
    logger.info("Starting connection tests...")

    # Test Neo4j first
    neo4j_ok = await test_neo4j_connection()

    if neo4j_ok:
        # If Neo4j works, test Graphiti
        graphiti_ok = await test_graphiti_initialization()

        if graphiti_ok:
            logger.info("🎉 All tests passed!")
        else:
            logger.warning("⚠️ Graphiti tests failed")
    else:
        logger.warning("⚠️ Neo4j connection failed, skipping Graphiti tests")


if __name__ == "__main__":
    asyncio.run(main())
