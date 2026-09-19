"""Renderer for geological segments."""

from __future__ import annotations

from qgis.core import QgsVectorLayer

from sec_interp.gui.renderers.base_renderer import (
    BasePreviewRenderer,
    build_categorized_line_style,
)
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
        layer.setRenderer(build_categorized_line_style(self.color_manager, unique_units))
