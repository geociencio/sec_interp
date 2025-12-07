# -*- coding: utf-8 -*-
"""
Image exporter module for raster formats (PNG, JPG).
"""

from pathlib import Path
from typing import List

from qgis.PyQt.QtGui import QImage, QPainter, QColor
from qgis.PyQt.QtCore import QSize, QRectF
from qgis.core import QgsMapSettings, QgsMapRendererCustomPainterJob

from .base_exporter import BaseExporter
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class ImageExporter(BaseExporter):
    """Exporter for raster image formats (PNG, JPG, JPEG)."""

    def get_supported_extensions(self) -> List[str]:
        """Get supported image extensions."""
        return [".png", ".jpg", ".jpeg"]

    def export(self, output_path: Path, map_settings: QgsMapSettings) -> bool:
        """Export map to raster image.

        Args:
            output_path: Output file path
            map_settings: QgsMapSettings instance configured for rendering

        Returns:
            True if export successful, False otherwise
        """
        try:
            width = self.get_setting("width", 800)
            height = self.get_setting("height", 600)
            background_color = self.get_setting(
                "background_color", QColor(255, 255, 255)
            )

            # Create image
            image = QImage(QSize(width, height), QImage.Format_ARGB32)
            image.fill(background_color)

            # Setup painter
            painter = QPainter(image)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)

            # Render map
            job = QgsMapRendererCustomPainterJob(map_settings, painter)
            job.start()
            job.waitForFinished()

            # Draw legend if available
            legend_renderer = self.get_setting("legend_renderer")
            if legend_renderer:
                legend_renderer.draw_legend(painter, QRectF(0, 0, width, height))

            painter.end()

            # Save image
            ext = output_path.suffix.lower()
            quality = 95 if ext in [".jpg", ".jpeg"] else -1

            return image.save(str(output_path))

        except Exception as e:
            logger.error(f"Image export failed for {output_path}: {e}")
            return False
