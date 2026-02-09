"""Base test class and mocks for unittest migration.

This module acts as an aggregator for the fragmented mocks in tests/mocks/
and provides the BaseTestCase for all project tests.
"""

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

# Import fragmented mocks
from .mocks.qgis_base import MockQgsBase, MockQObject, ModuleProxy
from .mocks.qgis_geometry import (
    MockQgsGeometry,
    MockQgsLineString,
    MockQgsPolygon,
    MockQgsPoint,
    MockQgsPointXY,
)
from .mocks.qgis_core import (
    MockQgsCoordinateReferenceSystem,
    MockQgsCoordinateTransform,
    MockQgsSpatialIndex,
    MockQgsFeatureRequest,
    MockQgsRectangle,
    MockQgsProject,
    MockQgsSettings,
)
from .mocks.qgis_features import MockQgsField, MockQgsFields, MockQgsFeature
from .mocks.qgis_layers import MockQgsMapLayer, MockQgsVectorLayer, MockQgsRasterLayer
from .mocks.qt_mocks import (
    mock_signal,
    MockQApplication,
    MockQThread,
    MockQPainter,
    MockQImage,
    MockQColor,
    MockQPoint,
    MockQRectF,
    MockQWidget,
    MockQLayout,
)
from .mocks.qgis_gui import (
    MockQgsMapCanvas,
    MockQgsMapTool,
    MockQgsRubberBand,
    MockQgsVertexMarker,
    MockQgsMapToolEmitPoint,
)
from .mocks.qgis_utils import MockQgsWkbTypes, MockQgis, MockQgsTask
from .mocks.processing_mocks import mock_processing

# --- 1. Additional specialized mocks ---


