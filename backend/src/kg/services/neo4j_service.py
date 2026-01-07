"""
Neo4j service for Knowledge Graph storage.
Direct interaction with Neo4j database.
"""
from neo4j import GraphDatabase, Driver, Session
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger

from src.core.config import get_settings
from src.kg.models.entity import Entity, EntityBatch
from src.kg.models.relation import Relation, RelationBatch


class Neo4jService:
    """Service for Neo4j Knowledge Graph operations."""

    def __init__(self):
        settings = get_settings()
        self.uri = settings.neo4j_uri
        self.user = settings.neo4j_user
        self.password = settings.neo4j_password
        self.driver: Optional[Driver] = None

    def connect(self):
        """Establish connection to Neo4j."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # Test connection
            with self.driver.session() as session:
                result = session.run("RETURN 1 AS test")
                result.single()
            logger.info(f"Connected to Neo4j at {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    # ==================== Entity Operations ====================

    def create_entity(self, entity: Entity) -> str:
        """
        Create a single entity (node) in Neo4j.

        Args:
            entity: Entity to create

        Returns:
            Neo4j internal node ID
        """
        with self.driver.session() as session:
            result = session.execute_write(self._create_entity_tx, entity)
            logger.info(f"Created entity: {entity.type} - {entity.name}")
            return result

    @staticmethod
    def _create_entity_tx(tx, entity: Entity) -> str:
        """Transaction function to create entity."""
        label = entity.get_label()
        props = entity.to_neo4j_props()

        # Create node with MERGE to avoid duplicates on name
        query = f"""
        MERGE (n:{label} {{name: $name}})
        SET n += $props
        RETURN elementId(n) as id
        """

        result = tx.run(query, name=entity.name, props=props)
        record = result.single()
        return record["id"] if record else None

    def create_entities_batch(self, entities: List[Entity]) -> List[str]:
        """
        Create multiple entities in a single transaction.

        Args:
            entities: List of entities to create

        Returns:
            List of Neo4j node IDs
        """
        with self.driver.session() as session:
            ids = session.execute_write(self._create_entities_batch_tx, entities)
            logger.info(f"Created {len(ids)} entities in batch")
            return ids

    @staticmethod
    def _create_entities_batch_tx(tx, entities: List[Entity]) -> List[str]:
        """Transaction function to create entities in batch."""
        ids = []
        for entity in entities:
            label = entity.get_label()
            props = entity.to_neo4j_props()

            query = f"""
            MERGE (n:{label} {{name: $name}})
            SET n += $props
            RETURN elementId(n) as id
            """

            result = tx.run(query, name=entity.name, props=props)
            record = result.single()
            if record:
                ids.append(record["id"])

        return ids

    # ==================== Relation Operations ====================

    def create_relation(self, relation: Relation) -> str:
        """
        Create a single relation (edge) in Neo4j.

        Args:
            relation: Relation to create

        Returns:
            Neo4j internal relationship ID
        """
        with self.driver.session() as session:
            result = session.execute_write(self._create_relation_tx, relation)
            logger.info(
                f"Created relation: {relation.from_entity} -[{relation.type}]-> {relation.to_entity}"
            )
            return result

    @staticmethod
    def _create_relation_tx(tx, relation: Relation) -> str:
        """Transaction function to create relation."""
        rel_type = relation.get_type()
        props = relation.to_neo4j_props()

        # Match nodes by name and create relationship
        query = f"""
        MATCH (from {{name: $from_name}})
        MATCH (to {{name: $to_name}})
        MERGE (from)-[r:{rel_type}]->(to)
        SET r += $props
        RETURN elementId(r) as id
        """

        result = tx.run(
            query,
            from_name=relation.from_entity,
            to_name=relation.to_entity,
            props=props
        )
        record = result.single()
        return record["id"] if record else None

    def create_relations_batch(self, relations: List[Relation]) -> List[str]:
        """
        Create multiple relations in a single transaction.

        Args:
            relations: List of relations to create

        Returns:
            List of Neo4j relationship IDs
        """
        with self.driver.session() as session:
            ids = session.execute_write(self._create_relations_batch_tx, relations)
            logger.info(f"Created {len(ids)} relations in batch")
            return ids

    @staticmethod
    def _create_relations_batch_tx(tx, relations: List[Relation]) -> List[str]:
        """Transaction function to create relations in batch."""
        ids = []
        for relation in relations:
            rel_type = relation.get_type()
            props = relation.to_neo4j_props()

            query = f"""
            MATCH (from {{name: $from_name}})
            MATCH (to {{name: $to_name}})
            MERGE (from)-[r:{rel_type}]->(to)
            SET r += $props
            RETURN elementId(r) as id
            """

            result = tx.run(
                query,
                from_name=relation.from_entity,
                to_name=relation.to_entity,
                props=props
            )
            record = result.single()
            if record:
                ids.append(record["id"])

        return ids

    # ==================== Query Operations ====================

    def get_entity_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get entity by name.

        Args:
            name: Entity name

        Returns:
            Entity properties dict or None
        """
        with self.driver.session() as session:
            result = session.run(
                "MATCH (n {name: $name}) RETURN n, labels(n) as labels",
                name=name
            )
            record = result.single()
            if record:
                node = record["n"]
                return {
                    "labels": record["labels"],
                    "properties": dict(node)
                }
            return None

    def get_graph_stats(self) -> Dict[str, Any]:
        """
        Get graph statistics.

        Returns:
            Dict with node count, relationship count, etc.
        """
        with self.driver.session() as session:
            # Count nodes
            node_result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = node_result.single()["count"]

            # Count relationships
            rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_count = rel_result.single()["count"]

            # Count by node labels
            label_result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, count(n) as count
                ORDER BY count DESC
            """)
            labels = {record["label"]: record["count"] for record in label_result}

            # Count by relationship types
            rel_type_result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count
                ORDER BY count DESC
            """)
            rel_types = {record["type"]: record["count"] for record in rel_type_result}

            return {
                "total_nodes": node_count,
                "total_relationships": rel_count,
                "nodes_by_label": labels,
                "relationships_by_type": rel_types
            }

    def get_graph_data(self, limit: int = 100) -> Dict[str, Any]:
        """
        Get graph data for visualization.

        Args:
            limit: Maximum number of nodes to return

        Returns:
            Dict with nodes and edges arrays
        """
        with self.driver.session() as session:
            result = session.run(f"""
                MATCH (n)
                OPTIONAL MATCH (n)-[r]->(m)
                RETURN n, r, m
                LIMIT {limit}
            """)

            nodes = {}
            edges = []

            for record in result:
                # Source node
                if record["n"]:
                    node = record["n"]
                    node_id = node.element_id
                    if node_id not in nodes:
                        nodes[node_id] = {
                            "id": node_id,
                            "label": list(node.labels)[0] if node.labels else "Unknown",
                            "properties": dict(node)
                        }

                # Target node
                if record["m"]:
                    node = record["m"]
                    node_id = node.element_id
                    if node_id not in nodes:
                        nodes[node_id] = {
                            "id": node_id,
                            "label": list(node.labels)[0] if node.labels else "Unknown",
                            "properties": dict(node)
                        }

                # Relationship
                if record["r"]:
                    rel = record["r"]
                    edges.append({
                        "id": rel.element_id,
                        "from": record["n"].element_id,
                        "to": record["m"].element_id,
                        "type": rel.type,
                        "properties": dict(rel)
                    })

            return {
                "nodes": list(nodes.values()),
                "edges": edges
            }

    def clear_graph(self):
        """Delete all nodes and relationships. Use with caution!"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.warning("Graph cleared - all nodes and relationships deleted")


# Singleton instance
_neo4j_service: Optional[Neo4jService] = None


def get_neo4j_service() -> Neo4jService:
    """
    Get or create Neo4j service singleton.

    Returns:
        Neo4jService instance
    """
    global _neo4j_service
    if _neo4j_service is None:
        _neo4j_service = Neo4jService()
        _neo4j_service.connect()
    return _neo4j_service
