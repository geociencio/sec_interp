# -*- coding: utf-8 -*-
"""
Export management module for SecInterp main dialog.

This module handles all export operations for preview data,
supporting multiple formats (PNG, JPG, PDF, SVG).
"""

from typing import Dict, Any, Optional, List, TYPE_CHECKING
from pathlib import Path

from qgis.core import QgsVectorLayer, QgsMapSettings, QgsRectangle
from qgis.PyQt.QtWidgets import QFileDialog
from qgis.PyQt.QtGui import QColor

from ..exporters.image_exporter import ImageExporter
from ..exporters.pdf_exporter import PDFExporter
from ..exporters.svg_exporter import SVGExporter
from .main_dialog_config import DialogDefaults
from ..logger_config import get_logger

if TYPE_CHECKING:
    from .main_dialog import SecInterpDialog

logger = get_logger(__name__)


class ExportManager:
    """Manages export operations for the dialog.
    
    This class handles exporting preview data to various file formats,
    managing export settings and file dialogs.
    """
    
    def __init__(self, dialog: 'SecInterpDialog'):
        """Initialize export manager with reference to parent dialog.
        
        Args:
            dialog: The SecInterpDialog instance
        """
        self.dialog = dialog
    
    def export_preview(self) -> bool:
        """Export the current preview to a file using dedicated exporters.
        
        Returns:
            True if export successful, False otherwise
        """
        try:
            # Get current canvas and layers
            canvas = self.dialog.plugin_instance.preview_canvas
            if not canvas:
                self.dialog.messagebar.pushMessage(
                    "Export Error",
                    "No preview available to export. Generate a preview first.",
                    level=2  # Warning
                )
                return False
            
            layers = canvas.layers()
            if not layers:
                self.dialog.messagebar.pushMessage(
                    "Export Error",
                    "No layers to export. Generate a preview first.",
                    level=2
                )
                return False
            
            # Get export format from user
            file_filter = (
                "PNG Image (*.png);;"
                "JPEG Image (*.jpg *.jpeg);;"
                "PDF Document (*.pdf);;"
                "SVG Vector (*.svg)"
            )
            
            output_path, selected_filter = QFileDialog.getSaveFileName(
                self.dialog,
                "Export Preview",
                "",
                file_filter
            )
            
            if not output_path:
                return False  # User cancelled
            
            output_path = Path(output_path)
            
            # Get export settings
            extent = canvas.extent()
            width = DialogDefaults.PREVIEW_WIDTH
            height = DialogDefaults.PREVIEW_HEIGHT
            dpi = DialogDefaults.DPI
            
            settings = self.get_export_settings(width, height, dpi, extent)
            
            # Export based on format
            success = self._export_to_format(output_path, settings, canvas)
            
            if success:
                self.dialog.messagebar.pushMessage(
                    "Export Successful",
                    f"Preview exported to {output_path.name}",
                    level=3  # Success
                )
            else:
                self.dialog.messagebar.pushMessage(
                    "Export Failed",
                    f"Failed to export preview to {output_path}",
                    level=1  # Critical
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Export failed: {e}", exc_info=True)
            self.dialog.messagebar.pushMessage(
                "Export Error",
                f"An error occurred during export: {str(e)}",
                level=1
            )
            return False
    
    def get_export_settings(
        self,
        width: int,
        height: int,
        dpi: int,
        extent: QgsRectangle
    ) -> Dict[str, Any]:
        """Get export settings dictionary.
        
        Args:
            width: Output width in pixels
            height: Output height in pixels
            dpi: Dots per inch
            extent: Map extent to export
        
        Returns:
            Dictionary of export settings
        """
        return {
            'width': width,
            'height': height,
            'dpi': dpi,
            'extent': extent,
            'background_color': DialogDefaults.BACKGROUND_COLOR,
            'legend_renderer': getattr(self.dialog.plugin_instance, 'preview_renderer', None)
        }
    
    def _export_to_format(
        self,
        output_path: Path,
        settings: Dict[str, Any],
        canvas
    ) -> bool:
        """Export to specific format using appropriate exporter.
        
        Args:
            output_path: Output file path
            settings: Export settings dictionary
            canvas: QgsMapCanvas instance
        
        Returns:
            True if successful, False otherwise
        """
        ext = output_path.suffix.lower()
        
        # Create map settings from canvas
        map_settings = QgsMapSettings()
        map_settings.setLayers(canvas.layers())
        map_settings.setExtent(settings['extent'])
        map_settings.setOutputSize(canvas.size())
        map_settings.setBackgroundColor(settings['background_color'])
        
        try:
            if ext in ['.png', '.jpg', '.jpeg']:
                exporter = ImageExporter(settings)
                return exporter.export(output_path, map_settings)
            
            elif ext == '.pdf':
                exporter = PDFExporter(settings)
                return exporter.export(output_path, map_settings)
            
            elif ext == '.svg':
                exporter = SVGExporter(settings)
                return exporter.export(output_path, map_settings)
            
            else:
                logger.error(f"Unsupported export format: {ext}")
                return False
                
        except Exception as e:
            logger.error(f"Export to {ext} failed: {e}", exc_info=True)
            return False
