# -*- coding: utf-8 -*-
"""
Tests for Interpretation2DExporter
"""

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
        self.assertEqual(len(extensions), 1)

    def test_export_empty_data(self):
        """Test export fails when given empty interpretation list."""
        output_path = self.output_dir / "empty_interp.shp"
        data = {"interpretations": []}

        result = self.exporter.export(output_path, data)

        self.assertFalse(result)
        self.assertFalse(output_path.exists())

    @patch("sec_interp.exporters.interpretation_exporters.QgsVectorFileWriter")
    @patch("sec_interp.exporters.interpretation_exporters.QgsProject")
    def test_export_success(self, mock_project, mock_writer_class):
        """Test successful export of interpretation polygons."""
        output_path = self.output_dir / "interp.shp"
        data = {"interpretations": self.test_interps, "crs": MagicMock()}  # Mock CRS
        data["crs"].isValid.return_value = True
        data["crs"].authid.return_value = "EPSG:32719"

        # Mock the Writer
        mock_writer_instance = MagicMock()
        mock_writer_instance.hasError.return_value = QgsVectorFileWriter.NoError
        mock_writer_class.create.return_value = mock_writer_instance
        mock_writer_class.NoError = QgsVectorFileWriter.NoError

        # Mock Context
        mock_project.instance().transformContext.return_value = MagicMock()

        result = self.exporter.export(output_path, data)

        self.assertTrue(result)
        mock_writer_class.create.assert_called_once()
        self.assertEqual(mock_writer_instance.addFeature.call_count, 2)

    @patch("sec_interp.exporters.interpretation_exporters.QgsVectorFileWriter")
    @patch("sec_interp.exporters.interpretation_exporters.QgsProject")
    def test_export_writer_error(self, mock_project, mock_writer_class):
        """Test exporter handles writer instantiation failures correctly."""
        output_path = self.output_dir / "interp_fail.shp"
        data = {"interpretations": self.test_interps, "crs": MagicMock()}
        data["crs"].isValid.return_value = True

        # Mock the Writer with an Error state
        mock_writer_instance = MagicMock()
        mock_writer_instance.hasError.return_value = (
            QgsVectorFileWriter.ErrCreateDataSource
        )
        mock_writer_instance.errorMessage.return_value = "Permission Denied"
        mock_writer_class.create.return_value = mock_writer_instance

        # Execute
        result = self.exporter.export(output_path, data)

        # Assertions
        self.assertFalse(result)
        mock_writer_instance.addFeature.assert_not_called()

    @patch("sec_interp.exporters.interpretation_exporters.QgsVectorLayer")
    def test_export_exception_handling(self, mock_layer_class):
        """Test catching unhandled exceptions."""
        output_path = self.output_dir / "interp_exc.shp"
        data = {"interpretations": self.test_interps}

        mock_layer_class.side_effect = Exception("Test unhandled exception")

        result = self.exporter.export(output_path, data)

        self.assertFalse(result)
