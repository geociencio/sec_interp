"""Image export utilities."""

from __future__ import annotations

"""Image exporter module for raster formats (PNG, JPG)."""

from pathlib import Path  # noqa: E402

from qgis.core import QgsMapRendererCustomPainterJob, QgsMapSettings  # noqa: E402
from qgis.PyQt.QtCore import QRectF, QSize  # noqa: E402
from qgis.PyQt.QtGui import QColor, QImage, QPainter  # noqa: E402

from sec_interp.logger_config import get_logger  # noqa: E402

from .base_exporter import BaseExporter  # noqa: E402

logger = get_logger(__name__)


class ImageExporter(BaseExporter):
    """Exporter for raster image formats (PNG, JPG, JPEG)."""

    def get_supported_extensions(self) -> list[str]:
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
            background_color = self.get_setting("background_color", QColor(255, 255, 255))

            # Create image (Qt5/Qt6 compatibility for enum)
            img_format = getattr(QImage, "Format", QImage).Format_ARGB32
            image = QImage(QSize(width, height), img_format)
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
            show_legend = self.get_setting("show_legend", True)
            legend_renderer = self.get_setting("legend_renderer")
            if legend_renderer and show_legend:
                legend_renderer.draw_legend(painter, QRectF(0, 0, width, height))

            painter.end()

            # Save image

            return image.save(str(output_path))

        except Exception:
            logger.exception(f"Image export failed for {output_path}")
            return False
