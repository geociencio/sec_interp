# -*- coding: utf-8 -*-
"""
Tests for Interpretation2DExporter
"""

from pathlib import Path
from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from sec_interp.exporters.interpretation_exporters import Interpretation2DExporter
from qgis.core import QgsVectorFileWriter


class MockInterpretationPolygon:
    """Mock for an interpretation polygon."""

    def __init__(self, obj_id, name, obj_type, color, date, attributes=None):
        self.id = obj_id
        self.name = name
        self.type = obj_type
        self.color = color
        self.created_at = date
        self.attributes = attributes or {}
        # Simple square
        self.vertices_2d = [(0, 0), (10, 0), (10, 10), (0, 10)]


class TestInterpretation2DExporter(BaseTestCase):
    """Tests for Interpretation2DExporter form."""

    def setUp(self):
        super().setUp()
        self.exporter = Interpretation2DExporter({})
        self.test_interps = [
            MockInterpretationPolygon(
                "ID1", "Group A", "Geology", "#ff0000", "2023-01-01", {"unit": "Basalt"}
            ),
            MockInterpretationPolygon(
                "ID2", "Group B", "Structure", "#00ff00", "2023-01-02", {"dip": "45"}
            ),
        ]

    def test_get_supported_extensions(self):
        """Test supported extensions."""
        extensions = self.exporter.get_supported_extensions()
        self.assertIn(".shp", extensions)
        self.assertGreaterEqual(len(extensions), 1)

    def test_export_empty_data(self):
        """Test export fails when given empty interpretation list."""
        output_path = self.output_dir / "empty_interp.shp"
        data = {"interpretations": []}

        result = self.exporter.export(output_path, data)

        self.assertFalse(result)
        self.assertFalse(output_path.exists())

    @patch("sec_interp.exporters.interpretation_exporters.scu_io.create_vector_writer")
    def test_export_success(self, mock_writer_factory):
        """Test successful export of interpretation polygons."""
        # 1. Setup mock writer
        mock_writer = MagicMock()
        mock_writer.hasError.return_value = QgsVectorFileWriter.NoError
        mock_writer_factory.return_value = mock_writer

        output_path = Path("/tmp/interpretations.shp")
        data = {"interpretations": self.test_interps, "crs": MagicMock()}
        data["crs"].isValid.return_value = True

        # 2. Execute
        result = self.exporter.export(output_path, data)

        # 3. Assert
        self.assertTrue(result)
        mock_writer_factory.assert_called_once()
        self.assertEqual(mock_writer.addFeature.call_count, 2)

    @patch("sec_interp.exporters.interpretation_exporters.scu_io.create_vector_writer")
    def test_export_writer_error(self, mock_writer_factory):
        """Test export failure when writer has error."""
        output_path = self.output_dir / "interp_fail.shp"
        data = {"interpretations": self.test_interps, "crs": MagicMock()}
        data["crs"].isValid.return_value = True

        # Mock the Writer with an Error state
        mock_writer = MagicMock()
        mock_writer.hasError.return_value = QgsVectorFileWriter.ErrCreateDataSource
        mock_writer.errorMessage.return_value = "Permission Denied"
        mock_writer_factory.return_value = mock_writer

        # Execute
        result = self.exporter.export(output_path, data)

        # Assertions
        self.assertFalse(result)
        mock_writer.addFeature.assert_not_called()

    @patch("sec_interp.exporters.interpretation_exporters.scu_io.create_vector_writer")
    def test_export_exception(self, mock_writer_factory):
        """Test export failure on general exception."""
        output_path = self.output_dir / "interp_exc.shp"
        data = {"interpretations": self.test_interps}

        mock_writer_factory.side_effect = Exception("Test unhandled exception")

        result = self.exporter.export(output_path, data)

        self.assertFalse(result)
