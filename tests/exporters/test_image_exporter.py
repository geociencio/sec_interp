# -*- coding: utf-8 -*-
"""
Tests for ImageExporter
"""

from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from sec_interp.exporters.image_exporter import ImageExporter
from qgis.PyQt.QtGui import QColor, QImage
from qgis.core import QgsMapSettings


class TestImageExporter(BaseTestCase):
    """Tests for ImageExporter format."""

    def setUp(self):
        super().setUp()
        self.exporter = ImageExporter({})

    def test_get_supported_extensions(self):
        """Test supported extensions are correct."""
        extensions = self.exporter.get_supported_extensions()
        self.assertIn(".png", extensions)
        self.assertIn(".jpg", extensions)
        self.assertIn(".jpeg", extensions)
        self.assertEqual(len(extensions), 3)

    @patch("sec_interp.exporters.image_exporter.QgsMapRendererCustomPainterJob")
    @patch("sec_interp.exporters.image_exporter.QPainter")
    @patch("sec_interp.exporters.image_exporter.QImage.save")
    def test_export_success(self, mock_save, mock_painter, mock_job):
        """Test successful image export."""
        mock_save.return_value = True

        output_path = self.output_dir / "test.png"
        map_settings = QgsMapSettings()

        result = self.exporter.export(output_path, map_settings)

        self.assertTrue(result)
        mock_save.assert_called_once_with(str(output_path))
        mock_job.return_value.start.assert_called_once()
        mock_job.return_value.waitForFinished.assert_called_once()

    @patch("sec_interp.exporters.image_exporter.QgsMapRendererCustomPainterJob")
    @patch("sec_interp.exporters.image_exporter.QPainter")
    @patch("sec_interp.exporters.image_exporter.QImage.save")
    def test_export_with_custom_settings(self, mock_save, mock_painter, mock_job):
        """Test export using custom width, height and background color."""
        mock_save.return_value = True

        custom_exporter = ImageExporter(
            {
                "width": 1024,
                "height": 768,
                "background_color": QColor(255, 0, 0),
                "show_legend": False,
            }
        )

        output_path = self.output_dir / "test_custom.jpg"
        map_settings = QgsMapSettings()

        # Mock the QImage and QSize to verify initialization arguments
        with (
            patch("sec_interp.exporters.image_exporter.QImage") as mock_image,
            patch("sec_interp.exporters.image_exporter.QSize") as mock_size,
        ):

            mock_image_instance = MagicMock()
            mock_image_instance.save = mock_save
            mock_image.return_value = mock_image_instance

            # Ensure mock_size captures arguments properly
            mock_size_instance = MagicMock()
            mock_size_instance.width.return_value = 1024
            mock_size_instance.height.return_value = 768
            mock_size.return_value = mock_size_instance

            # Since mock_image expects a QSize, we configure it
            args_list = []

            def record_args(*args, **kwargs):
                args_list.extend(args)
                return mock_image_instance

            mock_image.side_effect = record_args

            result = custom_exporter.export(output_path, map_settings)

            self.assertTrue(result)
            from unittest.mock import ANY

            mock_image_instance.fill.assert_called_once_with(ANY)

            # Check QSize arguments directly
            mock_size.assert_called_once_with(1024, 768)

    @patch("sec_interp.exporters.image_exporter.QgsMapRendererCustomPainterJob")
    def test_export_exception_handling(self, mock_job):
        """Test exporter gracefully handles exceptions."""
        mock_job.side_effect = Exception("Test Exception")

        output_path = self.output_dir / "test_error.png"
        map_settings = QgsMapSettings()

        result = self.exporter.export(output_path, map_settings)

        self.assertFalse(result)
