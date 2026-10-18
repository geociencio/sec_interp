"""Renderer for drillhole traces and intervals."""

from __future__ import annotations

from qgis.core import (
    QgsLineSymbol,
    QgsPalLayerSettings,
    QgsSingleSymbolRenderer,
    QgsTextFormat,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
)
from qgis.PyQt.QtGui import QColor

from sec_interp.gui.renderers.base_renderer import (
    BasePreviewRenderer,
    build_categorized_line_style,
    color_to_rgb_string,
)
from sec_interp.gui.renderers.color_manager import ColorManager


class DrillholeRenderer(BasePreviewRenderer):
    """Renderer for drillhole trace and interval layers."""

    def __init__(self, color_manager: ColorManager) -> None:
        """Initialize the drillhole renderer.

        Args:
            color_manager: Manager for geological unit colors.

        """
        self.color_manager = color_manager

    def apply_style(self, layer: QgsVectorLayer, **kwargs) -> None:
        """Apply styling based on layer role (trace or interval)."""
        role = kwargs.get("role", "trace")
        if role == "trace":
            self._apply_trace_style(
                layer,
                color=kwargs.get("color"),
                width=kwargs.get("width"),
                labels=kwargs.get("labels", True),
            )
        else:
            self._apply_interval_style(layer, kwargs.get("unique_units", set()))

    def _apply_trace_style(
        self,
        layer: QgsVectorLayer,
        color: str | None = None,
        width: object = None,
        labels: bool = True,
    ) -> None:
        """Style for drillhole traces (color/width/labels configurable)."""
        symbol = QgsLineSymbol.createSimple(
            {
                "color": color_to_rgb_string(color, "50,50,50"),
                "width": str(width or "0.3"),
                "capstyle": "round",
            }
        )
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))

        if not labels:
            layer.setLabelsEnabled(False)
            return

        settings = QgsPalLayerSettings()
        settings.fieldName = "hole_id"
        settings.placement = QgsPalLayerSettings.Placement.Line

        txt_format = QgsTextFormat()
        txt_format.setColor(QColor(0, 0, 0))
        txt_format.setSize(8)
        settings.setFormat(txt_format)

        layer.setLabeling(QgsVectorLayerSimpleLabeling(settings))
        layer.setLabelsEnabled(True)

    def _apply_interval_style(self, layer: QgsVectorLayer, unique_units: set[str]) -> None:
        """Styling for lithological intervals (honoring hidden units)."""
        layer.setRenderer(
            build_categorized_line_style(
                self.color_manager,
                unique_units,
                width="2.0",
                capstyle="flat",
                joinstyle="bevel",
                hidden=self.color_manager.hidden_units(),
            )
        )
