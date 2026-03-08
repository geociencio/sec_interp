"""Preview Renderer Module (PyQGIS Native).

Handles rendering of interactive previews using native QGIS resources.
This module has been refactored to delegate specialized tasks to modular components.
"""

from __future__ import annotations

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

    def __init__(self, canvas: QgsMapCanvas | None = None) -> None:
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
    def active_units(self) -> dict[str, Any]:
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

        # 2. Create data layers via internal orchestrator
        data_layers = self._collect_data_layers(
            topo_data,
            geol_data,
            struct_data,
            vert_exag,
            max_points,
            use_adaptive_sampling,
            dip_line_length,
            drillhole_data,
        )

        # 2.5 Render interpretations (using rubber bands)
        if interp_data:
            self._render_interpretations(interp_data, vert_exag)

        if not data_layers:
            logger.debug("No valid data layers to render yet")
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
                padded_extent = extent
                padded_extent.scale(1.1)
                self.canvas.setExtent(padded_extent)
            self.canvas.refresh()

        return self.canvas, layers

    def _collect_data_layers(
        self,
        topo_data,
        geol_data,
        struct_data,
        vert_exag,
        max_points,
        use_adaptive,
        dip_len,
        drill_data,
    ) -> list:
        """Collect all data layers in order."""
        # Topography & Geology
        topo_layer = self.layer_factory.create_topo_layer(
            topo_data, vert_exag, max_points, use_adaptive
        )
        if topo_layer:
            self.has_topography = True

        topo_fill = self.layer_factory.create_topo_fill_layer(topo_data, vert_exag, max_points)
        geol_layer = self.layer_factory.create_geol_layer(geol_data, vert_exag, max_points)

        # Specialized layers
        struct_layer = self._add_struct_layer(struct_data, topo_data, geol_data, vert_exag, dip_len)
        drill_layers = self._add_drillhole_layers(drill_data, vert_exag)

        # Combine in Z-order (top to bottom)
        candidates = [struct_layer, geol_layer, topo_layer, topo_fill, *drill_layers]
        return [L for L in candidates if L is not None]

    def _add_struct_layer(self, data, topo, geol, exag, dip_len) -> Any | None:
        """Create structural layer if data exists."""
        ref = topo if topo else ([p for s in geol for p in s.points] if geol else None)
        layer = self.layer_factory.create_struct_layer(data, ref, exag, dip_len)
        if layer:
            self.has_structures = True
        return layer

    def _add_drillhole_layers(self, data, exag) -> list:
        """Create drillhole layers if data exists."""
        layers = []
        if not data:
            return layers

        t_layer = self.layer_factory.create_drillhole_trace_layer(data, exag)
        if t_layer:
            layers.append(t_layer)

        i_layer = self.layer_factory.create_drillhole_interval_layer(data, exag)
        if i_layer:
            layers.append(i_layer)

        return layers

    def draw_legend(self, painter: QPainter, rect: QRectF) -> None:
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

    def _cleanup_layers(self) -> None:
        """Remove previous layers from QgsProject with complete cleanup."""
        # Clean up data layers
        for layer in self.layers:
            if layer and layer.isValid():
                try:
                    QgsProject.instance().removeMapLayer(layer.id())
                except Exception as e:
                    logger.warning(f"Failed to remove map layer: {e}")

        self.layers = []
        self.layer_factory.active_units = {}

        # Cleanup interpretation rubber bands COMPLETELY
        if self.canvas and self.canvas.scene():
            scene = self.canvas.scene()
            for rb in self.interpretation_rubbers:
                if rb:
                    try:
                        # 1. Hide first
                        rb.hide()
                        # 2. Reset geometry (releases C++ memory)
                        rb.reset(QgsWkbTypes.PolygonGeometry)
                        # 3. Remove from scene
                        scene.removeItem(rb)
                    except Exception as e:
                        logger.warning(f"Failed to remove rubber band: {e}")

        # Clear references to allow GC
        self.interpretation_rubbers = []

        logger.debug("PreviewRenderer cleanup completed")

    def _render_interpretations(
        self, interp_data: list[InterpretationPolygon], vert_exag: float
    ) -> None:
        """Render interpretations as QgsRubberBand objects."""
        if not self.canvas:
            return

        MIN_INTERP_VERTICES = 3
        for interp in interp_data:
            if not interp.vertices_2d or len(interp.vertices_2d) < MIN_INTERP_VERTICES:
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

    def _calculate_extent(self, layers: list) -> Any | None:
        """Combine extents of all given layers."""
        extent = None
        for layer in layers:
            layer_extent = layer.extent()
            if extent is None:
                extent = layer_extent
            else:
                extent.combineExtentWith(layer_extent)
        return extent
