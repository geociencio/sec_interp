"""Measurement tool for Profile View.

This module provides the ProfileMeasureTool for measuring distances,
elevation differences, and slopes in the profile preview window.
It separates UI event handling from spatial snapping logic.
"""

from __future__ import annotations

import math
import time
from typing import Optional

from qgis.core import (
    QgsMapLayer,
    QgsPointLocator,
    QgsPointXY,
    QgsProject,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.gui import (
    QgsMapCanvas,
    QgsMapToolEmitPoint,
    QgsMapToolPan,
    QgsRubberBand,
    QgsVertexMarker,
)
from qgis.PyQt.QtCore import QPoint, Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor

from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


class ProfileSnapper:
    """Helper class to handle point snapping functionality."""

    def __init__(self, canvas: QgsMapCanvas):
        self.canvas = canvas
        self._locators: dict[str, QgsPointLocator] = {}

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

    def _cleanup_locators(self, current_ids: set[str]):
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
    """Map tool for measuring distances in profile view.

    Supports multi-point polyline measurements:
    - Click to add points along the trace
    - Click "Finalizar" button in UI to complete measurement
    - Right-click or Escape to cancel and reset
    """

    # args: dict with measurement metrics
    measurementChanged = pyqtSignal(dict)
    measurementCleared = pyqtSignal()

    def __init__(self, canvas: QgsMapCanvas):
        super().__init__(canvas)
        self.canvas = canvas
        self.points: list[QgsPointXY] = []
        self.finalized: bool = False  # Track if measurement is finalized
        self.finalized_points: list[QgsPointXY] = []  # Store final points

        self.rubber_band: QgsRubberBand | None = None
        self.vertex_markers: list[QgsVertexMarker] = []
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
        """Resets the tool state.

        If measurement is finalized, only clears the points data but keeps
        the visual elements (rubber band and markers) visible.
        """
        logger.info(f"reset() called, finalized={self.finalized}")

        # If finalized, only clear the data, keep visuals AND results text
        if self.finalized:
            logger.info(
                "Measurement is finalized - keeping visuals and results, clearing data only"
            )
            self.points = []
            self.finalized = False
            # Don't clear finalized_points yet - they're needed for display
            # Don't clear rubber_band, vertex_markers, or emit measurementCleared
            # This keeps everything visible!
            return

        # Normal reset - clear everything
        self.points = []
        self.finalized = False
        self.finalized_points = []

        if self.rubber_band:
            self.canvas.scene().removeItem(self.rubber_band)
            self.rubber_band = None

        # Remove all vertex markers
        for marker in self.vertex_markers:
            self.canvas.scene().removeItem(marker)
        self.vertex_markers = []

        self.measurementCleared.emit()

    def canvasReleaseEvent(self, event):
        """Handle mouse click release.

        - Left click: Add point to measurement
        - Right click: Cancel and reset
        - Press Enter to finalize (see keyPressEvent)
        """
        if event.button() == Qt.RightButton:
            self.reset()
            return

        # Don't add points if measurement is finalized
        if self.finalized:
            logger.info("Ignoring click - measurement is finalized")
            return

        snapped_point = self.snapper.snap(event.pos())

        # Simply add point to the polyline
        self._add_point(snapped_point)

    def canvasMoveEvent(self, event):
        """Handle mouse move for rubber band update."""
        # Don't update rubber band if measurement is finalized
        if self.finalized:
            return

        if len(self.points) > 0:
            current_point = self.snapper.snap(event.pos())
            self._update_rubber_band(current_point)
            self._calculate_and_emit_preview(current_point)

    def keyPressEvent(self, event):
        """Handle keyboard events.

        - Enter/Return: Finalize measurement
        - Escape: Cancel measurement
        """
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if len(self.points) >= 2:
                self.finalize_measurement()
                event.accept()
            return

        if event.key() == Qt.Key_Escape:
            self.reset()
            event.accept()
            return

        # Let parent handle other keys
        super().keyPressEvent(event)

    def _add_point(self, point: QgsPointXY):
        """Add a point to the measurement polyline."""
        self.points.append(point)
        self._ensure_rubber_band()
        self.rubber_band.addPoint(point, True)
        self._add_vertex_marker(point)

        logger.debug(
            f"Point {len(self.points)} added: {point.x():.2f}, {point.y():.2f}"
        )

        # Emit measurement update if we have at least 2 points
        if len(self.points) >= 2:
            metrics = self._calculate_metrics()
            self.measurementChanged.emit(metrics)

    def finalize_measurement(self):
        """Finalize the measurement and emit final metrics.

        This is a public method that can be called from UI buttons.
        After finalizing, the tool is deactivated but results remain visible.
        """
        logger.info(f"finalize_measurement called with {len(self.points)} points")

        if len(self.points) < 2:
            logger.warning("Cannot finalize measurement with less than 2 points")
            return

        # Mark as finalized to prevent adding more points
        # Save a copy of the points before clearing
        self.finalized_points = self.points.copy()
        self.finalized = True
        logger.info("Setting finalized = True")

        metrics = self._calculate_metrics()
        self.measurementChanged.emit(metrics)

        logger.info(
            f"Measurement finalized: {len(self.points)} points, "
            f"{metrics['total_distance']:.2f}m total distance"
        )

        # Redraw rubber band with ONLY the final points (no temporary line)
        if self.rubber_band:
            self.rubber_band.reset(QgsWkbTypes.LineGeometry)
            for point in self.finalized_points:
                self.rubber_band.addPoint(point, False)
            self.rubber_band.show()
            logger.info("Rubber band redrawn with final points only")

        # Switch back to pan tool (this preserves the measurement)
        # The main dialog will handle unchecking the measure button
        logger.info("Switching to pan tool to stop measurement")
        pan_tool = QgsMapToolPan(self.canvas)
        self.canvas.setMapTool(pan_tool)
        logger.info("Pan tool activated - measurement should be frozen")

    def _add_vertex_marker(self, point: QgsPointXY):
        """Add a visual marker at the point location."""
        marker = QgsVertexMarker(self.canvas)
        marker.setCenter(point)
        marker.setColor(QColor(0, 255, 0))  # Green for intermediate points
        marker.setIconSize(8)
        marker.setIconType(QgsVertexMarker.ICON_CIRCLE)
        marker.setPenWidth(2)
        self.vertex_markers.append(marker)

    def _ensure_rubber_band(self):
        """Creates rubber band if not exists."""
        if self.rubber_band:
            return

        self.rubber_band = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
        self.rubber_band.setColor(QColor(255, 0, 0))
        self.rubber_band.setWidth(2)

    def _update_rubber_band(self, current_point: QgsPointXY):
        """Updates the rubber band geometry dynamically."""
        if not self.rubber_band or len(self.points) == 0:
            return

        self.rubber_band.reset(QgsWkbTypes.LineGeometry)

        # Add all existing points
        for point in self.points:
            self.rubber_band.addPoint(point, False)

        # Add temporary line to current cursor position
        self.rubber_band.addPoint(current_point, True)

    def _calculate_and_emit_preview(self, target_point: QgsPointXY):
        """Calculate and emit preview metrics while moving cursor."""
        if len(self.points) == 0:
            return

        # Create temporary points list including cursor position
        temp_points = [*self.points, target_point]
        metrics = self._calculate_metrics_from_points(temp_points)
        self.measurementChanged.emit(metrics)

    def _calculate_metrics(self) -> dict:
        """Calculate final metrics from current points."""
        return self._calculate_metrics_from_points(self.points)

    def _calculate_metrics_from_points(self, points: list[QgsPointXY]) -> dict:
        """Calculate comprehensive measurement metrics from a list of points.

        Args:
            points: List of QgsPointXY points defining the polyline

        Returns:
            Dictionary containing:
                - total_distance: Accumulated distance along all segments
                - horizontal_distance: Total horizontal distance
                - elevation_change: Total elevation change (first to last point)
                - avg_slope: Average slope in degrees
                - segment_count: Number of segments
                - segments: List of segment details
                - point_count: Number of points
        """
        if len(points) < 2:
            return {
                "total_distance": 0.0,
                "horizontal_distance": 0.0,
                "elevation_change": 0.0,
                "avg_slope": 0.0,
                "segment_count": 0,
                "segments": [],
                "point_count": len(points),
            }

        total_dist = 0.0
        total_dx = 0.0
        segments = []

        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]

            dx = abs(p2.x() - p1.x())
            dy = p2.y() - p1.y()
            seg_dist = math.sqrt(dx * dx + dy * dy)

            total_dist += seg_dist
            total_dx += dx

            segments.append(
                {
                    "distance": seg_dist,
                    "dx": dx,
                    "dy": dy,
                    "start": (p1.x(), p1.y()),
                    "end": (p2.x(), p2.y()),
                }
            )

        # Total elevation change (first to last point)
        elevation_change = points[-1].y() - points[0].y()

        # Average slope
        avg_slope = 0.0
        if total_dx > 0:
            avg_slope = math.degrees(math.atan(abs(elevation_change) / total_dx))

        return {
            "total_distance": total_dist,
            "horizontal_distance": total_dx,
            "elevation_change": elevation_change,
            "avg_slope": avg_slope,
            "segment_count": len(segments),
            "segments": segments,
            "point_count": len(points),
        }
