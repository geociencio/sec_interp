"""Measurement tool for Profile View.

This module provides the ProfileMeasureTool for measuring distances,
elevation differences, and slopes in the profile preview window.
It separates UI event handling from spatial snapping logic.
"""

import math
from typing import Optional, Dict, Set

from qgis.core import (
    QgsPointXY,
    QgsWkbTypes,
    QgsPointLocator,
    QgsProject,
    QgsMapLayer,
    QgsVectorLayer
)
from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand, QgsMapCanvas
from qgis.PyQt.QtCore import Qt, pyqtSignal, QPoint
from qgis.PyQt.QtGui import QColor

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class ProfileSnapper:
    """Helper class to handle point snapping functionality."""

    def __init__(self, canvas: QgsMapCanvas):
        self.canvas = canvas
        self._locators: Dict[str, QgsPointLocator] = {}

    def snap(self, mouse_pos: QPoint) -> QgsPointXY:
        """Finds the nearest vertex or edge to the mouse position."""
        point = self.canvas.getCoordinateTransform().toMapCoordinates(mouse_pos)

        # Search tolerance in map units (approx 12 pixels)
        tolerance = (self.canvas.mapUnitsPerPixel() or 1.0) * 12

        best_match = None
        best_dist = float("inf")

        layers = self.canvas.layers()
        current_layer_ids = {layer.id() for layer in layers if layer is not None}

        # Clean obsolete locators
        self._cleanup_locators(current_layer_ids)

        crs = self.canvas.mapSettings().destinationCrs()
        context = QgsProject.instance().transformContext()

        for layer in layers:
            if not self._is_snappable(layer):
                continue

            locator = self._get_locator(layer, crs, context)
            if not locator:
                continue

            # Try vertex snap
            v_match = locator.nearestVertex(point, tolerance)
            if v_match.isValid() and v_match.distance() < best_dist:
                best_match = v_match
                best_dist = v_match.distance()

            # Try edge snap
            e_match = locator.nearestEdge(point, tolerance)
            if e_match.isValid() and e_match.distance() < best_dist:
                best_match = e_match
                best_dist = e_match.distance()

        if best_match:
            return best_match.point()

        return point

    def _cleanup_locators(self, current_ids: Set[str]):
        """Removes locators for layers that are no longer active."""
        hits_to_remove = [lid for lid in self._locators if lid not in current_ids]
        for lid in hits_to_remove:
            del self._locators[lid]

    def _is_snappable(self, layer: QgsMapLayer) -> bool:
        """Checks if a layer is valid for snapping."""
        return bool(layer and layer.type() == QgsMapLayer.VectorLayer)

    def _get_locator(
        self, layer: QgsVectorLayer, crs, context
    ) -> Optional[QgsPointLocator]:
        """Retrieves or creates a locator for a layer."""
        if layer.id() not in self._locators:
            try:
                self._locators[layer.id()] = QgsPointLocator(layer, crs, context)
            except Exception as e:
                logger.warning(
                    f"Failed to create locator for layer {layer.name()}: {e}"
                )
                return None
        return self._locators[layer.id()]


class ProfileMeasureTool(QgsMapToolEmitPoint):
    """Map tool for measuring distances in profile view."""

    # args: (dx, dy, total_dist, slope_degrees)
    measurementChanged = pyqtSignal(float, float, float, float)
    measurementCleared = pyqtSignal()

    def __init__(self, canvas: QgsMapCanvas):
        super().__init__(canvas)
        self.canvas = canvas
        self.start_point: Optional[QgsPointXY] = None
        self.end_point: Optional[QgsPointXY] = None

        self.rubber_band: Optional[QgsRubberBand] = None
        self.cursor = Qt.CrossCursor

        # Delegate snapping logic
        self.snapper = ProfileSnapper(canvas)

    def activate(self):
        super().activate()
        self.canvas.setCursor(self.cursor)
        logger.debug("ProfileMeasureTool activated")

    def deactivate(self):
        self.reset()
        super().deactivate()
        logger.debug("ProfileMeasureTool deactivated")

    def reset(self):
        """Resets the tool state."""
        self.start_point = None
        self.end_point = None
        if self.rubber_band:
            self.canvas.scene().removeItem(self.rubber_band)
            self.rubber_band = None
        self.measurementCleared.emit()

    def canvasReleaseEvent(self, event):
        """Handle mouse click release."""
        if event.button() == Qt.RightButton:
            self.reset()
            return

        snapped_point = self.snapper.snap(event.pos())

        if self.start_point is None:
            self._handle_first_point(snapped_point)
        elif self.end_point is None:
            self._handle_second_point(snapped_point)
        else:
            # Third click resets and starts over
            self.reset()
            self._handle_first_point(snapped_point)

    def canvasMoveEvent(self, event):
        """Handle mouse move for rubber band update."""
        if self.start_point and self.end_point is None:
            current_point = self.snapper.snap(event.pos())
            self._update_rubber_band(current_point)
            self._calculate_and_emit(current_point)

    def _handle_first_point(self, point: QgsPointXY):
        self.start_point = point
        self._ensure_rubber_band()
        self.rubber_band.addPoint(point, True)
        logger.debug(f"Start point set: {point.x()}, {point.y()}")

    def _handle_second_point(self, point: QgsPointXY):
        self.end_point = point
        self.rubber_band.addPoint(point, True)
        self._calculate_and_emit(point)
        logger.debug(f"End point set: {point.x()}, {point.y()}")

    def _ensure_rubber_band(self):
        """Creates rubber band if not exists."""
        if self.rubber_band:
            return

        self.rubber_band = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
        self.rubber_band.setColor(QColor(255, 0, 0))
        self.rubber_band.setWidth(2)

    def _update_rubber_band(self, current_point: QgsPointXY):
        """Updates the rubber band geometry dynamically."""
        if not self.rubber_band:
            return

        self.rubber_band.reset(QgsWkbTypes.LineGeometry)
        self.rubber_band.addPoint(self.start_point, False)
        self.rubber_band.addPoint(current_point, True)

    def _calculate_and_emit(self, target_point: QgsPointXY):
        """Calculates measurement stats and emits signal."""
        if not self.start_point or not target_point:
            return

        dx = abs(target_point.x() - self.start_point.x())
        dy = target_point.y() - self.start_point.y()

        dist = math.sqrt(dx*dx + dy*dy)

        slope = 0.0
        if dx == 0:
            slope = 90.0 if dy != 0 else 0.0
        else:
            slope = math.degrees(math.atan(abs(dy) / dx))

        self.measurementChanged.emit(dx, dy, dist, slope)
