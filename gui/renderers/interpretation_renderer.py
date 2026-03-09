"""Renderer for interpretation polygons."""

from __future__ import annotations

from qgis.core import (
    QgsCategorizedSymbolRenderer,
    QgsFillSymbol,
    QgsRendererCategory,
    QgsVectorLayer,
)
from qgis.PyQt.QtGui import QColor

from sec_interp.gui.renderers.base_renderer import BasePreviewRenderer


class InterpretationRenderer(BasePreviewRenderer):
    """Renderer for interpretation polygons with unique colors."""

    def apply_style(self, layer: QgsVectorLayer, **kwargs) -> None:
        """Apply categorized styling based on interpretation ID and custom color."""
        interp_data = kwargs.get("interp_data", [])
        categories = []

        for interp in interp_data:
            # Use interpretation color directly
            hex_color = interp.color if interp.color else "#FF0000"
            color = QColor(hex_color)

            # Fill color with transparency - create from hex string again to avoid copy constructor issues in mocks
            fill_color = QColor(hex_color)
            fill_color.setAlpha(180)

            symbol = QgsFillSymbol.createSimple(
                {
                    "color": hex_color,
                    "alpha": "0.7",  # 70% opacity
                    "outline_color": f"{color.darker(160).red()},{color.darker(160).green()},{color.darker(160).blue()}",
                    "outline_width": "0.5",
                }
            )
            categories.append(QgsRendererCategory(interp.id, symbol, interp.name))

        layer.setRenderer(QgsCategorizedSymbolRenderer("id", categories))
