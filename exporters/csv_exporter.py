"""CSV exporter module for tabular data."""

import csv
from pathlib import Path
from typing import Any

from sec_interp.logger_config import get_logger

from .base_exporter import BaseExporter


logger = get_logger(__name__)


class CSVExporter(BaseExporter):
    """Exporter for CSV tabular format."""

    def get_supported_extensions(self) -> list[str]:
        """Get supported CSV extension."""
        return [".csv"]

    def export(self, output_path: Path, data: dict[str, Any]) -> bool:
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

        except Exception:
            logger.exception(f"CSV export failed for {output_path}")
            return False
