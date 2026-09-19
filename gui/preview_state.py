"""Shared preview state objects for SecInterp dialog managers."""

from __future__ import annotations

from typing import Any

_CACHE_KEYS = ("topo", "geol", "struct", "drillhole")


class PreviewCache:
    """Shared mutable cache of generated preview data.

    Owned by the dialog and shared between PreviewManager and
    InterpretationManager so that neither manager reaches into the other.
    """

    def __init__(self) -> None:
        """Initialize an empty cache with the standard preview keys."""
        self._data: dict[str, Any] = dict.fromkeys(_CACHE_KEYS)

    def get(self, key: str, default: Any = None) -> Any:
        """Return the cached value for ``key``, or ``default``."""
        return self._data.get(key, default)

    def update(self, other: dict[str, Any] | None = None, **kwargs: Any) -> None:
        """Update the cache from a mapping and/or keyword arguments."""
        if other:
            self._data.update(other)
        if kwargs:
            self._data.update(kwargs)

    def __getitem__(self, key: str) -> Any:
        """Return the cached value for ``key``."""
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Store ``value`` in the cache under ``key``."""
        self._data[key] = value


class RenderState:
    """Shared holder for the current preview render output.

    Owned by the dialog, written by the plugin's draw_preview and read by
    ExportManager so the export path no longer depends on loose dialog
    attributes (``current_canvas``/``current_layers``).
    """

    def __init__(self) -> None:
        """Initialize an empty render state."""
        self.canvas: Any = None
        self.layers: list = []

    def update(self, canvas: Any, layers: list) -> None:
        """Store the latest render output."""
        self.canvas = canvas
        self.layers = layers
