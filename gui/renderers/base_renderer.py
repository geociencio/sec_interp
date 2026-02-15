"""Base class for preview renderers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from qgis.core import QgsVectorLayer


class BasePreviewRenderer(ABC):
    """Base class for all preview layer renderers."""

    @abstractmethod
    def apply_style(self, layer: QgsVectorLayer, **kwargs) -> None:
        """Apply symbology and settings to the given layer."""
        pass
