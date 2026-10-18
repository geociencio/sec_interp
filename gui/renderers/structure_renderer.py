"""Renderer for structural data dips."""

from __future__ import annotations

from qgis.core import QgsLineSymbol, QgsSingleSymbolRenderer, QgsVectorLayer

from sec_interp.gui.renderers.base_renderer import (
    BasePreviewRenderer,
    color_to_rgb_string,
)


class StructureRenderer(BasePreviewRenderer):
    """Renderer for structural measurement symbols."""

    def apply_style(self, layer: QgsVectorLayer, **kwargs) -> None:
        """Apply a simple line style for structural dips (color/width configurable)."""
        color = color_to_rgb_string(kwargs.get("color"), "204,0,0")
        width = str(kwargs.get("width") or "0.5")
        symbol = QgsLineSymbol.createSimple({"color": color, "width": width, "capstyle": "round"})
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))
