"""Preview Renderer Module (PyQGIS Native).

Handles rendering of interactive previews using native QGIS resources.
This module has been refactored to delegate specialized tasks to modular components.
"""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Optional

from qgis.core import (
    QgsFeature,
    QgsGeometry,
    QgsMapRendererCustomPainterJob,
    QgsMapSettings,
    QgsPointXY,
    QgsProject,
    QgsRectangle,
    QgsWkbTypes,
)
from qgis.gui import QgsMapCanvas, QgsRubberBand
from qgis.PyQt.QtCore import QRectF, QSize, Qt
from qgis.PyQt.QtGui import QColor, QImage, QPainter

from sec_interp.core.types import GeologyData, ProfileData, StructureData
from sec_interp.logger_config import get_logger

from .preview_axes_manager import PreviewAxesManager
from .preview_layer_factory import PreviewLayerFactory
from .preview_legend_renderer import PreviewLegendRenderer
from .preview_optimizer import PreviewOptimizer


logger = get_logger(__name__)


class PreviewRenderer:
    """Renders interactive preview using native PyQGIS resources.

    Acts as an orchestrator for several specialized modules:
    - PreviewLayerFactory: Handles layer creation and symbology.
    - PreviewAxesManager: Handles grid lines and axes labels.
    - PreviewOptimizer: Handles geometric simplification (LOD).
    - PreviewLegendRenderer: Handles legend drawing.
    """

    def __init__(self, canvas: Optional[QgsMapCanvas] = None):
        """Initialize preview renderer.

        Args:
            canvas: QgsMapCanvas instance (optional)
        """
        self.canvas = canvas
        self.layers = []
        self.interpretation_rubbers = []  # Store active rubber bands

        # Specialized components
        self.layer_factory = PreviewLayerFactory()
        self.axes_manager = PreviewAxesManager()
        self.legend_renderer = PreviewLegendRenderer()

        # State for legend rendering (maintained for backward compatibility)
        self.has_topography = False
        self.has_structures = False

    @property
    def active_units(self):
        """Expose active units from factory for legend compatibility."""
        return self.layer_factory.active_units

    def render(
        self,
        topo_data: ProfileData,
        geol_data: Optional[GeologyData] = None,
        struct_data: Optional[StructureData] = None,
        vert_exag: float = 1.0,
        dip_line_length: Optional[float] = None,
        max_points: int = 1000,
        preserve_extent: bool = False,
        use_adaptive_sampling: bool = False,
        drillhole_data: Optional[list] = None,
        interp_data: Optional[list] = None,
        **kwargs,
    ) -> tuple[Optional[QgsMapCanvas], list]:
        """Render preview with all data layers."""
        logger.debug("PreviewRenderer.render() called")
        if not self.canvas:
            logger.warning("PreviewRenderer.render() - no canvas available")
            return None, []

        logger.debug(f"PreviewRenderer.render() - starting with {len(self.layers)} existing layers")

        # 1. Clean up previous layers
        logger.debug("PreviewRenderer.render() - calling _cleanup_layers()")
        self._cleanup_layers()
        logger.debug("PreviewRenderer.render() - cleanup completed")
        self.has_topography = False
        self.has_structures = False

        # 2. Create data layers via LayerFactory
        topo_layer = self.layer_factory.create_topo_layer(
            topo_data, vert_exag, max_points, use_adaptive_sampling
        )
        if topo_layer:
            self.has_topography = True

        geol_layer = self.layer_factory.create_geol_layer(geol_data, vert_exag, max_points)

        # Interpretation Drawing (using QgsRubberBand)
        # We use RubberBands instead of memory layers to prevent QPainter crashes
        # that were occurring with the vector layer renderer
        self._clear_interpretation_rubbers()
        if interp_data:
            logger.debug(f"Rendering {len(interp_data)} interpretations using QgsRubberBand")
            self._render_interpretations(interp_data, vert_exag)

        # For structural layer, use topo or geol as reference
        reference_data = (
            topo_data if topo_data else ([(d, e) for d, e, _ in geol_data] if geol_data else None)
        )
        struct_layer = self.layer_factory.create_struct_layer(
            struct_data, reference_data, vert_exag, dip_line_length
        )
        if struct_layer:
            self.has_structures = True

        # Drillhole layers
        drillhole_layers = []
        if drillhole_data:
            trace_layer = self.layer_factory.create_drillhole_trace_layer(drillhole_data, vert_exag)
            if trace_layer:
                drillhole_layers.append(trace_layer)
            interval_layer = self.layer_factory.create_drillhole_interval_layer(
                drillhole_data, vert_exag
            )
            if interval_layer:
                drillhole_layers.append(interval_layer)

        # 3. Collect valid data layers
        data_layers = [
            layer
            for layer in [
                struct_layer,
                # interpreted polygons are now handled via rubber bands
                geol_layer,
                topo_layer,
                *drillhole_layers,
            ]
            if layer is not None
        ]

        if not data_layers:
            logger.warning("No valid layers to render")
            return None, []

        # 3. Set layers on canvas
        logger.debug(f"PreviewRenderer.render() - setting {len(data_layers)} layers on canvas")
        self.canvas.setLayers(data_layers)
        logger.debug("PreviewRenderer.render() - layers set on canvas")

        # 4. Axes and Labels
        extent = self._calculate_extent(data_layers)
        axes_layer = self.axes_manager.create_axes_layer(extent, vert_exag)
        labels_layer = self.axes_manager.create_axes_labels_layer(extent, vert_exag)

        # 5. Finalize layers list
        layers = [labels_layer, *data_layers, axes_layer]
        layers = [layer for layer in layers if layer is not None]
        self.layers = layers

        # 6. Configure canvas
        if self.canvas and extent:
            self.canvas.setLayers(layers)
            if not preserve_extent:
                # Add 10% padding to extent
                padded_extent = extent
                padded_extent.scale(1.1)
                self.canvas.setExtent(padded_extent)
            self.canvas.refresh()

        return self.canvas, layers

    def draw_legend(self, painter: QPainter, rect: QRectF):
        """Draw legend on the given painter. Delegates to PreviewLegendRenderer."""
        self.legend_renderer.draw_legend(
            painter, rect, self.active_units, self.has_topography, self.has_structures
        )

    def export_to_image(
        self,
        layers: list,
        extent,
        width: int,
        height: int,
        output_path: str,
        dpi: int = 300,
    ) -> bool:
        """Export preview to image file. Maintains same logic but orchestrated."""
        try:
            settings = QgsMapSettings()
            settings.setLayers(layers)
            settings.setExtent(extent)
            settings.setOutputSize(QSize(width, height))
            settings.setOutputDpi(dpi)

            image = QImage(QSize(width, height), QImage.Format_ARGB32)
            image.fill(QColor(255, 255, 255))

            painter = QPainter(image)
            painter.setRenderHint(QPainter.Antialiasing)

            job = QgsMapRendererCustomPainterJob(settings, painter)
            job.start()
            job.waitForFinished()

            # Delegate legend drawing
            self.draw_legend(painter, QRectF(0, 0, width, height))
            painter.end()

            return image.save(output_path)

        except Exception:
            logger.exception("Error exporting preview")
            return False

    def _cleanup_layers(self):
        """Reset internal layers list, clear canvas, and remove rubber bands.

        Memory layers NOT added to the project are automatically cleaned up
        when their reference count drops to zero.
        """
        logger.debug(f"_cleanup_layers() called - {len(self.layers)} layers to clean")
        self._clear_interpretation_rubbers()  # Clean up rubber bands
        if self.canvas:
            try:
                logger.debug("_cleanup_layers() - clearing canvas layers")
                self.canvas.setLayers([])
                logger.debug("_cleanup_layers() - canvas layers cleared")
                self.canvas.refresh()
            except Exception as e:
                logger.error(f"Failed to clear canvas layers during cleanup: {e}", exc_info=True)

        # Just clear the list to let Python's garbage collector handle the C++ objects
        # if they are no longer used by the canvas.
        logger.debug(f"_cleanup_layers() - clearing {len(self.layers)} layer references")
        self.layers = []
        self.layer_factory.active_units = {}
        logger.debug("_cleanup_layers() completed")

    def _clear_interpretation_rubbers(self):
        """Remove all interpretation rubber bands from canvas."""
        if not self.canvas:
            return

        for rb in self.interpretation_rubbers:
            with contextlib.suppress(RuntimeError, AttributeError):
                self.canvas.scene().removeItem(rb)
        self.interpretation_rubbers.clear()

    def _render_interpretations(self, interp_data, vert_exag):
        """Render interpretations as QgsRubberBand objects."""
        if not self.canvas:
            return

        for interp in interp_data:
            if not interp.vertices_2d or len(interp.vertices_2d) < 3:
                continue

            # Create rubber band
            rb = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)

            # Set style (use polygon color)
            try:
                # Handle both hex strings and color names
                poly_color = QColor(interp.color)
                if not poly_color.isValid():
                    poly_color = QColor("#FF0000")  # Fallback
            except (ValueError, TypeError):
                poly_color = QColor("#FF0000")

            poly_color.setAlpha(120)
            rb.setColor(poly_color)
            rb.setWidth(1)
            rb.setStrokeColor(poly_color.darker(150))

            # Add geometry
            points = [QgsPointXY(x, y * vert_exag) for x, y in interp.vertices_2d]
            # Ensure closed
            if points[0] != points[-1]:
                points.append(points[0])

            geom = QgsGeometry.fromPolygonXY([points])
            rb.setToGeometry(geom, None)
            rb.show()

            self.interpretation_rubbers.append(rb)

    def _calculate_extent(self, layers: list):
        """Combine extents of all given layers."""
        extent = None
        for layer in layers:
            layer_extent = layer.extent()
            if extent is None:
                extent = layer_extent
            else:
                extent.combineExtentWith(layer_extent)
        return extent
