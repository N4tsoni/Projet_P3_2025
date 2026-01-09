"""
PDF Parser for Knowledge Graph construction.

Parses PDF files and extracts text content.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path

from loguru import logger


class PDFParser:
    """
    Parser for PDF files.

    Requires: pypdf or pdfplumber
    """

    def __init__(self, use_pdfplumber: bool = True):
        """
        Initialize PDF parser.

        Args:
            use_pdfplumber: Use pdfplumber if True, pypdf if False
        """
        self.use_pdfplumber = use_pdfplumber
        self._check_dependencies()

    def _check_dependencies(self):
        """Check if required libraries are installed."""
        if self.use_pdfplumber:
            try:
                import pdfplumber
                self.pdfplumber = pdfplumber
            except ImportError:
                logger.warning("pdfplumber not installed, falling back to pypdf")
                self.use_pdfplumber = False

        if not self.use_pdfplumber:
            try:
                import pypdf
                self.pypdf = pypdf
            except ImportError:
                raise ImportError(
                    "Neither pdfplumber nor pypdf is installed. "
                    "Install with: pip install pdfplumber or pip install pypdf"
                )

    def parse(
        self,
        file_path: str | Path,
        extract_images: bool = False
    ) -> tuple[str, Dict[str, Any]]:
        """
        Parse a PDF file and extract text.

        Args:
            file_path: Path to PDF file
            extract_images: Whether to extract images (not implemented yet)

        Returns:
            Tuple of (text_content, metadata)
        """
        file_path = Path(file_path)

        logger.info(f"Parsing PDF file: {file_path.name}")

        try:
            if self.use_pdfplumber:
                return self._parse_with_pdfplumber(file_path)
            else:
                return self._parse_with_pypdf(file_path)

        except Exception as e:
            logger.error(f"Failed to parse PDF: {e}")
            raise

    def _parse_with_pdfplumber(
        self,
        file_path: Path
    ) -> tuple[str, Dict[str, Any]]:
        """
        Parse PDF using pdfplumber (better text extraction).

        Args:
            file_path: Path to PDF

        Returns:
            Tuple of (text, metadata)
        """
        import pdfplumber

        all_text = []
        pages_data = []

        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                all_text.append(text)

                pages_data.append({
                    "page": i,
                    "char_count": len(text),
                    "word_count": len(text.split())
                })

        full_text = "\n\n".join(all_text)

        metadata = {
            "filename": file_path.name,
            "size_bytes": file_path.stat().st_size,
            "format": "pdf",
            "page_count": len(pages_data),
            "char_count": len(full_text),
            "word_count": len(full_text.split()),
            "pages": pages_data,
            "parser": "pdfplumber"
        }

        logger.info(
            f"Parsed PDF: {metadata['page_count']} pages, "
            f"{metadata['word_count']} words"
        )

        return full_text, metadata

    def _parse_with_pypdf(
        self,
        file_path: Path
    ) -> tuple[str, Dict[str, Any]]:
        """
        Parse PDF using pypdf (fallback).

        Args:
            file_path: Path to PDF

        Returns:
            Tuple of (text, metadata)
        """
        from pypdf import PdfReader

        reader = PdfReader(file_path)

        all_text = []
        pages_data = []

        for i, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            all_text.append(text)

            pages_data.append({
                "page": i,
                "char_count": len(text),
                "word_count": len(text.split())
            })

        full_text = "\n\n".join(all_text)

        metadata = {
            "filename": file_path.name,
            "size_bytes": file_path.stat().st_size,
            "format": "pdf",
            "page_count": len(reader.pages),
            "char_count": len(full_text),
            "word_count": len(full_text.split()),
            "pages": pages_data,
            "parser": "pypdf"
        }

        logger.info(
            f"Parsed PDF: {metadata['page_count']} pages, "
            f"{metadata['word_count']} words"
        )

        return full_text, metadata

    def extract_pages(
        self,
        file_path: Path,
        page_numbers: List[int]
    ) -> List[str]:
        """
        Extract text from specific pages.

        Args:
            file_path: Path to PDF
            page_numbers: List of page numbers (1-indexed)

        Returns:
            List of page texts
        """
        if self.use_pdfplumber:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                pages = [pdf.pages[i-1].extract_text() for i in page_numbers]
        else:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            pages = [reader.pages[i-1].extract_text() for i in page_numbers]

        return pages

    def to_records(
        self,
        text: str,
        chunk_size: int = 2000
    ) -> List[Dict[str, Any]]:
        """
        Convert PDF text to records (chunks).

        Args:
            text: Extracted PDF text
            chunk_size: Size of each chunk

        Returns:
            List of record dictionaries
        """
        # Split into chunks
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]

            chunks.append({
                "id": len(chunks),
                "content": chunk_text,
                "type": "pdf_chunk",
                "metadata": {
                    "start": start,
                    "end": end,
                    "length": len(chunk_text)
                }
            })

            start = end

        return chunks
