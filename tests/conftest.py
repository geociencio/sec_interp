import sys
from unittest.mock import MagicMock

# Base class for QGIS mocks to consolidate common methods
class MockQgsBase:
    def isNull(self): return False
    def type(self): return 0

class MockQgsMapLayer(MockQgsBase):
    def isValid(self): return True
    def featureCount(self): return 0
    def setCrs(self, crs): pass
    def dataProvider(self): return MagicMock()
    def updateFields(self): pass
    def getFeatures(self, request=None): return iter([])

class MockQgsVectorLayer(MockQgsMapLayer):
    def __init__(self, *args, **kwargs):
        pass
class MockQgsRasterLayer(MockQgsMapLayer): pass

class MockQgsGeometry(MockQgsBase):
    def __init__(self):
        super().__init__()
        self._polyline = []
        self._point = MockQgsPointXY()
        self._wkb_type = 1 # LineString
    @staticmethod
    def fromPolylineXY(points):
        geom = MockQgsGeometry()
        geom._polyline = points
        geom._wkb_type = 1 # LineString
        return geom
    @staticmethod
    def fromPointXY(point):
        geom = MockQgsGeometry()
        geom._point = point
        geom._wkb_type = 0 # Point
        return geom
    def boundingBox(self): return MagicMock()
    def intersects(self, other): return True
    def isMultipart(self): return False
    def asPolyline(self): return self._polyline
    def asMultiPolyline(self): return [self._polyline]
    def asPoint(self): return self._point
    def wkbType(self): return self._wkb_type
    def length(self): return 10.0

class MockQgsCoordinateReferenceSystem(MockQgsBase):
    def authid(self): return "EPSG:4326"
    def ellipsoidAcronym(self): return "WGS84"

class MockQgsSpatialIndex:
    def __init__(self, features=None): pass
    def intersects(self, rect): return []

class MockQgsFeatureRequest:
    def setFilterFids(self, fids): return self

class MockQgsPointXY:
    def __init__(self, x=0, y=0):
        self._x = x
        self._y = y
    def x(self): return self._x
    def y(self): return self._y

class MockQgsDistanceArea(MockQgsBase):
    def setSourceCrs(self, crs, context): pass
    def setEllipsoid(self, ellipsoid): pass

# Mock QGIS and PyQt before importing any project modules during test collection
if "qgis" not in sys.modules:
    mock_qgis = MagicMock()
    sys.modules["qgis"] = mock_qgis
    
    mock_core = MagicMock()
    mock_core.QgsMapLayer = MockQgsMapLayer
    mock_core.QgsVectorLayer = MockQgsVectorLayer
    mock_core.QgsRasterLayer = MockQgsRasterLayer
    mock_core.QgsGeometry = MockQgsGeometry
    mock_core.QgsCoordinateReferenceSystem = MockQgsCoordinateReferenceSystem
    mock_core.QgsDistanceArea = MockQgsDistanceArea
    mock_core.QgsPointXY = MockQgsPointXY
    mock_core.QgsProject.instance().transformContext.return_value = MagicMock()
    
    # Constants
    mock_core.QgsWkbTypes.PointGeometry = 0
    mock_core.QgsWkbTypes.LineGeometry = 1
    mock_core.QgsWkbTypes.PolygonGeometry = 2
    mock_core.QgsWkbTypes.Point = 0
    mock_core.QgsWkbTypes.LineString = 1
    
    mock_core.QgsFeature = MagicMock
    mock_core.QgsFeatureRequest = MockQgsFeatureRequest
    mock_core.QgsSpatialIndex = MockQgsSpatialIndex
    
    sys.modules["qgis.core"] = mock_core
    sys.modules["qgis.gui"] = MagicMock()
    sys.modules["qgis.PyQt"] = MagicMock()
    sys.modules["qgis.PyQt.QtCore"] = MagicMock()
    sys.modules["qgis.PyQt.QtWidgets"] = MagicMock()
    sys.modules["qgis.PyQt.QtGui"] = MagicMock()
    sys.modules["qgis.PyQt.QtSvg"] = MagicMock()
    
    mock_processing = MagicMock()
    sys.modules["qgis.processing"] = mock_processing
    mock_qgis.processing = mock_processing

import pytest
from pathlib import Path


@pytest.fixture
def sample_strike_values():
    """Sample strike values for testing."""
    return {
        "numeric": [0, 45, 90, 180, 270, 360],
        "quadrant": ["N 30 E", "N 45 W", "S 60 E", "S 15 W"],
        "invalid": ["invalid", None, "ABC"],
    }


@pytest.fixture
def sample_dip_values():
    """Sample dip values for testing."""
    return {
        "numeric": [0, 30, 45, 60, 90],
        "with_direction": ["45 NE", "30 SW", "60 N"],
        "invalid": ["invalid", None, "100", "-10"],
    }


@pytest.fixture
def sample_profile_data():
    """Sample topographic profile data."""
    return [
        (0.0, 100.0),
        (100.0, 150.0),
        (200.0, 120.0),
        (300.0, 180.0),
        (400.0, 140.0),
    ]


@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary directory for output files."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing."""
    return {
        "headers": ["distance", "elevation", "unit"],
        "rows": [
            [0.0, 100.0, "Unit A"],
            [100.0, 150.0, "Unit B"],
            [200.0, 120.0, "Unit A"],
        ],
    }
