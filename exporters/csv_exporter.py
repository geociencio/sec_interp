# -*- coding: utf-8 -*-
"""
CSV exporter module for tabular data.
"""

import csv
from pathlib import Path
from typing import List, Dict, Any

from .base_exporter import BaseExporter


class CSVExporter(BaseExporter):
    """Exporter for CSV tabular format."""

    def get_supported_extensions(self) -> List[str]:
        """Get supported CSV extension."""
        return ['.csv']

    def export(self, output_path: Path, data: List[Dict[str, Any]]) -> bool:
        """Export tabular data to CSV.
        
        Args:
            output_path: Output file path
            data: List of dictionaries representing rows
            
        Returns:
            True if export successful, False otherwise
        """
        if not data:
            return False

        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                # Get fieldnames from first row
                fieldnames = list(data[0].keys())
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
                
            return True

        except Exception:
            return False
