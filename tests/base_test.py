"""Base test class and mocks for unittest migration."""

import sys
import unittest
import tempfile
import shutil
from unittest.mock import MagicMock
from pathlib import Path

class MockQgsBase:
    def isNull(self):
        return False

    def type(self):
        return 0

class MockQObject:
    def __init__(self, *args, **kwargs):
        pass

    def tr(self, text, disambiguation=None, n=-1):
        return text

    def setObjectName(self, name):
        pass

    def setToolTip(self, tip):
        pass

    def property(self, name):
        return None

    def setProperty(self, name, value):
        pass

class MockQgsMapLayer(MockQObject):
    class LayerType:
        VectorLayer = 0
        RasterLayer = 1
        PluginLayer = 2
        MeshLayer = 3
        VectorTileLayer = 4
        PointCloudLayer = 5
        AnnotationLayer = 6

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dataProvider = MagicMock()
        self.name = args[1] if len(args) > 1 else "MockLayer" if len(args) > 0 else ""
        self.id = MagicMock(return_value="mock_layer_id")
        self.renderer = MagicMock()
        self.setRenderer = MagicMock()
        self.setRenderer = MagicMock()
        self.setSubsetString = MagicMock()
        self.triggerRepaint = MagicMock()
        self.getFeatures = MagicMock(return_value=iter([]))

    def isValid(self):
        return True

    def featureCount(self):
        return 0

    def setCrs(self, crs):
        pass

    def dataProvider(self):
        return self._dataProvider

    def updateFields(self):
        pass

    # getFeatures is now an instance attribute

    def crs(self):
        return MagicMock()

    def rasterUnitsPerPixelX(self):
        return 1.0

    def source(self):
        return "mock_source"

    def updateExtents(self):
        pass

class MockQgsVectorLayer(MockQgsMapLayer):
    def __init__(self, path="path", name="layer", provider="memory", options=None):
        # Handle various init signatures
        super().__init__(path, name)


class MockQgsRasterLayer(MockQgsMapLayer):
    pass


class MockQgsGeometry(MockQgsBase):
    def __init__(self):
        super().__init__()
        self._polyline = []
        self._point = MockQgsPointXY()
        self._wkb_type = 1  # LineString

    @staticmethod
    def fromPolylineXY(points):
        geom = MockQgsGeometry()
        geom._polyline = points
        geom._wkb_type = 1  # LineString
        return geom

    @staticmethod
    def fromPointXY(point):
        geom = MockQgsGeometry()
        geom._point = point
        geom._wkb_type = 0  # Point
        return geom

    def boundingBox(self):
        return MagicMock()

    def intersects(self, other):
        return True

    def isMultipart(self):
        return False

    def asPolyline(self):
        return self._polyline

    def asMultiPolyline(self):
        return [self._polyline]

    def asPoint(self):
        return self._point

    def wkbType(self):
        return self._wkb_type

    def length(self):
        return 100.0

    def interpolate(self, distance):
        # Mock interpolation: assume line is on X axis for simplicity
        return MockQgsGeometry.fromPointXY(MockQgsPointXY(distance, 0.0))


class MockQgsCoordinateReferenceSystem(MockQgsBase):
    def authid(self):
        return "EPSG:4326"

    def ellipsoidAcronym(self):
        return "WGS84"

    def mapUnits(self):
        return 0 # DistanceUnit.Meters -> often 0 or derived from QgsUnitTypes


class MockQgsSpatialIndex:
    def __init__(self, features=None):
        pass

    def intersects(self, rect):
        return []


class MockQgsFeatureRequest:
    def setFilterFids(self, fids):
        return self


class MockQgsPointXY:
    def __init__(self, x=0, y=0):
        self._x = x
        self._y = y

    def x(self):
        return self._x

    def y(self):
        return self._y


class MockQgsDistanceArea(MockQgsBase):
    def setSourceCrs(self, crs, context):
        pass

    def setEllipsoid(self, ellipsoid):
        pass


class MockQgsSettings(MockQgsBase):
    _shared_values = {}

    def __init__(self):
        pass

    def value(self, key, default=None, type=None):
        return self._shared_values.get(key, default)

    def setValue(self, key, value):
        self._shared_values[key] = value

    def remove(self, key):
        if key in self._shared_values:
            del self._shared_values[key]

# Define custom mock widgets - MockQObject is defined earlier

class MockQApplication(MockQObject):
    def __init__(self, args):
        super().__init__()

    @staticmethod
    def instance():
        return MockQApplication([])

class MockQWidget(MockQObject):
    def __init__(self, parent=None):
        super().__init__()
        self._layout = None

    def setLayout(self, layout):
        self._layout = layout

    def layout(self):
        return self._layout

    def findChildren(self, type, name=""):
        return []

    def setStyleSheet(self, style):
        pass

    def setWindowTitle(self, title):
        pass

    def resize(self, w, h):
        pass

    def show(self):
        pass

    def hide(self):
        pass

    def exec(self): # commonly used for dialogs
        return 1

    def setVisible(self, visible):
        pass

    def setEnabled(self, enabled):
        pass

    def setFixedSize(self, w, h):
        pass

    def setFixedHeight(self, h):
        pass

    def setFixedWidth(self, w):
        pass

    def setAttribute(self, attr, on=True):
        pass

    def setAutoFillBackground(self, enabled):
        pass

class MockQDialog(MockQWidget):
    def accept(self):
        pass
    def reject(self):
        pass

class MockQCheckBox(MockQWidget):
    def __init__(self, text="", parent=None):
        super().__init__()
        self.stateChanged = MagicMock()
        self.stateChanged.connect = MagicMock()
        self.toggled = MagicMock()
        self.toggled.connect = MagicMock()
        self._checked = False
        self.isChecked = MagicMock(return_value=False)
        self.setChecked = MagicMock(side_effect=self._set_checked)

    def _set_checked(self, checked):
        self._checked = checked
        self.isChecked.return_value = checked

