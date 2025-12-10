"""Measurement tool for Profile View.

Provides a map tool to measure distances, elevation differences, and slopes
in the profile preview window.
"""

import math
from typing import Optional

from qgis.core import QgsPointXY
from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class ProfileMeasureTool(QgsMapToolEmitPoint):
    """Map tool for measuring distances in profile view."""

    # Signal emitted when measurement changes
    # args: (dx, dy, total_dist, slope_degrees)
    measurementChanged = pyqtSignal(float, float, float, float)
    
    # Signal emitted when measurement is reset
    measurementCleared = pyqtSignal()

    def __init__(self, canvas):
        """Initialize tool.

        Args:
            canvas: QgsMapCanvas instance
        """
        super().__init__(canvas)
        self.canvas = canvas
        self.start_point: Optional[QgsPointXY] = None
        self.end_point: Optional[QgsPointXY] = None
        self.rubber_band: Optional[QgsRubberBand] = None
        
        self.cursor = Qt.CrossCursor

    def activate(self):
        """Called when tool is activated."""
        super().activate()
        self.canvas.setCursor(self.cursor)
        logger.debug("ProfileMeasureTool activated")

    def deactivate(self):
        """Called when tool is deactivated."""
        self.reset()
        super().deactivate()
        logger.debug("ProfileMeasureTool deactivated")

    def reset(self):
        """Reset measurement state."""
        self.start_point = None
        self.end_point = None
        if self.rubber_band:
            self.canvas.scene().removeItem(self.rubber_band)
            self.rubber_band = None
        self.measurementCleared.emit()

    def canvasReleaseEvent(self, event):
        """Handle mouse click release."""
        # Get point in map coordinates
        point = self.toMapCoordinates(event.pos())
        
        if event.button() == Qt.RightButton:
            # Right click resets
            self.reset()
            return

        if self.start_point is None:
            # First point
            self.start_point = point
            self._create_rubber_band()
            self.rubber_band.addPoint(point, True)
            logger.debug(f"Start point set: {point.x()}, {point.y()}")
        elif self.end_point is None:
            # Second point - finish measurement
            self.end_point = point
            self.rubber_band.addPoint(point, True)
            self._calculate_measurement()
            logger.debug(f"End point set: {point.x()}, {point.y()}")
        else:
            # Third click - restart
            self.reset()
            self.start_point = point
            self._create_rubber_band()
            self.rubber_band.addPoint(point, True)

    def canvasMoveEvent(self, event):
        """Handle mouse move for rubber band update."""
        if self.start_point and self.end_point is None:
            point = self.toMapCoordinates(event.pos())
            
            # Update rubber band geometry
            if self.rubber_band:
                # Reset to start point only
                self.rubber_band.reset(True) # True = LineGeometry
                self.rubber_band.addPoint(self.start_point, False)
                self.rubber_band.addPoint(point, True)
            
            # Update provisional measurement
            self._calculate_measurement(temp_end=point)

    def _create_rubber_band(self):
        """Initialize rubber band for visualization."""
        if self.rubber_band:
            self.canvas.scene().removeItem(self.rubber_band)
        
        self.rubber_band = QgsRubberBand(self.canvas, True)  # True = Line
        self.rubber_band.setColor(QColor(255, 0, 0))
        self.rubber_band.setWidth(2)

    def _calculate_measurement(self, temp_end=None):
        """Calculate stats between start_point and end_point (or temp_end)."""
        p1 = self.start_point
        p2 = self.end_point if self.end_point else temp_end
        
        if not p1 or not p2:
            return

        dx = abs(p2.x() - p1.x())
        dy = p2.y() - p1.y() # Keep sign for up/down
        
        dist = math.sqrt(dx*dx + dy*dy)
        
        # Calculate slope (degrees)
        # Avoid division by zero
        if dx == 0:
            slope = 90.0 if dy != 0 else 0.0
        else:
            slope = math.degrees(math.atan(abs(dy) / dx))

        self.measurementChanged.emit(dx, dy, dist, slope)
