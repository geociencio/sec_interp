"""QGIS-specific utilities for SecInterp.

This module centralizes interaction with the QGIS API to ensure consistent
behavior and reduce code duplication across the plugin.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qgis.core import QgsProject

if TYPE_CHECKING:
    from qgis.core import QgsMapLayer


class LayerResolver:
    """Centralized service to resolve and cache QgsMapLayer references.

    Acts as a singleton/cache to avoid repeated `project.mapLayer()` calls
    within the same processing transaction.
    """

    _cache: dict[str, QgsMapLayer] = {}

    @classmethod
    def resolve(cls, layer_ref: Any, use_cache: bool = True) -> QgsMapLayer | None:
        """Resolve a layer reference (ID, name, or object) to a QgsMapLayer.

        Args:
            layer_ref: A string (layer ID or name) or a QgsMapLayer object.
            use_cache: If True, uses the internal dict cache for faster lookups.

        Returns:
            The resolved QgsMapLayer object if valid, else None.

        """
        if layer_ref is None:
            return None

        # 0. Check if it's already a valid QgsMapLayer
        if not isinstance(layer_ref, str):
            if hasattr(layer_ref, "isValid") and layer_ref.isValid():
                return layer_ref
            return None

        ref_str = str(layer_ref)

        # 1. Check cache first
        cached_layer = cls._resolve_from_cache(ref_str, use_cache)
        if cached_layer:
            return cached_layer

        project = QgsProject.instance()

        # 2. Try resolving by ID
        layer = cls._resolve_by_id(project, ref_str)
        if layer:
            return layer

        # 3. Try resolving by Name (fallback)
        return cls._resolve_by_name(project, ref_str)

    @classmethod
    def _resolve_from_cache(cls, ref_str: str, use_cache: bool) -> QgsMapLayer | None:
        if use_cache and ref_str in cls._cache:
            cached_layer = cls._cache[ref_str]
            if cached_layer and cached_layer.isValid():
                return cached_layer
            # Invalidate broken cache
            del cls._cache[ref_str]
        return None

    @classmethod
    def _resolve_by_id(cls, project: Any, ref_str: str) -> QgsMapLayer | None:
        layer = project.mapLayer(ref_str)
        if layer and layer.isValid():
            cls._cache[ref_str] = layer
            # Also cache by name if possible
            cls._cache[layer.name()] = layer
            return layer
        return None

    @classmethod
    def _resolve_by_name(cls, project: Any, ref_str: str) -> QgsMapLayer | None:
        layers_by_name = project.mapLayersByName(ref_str)
        if layers_by_name:
            for lyr in layers_by_name:
                if lyr.isValid():
                    cls._cache[ref_str] = lyr
                    cls._cache[lyr.id()] = lyr
                    return lyr
        return None

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the internal layer cache."""
        cls._cache.clear()

    @classmethod
    def invalidate(cls, layer_id: str) -> None:
        """Remove a specific layer from the cache."""
        if layer_id in cls._cache:
            del cls._cache[layer_id]


def resolve_layer(layer_ref: Any) -> QgsMapLayer | None:
    """Resolve a layer reference. (Legacy wrapper).

    Delegates to LayerResolver for backward compatibility.
    """
    return LayerResolver.resolve(layer_ref)
