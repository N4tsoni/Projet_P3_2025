"""
Entity Extractor Agent for Knowledge Graph pipeline.
Uses Claude via OpenRouter to extract typed entities from data.
"""
import json
from typing import List, Dict, Any, Optional
from loguru import logger
import httpx

from src.core.config import get_settings
from src.kg.models.entity import Entity, EntityType


class EntityExtractorAgent:
    """Agent that extracts entities from structured data using Claude LLM."""

    def __init__(self):
        """Initialize the entity extractor agent."""
        settings = get_settings()
        self.api_key = settings.openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "anthropic/claude-3.5-sonnet"
        self.timeout = 60.0

    async def extract_entities_from_csv(
        self,
        records: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        source_filename: str
    ) -> List[Entity]:
        """
        Extract entities from CSV records.

        Args:
            records: List of row dictionaries from CSV
            metadata: CSV metadata (columns, types, etc.)
            source_filename: Source file name for tracking

        Returns:
            List of extracted Entity objects
        """
        logger.info(f"Extracting entities from {len(records)} CSV records")

        # Build prompt for Claude
        prompt = self._build_extraction_prompt(records, metadata)

        # Call Claude via OpenRouter
        try:
            response = await self._call_claude(prompt)
            entities = self._parse_response(response, source_filename)
            logger.info(f"Extracted {len(entities)} entities")
            return entities

        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            raise

    def _build_extraction_prompt(
        self,
        records: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> str:
        """
        Build prompt for Claude to extract entities.

        Args:
            records: CSV records
            metadata: CSV metadata

        Returns:
            Formatted prompt string
        """
        # Limit records in prompt to avoid token limits
        sample_records = records[:50]  # Process in batches of 50

        prompt = f"""You are an expert at extracting structured entities from data for a Knowledge Graph.

Your task: Analyze the following CSV data and extract ALL entities with their properties.

Entity Types to extract:
- Person: People (actors, directors, etc.) - properties: name, role (actor/director), nationality
- Movie: Films - properties: name (title), year, genre, rating, budget_millions
- Studio: Production companies - properties: name, country

CSV Metadata:
- Columns: {', '.join(metadata['columns'])}
- Column types: {json.dumps(metadata['column_types'], indent=2)}

CSV Data (first {len(sample_records)} rows):
{json.dumps(sample_records, indent=2)}

Instructions:
1. Extract EVERY entity mentioned in the data
2. For actors: if multiple actors are in one field (separated by ;), extract each as separate Person entity
3. For directors: extract as Person entity with role="director"
4. For studios: extract as Studio entity
5. For movies: extract with all available properties
6. Use the exact names as they appear in the data
7. Return ONLY valid JSON, no explanation

Output format (JSON array):
[
  {{
    "type": "Person|Movie|Studio",
    "name": "Entity name",
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
        source_filename: str
    ) -> List[Entity]:
        """
        Parse Claude's response into Entity objects.

        Args:
            response: Claude's JSON response
            source_filename: Source file name

        Returns:
            List of Entity objects
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
            entities_data = json.loads(response)

            if not isinstance(entities_data, list):
                raise ValueError("Response is not a JSON array")

            # Convert to Entity objects
            entities = []
            for entity_dict in entities_data:
                try:
                    # Map type string to EntityType enum
                    entity_type = self._map_entity_type(entity_dict.get("type"))

                    entity = Entity(
                        type=entity_type,
                        name=entity_dict["name"],
                        properties=entity_dict.get("properties", {}),
                        source=source_filename,
                        confidence=entity_dict.get("confidence", 0.95)
                    )
                    entities.append(entity)

                except Exception as e:
                    logger.warning(f"Failed to parse entity {entity_dict}: {e}")
                    continue

            return entities

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response: {response}")
            raise

    def _map_entity_type(self, type_str: str) -> EntityType:
        """
        Map string type to EntityType enum.

        Args:
            type_str: Type string from LLM

        Returns:
            EntityType enum value
        """
        type_mapping = {
            "person": EntityType.PERSON,
            "movie": EntityType.MOVIE,
            "studio": EntityType.STUDIO,
            "organization": EntityType.ORGANIZATION,
            "location": EntityType.LOCATION,
            "concept": EntityType.CONCEPT
        }

        type_lower = type_str.lower() if type_str else ""
        return type_mapping.get(type_lower, EntityType.GENERIC)

    async def extract_entities_batch(
        self,
        records: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        source_filename: str,
        batch_size: int = 50
    ) -> List[Entity]:
        """
        Extract entities from large datasets in batches.

        Args:
            records: All CSV records
            metadata: CSV metadata
            source_filename: Source file name
            batch_size: Number of records per batch

        Returns:
            All extracted entities
        """
        all_entities = []

        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1} ({len(batch)} records)")

            entities = await self.extract_entities_from_csv(
                batch,
                metadata,
                source_filename
            )
            all_entities.extend(entities)

        # Deduplicate entities by name and type
        unique_entities = self._deduplicate_entities(all_entities)
        logger.info(f"Total unique entities: {len(unique_entities)}")

        return unique_entities

    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """
        Remove duplicate entities based on name and type.

        Args:
            entities: List of entities potentially with duplicates

        Returns:
            Deduplicated list
        """
        seen = {}
        unique = []

        for entity in entities:
            # Handle both Enum and string types (use_enum_values=True converts to string)
            entity_type = entity.type.value if hasattr(entity.type, 'value') else entity.type
            key = (entity_type, entity.name.lower())

            if key not in seen:
                seen[key] = entity
                unique.append(entity)
            else:
                # Merge properties from duplicate
                existing = seen[key]
                existing.properties.update(entity.properties)
                # Update confidence to average
                existing.confidence = (existing.confidence + entity.confidence) / 2

        return unique


# Convenience function
async def extract_entities_from_csv(
    records: List[Dict[str, Any]],
    metadata: Dict[str, Any],
    source_filename: str
) -> List[Entity]:
    """
    Convenience function to extract entities from CSV data.

    Args:
        records: CSV records
        metadata: CSV metadata
        source_filename: Source file name

    Returns:
        List of extracted entities
    """
    agent = EntityExtractorAgent()
    return await agent.extract_entities_batch(records, metadata, source_filename)
