"""Renderer for drillhole traces and intervals."""

from __future__ import annotations

from qgis.core import (
    QgsCategorizedSymbolRenderer,
    QgsLineSymbol,
    QgsPalLayerSettings,
    QgsRendererCategory,
    QgsSingleSymbolRenderer,
    QgsTextFormat,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
)
from qgis.PyQt.QtGui import QColor

from sec_interp.gui.renderers.base_renderer import BasePreviewRenderer
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
            self._apply_trace_style(layer)
        else:
            self._apply_interval_style(layer, kwargs.get("unique_units", set()))

    def _apply_trace_style(self, layer: QgsVectorLayer) -> None:
        """Style for drillhole traces with labels."""
        symbol = QgsLineSymbol.createSimple(
            {"color": "50,50,50", "width": "0.3", "capstyle": "round"}
        )
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))

        settings = QgsPalLayerSettings()
        settings.fieldName = "hole_id"
        settings.placement = QgsPalLayerSettings.Placement.Line

        txt_format = QgsTextFormat()
        txt_format.setColor(QColor(0, 0, 0))
        txt_format.setSize(8)
        settings.setFormat(txt_format)

        layer.setLabeling(QgsVectorLayerSimpleLabeling(settings))
        layer.setLabelsEnabled(True)

    def _apply_interval_style(
        self, layer: QgsVectorLayer, unique_units: set[str]
    ) -> None:
        """Styling for lithological intervals."""
        categories = []
        for unit_name in unique_units:
            color = self.color_manager.get_color(unit_name)
            symbol = QgsLineSymbol.createSimple(
                {
                    "color": f"{color.red()},{color.green()},{color.blue()}",
                    "width": "2.0",
                    "capstyle": "flat",
                    "joinstyle": "bevel",
                }
            )
            categories.append(QgsRendererCategory(unit_name, symbol, unit_name))

        layer.setRenderer(QgsCategorizedSymbolRenderer("unit", categories))
