# -*- coding: utf-8 -*-
"""
Tests for VectorExporter
"""

from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from sec_interp.exporters.vector_exporter import VectorExporter
from qgis.core import QgsWkbTypes, QgsCoordinateReferenceSystem, QgsVectorFileWriter


class TestVectorExporter(BaseTestCase):
    """Tests for VectorExporter format."""

    def setUp(self):
        super().setUp()
        self.exporter = VectorExporter({})
        self.test_data = [
            {
                "geometry": MagicMock(),
                "attributes": {"id": 1, "value": 12.5, "name": "Test Feature"},
            },
            {
                "geometry": MagicMock(),
                "attributes": {"id": 2, "value": 20.0, "name": "Another Feature"},
            },
        ]

    def test_get_supported_extensions(self):
        """Test supported vector extensions are correct."""
        extensions = self.exporter.get_supported_extensions()
        self.assertIn(".shp", extensions)
        self.assertIn(".gpkg", extensions)
        self.assertIn(".dxf", extensions)
        self.assertEqual(len(extensions), 3)

    @patch("sec_interp.exporters.vector_exporter.scu_io.create_vector_writer")
    def test_export_success(self, mock_create_writer):
        """Test successful shapefile export."""
        output_path = self.output_dir / "test.shp"

        # We need to simulate that create_vector_writer returns a writer that says NoError
        mock_writer_instance = MagicMock()
        mock_writer_instance.hasError.return_value = QgsVectorFileWriter.NoError
        mock_create_writer.return_value = mock_writer_instance

        # Execute Export
        result = self.exporter.export(output_path, self.test_data)

        self.assertTrue(result)
        mock_create_writer.assert_called_once()
        self.assertEqual(mock_writer_instance.addFeature.call_count, 2)

    def test_export_empty_data(self):
        """Test export fails and returns cleanly when given no features."""
        output_path = self.output_dir / "empty.shp"

        result = self.exporter.export(output_path, [])

        self.assertFalse(result)

    @patch("sec_interp.exporters.vector_exporter.scu_io.create_vector_writer")
    def test_export_writer_error(self, mock_create_writer):
        """Test exporter handles writer initialization failure."""
        output_path = self.output_dir / "test_err.shp"

        # Configure Mock Writer to simulate an error
        mock_writer_instance = MagicMock()
        mock_writer_instance.hasError.return_value = 3  # Error
        mock_writer_instance.errorMessage.return_value = "Permission Denied"
        mock_create_writer.return_value = mock_writer_instance

        result = self.exporter.export(output_path, self.test_data)

        self.assertFalse(result)
        mock_writer_instance.addFeature.assert_not_called()

    @patch("sec_interp.exporters.vector_exporter.scu_io.create_vector_writer")
    def test_export_exception_handling(self, mock_create_writer):
        """Test exporter gracefully handles runtime exceptions."""
        output_path = self.output_dir / "test_exc.shp"

        # Simulate exception during creation
        mock_create_writer.side_effect = Exception("Test Exception")

        result = self.exporter.export(output_path, self.test_data)

        self.assertFalse(result)
