"""Shared point snapping helper for profile view tools."""

from __future__ import annotations

from typing import Any

from qgis.core import (
    QgsMapLayer,
    QgsPointLocator,
    QgsPointXY,
    QgsProject,
    QgsVectorLayer,
)
from qgis.gui import QgsMapCanvas
from qgis.PyQt.QtCore import QPoint

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class ProfileSnapper:
    """Helper class to handle point snapping functionality."""

    def __init__(self, canvas: QgsMapCanvas) -> None:
        """Initialize the profile snapper.

        Args:
            canvas: The map canvas to snap on.

        """
        self.canvas = canvas
        self._locators: dict[str, QgsPointLocator] = {}

    def snap(self, mouse_pos: QPoint) -> QgsPointXY:
        """Find the nearest vertex or edge to the mouse position."""
        point = self.canvas.getCoordinateTransform().toMapCoordinates(mouse_pos)

        # Search tolerance in map units (approx 12 pixels)
        tolerance = (self.canvas.mapUnitsPerPixel() or 1.0) * 12

        best_match = None
        best_dist = float("inf")

        layers = self.canvas.layers()
        self._cleanup_locators({layer.id() for layer in layers if layer is not None})

        crs = self.canvas.mapSettings().destinationCrs()
        context = QgsProject.instance().transformContext()

        for layer in layers:
            if not self._is_snappable(layer):
                continue

            try:
                locator = self._get_locator(layer, crs, context)
                if locator:
                    best_match, best_dist = self._find_best_match_in_locator(
                        locator, point, tolerance, best_match, best_dist
                    )
            except Exception:  # nosec B112
                # If layer was deleted or something went wrong with locator
                continue

        if best_match:
            return best_match.point()

        return point

    def _find_best_match_in_locator(
        self,
        locator: QgsPointLocator,
        point: QgsPointXY,
        tolerance: float,
        current_best: Any,
        current_dist: float,
    ) -> tuple[Any, float]:
        """Find the best match (vertex or edge) in a given locator."""
        best_match = current_best
        best_dist = current_dist

        v_match = locator.nearestVertex(point, tolerance)
        if v_match.isValid() and v_match.distance() < best_dist:
            best_match = v_match
            best_dist = v_match.distance()

        e_match = locator.nearestEdge(point, tolerance)
        if e_match.isValid() and e_match.distance() < best_dist:
            best_match = e_match
            best_dist = e_match.distance()

        return best_match, best_dist

    def _cleanup_locators(self, current_ids: set[str]) -> None:
        """Remove locators for layers that are no longer active."""
        hits_to_remove = [lid for lid in self._locators if lid not in current_ids]
        for lid in hits_to_remove:
            del self._locators[lid]

    def _is_snappable(self, layer: QgsMapLayer) -> bool:
        """Check if a layer is valid for snapping."""
        return bool(layer and layer.type() == QgsMapLayer.LayerType.VectorLayer)

    def _get_locator(self, layer: QgsVectorLayer, crs, context) -> QgsPointLocator | None:
        """Retrieve or create a locator for a layer."""
        if layer.id() not in self._locators:
            try:
                self._locators[layer.id()] = QgsPointLocator(layer, crs, context)
            except Exception as e:
                logger.warning(f"Failed to create locator for layer {layer.name()}: {e}")
                return None
        return self._locators[layer.id()]
