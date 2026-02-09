"""QGIS Utility mocks (WkbTypes, Task, etc.)."""

from unittest.mock import MagicMock


def mock_geometry_type(wkb):
    if wkb in [1, 1001]:
        return 0  # Point
    if wkb in [2, 1002, 4, 1004]:
        return 1  # Line
    if wkb in [3, 1003, 6, 1006]:
        return 2  # Polygon
    return 3  # Unknown


class MockQgsWkbTypes:
    Point, LineString, Polygon = 1, 2, 3
    PointZ, LineStringZ, PolygonZ = 1001, 1002, 1003
    MultiPoint, MultiLineString, MultiPolygon = 4, 5, 6
    MultiPointZ, MultiLineStringZ, MultiPolygonZ = 1004, 1005, 1006

    PointGeometry = 0
    LineGeometry = 1
    PolygonGeometry = 2
    UnknownGeometry = 3
    NullGeometry = 4

    class GeometryType:
        PointGeometry, LineGeometry, PolygonGeometry = 0, 1, 2
        UnknownGeometry, NullGeometry = 3, 4

    @staticmethod
    def geometryType(wkb):
        return mock_geometry_type(wkb)

    @staticmethod
    def hasZ(wkb):
        return wkb >= 1000


class MockQgis:
    Critical, Warning, Info = 2, 1, 0
    LayerFilters = lambda x: x

    class LayerFilter:
        RasterLayer, PointLayer, LineLayer, PolygonLayer = 1, 2, 4, 8
        All = 15


class MockQgsTask(MagicMock):
    CanCancel = 1

    def __init__(self, description="", flags=0):
        super().__init__()
        self._description, self._flags = description, flags