class MockQGroupBox(MockQWidget):
    pass

class MockQVBoxLayout(MockQObject):
    def __init__(self, parent=None):
        super().__init__()
    def addWidget(self, widget, *args, **kwargs):
        pass
    def addSpacing(self, space):
        pass
    def setSpacing(self, space):
        pass
    def setContentsMargins(self, l, t, r, b):
        pass
    def insertWidget(self, index, widget):
        pass
    def addLayout(self, layout):
        pass
    def addStretch(self, stretch=0):
        pass

    def count(self):
        return 0

class MockQLabel(MockQWidget):
    def __init__(self, text="", parent=None):
        super().__init__()

    def setPixmap(self, pixmap):
        pass

class MockQPushButton(MockQWidget):
    def __init__(self, text="", parent=None):
        super().__init__()
        self.clicked = MagicMock()
        self._checkable = False
        self._checked = False
        self.isChecked = MagicMock(return_value=False)
        self.setChecked = MagicMock(side_effect=self._set_checked)
        self.toggled = MagicMock()
        self.toggled.connect = MagicMock()

    def setCheckable(self, checkable):
        self._checkable = checkable

    def _set_checked(self, checked):
        self._checked = checked
        self.isChecked.return_value = checked

# Setup module mock
mock_qtwidgets = MagicMock()
mock_qtwidgets.QApplication = MockQApplication
mock_qtwidgets.QCheckBox = MockQCheckBox
mock_qtwidgets.QGroupBox = MockQGroupBox
mock_qtwidgets.QVBoxLayout = MockQVBoxLayout
mock_qtwidgets.QLabel = MockQLabel
mock_qtwidgets.QPushButton = MockQPushButton
mock_qtwidgets.QWidget = MockQWidget
mock_qtwidgets.QDialog = MockQDialog
mock_qtwidgets.QDialogButtonBox = MagicMock()
mock_qtwidgets.QAction = MagicMock()
mock_qtwidgets.QFileDialog = MagicMock()
mock_qtwidgets.QStyle = MagicMock()
mock_qtwidgets.QMainWindow = MockQWidget



# Force usage of mocks to ensure pure unittest execution
CORE_AVAILABLE = False

if not CORE_AVAILABLE:
    mock_qgis = MagicMock()
    sys.modules["qgis"] = mock_qgis

    mock_core = MagicMock()

    # Define MockQgsProject to handle mapLayer calls appropriately
    mock_project_instance = MagicMock()
    mock_core.QgsProject.instance.return_value = mock_project_instance
    # Ensure mapLayer returns a mock
    mock_project_instance.mapLayer.return_value = MagicMock()

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

    # QgsUnitTypes constants
    mock_core.QgsUnitTypes.DistanceUnit.Meters = 0
    mock_core.QgsUnitTypes.toString = lambda x: "meters"

    mock_core.QgsFeature = MagicMock
    mock_core.QgsFeatureRequest = MockQgsFeatureRequest
    mock_core.QgsSpatialIndex = MockQgsSpatialIndex
    mock_core.QgsSettings = MockQgsSettings

    sys.modules["qgis.core"] = mock_core
    sys.modules["qgis.gui"] = MagicMock()
    sys.modules["qgis.PyQt"] = MagicMock()
    sys.modules["qgis.PyQt.QtCore"] = MagicMock()
    sys.modules["qgis.PyQt.QtWidgets"] = mock_qtwidgets
    sys.modules["qgis.PyQt.QtGui"] = MagicMock()
    sys.modules["qgis.PyQt.QtSvg"] = MagicMock()

    mock_processing = MagicMock()
    sys.modules["qgis.processing"] = mock_processing
    mock_qgis.processing = mock_processing

    # Also mock basic PyQt classes if needed by tests that don't need full QApp
    sys.modules["qgis.PyQt.QtCore"].QCoreApplication.translate = lambda c, t: t
    sys.modules["qgis.PyQt.QtCore"].QObject = MagicMock


class BaseTestCase(unittest.TestCase):
    """Base test case for all tests to inherit from."""

    @classmethod
    def setUpClass(cls):
        """Set up class resources."""
        # Initialize mocks if needed, though module level does most
        pass

    def setUp(self):
        """Set up per-test resources."""
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.test_dir)

    def tearDown(self):
        """Clean up per-test resources."""
        shutil.rmtree(self.test_dir)

    # Helper methods replicating pytest fixtures

    @property
    def sample_strike_values(self):
        """Sample strike values for testing."""
        return {
            "numeric": [0, 45, 90, 180, 270, 360],
            "quadrant": ["N 30 E", "N 45 W", "S 60 E", "S 15 W"],
            "invalid": ["invalid", None, "ABC"],
        }

    @property
    def sample_dip_values(self):
        """Sample dip values for testing."""
        return {
            "numeric": [0, 30, 45, 60, 90],
            "with_direction": ["45 NE", "30 SW", "60 N"],
            "invalid": ["invalid", None, "100", "-10"],
        }

    @property
    def sample_profile_data(self):
        """Sample topographic profile data."""
        return [
            (0.0, 100.0),
            (100.0, 150.0),
            (200.0, 120.0),
            (300.0, 180.0),
            (400.0, 140.0),
        ]

    @property
    def sample_csv_data(self):
        """Sample CSV data for testing."""
        return {
            "headers": ["distance", "elevation", "unit"],
            "rows": [
                [0.0, 100.0, "Unit A"],
                [100.0, 150.0, "Unit B"],
                [200.0, 120.0, "Unit A"],
            ],
        }
