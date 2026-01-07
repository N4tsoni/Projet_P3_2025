"""
Embedding Stage: Generate vector embeddings for chunks.

Creates dense vector representations for semantic search and similarity.
"""

from typing import List
import numpy as np

from loguru import logger

from ..base import Stage, StageResult, StageStatus
from ..pipeline import PipelineContext


class EmbeddingStage(Stage):
    """
    Stage 3: Embedding Generation

    Responsibilities:
    - Generate embeddings for text chunks
    - Use efficient embedding models (sentence-transformers, OpenAI, etc.)
    - Batch processing for performance
    - Store embeddings for downstream use

    Input:
        - context.chunks

    Output:
        - context.embeddings (list of vectors)
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", batch_size: int = 32):
        """
        Initialize embedding stage.

        Args:
            model_name: Name of sentence-transformers model to use.
            batch_size: Number of chunks to process in parallel.
        """
        super().__init__(name="EmbeddingStage")
        self.model_name = model_name
        self.batch_size = batch_size
        self.model = None
        self._model_loaded = False

    def _load_model(self):
        """Load the embedding model (lazy loading)."""
        if self._model_loaded:
            return

        try:
            from sentence_transformers import SentenceTransformer

            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self._model_loaded = True
            logger.success(f"Model loaded: {self.model_name}")

        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    async def execute(self, context: PipelineContext) -> StageResult:
        """Generate embeddings for chunks."""
        logger.info(f"Generating embeddings with model: {self.model_name}")

        try:
            if not context.chunks:
                logger.warning("No chunks to embed, skipping")
                return StageResult(
                    stage_name=self.name,
                    status=StageStatus.SKIPPED,
                    duration_seconds=0.0,
                    metadata={"reason": "No chunks available"}
                )

            # Load model if not already loaded
            try:
                self._load_model()
            except ImportError as e:
                logger.warning(f"Embedding dependencies not installed: {e}")
                return StageResult(
                    stage_name=self.name,
                    status=StageStatus.SKIPPED,
                    duration_seconds=0.0,
                    metadata={"reason": "sentence-transformers not installed"}
                )

            # Extract text from chunks
            texts = [self._chunk_to_text(chunk) for chunk in context.chunks]

            # Remove empty texts
            valid_indices = [i for i, text in enumerate(texts) if text.strip()]
            valid_texts = [texts[i] for i in valid_indices]

            if not valid_texts:
                logger.warning("No valid texts to embed")
                context.embeddings = []
                return StageResult(
                    stage_name=self.name,
                    status=StageStatus.COMPLETED,
                    duration_seconds=0.0,
                    output_data={"embeddings_count": 0}
                )

            logger.info(f"Embedding {len(valid_texts)} texts...")

            # Generate embeddings in batches
            embeddings = self.model.encode(
                valid_texts,
                batch_size=self.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True
            )

            # Store embeddings in context
            context.embeddings = embeddings.tolist() if isinstance(embeddings, np.ndarray) else embeddings

            logger.success(
                f"Generated {len(context.embeddings)} embeddings "
                f"(dim={len(context.embeddings[0])})"
            )

            return StageResult(
                stage_name=self.name,
                status=StageStatus.COMPLETED,
                duration_seconds=0.0,
                output_data={
                    "embeddings_count": len(context.embeddings),
                    "embedding_dim": len(context.embeddings[0]) if context.embeddings else 0,
                    "model": self.model_name
                }
            )

        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return StageResult(
                stage_name=self.name,
                status=StageStatus.FAILED,
                duration_seconds=0.0,
                error=str(e)
            )

    def _chunk_to_text(self, chunk: dict) -> str:
        """
        Convert a chunk to text for embedding.

        Handles different chunk structures from various parsers.
        """
        # Try to get content directly
        if isinstance(chunk.get("content"), str):
            return chunk["content"]

        # For structured data (CSV records), concatenate key-value pairs
        elif isinstance(chunk.get("content"), dict):
            pairs = [f"{k}: {v}" for k, v in chunk["content"].items() if v is not None]
            return " | ".join(pairs)

        # Try getting text field (some parsers use "text")
        elif isinstance(chunk.get("text"), str):
            return chunk["text"]

        # Fallback: convert entire chunk to string
        else:
            return str(chunk.get("content", ""))

    def get_embeddings_for_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts (utility method).

        Args:
            texts: List of text strings

        Returns:
            List of embedding vectors
        """
        if not self._model_loaded:
            self._load_model()

        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=False,
            convert_to_numpy=True
        )

        return embeddings.tolist() if isinstance(embeddings, np.ndarray) else embeddings
