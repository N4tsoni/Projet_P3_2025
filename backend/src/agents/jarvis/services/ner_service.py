"""
Named Entity Recognition (NER) service using spaCy.
"""
import spacy
from typing import List, Dict, Optional
from loguru import logger


class NERService:
    """Service for extracting named entities from text using spaCy."""

    def __init__(self, model: str = "en_core_web_sm"):
        """
        Initialize NER service.

        Args:
            model: spaCy model to use (default: en_core_web_sm)
        """
        try:
            self.spacy_model = spacy.load(model)
            logger.info(f"Loaded spaCy model: {model}")
        except OSError:
            logger.error(f"spaCy model {model} not found. Please run: python -m spacy download {model}")
            raise

    def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract named entities from text.

        Args:
            text: Input text to extract entities from

        Returns:
            List of dictionaries containing entity information:
            - text: The entity text
            - label: Entity type (PERSON, ORG, GPE, DATE, etc.)
            - start: Start character position
            - end: End character position
            - confidence: Confidence score (1.0 for spaCy)
        """
        doc = self.spacy_model(text)
        entities = []

        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,  # PERSON, ORG, GPE, DATE, etc.
                "start": ent.start_char,
                "end": ent.end_char,
                "confidence": 1.0  # spaCy does not provide confidence scores
            })

        logger.debug(f"Extracted {len(entities)} entities from text: {text[:50]}...")
        return entities


# Singleton instance
_ner_service: Optional[NERService] = None


def get_ner_service() -> NERService:
    """
    Get or create NER service singleton.

    Returns:
        NERService instance
    """
    global _ner_service
    if _ner_service is None:
        _ner_service = NERService()
    return _ner_service
