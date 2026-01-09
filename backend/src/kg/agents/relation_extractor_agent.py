"""
Relation Extractor Agent for Knowledge Graph pipeline.
Uses Claude via OpenRouter to extract relationships between entities.
"""
import json
from typing import List, Dict, Any, Optional
from loguru import logger
import httpx

from src.core.config import get_settings
from src.kg.models.entity import Entity
from src.kg.models.relation import Relation, RelationType


class RelationExtractorAgent:
    """Agent that extracts relationships between entities using Claude LLM."""

    def __init__(self):
        """Initialize the relation extractor agent."""
        settings = get_settings()
        self.api_key = settings.openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "anthropic/claude-3.5-sonnet"
        self.timeout = 60.0

    async def extract_relations_from_csv(
        self,
        records: List[Dict[str, Any]],
        entities: List[Entity],
        metadata: Dict[str, Any],
        source_filename: str
    ) -> List[Relation]:
        """
        Extract relations from CSV records given extracted entities.

        Args:
            records: List of row dictionaries from CSV
            entities: Previously extracted entities
            metadata: CSV metadata
            source_filename: Source file name for tracking

        Returns:
            List of extracted Relation objects
        """
        logger.info(f"Extracting relations from {len(records)} CSV records")

        # Build entity lookup for validation
        entity_names = {entity.name.lower(): entity for entity in entities}

        # Build prompt for Claude
        prompt = self._build_extraction_prompt(records, entities, metadata)

        # Call Claude via OpenRouter
        try:
            response = await self._call_claude(prompt)
            relations = self._parse_response(response, entity_names, source_filename)
            logger.info(f"Extracted {len(relations)} relations")
            return relations

        except Exception as e:
            logger.error(f"Relation extraction failed: {e}")
            raise

    def _build_extraction_prompt(
        self,
        records: List[Dict[str, Any]],
        entities: List[Entity],
        metadata: Dict[str, Any]
    ) -> str:
        """
        Build prompt for Claude to extract relations.

        Args:
            records: CSV records
            entities: Extracted entities
            metadata: CSV metadata

        Returns:
            Formatted prompt string
        """
        # Limit records in prompt
        sample_records = records[:50]

        # Build entity list by type for context
        entities_by_type = {}
        for entity in entities:
            # Handle both Enum and string types (use_enum_values=True converts to string)
            entity_type = entity.type.value if hasattr(entity.type, 'value') else entity.type
            if entity_type not in entities_by_type:
                entities_by_type[entity_type] = []
            entities_by_type[entity_type].append(entity.name)

        prompt = f"""You are an expert at extracting relationships between entities for a Knowledge Graph.

Your task: Analyze the CSV data and identify ALL relationships between the extracted entities.

Relation Types to extract:
- ACTED_IN: Person -> Movie (properties: role/character name if available)
- DIRECTED: Person -> Movie (properties: none)
- PRODUCED_BY: Movie -> Studio (properties: budget_millions if available)
- WORKS_AT: Person -> Organization (properties: role/position)
- KNOWS: Person -> Person (generic relationship)
- RELATED_TO: Generic relationship between any entities

Extracted Entities:
{json.dumps(entities_by_type, indent=2)}

CSV Data (first {len(sample_records)} rows):
{json.dumps(sample_records, indent=2)}

Instructions:
1. Extract ALL relationships you can identify from the data
2. Use EXACT entity names as they were extracted (case-sensitive)
3. For actors field with multiple actors (separated by ;), create separate ACTED_IN relations for each
4. For directors, create DIRECTED relations
5. For studios, create PRODUCED_BY relations from Movie to Studio
6. Only create relations between entities that actually exist in the entity list
7. Add relevant properties (e.g., character role, budget)
8. Return ONLY valid JSON, no explanation

Output format (JSON array):
[
  {{
    "type": "ACTED_IN|DIRECTED|PRODUCED_BY|WORKS_AT|KNOWS|RELATED_TO",
    "from_entity": "Source entity name",
    "to_entity": "Target entity name",
    "properties": {{"key": "value", ...}},
    "confidence": 0.0-1.0
  }},
  ...
]

Return the JSON array now:"""

        return prompt

    async def _call_claude(self, prompt: str) -> str:
        """
        Call Claude via OpenRouter API.

        Args:
            prompt: The prompt to send

        Returns:
            Claude's response text
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Jarvis KG Builder"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,  # Low temperature for consistent extraction
            "max_tokens": 4000
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()

            # Extract response text
            content = result["choices"][0]["message"]["content"]
            return content

    def _parse_response(
        self,
        response: str,
        entity_names: Dict[str, Entity],
        source_filename: str
    ) -> List[Relation]:
        """
        Parse Claude's response into Relation objects.

        Args:
            response: Claude's JSON response
            entity_names: Dict of lowercase entity names to Entity objects
            source_filename: Source file name

        Returns:
            List of Relation objects
        """
        try:
            # Extract JSON from response (Claude might add markdown)
            response = response.strip()
            if response.startswith("```json"):
                response = response.split("```json")[1]
            if response.startswith("```"):
                response = response.split("```")[1]
            if response.endswith("```"):
                response = response.rsplit("```", 1)[0]
            response = response.strip()

            # Parse JSON
            relations_data = json.loads(response)

            if not isinstance(relations_data, list):
                raise ValueError("Response is not a JSON array")

            # Convert to Relation objects
            relations = []
            for rel_dict in relations_data:
                try:
                    # Validate entities exist
                    from_name = rel_dict["from_entity"]
                    to_name = rel_dict["to_entity"]

                    if from_name.lower() not in entity_names:
                        logger.warning(f"Source entity not found: {from_name}")
                        continue
                    if to_name.lower() not in entity_names:
                        logger.warning(f"Target entity not found: {to_name}")
                        continue

                    # Map type string to RelationType enum
                    relation_type = self._map_relation_type(rel_dict.get("type"))

                    # Get entity types
                    from_entity = entity_names[from_name.lower()]
                    to_entity = entity_names[to_name.lower()]

                    # Handle both Enum and string types (use_enum_values=True converts to string)
                    from_type = from_entity.type.value if hasattr(from_entity.type, 'value') else from_entity.type
                    to_type = to_entity.type.value if hasattr(to_entity.type, 'value') else to_entity.type

                    relation = Relation(
                        type=relation_type,
                        from_entity=from_name,
                        to_entity=to_name,
                        from_entity_type=from_type,
                        to_entity_type=to_type,
                        properties=rel_dict.get("properties", {}),
                        source=source_filename,
                        confidence=rel_dict.get("confidence", 0.95)
                    )
                    relations.append(relation)

                except Exception as e:
                    logger.warning(f"Failed to parse relation {rel_dict}: {e}")
                    continue

            return relations

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response: {response}")
            raise

    def _map_relation_type(self, type_str: str) -> RelationType:
        """
        Map string type to RelationType enum.

        Args:
            type_str: Type string from LLM

        Returns:
            RelationType enum value
        """
        type_mapping = {
            "acted_in": RelationType.ACTED_IN,
            "directed": RelationType.DIRECTED,
            "produced_by": RelationType.PRODUCED_BY,
            "works_at": RelationType.WORKS_AT,
            "knows": RelationType.KNOWS,
            "related_to": RelationType.RELATED_TO,
            "located_in": RelationType.LOCATED_IN,
            "part_of": RelationType.PART_OF
        }

        type_lower = type_str.lower() if type_str else ""
        return type_mapping.get(type_lower, RelationType.RELATED_TO)

    async def extract_relations_batch(
        self,
        records: List[Dict[str, Any]],
        entities: List[Entity],
        metadata: Dict[str, Any],
        source_filename: str,
        batch_size: int = 50
    ) -> List[Relation]:
        """
        Extract relations from large datasets in batches.

        Args:
            records: All CSV records
            entities: All extracted entities
            metadata: CSV metadata
            source_filename: Source file name
            batch_size: Number of records per batch

        Returns:
            All extracted relations
        """
        all_relations = []

        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1} ({len(batch)} records)")

            relations = await self.extract_relations_from_csv(
                batch,
                entities,
                metadata,
                source_filename
            )
            all_relations.extend(relations)

        # Deduplicate relations
        unique_relations = self._deduplicate_relations(all_relations)
        logger.info(f"Total unique relations: {len(unique_relations)}")

        return unique_relations

    def _deduplicate_relations(self, relations: List[Relation]) -> List[Relation]:
        """
        Remove duplicate relations based on type, from, and to.

        Args:
            relations: List of relations potentially with duplicates

        Returns:
            Deduplicated list
        """
        seen = {}
        unique = []

        for relation in relations:
            # Handle both Enum and string types (use_enum_values=True converts to string)
            relation_type = relation.type.value if hasattr(relation.type, 'value') else relation.type
            key = (
                relation_type,
                relation.from_entity.lower(),
                relation.to_entity.lower()
            )

            if key not in seen:
                seen[key] = relation
                unique.append(relation)
            else:
                # Merge properties from duplicate
                existing = seen[key]
                existing.properties.update(relation.properties)
                # Update confidence to average
                existing.confidence = (existing.confidence + relation.confidence) / 2

        return unique


# Convenience function
async def extract_relations_from_csv(
    records: List[Dict[str, Any]],
    entities: List[Entity],
    metadata: Dict[str, Any],
    source_filename: str
) -> List[Relation]:
    """
    Convenience function to extract relations from CSV data.

    Args:
        records: CSV records
        entities: Extracted entities
        metadata: CSV metadata
        source_filename: Source file name

    Returns:
        List of extracted relations
    """
    agent = RelationExtractorAgent()
    return await agent.extract_relations_batch(records, entities, metadata, source_filename)
