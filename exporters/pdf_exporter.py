# -*- coding: utf-8 -*-
"""
PDF exporter module for PDF documents.
"""

from pathlib import Path
from typing import List, Dict, Any

from qgis.PyQt.QtCore import QSize, QRectF, QSizeF
from qgis.PyQt.QtGui import QPainter, QPdfWriter, QPageSize
from qgis.core import QgsMapSettings, QgsMapRendererCustomPainterJob

from .base_exporter import BaseExporter
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class PDFExporter(BaseExporter):
    """Exporter for PDF format."""

    def get_supported_extensions(self) -> List[str]:
        """Get supported PDF extension."""
        return [".pdf"]

    def export(self, output_path: Path, map_settings: QgsMapSettings) -> bool:
        """Export map to PDF.

        Args:
            output_path: Output file path
            map_settings: QgsMapSettings instance configured for rendering

        Returns:
            True if export successful, False otherwise
        """
        try:
            width = self.get_setting("width", 800)
            height = self.get_setting("height", 600)

            # Setup PDF writer
            writer = QPdfWriter(str(output_path))
            writer.setResolution(300)  # Set a default resolution, e.g., 300 DPI
            writer.setPageSize(QPageSize(QSizeF(width, height), QPageSize.Point))
            writer.setPageMargins(0.0, 0.0, 0.0, 0.0, QPdfWriter.Point)

            # Setup painter
            painter = QPainter()
            if not painter.begin(writer):
                logger.error(f"Failed to begin painting for PDF export to {output_path}")
                return False

            try:
                painter.setRenderHint(QPainter.Antialiasing)

                # Update map settings with actual writer device dimensions and DPI
                dev = painter.device()
                map_settings.setOutputSize(QSize(dev.width(), dev.height()))
                map_settings.setOutputDpi(writer.resolution())

                # Render map
                job = QgsMapRendererCustomPainterJob(map_settings, painter)
                job.start()
                job.waitForFinished()

                # Draw legend if available
                legend_renderer = self.get_setting("legend_renderer")
                if legend_renderer:
                    legend_renderer.draw_legend(
                        painter, QRectF(0, 0, dev.width(), dev.height())
                    )

            finally:
                painter.end()

            return True

        except Exception as e:
            logger.error(f"PDF export failed for {output_path}: {e}")
            return False
