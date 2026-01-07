"""
NER Stage: Named Entity Recognition using NLP models.

Identifies named entities in text using spaCy, transformers, or other NER models.
"""

from typing import List, Dict, Any

from loguru import logger

from ..base import Stage, StageResult, StageStatus
from ..pipeline import PipelineContext


class NERStage(Stage):
    """
    Stage 4: Named Entity Recognition

    Responsibilities:
    - Identify named entities in text (persons, organizations, locations, etc.)
    - Use NLP models (spaCy, transformers, etc.)
    - Extract entity types and positions
    - Build preliminary entity list

    Input:
        - context.chunks

    Output:
        - Enriches context.entities with NER-detected entities
    """

    def __init__(self, model_name: str = "en_core_web_sm", max_length: int = 1000000):
        """
        Initialize NER stage.

        Args:
            model_name: Name of spaCy model to use for NER.
            max_length: Maximum text length for spaCy processing.
        """
        super().__init__(name="NERStage")
        self.model_name = model_name
        self.max_length = max_length
        self.nlp = None
        self._model_loaded = False

    def _load_model(self):
        """Load the spaCy NER model (lazy loading)."""
        if self._model_loaded:
            return

        try:
            import spacy

            logger.info(f"Loading spaCy model: {self.model_name}")
            self.nlp = spacy.load(self.model_name)

            # Set max length
            self.nlp.max_length = self.max_length

            self._model_loaded = True
            logger.success(f"spaCy model loaded: {self.model_name}")

        except ImportError:
            raise ImportError(
                "spaCy not installed. Install with: pip install spacy && "
                f"python -m spacy download {self.model_name}"
            )
        except OSError:
            raise OSError(
                f"spaCy model '{self.model_name}' not found. "
                f"Download with: python -m spacy download {self.model_name}"
            )
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {e}")
            raise

    async def execute(self, context: PipelineContext) -> StageResult:
        """Perform named entity recognition."""
        logger.info(f"Running NER with model: {self.model_name}")

        try:
            if not context.chunks:
                logger.warning("No chunks to process, skipping NER")
                return StageResult(
                    stage_name=self.name,
                    status=StageStatus.SKIPPED,
                    duration_seconds=0.0,
                    metadata={"reason": "No chunks available"}
                )

            # Load spaCy model if not already loaded
            try:
                self._load_model()
            except (ImportError, OSError) as e:
                logger.warning(f"spaCy not available: {e}")
                return StageResult(
                    stage_name=self.name,
                    status=StageStatus.SKIPPED,
                    duration_seconds=0.0,
                    metadata={"reason": f"spaCy not available: {str(e)}"}
                )

            # Process chunks and extract entities
            ner_entities = []
            entity_counts = {}

            for i, chunk in enumerate(context.chunks):
                text = self._chunk_to_text(chunk)

                if not text.strip():
                    continue

                # Truncate if too long
                if len(text) > self.max_length:
                    text = text[:self.max_length]

                # Process with spaCy
                doc = self.nlp(text)

                # Extract entities
                for ent in doc.ents:
                    entity_data = {
                        "text": ent.text,
                        "label": ent.label_,
                        "start_char": ent.start_char,
                        "end_char": ent.end_char,
                        "chunk_id": i,
                        "source": "NER",
                        "confidence": 1.0  # spaCy doesn't provide confidence by default
                    }
                    ner_entities.append(entity_data)

                    # Count by label
                    entity_counts[ent.label_] = entity_counts.get(ent.label_, 0) + 1

            # Deduplicate entities by text
            unique_entities = self._deduplicate_entities(ner_entities)

            # Add to context (don't overwrite existing entities)
            context.entities.extend(unique_entities)

            logger.success(
                f"NER extracted {len(unique_entities)} unique entities "
                f"from {len(ner_entities)} total"
            )

            return StageResult(
                stage_name=self.name,
                status=StageStatus.COMPLETED,
                duration_seconds=0.0,
                output_data={
                    "ner_entities_total": len(ner_entities),
                    "ner_entities_unique": len(unique_entities),
                    "entity_types": entity_counts,
                    "model": self.model_name
                }
            )

        except Exception as e:
            logger.error(f"NER failed: {e}")
            return StageResult(
                stage_name=self.name,
                status=StageStatus.FAILED,
                duration_seconds=0.0,
                error=str(e)
            )

    def _chunk_to_text(self, chunk: dict) -> str:
        """Convert chunk to text for NER processing."""
        # Try content field first
        if isinstance(chunk.get("content"), str):
            return chunk["content"]

        # For structured data, concatenate values with context
        elif isinstance(chunk.get("content"), dict):
            pairs = [f"{k}: {v}" for k, v in chunk["content"].items() if v is not None]
            return " | ".join(pairs)

        # Try text field
        elif isinstance(chunk.get("text"), str):
            return chunk["text"]

        # Fallback
        else:
            return str(chunk.get("content", ""))

    def _deduplicate_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicate entities by text and label.

        Args:
            entities: List of entity dictionaries

        Returns:
            Deduplicated list
        """
        seen = set()
        unique = []

        for entity in entities:
            key = (entity["text"].lower(), entity["label"])

            if key not in seen:
                seen.add(key)
                unique.append(entity)

        return unique

    def get_entity_types(self) -> List[str]:
        """
        Get list of entity types supported by the loaded model.

        Returns:
            List of entity type labels
        """
        if not self._model_loaded:
            self._load_model()

        # spaCy entity labels
        return list(self.nlp.get_pipe("ner").labels)
