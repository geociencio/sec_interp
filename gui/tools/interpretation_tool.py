"""Interpretation tool for Profile View.

This module provides the ProfileInterpretationTool for drawing 
interpretation polygons in the profile preview window.
"""

from __future__ import annotations

import datetime
import uuid
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
    QgsRubberBand,
    QgsVertexMarker,
)
from qgis.PyQt.QtCore import QPoint, Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor

from sec_interp.core.types import InterpretationPolygon
from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


class ProfileSnapper:
    """Helper class to handle point snapping functionality.

    Duplicates logic from ProfileMeasureTool to avoid tight coupling.
    """

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
        self._cleanup_locators(current_layer_ids)

        crs = self.canvas.mapSettings().destinationCrs()
        context = QgsProject.instance().transformContext()

        for layer in layers:
            if not self._is_snappable(layer):
                continue

            try:
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
            except Exception:
                # If layer was deleted or something went wrong with locator
                continue

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


class ProfileInterpretationTool(QgsMapToolEmitPoint):
    """Tool for drawing interpretation polygons on the profile canvas.

    - Left Click: Add vertex
    - Move: Update preview rubber band
    - Right Click: Remove last vertex
    - Enter/Double Click: Finalize polygon
    - Escape: Cancel
    """

    polygonFinished = pyqtSignal(InterpretationPolygon)

    def __init__(self, canvas: QgsMapCanvas):
        super().__init__(canvas)
        self.canvas = canvas
        self.points: list[QgsPointXY] = []
        self.rubber_band: Optional[QgsRubberBand] = None
        self.vertex_markers: list[QgsVertexMarker] = []
        self.snapper = ProfileSnapper(canvas)
        self.cursor = Qt.CrossCursor

    def activate(self):
        super().activate()
        self.canvas.setCursor(self.cursor)
        logger.debug("ProfileInterpretationTool activated")

    def deactivate(self):
        """Cleanup when tool is deactivated."""
        self.reset()
        super().deactivate()
        logger.debug("ProfileInterpretationTool deactivated")

    def reset(self):
        """Resets the tool state safely."""
        self.points = []
        
        # Rubber band cleanup
        if self.rubber_band:
            try:
                self.rubber_band.reset(QgsWkbTypes.PolygonGeometry)
                self.canvas.scene().removeItem(self.rubber_band)
            except Exception:
                pass
            self.rubber_band = None
            
        # Markers cleanup
        for marker in self.vertex_markers:
            try:
                self.canvas.scene().removeItem(marker)
            except Exception:
                pass
        self.vertex_markers = []
        
        self.is_drawing = False
        if self.canvas:
            self.canvas.refresh()

    def canvasReleaseEvent(self, event):
        """Handle mouse click release."""
        if event.button() == Qt.RightButton:
            if self.points:
                self._remove_last_point()
            return

        snapped_point = self.snapper.snap(event.pos())
        self._add_point(snapped_point)

    def canvasMoveEvent(self, event):
        """Handle mouse move for rubber band update."""
        if not self.points:
            return
        current_point = self.snapper.snap(event.pos())
        self._update_rubber_band(current_point)

    def canvasDoubleClickEvent(self, event):
        """Finalize polygon on double click."""
        if len(self.points) >= 3:
            self.finalize_polygon()

    def keyPressEvent(self, event):
        """Handle keyboard events."""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if len(self.points) >= 3:
                self.finalize_polygon()
                event.accept()
            return
        if event.key() == Qt.Key_Escape:
            self.reset()
            event.accept()
            return
        super().keyPressEvent(event)

    def _add_point(self, point: QgsPointXY):
        """Add a vertex to the current polygon."""
        self.points.append(point)
        self._ensure_rubber_band()
        self.rubber_band.addPoint(point, True)
        self._add_vertex_marker(point)

    def _remove_last_point(self):
        """Remove the last added vertex."""
        if not self.points:
            return
        self.points.pop()
        if self.vertex_markers:
            marker = self.vertex_markers.pop()
            self.canvas.scene().removeItem(marker)

        if not self.points:
            if self.rubber_band:
                self.canvas.scene().removeItem(self.rubber_band)
                self.rubber_band = None
        else:
            self.rubber_band.reset(QgsWkbTypes.PolygonGeometry)
            for p in self.points:
                self.rubber_band.addPoint(p, False)

    def _add_vertex_marker(self, point: QgsPointXY):
        """Add a visual marker for a vertex."""
        marker = QgsVertexMarker(self.canvas)
        marker.setCenter(point)
        marker.setColor(QColor(255, 165, 0))  # Orange
        marker.setIconSize(10)
        marker.setIconType(QgsVertexMarker.ICON_X)
        marker.setPenWidth(2)
        self.vertex_markers.append(marker)

    def _ensure_rubber_band(self):
        """Ensure the rubber band exists."""
        if self.rubber_band:
            return
        self.rubber_band = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        color = QColor(255, 0, 0, 100)  # Semi-transparent red
        self.rubber_band.setColor(color)
        self.rubber_band.setFillColor(color)
        self.rubber_band.setWidth(2)

    def _update_rubber_band(self, current_point: QgsPointXY):
        """Update rubber band geometry."""
        if not self.rubber_band or not self.points:
            return
        self.rubber_band.reset(QgsWkbTypes.PolygonGeometry)
        for p in self.points:
            self.rubber_band.addPoint(p, False)
        self.rubber_band.addPoint(current_point, True)

    def finalize_polygon(self):
        """Finalize the polygon and emit signal."""
        if len(self.points) < 3:
            return

        # Capture the points as (dist, elev) which are (x, y) in profile units
        vertices_2d = [(p.x(), p.y()) for p in self.points]

        interp = InterpretationPolygon(
            id=str(uuid.uuid4()),
            name="New Interpretation",
            type="lithology",
            vertices_2d=vertices_2d,
            attributes={},
            color="#FF0000",
            created_at=datetime.datetime.now().isoformat(),
        )

        self.polygonFinished.emit(interp)
        # Note: Do NOT call reset() here. 
        # The dialog handler should deactivate the tool, which calls reset() cleanly.
        logger.info(
            f"Interpretation polygon finalized with {len(vertices_2d)} vertices"
        )
