# -*- coding: utf-8 -*-
"""
Tests for exporters
"""

from pathlib import Path
from tests.base_test import BaseTestCase

from exporters.csv_exporter import CSVExporter
from exporters.base_exporter import BaseExporter


class TestCSVExporter(BaseTestCase):
    """Tests for CSV exporter."""

    def test_get_supported_extensions(self):
        """Test CSV exporter returns correct extensions."""
        exporter = CSVExporter({})
        extensions = exporter.get_supported_extensions()
        self.assertIn(".csv", extensions)
        self.assertEqual(len(extensions), 1)

    def test_export_valid_data(self):
        """Test exporting valid CSV data."""
        exporter = CSVExporter({})
        output_path = self.output_dir / "test.csv"

        result = exporter.export(output_path, self.sample_csv_data)
        self.assertTrue(result)
        self.assertTrue(output_path.exists())

        # Verify content
        content = output_path.read_text()
        self.assertIn("distance", content)
        self.assertIn("elevation", content)
        self.assertIn("Unit A", content)

    def test_export_empty_data(self):
        """Test exporting empty data."""
        exporter = CSVExporter({})
        output_path = self.output_dir / "empty.csv"

        result = exporter.export(output_path, {})
        self.assertFalse(result)

    def test_export_missing_headers(self):
        """Test exporting data without headers."""
        exporter = CSVExporter({})
        output_path = self.output_dir / "no_headers.csv"

        data = {"rows": [[1, 2, 3]]}  # Missing headers
        result = exporter.export(output_path, data)
        self.assertFalse(result)

    def test_export_missing_rows(self):
        """Test exporting data without rows."""
        exporter = CSVExporter({})
        output_path = self.output_dir / "no_rows.csv"

        data = {"headers": ["a", "b", "c"]}  # Missing rows
        result = exporter.export(output_path, data)
        self.assertFalse(result)


class TestBaseExporter(BaseTestCase):
    """Tests for base exporter functionality."""

    def test_get_setting_with_default(self):
        """Test getting setting with default value."""
        exporter = CSVExporter({"dpi": 300})
        self.assertEqual(exporter.get_setting("nonexistent", "default"), "default")

    def test_get_setting_no_default(self):
        """Test getting non-existent setting without default."""
        exporter = CSVExporter({})
        self.assertIsNone(exporter.get_setting("nonexistent"))
