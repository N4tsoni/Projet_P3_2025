"""
JSON Parser for Knowledge Graph construction.

Parses JSON files into structured data for downstream processing.
"""

import json
from typing import Dict, Any, List
from pathlib import Path

from loguru import logger


class JSONParser:
    """Parser for JSON files."""

    def parse(self, file_path: str | Path) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Parse a JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            Tuple of (records, metadata)
            - records: List of dictionaries (flattened if needed)
            - metadata: Parsing metadata
        """
        file_path = Path(file_path)

        logger.info(f"Parsing JSON file: {file_path.name}")

        try:
            # Read JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Convert to records based on structure
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                # If dict has a key that's a list, use that
                list_keys = [k for k, v in data.items() if isinstance(v, list)]
                if list_keys:
                    # Use first list found
                    records = data[list_keys[0]]
                else:
                    # Single object, wrap in list
                    records = [data]
            else:
                raise ValueError(f"Unexpected JSON structure: {type(data)}")

            # Generate metadata
            metadata = self._generate_metadata(file_path, records)

            logger.info(f"Parsed JSON: {len(records)} records")

            return records, metadata

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON file: {e}")
            raise ValueError(f"Invalid JSON: {e}")
        except Exception as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise

    def _generate_metadata(
        self,
        file_path: Path,
        records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate metadata about the JSON file.

        Args:
            file_path: Path to file
            records: Parsed records

        Returns:
            Metadata dictionary
        """
        # Get all keys from all records
        all_keys = set()
        for record in records:
            if isinstance(record, dict):
                all_keys.update(record.keys())

        # Sample records (first 3)
        sample_records = records[:3] if len(records) > 3 else records

        metadata = {
            "filename": file_path.name,
            "size_bytes": file_path.stat().st_size,
            "format": "json",
            "record_count": len(records),
            "keys": list(all_keys),
            "key_count": len(all_keys),
            "sample_records": sample_records
        }

        return metadata

    def to_records(self, data: Any) -> List[Dict[str, Any]]:
        """
        Convert parsed JSON data to list of records.

        Args:
            data: Parsed JSON data

        Returns:
            List of record dictionaries
        """
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
        else:
            return [{"value": data}]
