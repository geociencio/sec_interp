# -*- coding: utf-8 -*-
"""
Tests for SVGExporter
"""

from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from sec_interp.exporters.svg_exporter import SVGExporter
from qgis.core import QgsMapSettings


class TestSVGExporter(BaseTestCase):
    """Tests for SVGExporter format."""

    def setUp(self):
        super().setUp()
        self.exporter = SVGExporter({})

    def test_get_supported_extensions(self):
        """Test supported extensions are correct."""
        extensions = self.exporter.get_supported_extensions()
        self.assertIn(".svg", extensions)
        self.assertEqual(len(extensions), 1)

    @patch("sec_interp.exporters.svg_exporter.QgsMapRendererCustomPainterJob")
    @patch("sec_interp.exporters.svg_exporter.QPainter")
    @patch("sec_interp.exporters.svg_exporter.QSvgGenerator")
    def test_export_success(self, mock_generator, mock_painter, mock_job):
        """Test successful SVG export."""
        output_path = self.output_dir / "test.svg"
        map_settings = QgsMapSettings()

        # Configure the SVG Generator Mock
        mock_generator_instance = MagicMock()
        mock_generator.return_value = mock_generator_instance

        # Execute Export
        result = self.exporter.export(output_path, map_settings)

        # Assertions
        self.assertTrue(result)
        mock_generator_instance.setFileName.assert_called_once_with(str(output_path))
        mock_job.return_value.start.assert_called_once()
        mock_job.return_value.waitForFinished.assert_called_once()

    @patch("sec_interp.exporters.svg_exporter.QgsMapRendererCustomPainterJob")
    def test_export_exception_handling(self, mock_job):
        """Test exporter gracefully handles exceptions."""
        mock_job.side_effect = Exception("Test Exception")

        output_path = self.output_dir / "test_error.svg"
        map_settings = QgsMapSettings()

        result = self.exporter.export(output_path, map_settings)

        self.assertFalse(result)
