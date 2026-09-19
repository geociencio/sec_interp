"""Measurement tool for Profile View.

This module provides the ProfileMeasureTool for measuring distances,
elevation differences, and slopes in the profile preview window.
It separates UI event handling from spatial snapping logic.
"""

from __future__ import annotations

import contextlib
from typing import Any

from qgis.core import (
    QgsPointXY,
    QgsWkbTypes,
)
from qgis.gui import (
    QgsMapCanvas,
    QgsMapToolEmitPoint,
    QgsMapToolPan,
    QgsRubberBand,
    QgsVertexMarker,
)
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor

from sec_interp.core.utils.geometry_utils.measurement import calculate_polyline_metrics
from sec_interp.gui.tools.snapper import ProfileSnapper
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class ProfileMeasureTool(QgsMapToolEmitPoint):
    """Map tool for measuring distances in profile view.

    Supports multi-point polyline measurements:
    - Click to add points along the trace
    - Click "Finalizar" button in UI to complete measurement
    - Right-click or Escape to cancel and reset
    """

    # signals use dict with measurement metrics
    measurementChanged = pyqtSignal(dict)
    measurementCleared = pyqtSignal()
    measurementFinished = pyqtSignal()

    def __init__(self, canvas: QgsMapCanvas) -> None:
        """Initialize the profile measurement tool.

        Args:
            canvas: The map canvas where measurement is performed.

        """
        super().__init__(canvas)
        self.canvas = canvas
        self.points: list[QgsPointXY] = []
        self.finalized: bool = False  # Track if measurement is finalized
        self.finalized_points: list[QgsPointXY] = []  # Store final points

        self.rubber_band: QgsRubberBand | None = None
        self.vertex_markers: list[QgsVertexMarker] = []
        self.cursor = Qt.CursorShape.CrossCursor

        # Delegate snapping logic
        self.snapper = ProfileSnapper(canvas)

    def activate(self) -> None:
        """Activate the measurement tool."""
        super().activate()
        self.canvas.setCursor(self.cursor)
        logger.debug("ProfileMeasureTool activated")

    def deactivate(self) -> None:
        """Deactivate the measurement tool.

        Note: We no longer call reset() here to allow measurements to persist
        visually until a new one is started or explicitly cleared.
        """
        super().deactivate()
        logger.debug("ProfileMeasureTool deactivated")

    def disconnect_signals(self) -> None:
        """Disconnect signals to prevent memory leaks."""
        try:
            self.measurementChanged.disconnect()
            self.measurementCleared.disconnect()
            self.measurementFinished.disconnect()
        except TypeError:
            pass

    def cleanup_finalized(self) -> None:
        """Clean up finalized measurement elements.

        Call this when dialog is closing to ensure no orphaned graphics.
        """
        logger.debug("Cleaning up finalized measurement elements")

        if self.rubber_band:
            with contextlib.suppress(Exception):
                self.rubber_band.hide()
                if self.canvas.scene():
                    self.canvas.scene().removeItem(self.rubber_band)
                logger.debug("Removed rubber band from scene")
            self.rubber_band = None

        for marker in self.vertex_markers:
            with contextlib.suppress(Exception):
                marker.hide()
                if self.canvas.scene():
                    self.canvas.scene().removeItem(marker)

        self.vertex_markers = []
        self.finalized_points = []
        self.finalized = False
        self.points = []

        logger.debug("Finalized measurement cleanup completed")

    def reset(self) -> None:
        """Reset the tool state.

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
            with contextlib.suppress(Exception):
                self.canvas.scene().removeItem(self.rubber_band)
            self.rubber_band = None

        # Remove all vertex markers
        for marker in self.vertex_markers:
            with contextlib.suppress(Exception):
                self.canvas.scene().removeItem(marker)
        self.vertex_markers = []

        self.measurementCleared.emit()

    def canvasReleaseEvent(self, event: Any) -> None:
        """Handle mouse click release.

        - Left click: Add point to measurement
        - Right click: Cancel and reset
        - Press Enter to finalize (see keyPressEvent)

        Args:
            event: Map tool event from QGIS

        """
        if event.button() == Qt.MouseButton.RightButton:
            self.reset()
            return

        # Don't add points if measurement is finalized
        if self.finalized:
            logger.info("Ignoring click - measurement is finalized")
            return

        snapped_point = self.snapper.snap(event.pos())

        # Simply add point to the polyline
        self._add_point(snapped_point)

    def canvasMoveEvent(self, event: Any) -> None:
        """Handle mouse move for rubber band update.

        Args:
            event: Map tool event from QGIS

        """
        # Don't update rubber band if measurement is finalized
        if self.finalized:
            return

        if len(self.points) > 0:
            current_point = self.snapper.snap(event.pos())
            self._update_rubber_band(current_point)
            self._calculate_and_emit_preview(current_point)

    def keyPressEvent(self, event: Any) -> None:
        """Handle keyboard events.

        - Enter/Return: Finalize measurement
        - Escape: Cancel measurement

        Args:
            event: Key event from QGIS

        """
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            MIN_MEASURE_POINTS = 2
            if len(self.points) >= MIN_MEASURE_POINTS:
                self.finalize_measurement()
                event.accept()
            return

        if event.key() == Qt.Key.Key_Escape:
            self.reset()
            event.accept()
            return

        # Let parent handle other keys
        super().keyPressEvent(event)

    def _add_point(self, point: QgsPointXY) -> None:
        """Add a point to the measurement polyline."""
        self.points.append(point)
        self._ensure_rubber_band()
        self.rubber_band.addPoint(point, True)
        self._add_vertex_marker(point)

        logger.debug(f"Point {len(self.points)} added: {point.x():.2f}, {point.y():.2f}")

        # Emit measurement update if we have at least 2 points
        MIN_RELEVANT_POINTS = 2
        if len(self.points) >= MIN_RELEVANT_POINTS:
            metrics = calculate_polyline_metrics(self.points)
            self.measurementChanged.emit(metrics)

    def finalize_measurement(self) -> None:
        """Finalize the measurement and emit final metrics.

        This is a public method that can be called from UI buttons.
        After finalizing, the tool is deactivated but results remain visible.
        """
        logger.info(f"finalize_measurement called with {len(self.points)} points")

        MIN_RELEVANT_POINTS = 2
        if len(self.points) < MIN_RELEVANT_POINTS:
            logger.warning("Cannot finalize measurement with less than 2 points")
            return

        # Mark as finalized to prevent adding more points
        # Save a copy of the points before clearing
        self.finalized_points = self.points.copy()
        self.finalized = True
        logger.info("Setting finalized = True")

        metrics = calculate_polyline_metrics(self.points)
        self.measurementChanged.emit(metrics)

        logger.info(
            f"Measurement finalized: {len(self.points)} points, "
            f"{metrics['total_distance']:.2f}m total distance"
        )

        # Redraw rubber band with ONLY the final points (no temporary line)
        if self.rubber_band:
            self.rubber_band.reset(QgsWkbTypes.GeometryType.LineGeometry)
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

        # Notify that measurement is officially finished
        self.measurementFinished.emit()

    def _add_vertex_marker(self, point: QgsPointXY) -> None:
        """Add a visual marker at the point location."""
        marker = QgsVertexMarker(self.canvas)
        marker.setCenter(point)
        marker.setColor(QColor(0, 255, 0))  # Green for intermediate points
        marker.setIconSize(8)
        marker.setIconType(QgsVertexMarker.IconType.ICON_CIRCLE)
        marker.setPenWidth(2)
        self.vertex_markers.append(marker)

    def _ensure_rubber_band(self) -> None:
        """Create rubber band if not exists."""
        if self.rubber_band:
            return

        self.rubber_band = QgsRubberBand(self.canvas, QgsWkbTypes.GeometryType.LineGeometry)
        self.rubber_band.setColor(QColor(255, 0, 0))
        self.rubber_band.setWidth(2)

    def _update_rubber_band(self, current_point: QgsPointXY) -> None:
        """Update the rubber band geometry dynamically."""
        if not self.rubber_band or len(self.points) == 0:
            return

        self.rubber_band.reset(QgsWkbTypes.GeometryType.LineGeometry)

        # Add all existing points
        for point in self.points:
            self.rubber_band.addPoint(point, False)

        # Add temporary line to current cursor position
        self.rubber_band.addPoint(current_point, True)

    def _calculate_and_emit_preview(self, target_point: QgsPointXY) -> None:
        """Calculate and emit preview metrics while moving cursor."""
        if len(self.points) == 0:
            return

        # Create temporary points list including cursor position
        temp_points = [*self.points, target_point]
        metrics = calculate_polyline_metrics(temp_points)
        self.measurementChanged.emit(metrics)
