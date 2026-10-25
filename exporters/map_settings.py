"""Factory for QgsMapSettings — isolates QGIS import to one module."""

from __future__ import annotations

from typing import Any

from qgis.core import QgsMapSettings, QgsRectangle


def create_map_settings(
    layers: list[Any],
    extent: QgsRectangle,
    size: Any | None,
    background_color: Any,
) -> QgsMapSettings:
    """Create and configure QgsMapSettings for export rendering.

    Args:
        layers: List of map layers to be rendered.
        extent: Spatial extent of the view.
        size: Optional output size in pixels (QSize).
        background_color: Background color (QColor).

    Returns:
        Configured QgsMapSettings instance.

    """
    map_settings = QgsMapSettings()
    map_settings.setLayers(layers)
    map_settings.setExtent(extent)
    if size is not None:
        map_settings.setOutputSize(size)
    map_settings.setBackgroundColor(background_color)
    return map_settings
