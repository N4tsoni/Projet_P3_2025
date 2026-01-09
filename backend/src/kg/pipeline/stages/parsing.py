"""
Parsing Stage: Parse raw documents into structured data.

Supports multiple formats: CSV, JSON, PDF, TXT, XLSX, XML.
"""

from typing import Dict, Any
from pathlib import Path

from loguru import logger

from ..base import Stage, StageResult, StageStatus
from ..pipeline import PipelineContext
from ...parsers.csv_parser import CSVParser
from ...parsers.json_parser import JSONParser
from ...parsers.pdf_parser import PDFParser
from ...parsers.txt_parser import TXTParser


class ParsingStage(Stage):
    """
    Stage 1: Document Parsing

    Responsibilities:
    - Detect file format
    - Parse file into structured data
    - Extract metadata (encoding, size, columns, etc.)
    - Convert to standard format for downstream processing

    Input:
        - context.file_path
        - context.file_format

    Output:
        - context.raw_data (parsed data structure)
        - context.metadata (file metadata)
    """

    def __init__(self):
        super().__init__(name="ParsingStage")
        self.csv_parser = CSVParser()
        self.json_parser = JSONParser()
        self.txt_parser = TXTParser()
        try:
            self.pdf_parser = PDFParser()
        except ImportError:
            logger.warning("PDF parser dependencies not installed")
            self.pdf_parser = None

    async def execute(self, context: PipelineContext) -> StageResult:
        """Parse document based on format."""
        logger.info(f"Parsing file: {context.filename} (format: {context.file_format})")

        try:
            if context.file_format.lower() == "csv":
                return await self._parse_csv(context)
            elif context.file_format.lower() == "json":
                return await self._parse_json(context)
            elif context.file_format.lower() == "pdf":
                return await self._parse_pdf(context)
            elif context.file_format.lower() == "txt":
                return await self._parse_txt(context)
            else:
                raise ValueError(f"Unsupported file format: {context.file_format}")

        except Exception as e:
            logger.error(f"Parsing failed: {e}")
            return StageResult(
                stage_name=self.name,
                status=StageStatus.FAILED,
                duration_seconds=0.0,
                error=str(e)
            )

    async def _parse_csv(self, context: PipelineContext) -> StageResult:
        """Parse CSV file."""
        df, metadata = self.csv_parser.parse(str(context.file_path))
        records = self.csv_parser.to_records(df)

        context.raw_data = records
        context.metadata = metadata

        logger.info(f"Parsed CSV: {len(records)} rows, {len(df.columns)} columns")

        return StageResult(
            stage_name=self.name,
            status=StageStatus.COMPLETED,
            duration_seconds=0.0,
            output_data={
                "rows": len(records),
                "columns": len(df.columns),
                "format": "csv"
            }
        )

    async def _parse_json(self, context: PipelineContext) -> StageResult:
        """Parse JSON file."""
        records, metadata = self.json_parser.parse(str(context.file_path))

        context.raw_data = records
        context.metadata = metadata

        logger.info(f"Parsed JSON: {len(records)} records")

        return StageResult(
            stage_name=self.name,
            status=StageStatus.COMPLETED,
            duration_seconds=0.0,
            output_data={
                "records": len(records),
                "format": "json"
            }
        )

    async def _parse_pdf(self, context: PipelineContext) -> StageResult:
        """Parse PDF file."""
        if self.pdf_parser is None:
            return StageResult(
                stage_name=self.name,
                status=StageStatus.FAILED,
                duration_seconds=0.0,
                error="PDF parser dependencies not installed (pip install pdfplumber)"
            )

        text, metadata = self.pdf_parser.parse(context.file_path)

        # Convert text to records (chunks for downstream processing)
        records = self.pdf_parser.to_records(text, chunk_size=2000)

        context.raw_data = records
        context.metadata = metadata

        logger.info(
            f"Parsed PDF: {metadata['page_count']} pages, "
            f"{len(records)} chunks"
        )

        return StageResult(
            stage_name=self.name,
            status=StageStatus.COMPLETED,
            duration_seconds=0.0,
            output_data={
                "pages": metadata['page_count'],
                "chunks": len(records),
                "format": "pdf"
            }
        )

    async def _parse_txt(self, context: PipelineContext) -> StageResult:
        """Parse TXT file."""
        text, metadata = self.txt_parser.parse(context.file_path)

        # Convert text to chunks as records
        records = self.txt_parser.to_chunks(text, chunk_size=1000, overlap=200)

        context.raw_data = records
        context.metadata = metadata

        logger.info(
            f"Parsed TXT: {metadata['line_count']} lines, "
            f"{len(records)} chunks"
        )

        return StageResult(
            stage_name=self.name,
            status=StageStatus.COMPLETED,
            duration_seconds=0.0,
            output_data={
                "lines": metadata['line_count'],
                "words": metadata['word_count'],
                "chunks": len(records),
                "format": "txt"
            }
        )
