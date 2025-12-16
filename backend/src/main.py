"""
Main entry point for the GraphRAG Accounting Agent application.
"""
import os
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Main application entry point."""
    logger.info("Starting GraphRAG Accounting Agent")
    logger.info(f"Environment: {os.getenv('APP_ENV', 'development')}")
    logger.info(f"Neo4j URI: {os.getenv('NEO4J_URI')}")

    # TODO: Initialize application components
    # - Connect to Neo4j
    # - Initialize Graphiti
    # - Setup agents
    # - Launch interface (CLI/Streamlit)

    logger.info("Application initialized successfully")

if __name__ == "__main__":
    main()
