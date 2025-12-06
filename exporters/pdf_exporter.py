# -*- coding: utf-8 -*-
"""
PDF exporter module for PDF documents.
"""

from pathlib import Path
from typing import List

from qgis.PyQt.QtPrintSupport import QPrinter
from qgis.PyQt.QtGui import QPainter, QPageSize
from qgis.PyQt.QtCore import QSize, QSizeF, QRectF
from qgis.core import QgsMapRendererCustomPainterJob

from .base_exporter import BaseExporter


class PDFExporter(BaseExporter):
    """Exporter for PDF format."""

    def get_supported_extensions(self) -> List[str]:
        """Get supported PDF extension."""
        return ['.pdf']

    def export(self, output_path: Path, map_settings) -> bool:
        """Export map to PDF.
        
        Args:
            output_path: Output file path
            map_settings: QgsMapSettings instance configured for rendering
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            width = self.get_setting('width', 800)
            height = self.get_setting('height', 600)

            # Setup printer
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(str(output_path))
            printer.setPageSize(QPageSize(QSizeF(width, height), QPageSize.Point))
            printer.setPageMargins(0.0, 0.0, 0.0, 0.0, QPrinter.Point)
            printer.setFullPage(True)

            # Setup painter
            painter = QPainter()
            if not painter.begin(printer):
                return False

            try:
                painter.setRenderHint(QPainter.Antialiasing)

                # Update map settings with actual printer device dimensions and DPI
                dev = painter.device()
                map_settings.setOutputSize(QSize(dev.width(), dev.height()))
                map_settings.setOutputDpi(printer.resolution())

                # Render map
                job = QgsMapRendererCustomPainterJob(map_settings, painter)
                job.start()
                job.waitForFinished()

                # Draw legend if available
                legend_renderer = self.get_setting('legend_renderer')
                if legend_renderer:
                    legend_renderer.draw_legend(
                        painter, QRectF(0, 0, dev.width(), dev.height())
                    )

                return True

            finally:
                painter.end()

        except Exception:
            return False
