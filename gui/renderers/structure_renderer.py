from __future__ import annotations

from qgis.core import QgsLineSymbol, QgsSingleSymbolRenderer, QgsVectorLayer

from sec_interp.gui.renderers.base_renderer import BasePreviewRenderer


class StructureRenderer(BasePreviewRenderer):
    """Renderer for structural measurement symbols."""

    def apply_style(self, layer: QgsVectorLayer, **kwargs) -> None:
        """Apply a simple red line style for structural dips."""
        symbol = QgsLineSymbol.createSimple(
            {"color": "204,0,0", "width": "0.5", "capstyle": "round"}
        )
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))
