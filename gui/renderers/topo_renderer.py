"""Renderer for topographic profile elevation polychromy."""

from __future__ import annotations

from qgis.core import (
    QgsClassificationFixedInterval,
    QgsGraduatedSymbolRenderer,
    QgsLineSymbol,
    QgsSingleSymbolRenderer,
    QgsStyle,
    QgsVectorLayer,
)
from qgis.PyQt.QtGui import QColor

from sec_interp.gui.renderers.base_renderer import BasePreviewRenderer

DEFAULT_RAMPS = ("Spectral", "RdYlGn")
LINE_STYLE = {"width": "0.8", "capstyle": "round"}


class TopoRenderer(BasePreviewRenderer):
    """Renderer for topographic profile layers."""

    def apply_style(self, layer: QgsVectorLayer, **kwargs) -> None:
        """Apply the selected topographic profile style.

        Args:
            layer: The preview topography memory layer.
            **kwargs: Style options: ``color_mode`` (``"gradient"`` or
                ``"single"``), ``ramp_name`` and ``single_color``.

        """
        width = str(kwargs.get("line_width") or LINE_STYLE["width"])
        if kwargs.get("color_mode") == "single":
            self._apply_single_color(layer, kwargs.get("single_color"), width)
            return
        self._apply_gradient(layer, kwargs.get("ramp_name"), width)

    def _apply_gradient(self, layer: QgsVectorLayer, ramp_name: str | None, width: str) -> None:
        """Apply graduated elevation styling, falling back to a known ramp."""
        renderer = QgsGraduatedSymbolRenderer("elev")
        renderer.setSourceSymbol(QgsLineSymbol.createSimple({**LINE_STYLE, "width": width}))

        ramp = self._resolve_ramp(ramp_name)
        if ramp is not None:
            renderer.updateColorRamp(ramp)

        renderer.setClassificationMethod(QgsClassificationFixedInterval())
        renderer.updateClasses(layer, 8)
        layer.setRenderer(renderer)

    def _apply_single_color(
        self, layer: QgsVectorLayer, single_color: str | None, width: str
    ) -> None:
        """Apply a single-color line style."""
        symbol = QgsLineSymbol.createSimple({**LINE_STYLE, "width": width})
        color = QColor(single_color) if single_color else QColor()
        if color.isValid():
            symbol.setColor(color)
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))

    @staticmethod
    def _resolve_ramp(ramp_name: str | None):
        """Return the requested ramp, or a default fallback, or None."""
        style = QgsStyle.defaultStyle()
        candidates = ([ramp_name] if ramp_name else []) + list(DEFAULT_RAMPS)
        for name in candidates:
            try:
                ramp = style.colorRamp(name)
            except (AttributeError, KeyError, RuntimeError, TypeError):
                ramp = None
            if ramp is not None:
                return ramp
        return None
