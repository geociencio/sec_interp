# -*- coding: utf-8 -*-
"""
Tests for exporters
"""

import pytest
from pathlib import Path

from exporters.csv_exporter import CSVExporter
from exporters.base_exporter import BaseExporter


class TestCSVExporter:
    """Tests for CSV exporter."""

    def test_get_supported_extensions(self):
        """Test CSV exporter returns correct extensions."""
        exporter = CSVExporter({})
        extensions = exporter.get_supported_extensions()
        assert ".csv" in extensions
        assert len(extensions) == 1

    def test_export_valid_data(self, temp_output_dir, sample_csv_data):
        """Test exporting valid CSV data."""
        exporter = CSVExporter({})
        output_path = temp_output_dir / "test.csv"

        result = exporter.export(output_path, sample_csv_data)
        assert result is True
        assert output_path.exists()

        # Verify content
        content = output_path.read_text()
        assert "distance" in content
        assert "elevation" in content
        assert "Unit A" in content

    def test_export_empty_data(self, temp_output_dir):
        """Test exporting empty data."""
        exporter = CSVExporter({})
        output_path = temp_output_dir / "empty.csv"

        result = exporter.export(output_path, {})
        assert result is False

    def test_export_missing_headers(self, temp_output_dir):
        """Test exporting data without headers."""
        exporter = CSVExporter({})
        output_path = temp_output_dir / "no_headers.csv"

        data = {"rows": [[1, 2, 3]]}  # Missing headers
        result = exporter.export(output_path, data)
        assert result is False

    def test_export_missing_rows(self, temp_output_dir):
        """Test exporting data without rows."""
        exporter = CSVExporter({})
        output_path = temp_output_dir / "no_rows.csv"

        data = {"headers": ["a", "b", "c"]}  # Missing rows
        result = exporter.export(output_path, data)
        assert result is False


class TestBaseExporter:
    """Tests for base exporter functionality."""

    def test_get_setting_with_default(self):
        """Test getting setting with default value."""
        exporter = CSVExporter({"dpi": 300})
        assert exporter.get_setting("nonexistent", "default") == "default"

    def test_get_setting_no_default(self):
        """Test getting non-existent setting without default."""
        exporter = CSVExporter({})
        assert exporter.get_setting("nonexistent") is None
