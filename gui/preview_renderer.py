from __future__ import annotations

"""Preview Renderer Module (PyQGIS Native).

Handles rendering of interactive previews using native QGIS resources.
This module has been refactored to delegate specialized tasks to modular components.
"""

import contextlib

from qgis.core import (
    QgsGeometry,
    QgsMapRendererCustomPainterJob,
    QgsMapSettings,
    QgsPointXY,
    QgsProject,
    QgsWkbTypes,
)
from qgis.gui import QgsMapCanvas, QgsRubberBand
from qgis.PyQt.QtCore import QRectF, QSize
from qgis.PyQt.QtGui import QColor, QImage, QPainter

from sec_interp.core.domain import (
    GeologyData,
    InterpretationPolygon,
    ProfileData,
    StructureData,
)
from sec_interp.logger_config import get_logger

from .preview_axes_manager import PreviewAxesManager
from .preview_layer_factory import PreviewLayerFactory
from .preview_legend_renderer import PreviewLegendRenderer

logger = get_logger(__name__)


class PreviewRenderer:
    """Renders interactive preview using native PyQGIS resources.

    Acts as an orchestrator for several specialized modules:
    - PreviewLayerFactory: Handles layer creation and symbology.
    - PreviewAxesManager: Handles grid lines and axes labels.
    - PreviewOptimizer: Handles geometric simplification (LOD).
    - PreviewLegendRenderer: Handles legend drawing.
    """

    def __init__(self, canvas: QgsMapCanvas | None = None):
        """Initialize preview renderer.

        Args:
            canvas: QgsMapCanvas instance (optional)

        """
        self.canvas = canvas
        self.layers = []
        self.interpretation_rubbers = []

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
        geol_data: GeologyData | None = None,
        struct_data: StructureData | None = None,
        vert_exag: float = 1.0,
        dip_line_length: float | None = None,
        max_points: int = 1000,
        preserve_extent: bool = False,
        use_adaptive_sampling: bool = False,
        drillhole_data: list | None = None,
        interp_data: list[InterpretationPolygon] | None = None,
        show_legend: bool = True,
        **kwargs,
    ) -> tuple[QgsMapCanvas | None, list]:
        """Render preview with all data layers."""
        logger.debug("render() called")

        # 1. Clean up previous layers
        self._cleanup_layers()
        self.has_topography = False
        self.has_structures = False

        # 2. Create data layers via LayerFactory
        topo_layer = self.layer_factory.create_topo_layer(
            topo_data, vert_exag, max_points, use_adaptive_sampling
        )
        if topo_layer:
            self.has_topography = True

        topo_fill_layer = self.layer_factory.create_topo_fill_layer(
            topo_data, vert_exag, max_points
        )

        geol_layer = self.layer_factory.create_geol_layer(geol_data, vert_exag, max_points)

        # ... rest of data layers ...
        # For structural layer, use topo or geol as reference
        reference_data = (
            topo_data
            if topo_data
            else ([p for seg in geol_data for p in seg.points] if geol_data else None)
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

        # 2.5 Render interpretations (using rubber bands)
        if interp_data:
            self._render_interpretations(interp_data, vert_exag)

        # 3. Collect valid data layers
        # Order: Structures on top, then Geology, then Topography line, then Fill, then Drillholes
        data_layers = [
            layer
            for layer in [
                struct_layer,
                geol_layer,
                topo_layer,
                topo_fill_layer,
                *drillhole_layers,
            ]
            if layer is not None
        ]

        if not data_layers:
            logger.warning("No valid layers to render")
            return None, []

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
        show_legend: bool = True,
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
            if show_legend:
                self.draw_legend(painter, QRectF(0, 0, width, height))
            painter.end()

            return image.save(output_path)

        except Exception:
            logger.exception("Error exporting preview")
            return False

    def _cleanup_layers(self):
        """Remove previous layers from QgsProject."""
        for layer in self.layers:
            if layer:
                with contextlib.suppress(Exception):
                    QgsProject.instance().removeMapLayer(layer.id())
        self.layers = []
        self.layer_factory.active_units = {}

        # Clear interpretation rubber bands
        for rb in self.interpretation_rubbers:
            if rb:
                with contextlib.suppress(Exception):
                    rb.hide()
                    # Python garbage collection should clean up QgsRubberBand if canvas reference is lost
                    # but explicit removal from canvas Scene is better
                    self.canvas.scene().removeItem(rb)
        self.interpretation_rubbers = []

    def _render_interpretations(self, interp_data: list[InterpretationPolygon], vert_exag: float):
        """Render interpretations as QgsRubberBand objects."""
        if not self.canvas:
            return

        for interp in interp_data:
            if not interp.vertices_2d or len(interp.vertices_2d) < 3:
                continue

            # Create rubber band
            rb = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)

            # Set style
            try:
                poly_color = QColor(interp.color)
                if not poly_color.isValid():
                    poly_color = QColor("#FF0000")
            except (ValueError, TypeError):
                poly_color = QColor("#FF0000")

            poly_color.setAlpha(180)  # More vibrant (approx 70%)
            rb.setColor(poly_color)
            rb.setWidth(2)  # Slightly thicker border
            rb.setStrokeColor(poly_color.darker(160))  # More defined border

            # Add geometry
            # Points are (dist, elev) -> (x, y * exag)
            points = [QgsPointXY(x, y * vert_exag) for x, y in interp.vertices_2d]
            # Ensure closed for polygon
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
