"""Renderer for geological segments."""

from __future__ import annotations

from qgis.core import (
    QgsCategorizedSymbolRenderer,
    QgsLineSymbol,
    QgsRendererCategory,
    QgsVectorLayer,
)

from sec_interp.gui.renderers.base_renderer import BasePreviewRenderer
from sec_interp.gui.renderers.color_manager import ColorManager


class GeologyRenderer(BasePreviewRenderer):
    """Renderer for geological units in section."""

    def __init__(self, color_manager: ColorManager) -> None:
        """Initialize the geology renderer.

        Args:
            color_manager: Manager for geological unit colors.

        """
        self.color_manager = color_manager

    def apply_style(self, layer: QgsVectorLayer, **kwargs) -> None:
        """Apply categorized styling based on unit names."""
        unique_units = kwargs.get("unique_units", set())
        categories = []

        for unit_name in unique_units:
            color = self.color_manager.get_color(unit_name)
            symbol = QgsLineSymbol.createSimple(
                {
                    "color": f"{color.red()},{color.green()},{color.blue()}",
                    "width": "0.7",
                    "capstyle": "round",
                    "joinstyle": "round",
                }
            )
            categories.append(QgsRendererCategory(unit_name, symbol, unit_name))

        layer.setRenderer(QgsCategorizedSymbolRenderer("unit", categories))
