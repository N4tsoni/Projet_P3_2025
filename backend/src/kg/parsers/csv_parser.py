"""
CSV Parser for Knowledge Graph pipeline.
Handles CSV file parsing and data extraction using Pandas.
"""
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from loguru import logger
import chardet


class CSVParser:
    """Parser for CSV files with automatic encoding and delimiter detection."""

    def __init__(self):
        """Initialize CSV parser."""
        self.supported_delimiters = [',', ';', '\t', '|']

    def detect_encoding(self, file_path) -> str:
        """
        Detect file encoding using chardet.

        Args:
            file_path: Path to the CSV file (str or Path)

        Returns:
            Detected encoding (e.g., 'utf-8', 'iso-8859-1')
        """
        file_path = Path(file_path) if isinstance(file_path, str) else file_path
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # Read first 10KB
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            confidence = result['confidence']
            logger.info(f"Detected encoding: {encoding} (confidence: {confidence:.2%})")
            return encoding

    def detect_delimiter(self, file_path, encoding: str) -> str:
        """
        Detect CSV delimiter by trying common delimiters.

        Args:
            file_path: Path to the CSV file (str or Path)
            encoding: File encoding

        Returns:
            Detected delimiter
        """
        file_path = Path(file_path) if isinstance(file_path, str) else file_path
        with open(file_path, 'r', encoding=encoding) as f:
            first_line = f.readline()

        # Count occurrences of each delimiter
        delimiter_counts = {
            delim: first_line.count(delim)
            for delim in self.supported_delimiters
        }

        # Choose delimiter with most occurrences
        delimiter = max(delimiter_counts, key=delimiter_counts.get)
        logger.info(f"Detected delimiter: '{delimiter}' (count: {delimiter_counts[delimiter]})")
        return delimiter

    def parse(
        self,
        file_path,
        encoding: Optional[str] = None,
        delimiter: Optional[str] = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Parse CSV file into pandas DataFrame.

        Args:
            file_path: Path to the CSV file (str or Path)
            encoding: Optional encoding (auto-detected if None)
            delimiter: Optional delimiter (auto-detected if None)

        Returns:
            Tuple of (DataFrame, metadata dict)
        """
        try:
            # Ensure file_path is a Path object
            file_path = Path(file_path) if isinstance(file_path, str) else file_path
            # Auto-detect encoding if not provided
            if encoding is None:
                encoding = self.detect_encoding(file_path)

            # Auto-detect delimiter if not provided
            if delimiter is None:
                delimiter = self.detect_delimiter(file_path, encoding)

            # Read CSV
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                delimiter=delimiter,
                dtype=str,  # Read all as strings initially
                keep_default_na=False  # Don't convert empty strings to NaN
            )

            # Generate metadata
            metadata = self._generate_metadata(df, file_path, encoding, delimiter)

            logger.info(
                f"Parsed CSV: {len(df)} rows, {len(df.columns)} columns"
            )

            return df, metadata

        except Exception as e:
            logger.error(f"Failed to parse CSV {file_path}: {e}")
            raise

    def _generate_metadata(
        self,
        df: pd.DataFrame,
        file_path: Path,
        encoding: str,
        delimiter: str
    ) -> Dict[str, Any]:
        """
        Generate metadata about the parsed CSV.

        Args:
            df: Parsed DataFrame
            file_path: Original file path
            encoding: Used encoding
            delimiter: Used delimiter

        Returns:
            Metadata dictionary
        """
        return {
            "filename": file_path.name,
            "size_bytes": file_path.stat().st_size,
            "encoding": encoding,
            "delimiter": delimiter,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "column_types": self._infer_column_types(df),
            "sample_rows": df.head(3).to_dict(orient='records') if len(df) > 0 else []
        }

    def _infer_column_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Infer semantic types for each column.

        Args:
            df: DataFrame to analyze

        Returns:
            Dict mapping column name to inferred type
        """
        column_types = {}

        for col in df.columns:
            # Try to infer type from column name and values
            col_lower = col.lower()
            sample_values = df[col].dropna().head(5).tolist()

            if not sample_values:
                column_types[col] = "empty"
                continue

            # Check for numeric
            try:
                pd.to_numeric(df[col])
                if '.' in str(sample_values[0]):
                    column_types[col] = "float"
                else:
                    column_types[col] = "integer"
                continue
            except (ValueError, TypeError):
                pass

            # Check for date
            if any(keyword in col_lower for keyword in ['date', 'time', 'year', 'created', 'updated']):
                column_types[col] = "date"
                continue

            # Check for boolean
            unique_values = set(str(v).lower() for v in df[col].dropna().unique())
            if unique_values.issubset({'true', 'false', '1', '0', 'yes', 'no'}):
                column_types[col] = "boolean"
                continue

            # Default to string
            column_types[col] = "string"

        return column_types

    def to_records(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Convert DataFrame to list of record dictionaries.

        Args:
            df: DataFrame to convert

        Returns:
            List of row dictionaries
        """
        return df.to_dict(orient='records')

    def get_column_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get statistical information about DataFrame columns.

        Args:
            df: DataFrame to analyze

        Returns:
            Statistics dictionary
        """
        stats = {}

        for col in df.columns:
            col_stats = {
                "total_rows": len(df),
                "non_empty": df[col].astype(bool).sum(),
                "empty": (~df[col].astype(bool)).sum(),
                "unique_values": df[col].nunique(),
            }

            # Add value counts for categorical columns
            if df[col].nunique() < 20:  # Arbitrary threshold
                col_stats["value_counts"] = df[col].value_counts().head(10).to_dict()

            stats[col] = col_stats

        return stats


def parse_csv_file(
    file_path: str | Path,
    encoding: Optional[str] = None,
    delimiter: Optional[str] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Convenience function to parse a CSV file.

    Args:
        file_path: Path to CSV file
        encoding: Optional encoding
        delimiter: Optional delimiter

    Returns:
        Tuple of (DataFrame, metadata)
    """
    parser = CSVParser()
    return parser.parse(Path(file_path), encoding, delimiter)
