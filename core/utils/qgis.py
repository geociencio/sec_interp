"""QGIS-specific utilities for SecInterp.

This module centralizes interaction with the QGIS API to ensure consistent
behavior and reduce code duplication across the plugin.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qgis.core import QgsProject

if TYPE_CHECKING:
    from qgis.core import QgsMapLayer


def resolve_layer(layer_ref: Any) -> QgsMapLayer | None:
    """Resolve a layer reference (ID, name, or object) to a QgsMapLayer.

    This function is the single point of entry for layer resolution, ensuring
    that the layer is valid and retrieved from the current QgsProject instance.

    Args:
        layer_ref: A string (layer ID or name) or a QgsMapLayer object.

    Returns:
        The resolved QgsMapLayer object if valid, else None.

    """
    if layer_ref is None:
        return None

    # If it's already a layer object, just check if it's still valid
    if not isinstance(layer_ref, str):
        if hasattr(layer_ref, "isValid") and layer_ref.isValid():
            return layer_ref
        return None

    project = QgsProject.instance()

    # 1. Try resolving by ID (fastest)
    layer = project.mapLayer(str(layer_ref))
    if layer and layer.isValid():
        return layer

    # 2. Try resolving by Name (fallback)
    layers_by_name = project.mapLayersByName(str(layer_ref))
    if layers_by_name:
        for lyr in layers_by_name:
            if lyr.isValid():
                return lyr

    return None
