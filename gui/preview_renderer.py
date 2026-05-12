"""Preview Renderer Module (PyQGIS Native).

Handles rendering of interactive previews using native QGIS resources.
This module has been refactored to delegate specialized tasks to modular components.
"""

from __future__ import annotations

import contextlib
from typing import Any

from qgis.core import (
    QgsMapRendererCustomPainterJob,
    QgsMapSettings,
    QgsProject,
    QgsWkbTypes,
)
from qgis.gui import QgsMapCanvas
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
        self.layers: list = []
        self.interpretation_rubbers: list = []

        # Specialized components
        self.layer_factory = PreviewLayerFactory()
        self.axes_manager = PreviewAxesManager()
        self.legend_renderer = PreviewLegendRenderer()

        # State for legend and rendering control
        self.has_topography = False
        self.has_structures = False
        self.is_rendering = False

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
        if self.is_rendering:
            logger.warning("Render already in progress, skipping overlapping call.")
            return None, []

        try:
            self.is_rendering = True
            logger.debug("render() called - LOCK ACQUIRED")

            # 1. Clean up previous layers
            self._cleanup_layers()
            self.has_topography = False
            self.has_structures = False

            # 2. Create data layers via internal orchestrator
            logger.debug("render: Collecting data layers...")
            data_layers = self._collect_data_layers(
                topo_data,
                geol_data,
                struct_data,
                vert_exag,
                max_points,
                use_adaptive_sampling,
                dip_line_length,
                drillhole_data,
                interp_data,
            )

            if not data_layers:
                logger.debug("No valid data layers to render yet")
                return None, []

            # 4. Axes and Labels
            logger.debug("render: Creating axes and labels...")
            extent = self._calculate_extent(data_layers)
            axes_layer = self.axes_manager.create_axes_layer(extent, vert_exag)
            labels_layer = self.axes_manager.create_axes_labels_layer(extent, vert_exag)

            # 5. Finalize layers list and register in project to ensure lifetime
            logger.debug("render: Finalizing layer list...")
            layers = [labels_layer, *data_layers, axes_layer]
            layers = [layer for layer in layers if layer is not None]

            # In QGIS 4, layers must be in a project to be reliably rendered without crashes
            for layer in layers:
                if layer and not QgsProject.instance().mapLayer(layer.id()):
                    QgsProject.instance().addMapLayer(layer, False)  # False = don't add to legend

            self.layers = layers

            # 6. Configure canvas
            if self.canvas and extent:
                logger.debug("render: Setting layers to canvas...")
                self.canvas.setLayers(layers)
                if not preserve_extent:
                    padded_extent = extent
                    with contextlib.suppress(AttributeError, TypeError, RuntimeError):
                        padded_extent.scale(1.1)
                    logger.debug("render: Setting canvas extent...")
                    self.canvas.setExtent(padded_extent)
                logger.debug("render: Refreshing canvas...")
                self.canvas.refresh()
                # Force a repaint of the scene to ensure stability in Qt6
                if self.canvas.scene():
                    self.canvas.scene().update()

            logger.debug("render: Complete.")
            return self.canvas, layers
        finally:
            self.is_rendering = False
            logger.debug("render: LOCK RELEASED")

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
        interp_data,
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
        interp_layer = self.layer_factory.create_interp_layer(interp_data, vert_exag)

        # Combine in Z-order (top to bottom)
        candidates = [
            struct_layer,
            geol_layer,
            topo_layer,
            topo_fill,
            *drill_layers,
            interp_layer,
        ]
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

    def _cleanup_layers(self, layers: list | None = None) -> None:
        """Safely remove transient layers from the project."""
        if layers is None:
            layers = self.layers

        project = QgsProject.instance()
        if not project or not layers:
            return

        valid_ids = self._get_valid_layer_ids(layers)
        if valid_ids:
            logger.debug(
                f"PreviewRenderer: Requesting removal of {len(valid_ids)} transient layers"
            )
            try:
                project.removeMapLayers(valid_ids)
                logger.debug("PreviewRenderer map layer cleanup successful")
            except Exception as e:
                logger.warning(f"Non-critical error during layer cleanup: {e}")

        self.layers = []
        self.layer_factory.active_units = {}
        self._cleanup_rubber_bands()
        logger.debug("PreviewRenderer cleanup completed")

    def _get_valid_layer_ids(self, layers: list) -> list[str]:
        """Extract valid IDs from a list of layers, handling stale objects."""
        valid_ids = []
        for layer in layers:
            try:
                if layer and hasattr(layer, "id"):
                    valid_ids.append(layer.id())
            except (RuntimeError, AttributeError):
                continue
        return valid_ids

    def _cleanup_rubber_bands(self) -> None:
        """Thoroughly cleanup interpretation rubber bands to release C++ memory."""
        if not self.canvas or not self.canvas.scene():
            self.interpretation_rubbers = []
            return

        scene = self.canvas.scene()
        for rb in self.interpretation_rubbers:
            if not rb:
                continue
            try:
                rb.hide()
                rb.reset(QgsWkbTypes.PolygonGeometry)
                scene.removeItem(rb)
            except Exception as e:
                logger.warning(f"Failed to remove rubber band: {e}")

        self.interpretation_rubbers = []

        logger.debug("PreviewRenderer cleanup completed")

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
