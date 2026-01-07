"""
TXT Parser for Knowledge Graph construction.

Parses plain text files into structured chunks for downstream processing.
"""

from typing import Dict, Any, List
from pathlib import Path
import chardet

from loguru import logger


class TXTParser:
    """Parser for plain text files."""

    def parse(
        self,
        file_path: str | Path,
        encoding: str = None
    ) -> tuple[str, Dict[str, Any]]:
        """
        Parse a text file.

        Args:
            file_path: Path to text file
            encoding: Text encoding (auto-detected if None)

        Returns:
            Tuple of (text_content, metadata)
        """
        file_path = Path(file_path)

        logger.info(f"Parsing TXT file: {file_path.name}")

        try:
            # Detect encoding if not provided
            if encoding is None:
                encoding = self.detect_encoding(file_path)
                logger.info(f"Detected encoding: {encoding}")

            # Read file
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()

            # Generate metadata
            metadata = self._generate_metadata(file_path, content, encoding)

            logger.info(
                f"Parsed TXT: {metadata['line_count']} lines, "
                f"{metadata['char_count']} chars, "
                f"{metadata['word_count']} words"
            )

            return content, metadata

        except Exception as e:
            logger.error(f"Failed to parse TXT: {e}")
            raise

    def detect_encoding(self, file_path: Path) -> str:
        """
        Detect file encoding using chardet.

        Args:
            file_path: Path to file

        Returns:
            Detected encoding (e.g., 'utf-8', 'iso-8859-1')
        """
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # Read first 10KB
            result = chardet.detect(raw_data)
            return result['encoding'] or 'utf-8'

    def _generate_metadata(
        self,
        file_path: Path,
        content: str,
        encoding: str
    ) -> Dict[str, Any]:
        """
        Generate metadata about the text file.

        Args:
            file_path: Path to file
            content: File content
            encoding: Detected encoding

        Returns:
            Metadata dictionary
        """
        lines = content.split('\n')
        words = content.split()

        # Get first few lines as sample
        sample_lines = lines[:5]

        metadata = {
            "filename": file_path.name,
            "size_bytes": file_path.stat().st_size,
            "encoding": encoding,
            "format": "txt",
            "line_count": len(lines),
            "char_count": len(content),
            "word_count": len(words),
            "sample_lines": sample_lines
        }

        return metadata

    def to_paragraphs(self, content: str) -> List[str]:
        """
        Split text into paragraphs.

        Args:
            content: Text content

        Returns:
            List of paragraphs
        """
        # Split on double newlines
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        return paragraphs

    def to_sentences(self, content: str) -> List[str]:
        """
        Split text into sentences (simple split on periods).

        Args:
            content: Text content

        Returns:
            List of sentences
        """
        # Simple sentence splitting (can be improved with nltk)
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        return sentences

    def to_chunks(
        self,
        content: str,
        chunk_size: int = 1000,
        overlap: int = 200
    ) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks.

        Args:
            content: Text content
            chunk_size: Maximum chunk size in characters
            overlap: Number of characters to overlap between chunks

        Returns:
            List of chunk dictionaries with metadata
        """
        chunks = []
        start = 0

        while start < len(content):
            end = start + chunk_size
            chunk_text = content[start:end]

            chunks.append({
                "id": len(chunks),
                "content": chunk_text,
                "start": start,
                "end": end,
                "length": len(chunk_text)
            })

            # Move start position with overlap
            start = end - overlap

        return chunks
