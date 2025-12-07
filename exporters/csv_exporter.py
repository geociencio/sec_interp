# -*- coding: utf-8 -*-
"""
CSV exporter module for tabular data.
"""

import csv
from pathlib import Path
from typing import List, Dict, Any

from .base_exporter import BaseExporter
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class CSVExporter(BaseExporter):
    """Exporter for CSV tabular format."""

    def get_supported_extensions(self) -> List[str]:
        """Get supported CSV extension."""
        return [".csv"]

    def export(self, output_path: Path, data: Dict[str, Any]) -> bool:
        """Export tabular data to CSV.

        Args:
            output_path: Output file path.
            data: A dictionary containing 'headers' (list of strings)
                  and 'rows' (list of tuples or lists).

        Returns:
            True if export successful, False otherwise
        """
        if not data:
            return False

        try:
            headers = data.get("headers")
            rows = data.get("rows")
            if not headers or not rows:
                return False

            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)

            return True

        except Exception as e:
            logger.error(f"CSV export failed for {output_path}: {e}")
            return False
