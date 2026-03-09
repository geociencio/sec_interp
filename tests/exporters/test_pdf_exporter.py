# -*- coding: utf-8 -*-
"""
Tests for PDFExporter
"""

from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from sec_interp.exporters.pdf_exporter import PDFExporter
from qgis.core import QgsMapSettings


class TestPDFExporter(BaseTestCase):
    """Tests for PDFExporter format."""

    def setUp(self):
        super().setUp()
        self.exporter = PDFExporter({})

    def test_get_supported_extensions(self):
        """Test supported extensions are correct."""
        extensions = self.exporter.get_supported_extensions()
        self.assertIn(".pdf", extensions)
        self.assertEqual(len(extensions), 1)

    @patch("sec_interp.exporters.pdf_exporter.QgsMapRendererCustomPainterJob")
    @patch("sec_interp.exporters.pdf_exporter.QPainter")
    @patch("sec_interp.exporters.pdf_exporter.QPdfWriter")
    def test_export_success(self, mock_writer, mock_painter, mock_job):
        """Test successful PDF export."""
        output_path = self.output_dir / "test.pdf"
        map_settings = QgsMapSettings()

        # Configure the PDF Writer Mock
        mock_writer_instance = MagicMock()
        mock_writer_instance.resolution.return_value = 300
        mock_writer.return_value = mock_writer_instance

        # Configure the Painter Mock
        mock_painter_instance = MagicMock()
        mock_painter.return_value = mock_painter_instance
        mock_painter_instance.begin.return_value = True

        # Configure the painter device
        mock_device = MagicMock()
        mock_device.width.return_value = 800
        mock_device.height.return_value = 600
        mock_painter_instance.device.return_value = mock_device

        # Execute Export
        result = self.exporter.export(output_path, map_settings)

        # Assertions
        self.assertTrue(result)
        mock_writer.assert_called_once_with(str(output_path))
        mock_painter_instance.begin.assert_called_once_with(mock_writer_instance)
        mock_painter_instance.end.assert_called_once()
        mock_job.return_value.start.assert_called_once()
        mock_job.return_value.waitForFinished.assert_called_once()

    @patch("sec_interp.exporters.pdf_exporter.QPainter")
    @patch("sec_interp.exporters.pdf_exporter.QPdfWriter")
    def test_export_painter_begin_fails(self, mock_writer, mock_painter):
        """Test exporter handles failure to begin painting."""
        output_path = self.output_dir / "test_begin_fail.pdf"
        map_settings = QgsMapSettings()

        # Configure the Painter Mock to fail begin()
        mock_painter_instance = MagicMock()
        mock_painter.return_value = mock_painter_instance
        mock_painter_instance.begin.return_value = False

        result = self.exporter.export(output_path, map_settings)

        self.assertFalse(result)

    @patch("sec_interp.exporters.pdf_exporter.QgsMapRendererCustomPainterJob")
    @patch("sec_interp.exporters.pdf_exporter.QPainter")
    @patch("sec_interp.exporters.pdf_exporter.QPdfWriter")
    def test_export_exception_handling(self, mock_writer, mock_painter, mock_job):
        """Test exporter gracefully handles exceptions during painting."""
        mock_painter_instance = MagicMock()
        mock_painter.return_value = mock_painter_instance
        mock_painter_instance.begin.return_value = True

        # Make the job raise an exception
        mock_job.side_effect = Exception("Test Exception")

        output_path = self.output_dir / "test_error.pdf"
        map_settings = QgsMapSettings()

        result = self.exporter.export(output_path, map_settings)

        self.assertFalse(result)
        mock_painter_instance.end.assert_called_once()  # Verify cleanup is called via finally
