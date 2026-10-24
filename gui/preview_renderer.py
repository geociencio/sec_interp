"""Preview Renderer Module (PyQGIS Native).

Handles rendering of interactive previews using native QGIS resources.
This module has been refactored to delegate specialized tasks to modular components.
"""

from __future__ import annotations

import contextlib
from typing import Any

from qgis.core import QgsProject
from qgis.gui import QgsMapCanvas
from qgis.PyQt.QtCore import QRectF
from qgis.PyQt.QtGui import QColor, QPainter

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
from .preview_renderer_cleanup import (
    cleanup_layers,
    cleanup_rubber_bands,
    get_valid_layer_ids,
)
from .preview_renderer_layers import (
    add_drillhole_layers,
    add_struct_layer,
    calculate_extent,
    collect_data_layers,
)

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
        self.has_drillholes = False
        self.is_rendering = False
        self._interpretations: list = []
        self._hidden_interp_ids: set[str] = set()
        self._layer_styles: dict = {}

    @property
    def active_units(self) -> dict[str, Any]:
        """Expose active units from factory for legend compatibility."""
        return self.layer_factory.active_units

    def legend_units(self) -> list[tuple[str, str, Any, bool, str]]:
        """Return ``(name, label, color, hidden, source)`` for known units, ordered.

        ``source`` is ``"geology"`` or ``"drillholes"``; a unit present in both is
        attributed to geology.
        """
        manager = self.layer_factory.color_manager
        geology = set(manager.units_for_source("geology"))
        drillholes = set(manager.units_for_source("drillholes"))
        entries = []
        for name in manager.ordered_units():
            source = "drillholes" if name in drillholes and name not in geology else "geology"
            entries.append(
                (
                    name,
                    manager.label(name),
                    manager.get_color(name),
                    manager.is_hidden(name),
                    source,
                )
            )
        return entries

    def cleanup(self) -> None:
        """Remove transient layers from the project and release resources.

        Idempotent; safe to call on dialog close and plugin unload to avoid
        leaking temporary (memory) layers that trigger QGIS's
        "scratch layers" warning on exit.
        """
        self._cleanup_layers()

    def render(  # noqa: PLR0913, PLR0917
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
        topo_color_mode: str = "gradient",
        topo_ramp_name: str | None = None,
        topo_single_color: str | None = None,
        topo_smooth_data: ProfileData | None = None,
        layer_styles: dict | None = None,
        hidden_interp_ids: set[str] | None = None,
    ) -> tuple[QgsMapCanvas | None, list]:
        """Render preview with all data layers."""
        if self.is_rendering:
            logger.warning("Render already in progress, skipping overlapping call.")
            return None, []

        self._interpretations = list(interp_data or [])
        self._hidden_interp_ids = {str(i) for i in (hidden_interp_ids or set())}
        self._layer_styles = dict(layer_styles or {})

        try:
            self.is_rendering = True
            logger.debug("render() called - LOCK ACQUIRED")

            # 1. Clean up previous layers
            self._cleanup_layers()
            self.has_topography = False
            self.has_structures = False
            self.has_drillholes = False

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
                topo_color_mode,
                topo_ramp_name,
                topo_single_color,
                topo_smooth_data,
                layer_styles,
                hidden_interp_ids,
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
            self._setup_canvas(layers, extent, preserve_extent)

            logger.debug("render: Complete.")
            return self.canvas, layers
        finally:
            self.is_rendering = False
            logger.debug("render: LOCK RELEASED")

    def _setup_canvas(self, layers: list, extent, preserve_extent: bool) -> None:
        """Set layers and extent on the map canvas.

        Args:
            layers: List of map layers to render.
            extent: The bounding box extent of the layers.
            preserve_extent: Whether to keep the current extent or zoom to the new layers.

        """
        if not self.canvas or not extent:
            return

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
        topo_color_mode: str = "gradient",
        topo_ramp_name: str | None = None,
        topo_single_color: str | None = None,
        topo_smooth_data: ProfileData | None = None,
        layer_styles: dict | None = None,
        hidden_interp_ids: set[str] | None = None,
    ) -> list:
        """Collect all data layers in order."""
        return collect_data_layers(
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
            topo_color_mode,
            topo_ramp_name,
            topo_single_color,
            topo_smooth_data,
            layer_styles,
            hidden_interp_ids,
        )

    def _add_struct_layer(self, data, topo, geol, exag, dip_len, style=None) -> Any | None:
        """Create structural layer if data exists."""
        return add_struct_layer(self, data, topo, geol, exag, dip_len, style)

    def _add_drillhole_layers(self, data, exag, style=None) -> list:
        """Create drillhole layers if data exists."""
        return add_drillhole_layers(self, data, exag, style)

    def draw_legend(self, painter: QPainter, rect: QRectF) -> None:
        """Draw legend on the given painter honoring the configured layout."""
        manager = self.layer_factory.color_manager
        style = self._layer_styles
        geology_set = set(manager.units_for_source("geology"))
        drill_set = set(manager.units_for_source("drillholes"))
        active = self.active_units
        geology_units = {n: c for n, c in active.items() if n in geology_set or n not in drill_set}
        drill_units = {n: c for n, c in active.items() if n in drill_set and n not in geology_set}
        self.legend_renderer.draw_legend(
            painter,
            rect,
            geology_units,
            self.has_topography,
            self.has_structures,
            self.has_drillholes,
            manager.labels(),
            drill_units or None,
            [
                i
                for i in self._interpretations
                if str(getattr(i, "id", "")) not in self._hidden_interp_ids
            ]
            or None,
            layout={
                "position": style.get("legend_pos", "top-right"),
                "font_size": style.get("legend_font_size", 8),
                "max_items": style.get("legend_max_items", 0),
            },
            layer_colors={
                "topography": self._legend_topo_color(style),
                "structures": QColor(str(style.get("struct_color") or "#cc0000")),
                "drillholes": QColor(str(style.get("drill_trace_color") or "#323232")),
            },
        )

    @staticmethod
    def _legend_topo_color(style: dict) -> QColor:
        """Return the topography color to show in the legend."""
        if style.get("color_mode") == "single":
            return QColor(str(style.get("single_color_hex") or "#1f77b4"))
        return QColor("#0066cc")

    def _cleanup_layers(self, layers: list | None = None) -> None:
        """Safely remove transient layers from the project."""
        cleanup_layers(self, layers)

    def _get_valid_layer_ids(self, layers: list) -> list[str]:
        """Extract valid IDs from a list of layers, handling stale objects."""
        return get_valid_layer_ids(layers)

    def _cleanup_rubber_bands(self) -> None:
        """Thoroughly cleanup interpretation rubber bands."""
        cleanup_rubber_bands(self)

    def _calculate_extent(self, layers: list) -> Any | None:
        """Combine extents of all given layers."""
        return calculate_extent(layers)
