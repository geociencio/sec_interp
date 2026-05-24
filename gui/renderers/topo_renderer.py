"""Renderer for topographic profile elevation polychromy."""

from __future__ import annotations

from qgis.core import (
    QgsClassificationFixedInterval,
    QgsGraduatedSymbolRenderer,
    QgsLineSymbol,
    QgsStyle,
    QgsVectorLayer,
)

from sec_interp.gui.renderers.base_renderer import BasePreviewRenderer


class TopoRenderer(BasePreviewRenderer):
    """Renderer for topographic profile layers."""

    def apply_style(self, layer: QgsVectorLayer, **kwargs) -> None:
        """Apply polychromatic elevation styling."""
        renderer = QgsGraduatedSymbolRenderer("elev")
        renderer.setSourceSymbol(
            QgsLineSymbol.createSimple({"width": "0.8", "capstyle": "round"})
        )

        style = QgsStyle.defaultStyle()
        # Try a terrain-like default ramp
        color_ramp = style.colorRamp("Spectral") or style.colorRamp("RdYlGn")
        if color_ramp:
            renderer.updateColorRamp(color_ramp)

        renderer.setClassificationMethod(QgsClassificationFixedInterval())
        renderer.updateClasses(layer, 8)
        layer.setRenderer(renderer)
