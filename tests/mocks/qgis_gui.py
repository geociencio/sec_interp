"""QGIS GUI mocks."""

from unittest.mock import MagicMock
from .qt_mocks import mock_signal


class MockQgsMapCanvas(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene = MagicMock()
        self._layers = []
        self._map_settings = MagicMock()
        self._map_settings.mapUnitsPerPixel.return_value = 1.0
        self._map_settings.extent.return_value = MagicMock()
        self._map_settings.destinationCrs.return_value = MagicMock()
        self.layers.return_value = self._layers

    def mapSettings(self):
        return self._map_settings

    def setLayers(self, layers):
        self._layers = layers

    def refresh(self):
        pass

    def xyCoords(self, p):
        return p

    def mapUnitsPerPixel(self):
        return 1.0

    def width(self):
        return 800

    def height(self):
        return 600


class MockQgsMapTool:
    def __init__(self, canvas):
        self.canvas = canvas
        self.activated = mock_signal()
        self.deactivated = mock_signal()
        self.messageEmitted = mock_signal()

    def activate(self):
        self.activated.emit()

    def deactivate(self):
        self.deactivated.emit()

    def canvasReleaseEvent(self, e):
        pass

    def canvasMoveEvent(self, e):
        pass

    def keyPressEvent(self, e):
        pass


class MockQgsMapToolEmitPoint(MockQgsMapTool):
    def __init__(self, canvas):
        super().__init__(canvas)

    def canvasPressEvent(self, e):
        pass

    def canvasReleaseEvent(self, e):
        pass

    def canvasMoveEvent(self, e):
        pass


class MockQgsRubberBand:
    def __init__(self, canvas, geometry_type=0):
        pass

    def addPoint(self, p, do_update=True):
        pass

    def reset(self, geometry_type=0):
        pass

    def show(self):
        pass

    def hide(self):
        pass

    def setColor(self, color):
        pass

    def setFillColor(self, color):
        pass

    def setStrokeColor(self, color):
        pass

    def setWidth(self, width):
        pass

    def setToGeometry(self, geom, context):
        pass


class MockQgsVertexMarker:
    ICON_CIRCLE, ICON_CROSS, ICON_X = 0, 1, 2

    def __init__(self, canvas):
        pass

    def setCenter(self, p):
        pass

    def setColor(self, color):
        pass

    def setIconSize(self, size):
        pass

    def setIconType(self, type):
        pass

    def setPenWidth(self, width):
        pass