class MockQgsDistanceArea(MockQgsBase):
    def __init__(self):
        super().__init__()

    def setSourceCrs(self, crs, context=None):
        pass

    def setEllipsoid(self, ellipsoid):
        pass

    def measureLength(self, geom):
        return geom.length()

    def measureLine(self, p1, p2):
        return ((p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2) ** 0.5

    def convertLengthMeasurement(self, val, unit):
        return val


class MockQgsProperty(MockQgsBase):
    def __init__(self):
        super().__init__()

    def setField(self, field):
        pass


class MockQgsPropertyCollection(MockQgsBase):
    def __init__(self):
        super().__init__()

    def setProperty(self, key, property):
        pass


class MockQgsPalLayerSettings(MockQgsBase):
    def __init__(self):
        super().__init__()
        self.fieldName = ""
        self.enabled = True

    def setFormat(self, format):
        pass


class MockQgsTextFormat(MockQgsBase):
    def __init__(self):
        super().__init__()

    def setSize(self, size):
        pass


class MockQgsVectorLayerSimpleLabeling(MockQgsBase):
    def __init__(self, settings):
        super().__init__()


class MockQgsSingleSymbolRenderer(MockQgsBase):
    def __init__(self, symbol):
        super().__init__()


class MockQgsLineSymbol:
    @staticmethod
    def createSimple(config):
        return MagicMock()


class MockQgsMarkerSymbol:
    @staticmethod
    def createSimple(config):
        return MagicMock()


class MockQgsLabelBackgroundSettings(MockQgsBase):
    def __init__(self):
        super().__init__()

    def setEnabled(self, enabled):
        pass

    def setFillColor(self, color):
        pass


# --- 2. Initialize Proxies and Modules ---

mock_core = ModuleProxy("qgis.core")
mock_gui = ModuleProxy("qgis.gui")
mock_qtwidgets = ModuleProxy("qgis.PyQt.QtWidgets")
mock_qtcore = ModuleProxy("qgis.PyQt.QtCore")
mock_qtgui = ModuleProxy("qgis.PyQt.QtGui")


def restore_mocks():
    """Re-assigns all stable mock classes to their respective proxies."""
    if os.environ.get("FORCE_MOCKS", "1") == "0":
        return

    # Qt Widgets
    mock_qtwidgets.QApplication = MockQApplication
    mock_qtwidgets.QWidget = MockQWidget
    mock_qtwidgets.QDialog = MockQWidget
    mock_qtwidgets.QVBoxLayout = MockQLayout
    mock_qtwidgets.QHBoxLayout = MockQLayout
    mock_qtwidgets.QScrollArea = MockQWidget
    from .mocks.qt_mocks import MockQFrame

    mock_qtwidgets.QFrame = MockQFrame
    mock_qtwidgets.QLabel = MockQWidget
    mock_qtwidgets.QPushButton = MockQWidget
    mock_qtwidgets.QCheckBox = MockQWidget
    mock_qtwidgets.QLineEdit = MockQWidget
    mock_qtwidgets.QComboBox = MockQWidget
    mock_qtwidgets.QProgressBar = MockQWidget
    mock_qtwidgets.QGroupBox = MockQWidget
    mock_qtwidgets.QAbstractItemView = MockQWidget
    mock_qtwidgets.QListView = MockQWidget
    from .mocks.qt_mocks import MockQListWidget, MockQListWidgetItem

    mock_qtwidgets.QListWidget = MockQListWidget
    mock_qtwidgets.QListWidgetItem = MockQListWidgetItem
    mock_qtwidgets.QLayout = MockQLayout

    # Core
    mock_core.QgsMapLayer = MockQgsMapLayer
    mock_core.QgsVectorLayer = MockQgsVectorLayer
    mock_core.QgsRasterLayer = MockQgsRasterLayer
    mock_core.QgsGeometry = MockQgsGeometry
    mock_core.QgsCoordinateReferenceSystem = MockQgsCoordinateReferenceSystem
    mock_core.QgsDistanceArea = MockQgsDistanceArea
    mock_core.QgsPointXY = MockQgsPointXY
    mock_core.QgsPoint = MockQgsPoint
    mock_core.QgsLineString = MockQgsLineString
    mock_core.QgsPolygon = MockQgsPolygon
    mock_core.QgsFeature = MockQgsFeature
    mock_core.QgsField = MockQgsField
    mock_core.QgsFields = MockQgsFields
    mock_core.QgsFeatureRequest = MockQgsFeatureRequest
    mock_core.QgsSpatialIndex = MockQgsSpatialIndex
    mock_core.QgsSettings = MockQgsSettings
    mock_core.QgsCoordinateTransform = MockQgsCoordinateTransform
    mock_core.QgsRectangle = MockQgsRectangle
    mock_core.QgsTask = MockQgsTask
    mock_core.Qgis = MockQgis
    mock_core.QgsWkbTypes = MockQgsWkbTypes

    # Gui
    mock_gui.QgsMapTool = MockQgsMapTool
    mock_gui.QgsMapToolEmitPoint = MockQgsMapToolEmitPoint
    mock_gui.QgsMapToolPan = MockQgsMapTool
    mock_gui.QgsRubberBand = MockQgsRubberBand
    mock_gui.QgsVertexMarker = MockQgsVertexMarker
    mock_gui.QgsMapCanvas = MockQgsMapCanvas

    # QtCore
    mock_qtcore.QPoint = MockQPoint
    mock_qtcore.QRectF = MockQRectF
    mock_qtcore.Qt.LeftButton = 1
    mock_qtcore.pyqtSignal = mock_signal
    mock_qtcore.QObject = MockQObject
    mock_qtcore.QThread = MockQThread
    mock_qtcore.QCoreApplication = MockQApplication

    # QtGui
    mock_qtgui.QPainter = MockQPainter
    mock_qtgui.QImage = MockQImage
    mock_qtgui.QColor = MockQColor

    # Specialized logic
    qgs_project = getattr(mock_core, "QgsProject")
    qgs_project.instance.side_effect = MockQgsProject.instance

    # Mock QgsVectorFileWriter.create for tests that need physical file creation
    writer = getattr(mock_core, "QgsVectorFileWriter")
    writer.NoError = 0

    def create_real_writer(
        output_path, fields, geometry_type, crs, transform_context, options
    ):
        import os

        base_path = os.path.splitext(output_path)[0]
        mock_writer = MagicMock()
        mock_writer.hasError.return_value = 0
        mock_writer.errorMessage.return_value = ""

        # Create supporting files
        with open(output_path, "w") as f:
            f.write("# Mock shapefile\n")
        for ext in [".shx", ".dbf", ".prj"]:
            with open(base_path + ext, "w") as f:
                f.write("# Mock file\n")

        return mock_writer

    writer.create.side_effect = create_real_writer
    writer.writeAsVectorFormatV3.return_value = (0, "", "", "")

    # QMetaType
    if not hasattr(mock_qtcore, "QMetaType"):
        mock_qtcore.QMetaType = MagicMock(name="QMetaType")
        mock_qtcore.QMetaType.Type.Int = 2
        mock_qtcore.QMetaType.Type.Double = 6
        mock_qtcore.QMetaType.Type.QString = 10


def apply_mock_patches():
    """Apply mock patches to sys.modules for unit testing."""
    import types

    global qgis_pkg, pyqt_pkg

    # Aggressively clear existing qgis modules to avoid pollution in environments with real QGIS
    for mod in list(sys.modules.keys()):
        if mod.startswith("qgis") or mod == "processing":
            del sys.modules[mod]

    qgis_pkg = types.ModuleType("qgis")
    qgis_pkg.__path__ = []
    sys.modules["qgis"] = qgis_pkg

    pyqt_pkg = types.ModuleType("qgis.PyQt")
    pyqt_pkg.__path__ = []
    sys.modules["qgis.PyQt"] = pyqt_pkg
    qgis_pkg.PyQt = pyqt_pkg

    sys.modules["qgis.core"] = mock_core
    sys.modules["qgis.gui"] = mock_gui
    sys.modules["qgis.PyQt.QtWidgets"] = mock_qtwidgets
    sys.modules["qgis.PyQt.QtCore"] = mock_qtcore
    sys.modules["qgis.PyQt.QtGui"] = mock_qtgui
    sys.modules["qgis.PyQt.QtSvg"] = MagicMock(name="qgis.PyQt.QtSvg")
    sys.modules["processing"] = mock_processing

    # Ensure proxies are correctly assigned in qgis package
    qgis_pkg.core = mock_core
    qgis_pkg.gui = mock_gui

    restore_mocks()


# Initial setup
if os.environ.get("FORCE_MOCKS", "1") == "1":
    apply_mock_patches()


class BaseTestCase(unittest.TestCase):
    """Base test case providing environment management."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.test_dir)
        MockQgsProject.instance().clear()
        MockQgsSettings._shared_values.clear()

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

    def tearDown(self):
        if hasattr(self, "test_dir") and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        mock_qtwidgets.reset_mock()
        mock_core.reset_mock()
        mock_gui.reset_mock()
        mock_qtcore.reset_mock()
        mock_qtgui.reset_mock()
        restore_mocks()
