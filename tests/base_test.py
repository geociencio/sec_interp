"""Base test class and mocks for unittest migration."""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock


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
    VectorLayer = 0
    RasterLayer = 1

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
        self.name = MagicMock(
            return_value=(
                args[1] if len(args) > 1 else "MockLayer" if len(args) > 0 else ""
            )
        )
        self.id = MagicMock(return_value="mock_layer_id")
        self.renderer = MagicMock()
        self.setRenderer = MagicMock()
        self.setSubsetString = MagicMock()
        self.triggerRepaint = MagicMock()
        self.getFeatures = MagicMock(return_value=iter([]))

        # Data provider mock
        self._provider = MagicMock()
        self._dataProvider.return_value = self._provider
        self.dataProvider = self._dataProvider
        self._internal_fields = MockQgsFields()
        self._provider.addAttributes.side_effect = self._add_attributes
        self._provider.addFeatures.side_effect = self._add_features
        self._features = []

        # Default sampling mock
        self._provider.sample.return_value = (100.0, True)
        self._provider.identify.return_value = MagicMock()
        self._provider.identify().isValid.return_value = True
        self._provider.identify().results.return_value = {1: 100.0}

        self._crs = MockQgsCoordinateReferenceSystem()

    def crs(self):
        return self._crs

    def fields(self):
        return self._internal_fields

    def _add_attributes(self, fields):
        for f in fields:
            self._internal_fields.append(f)
        return True

    def _add_features(self, features):
        self._features.extend(features)
        self.getFeatures.return_value = iter(self._features)
        return True

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

    def rasterUnitsPerPixelX(self):
        return 1.0

    def source(self):
        return "mock_source"

    def updateExtents(self):
        pass

    def setLabeling(self, labeling):
        pass

    def setLabelsEnabled(self, enabled):
        self._labels_enabled = enabled

    def saveNamedStyle(self, path):
        return "Success", True

    def labelsEnabled(self):
        return getattr(self, "_labels_enabled", False)

    def wkbType(self):
        return 3  # QgsWkbTypes.Point

    def extent(self):
        return MockQgsRectangle(0, 0, 100, 100)


class MockQgsVectorLayer(MockQgsMapLayer):
    def __init__(self, path="path", name="layer", provider="memory", options=None):
        # Handle various init signatures
        super().__init__(path, name)


class MockQgsRasterLayer(MockQgsMapLayer):
    pass


class MockQgsGeometry(MockQgsBase):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._polyline = []
        self._polygons = []
        self._point = MockQgsPointXY()
        self._wkb_type = 2  # Default LineString

        if args:
            arg = args[0]
            if isinstance(arg, MockQgsGeometry):
                self._polyline = arg._polyline
                self._wkb_type = arg._wkb_type
                self._point = arg._point
                self._polygons = arg._polygons
            elif "MockQgsPolygon" in str(type(arg)):
                self._polygons = arg._rings
                self._wkb_type = 3  # Default Polygon
                # Check for Z in points
                if self._polygons and self._polygons[0]:
                    first_pt = self._polygons[0][0]
                    if hasattr(first_pt, "z") or hasattr(first_pt, "_z"):
                        self._wkb_type = 1003  # PolygonZ
            elif "MockQgsLineString" in str(type(arg)):
                self._polyline = arg._points
                self._wkb_type = 2  # LineString
                if self._polyline:
                    first_pt = self._polyline[0]
                    if hasattr(first_pt, "z") or hasattr(first_pt, "_z"):
                        self._wkb_type = 1002  # LineStringZ
            elif "MockQgsPoint" in str(type(arg)):
                self._point = MockQgsPointXY(arg.x(), arg.y())
                self._wkb_type = 1  # Point
                if hasattr(arg, "z") or hasattr(arg, "_z"):
                    self._wkb_type = 1001  # PointZ

    @staticmethod
    def fromPolylineXY(points):
        geom = MockQgsGeometry()
        geom._polyline = points
        geom._wkb_type = 2  # LineString
        return geom

    @staticmethod
    def fromPointXY(point):
        geom = MockQgsGeometry()
        geom._point = point
        geom._wkb_type = 1  # Point
        return geom

    @staticmethod
    def fromPolygonXY(polygons):
        geom = MockQgsGeometry()
        geom._polygons = polygons
        geom._wkb_type = 3  # Polygon
        return geom

    def intersects(self, other):
        return True

    def isMultipart(self):
        return False

    def asPolyline(self):
        return self._polyline

    def asPolygon(self):
        # returns list of rings, each ring is a list of QgsPointXY
        return self._polygons

    def asMultiPolygon(self):
        # returns list of polygons, each polygon is a list of rings
        return [self._polygons]

    def asMultiPolyline(self):
        return [self._polyline]

    def isGeosValid(self):
        return True

    def centroid(self):
        # Mock centroid
        p = MockQgsPointXY(0, 0)
        if hasattr(self, "_point") and self._point:
            p = self._point
        elif hasattr(self, "_polyline") and self._polyline:
            p = self._polyline[0]
        elif hasattr(self, "_polygons") and self._polygons and self._polygons[0]:
            p = self._polygons[0][0]
        return MockQgsGeometry.fromPointXY(p)

    def makeValid(self):
        return self

    def isNull(self):
        return False

    def wkbType(self):
        return self._wkb_type

    def asPoint(self):
        return self._point

    def type(self):
        from qgis.core import QgsWkbTypes

        return QgsWkbTypes.geometryType(self.wkbType())

    def length(self):
        if len(self._polyline) < 2:
            return 0.0
        total = 0.0
        for i in range(len(self._polyline) - 1):
            p1 = self._polyline[i]
            p2 = self._polyline[i + 1]
            total += ((p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2) ** 0.5
        return total

    def interpolate(self, distance):
        # Mock interpolation: assume line is on X axis for simplicity
        return MockQgsGeometry.fromPointXY(MockQgsPointXY(distance, 0.0))

    def lineLocatePoint(self, point_geom):
        # Mock locate: for horizontal line starting at 0,0, it's just the X coordinate
        if isinstance(point_geom, MockQgsGeometry):
            return point_geom.asPoint().x()
        return 0.0

    def nearestPoint(self, other):
        # For mocking purposes, check if we're a horizontal line at y=0
        # and project the point accordingly. This supports drillhole tests.
        if self._wkb_type == 2 and self._polyline:
            if all(getattr(pt, "_y", 1) == 0 for pt in self._polyline):
                try:
                    other_pt = other.asPoint()
                    return MockQgsGeometry.fromPointXY(
                        MockQgsPointXY(other_pt.x(), 0.0)
                    )
                except AttributeError:
                    pass
        return other

    def simplify(self, tolerance):
        # For mock, just return self or a copy
        return self

    def buffer(self, distance, segments):
        # Simple mock: return a polygon-ish geometry
        geom = MockQgsGeometry()
        geom._wkb_type = 2  # Polygon
        return geom

    def densifyByDistance(self, distance):
        # Simple mock: just return self
        return self

    def boundingBox(self):
        if not self._polyline:
            return MagicMock()
        min_x = min(p.x() for p in self._polyline)
        max_x = max(p.x() for p in self._polyline)
        min_y = min(p.y() for p in self._polyline)
        max_y = max(p.y() for p in self._polyline)
        box = MagicMock()
        box.width.return_value = max_x - min_x
        box.height.return_value = max_y - min_y
        box.xMinimum.return_value = min_x
        box.xMaximum.return_value = max_x
        box.yMinimum.return_value = min_y
        box.yMaximum.return_value = max_y
        return box

    def intersection(self, other):
        # Mock intersection: for now just return self if it's not null
        if self.isNull():
            return self
        return self

    def isEmpty(self):
        return not self._polyline and not self._point

    def transform(self, transform):
        # Mock transformation: does nothing for now
        pass

    def vertices(self):
        return self._polyline

    def vertexAt(self, index):
        if self._wkb_type == 1:  # Point
            return self._point
        if index < len(self._polyline):
            return self._polyline[index]
        return MockQgsPointXY(0, 0)


class MockQgsLineString(MockQgsBase):
    def __init__(self, points):
        super().__init__()
        self._points = points

    def points(self):
        return self._points


class MockQgsPolygon(MockQgsBase):
    def __init__(self):
        super().__init__()
        self._rings = []

    def setExteriorRing(self, ring):
        if hasattr(ring, "points"):
            self._rings = [ring.points()]
        else:
            self._rings = [ring]

    def addInteriorRing(self, ring):
        if hasattr(ring, "points"):
            self._rings.append(ring.points())
        else:
            self._rings.append(ring)


class MockQgsPoint(MockQgsBase):
    def __init__(self, x=0, y=0, z=0):
        super().__init__()
        self._x, self._y, self._z = x, y, z

    def x(self):
        return self._x

    def y(self):
        return self._y

    def z(self):
        return self._z


class MockQgsCoordinateReferenceSystem(MockQgsBase):
    def __init__(self, authid="EPSG:4326"):
        super().__init__()
        self._authid = authid

    def authid(self):
        return self._authid

    def ellipsoidAcronym(self):
        return "WGS84"

    def isValid(self):
        return True


class MockQgsCoordinateTransform(MockQgsBase):
    def __init__(self, src_crs=None, dest_crs=None, project=None):
        super().__init__()

    def transform(self, geom):
        pass


class MockQgsSpatialIndex:
    def __init__(self, features=None):
        pass

    def intersects(self, rect):
        return []


class MockQgsFeatureRequest:
    NoGeometry = 1

    def setFilterFids(self, fids):
        return self

    def setFilterRect(self, rect):
        return self

    def setFilterExpression(self, expression):
        return self

    def setSubsetOfAttributes(self, attributes, fields):
        return self

    def setFlags(self, flags):
        return self


class MockQgsFeature:
    def __init__(self, fields=None):
        self._geometry = MockQgsGeometry()
        self._attributes = {}
        self._fields = fields

    def setGeometry(self, geom):
        self._geometry = geom

    def setFields(self, fields):
        self._fields = fields

    def setAttributes(self, attributes):
        if isinstance(attributes, list):
            fields = getattr(self, "_fields", None)
            if fields and hasattr(fields, "names"):
                names = fields.names()
                for i, val in enumerate(attributes):
                    if i < len(names):
                        self._attributes[names[i]] = val
                    self._attributes[i] = val
            else:
                for i, val in enumerate(attributes):
                    self._attributes[i] = val
        else:
            self._attributes = attributes

    def setAttribute(self, key, value):
        self._attributes[key] = value

    def geometry(self):
        return self._geometry

    def hasGeometry(self):
        return not self._geometry.isNull()

    def fields(self):
        fields = MagicMock()
        fields.names.return_value = list(self._attributes.keys())
        return fields

    def attributes(self):
        return list(self._attributes.values())

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._attributes.get(key)
        # Try as name
        res = self._attributes.get(key)
        # Fallback to index if name search fails
        if res is None:
            fields = getattr(self, "_fields", None)
            if fields and hasattr(fields, "indexOf"):
                idx = fields.indexOf(key)
                if idx != -1:
                    res = self._attributes.get(idx)
        return res

    def __setitem__(self, key, value):
        self._attributes[key] = value


class MockQgsRectangle(MockQgsBase):
    def __init__(self, xmin=0, ymin=0, xmax=0, ymax=0):
        super().__init__()
        self._xmin, self._ymin, self._xmax, self._ymax = xmin, ymin, xmax, ymax

    def xMinimum(self):
        return self._xmin

    def xMaximum(self):
        return self._xmax

    def yMinimum(self):
        return self._ymin

    def yMaximum(self):
        return self._ymax

    def width(self):
        return self._xmax - self._xmin

    def height(self):
        return self._ymax - self._ymin

    def isEmpty(self):
        return self._xmin == self._xmax and self._ymin == self._ymax

    def __bool__(self):
        return not self.isEmpty()

    def combineExtentWith(self, other):
        self._xmin = min(self._xmin, other.xMinimum())
        self._ymin = min(self._ymin, other.yMinimum())
        self._xmax = max(self._xmax, other.xMaximum())
        self._ymax = max(self._ymax, other.yMaximum())


class MockQgsPointXY:
    def __init__(self, x=0, y=0):
        if isinstance(x, MockQgsPointXY):
            self._x = x.x()
            self._y = x.y()
        else:
            self._x = x
            self._y = y

    def __iter__(self):
        yield self._x
        yield self._y

    def x(self):
        return self._x

    def y(self):
        return self._y

    def distance(self, other):
        return ((self._x - other.x()) ** 2 + (self._y - other.y()) ** 2) ** 0.5

    def compare(self, other, epsilon):
        return abs(self._x - other.x()) < epsilon and abs(self._y - other.y()) < epsilon

    def isValid(self):
        return True


class MockQgsField(MockQgsBase):
    def __init__(self, name=None, field_type=10, *args, **kwargs):
        super().__init__()
        self._name = name
        self._type = field_type

    def name(self):
        return self._name

    def type(self):
        return self._type


class MockQgsFields(MockQgsBase):
    def __init__(self):
        super().__init__()
        self._fields = []

    def append(self, field):
        self._fields.append(field)

    def indexOf(self, name):
        for i, f in enumerate(self._fields):
            if f.name() == name:
                return i
        return -1

    def names(self):
        return [f.name() for f in self._fields]

    def count(self):
        return len(self._fields)

    def __iter__(self):
        return iter(self._fields)

    def __len__(self):
        return len(self._fields)

    def field(self, index_or_name):
        if isinstance(index_or_name, int):
            return self._fields[index_or_name]
        for f in self._fields:
            if f.name() == index_or_name:
                return f
        return None


class MockQgsDistanceArea(MockQgsBase):
    def setSourceCrs(self, crs, context):
        pass

    def setEllipsoid(self, ellipsoid):
        pass

    def measureLine(self, p1, p2):
        # Calculate Euclidean distance for mock validation
        try:
            dx = p1.x() - p2.x()
            dy = p1.y() - p2.y()
            return (dx**2 + dy**2) ** 0.5
        except (AttributeError, TypeError):
            return 0.0


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


class MockQgsProject(MockQObject):
    _instance = None

    def __init__(self):
        super().__init__()
        self._layers = {}
        self._entries = {}

    def readEntry(self, scope, key, default=None):
        return self._entries.get(f"{scope}/{key}", default), True

    def writeEntry(self, scope, key, value):
        self._entries[f"{scope}/{key}"] = value
        return True

    def clear(self):
        self._layers = {}
        self._entries = {}

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = MockQgsProject()
        return cls._instance

    def mapLayer(self, layer_id):
        return self._layers.get(layer_id)

    def mapLayers(self):
        return self._layers

    def addMapLayer(self, layer):
        self._layers[layer.id()] = layer
        return layer

    def removeMapLayer(self, layer_id):
        if layer_id in self._layers:
            del self._layers[layer_id]

    def transformContext(self):
        return MagicMock()

    def crs(self):
        return MockQgsCoordinateReferenceSystem()


class MockQgsPalLayerSettings(MockQObject):
    class Placement:
        OverPoint = 0
        Line = 1

    class Property:
        OffsetQuad = 0
        LabelDistance = 1

    def __init__(self):
        super().__init__()
        self.fieldName = ""
        self.placement = 0
        self.dist = 0

    def setFormat(self, fmt):
        pass

    def setDataDefinedProperties(self, props):
        pass


class MockQgsTextFormat(MockQObject):
    def __init__(self):
        super().__init__()

    def setColor(self, color):
        pass

    def setSize(self, size):
        pass


class MockQgsPropertyCollection(MockQObject):
    def __init__(self):
        super().__init__()

    def setProperty(self, key, prop):
        pass


class MockQgsProperty(MockQObject):
    @staticmethod
    def fromField(name):
        return MagicMock()

    @staticmethod
    def fromExpression(expr):
        return MagicMock()


class MockQgsVectorLayerSimpleLabeling(MockQObject):
    def __init__(self, settings):
        super().__init__()


class MockQgsSymbol(MockQObject):
    @classmethod
    def createSimple(cls, props):
        return MagicMock()


class MockQgsLineSymbol(MockQgsSymbol):
    pass


class MockQgsMarkerSymbol(MockQgsSymbol):
    pass


class MockQgsSingleSymbolRenderer(MockQObject):
    def __init__(self, symbol):
        super().__init__()


# Define custom mock widgets - MockQObject is defined earlier


class MockQApplication(MockQObject):
    _instance = None

    def __init__(self, args):
        super().__init__()
        MockQApplication._instance = self
        self._thread = MockQThread()

    @staticmethod
    def instance():
        if MockQApplication._instance is None:
            MockQApplication._instance = MockQApplication([])
        return MockQApplication._instance

    @staticmethod
    def installTranslator(translator):
        pass

    def thread(self):
        return self._thread


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

    def exec(self):  # commonly used for dialogs
        return 1


class MockQThread(MockQObject):
    _main_thread = None

    def __init__(self, parent=None):
        super().__init__()
        # Mock signal factory usage for finished
        m = MagicMock()
        m.emit = MagicMock()
        self.finished = m
        self.started = m  # Reusing mock for simplicity

    @classmethod
    def currentThread(cls):
        if cls._main_thread is None:
            cls._main_thread = MockQThread()
        return cls._main_thread

    def start(self):
        self.run()

    def run(self):
        pass

    def wait(self):
        pass

    def quit(self):
        pass

    def terminate(self):
        pass

    def isFinished(self):
        return True

    def isRunning(self):
        return False

    def requestInterruption(self):
        pass

    def isInterruptionRequested(self):
        return False


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


class MockQListWidget(MockQWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dynamic_mocks = {}

    def __getattr__(self, name):
        if name not in self._dynamic_mocks:
            self._dynamic_mocks[name] = MagicMock()
        return self._dynamic_mocks[name]


class MockQListWidgetItem:
    def __init__(self, text="", parent=None):
        self._text = text
        self.setIcon = MagicMock()
        self.setTextAlignment = MagicMock()


mock_qtwidgets = MagicMock()
mock_core = MagicMock()
mock_gui = MagicMock()

# Setup module mock
mock_qtwidgets.QApplication = MockQApplication
mock_qtwidgets.QCheckBox = MockQCheckBox
mock_qtwidgets.QGroupBox = MockQGroupBox
mock_qtwidgets.QVBoxLayout = MockQVBoxLayout
mock_qtwidgets.QLabel = MockQLabel
mock_qtwidgets.QPushButton = MockQPushButton
mock_qtwidgets.QWidget = MockQWidget
mock_qtwidgets.QDialog = MockQDialog
mock_qtwidgets.QListWidget = MockQListWidget
mock_qtwidgets.QListWidgetItem = MockQListWidgetItem
mock_qtwidgets.QDialogButtonBox = MagicMock()
mock_qtwidgets.QAction = MagicMock()
mock_qtwidgets.QFileDialog = MagicMock()
mock_qtwidgets.QStyle = MagicMock()
mock_qtwidgets.QMainWindow = MockQWidget


# Force usage of mocks to ensure pure unittest execution
# Check if real QGIS is available
try:
    import qgis.core  # noqa: F401

    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False

if not CORE_AVAILABLE:
    mock_qgis = MagicMock()
    sys.modules["qgis"] = mock_qgis

    mock_qgis.core = mock_core

    # Use MockQgsProject
    mock_core.QgsProject.instance.side_effect = MockQgsProject.instance

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

def mock_geometry_type(wkb):
    if wkb == 1:  # Point
        return 0  # PointGeometry
    if wkb == 2:  # LineString
        return 1  # LineGeometry
    if wkb in [3, 1003]:  # Polygon or PolygonZ
        return 2  # PolygonGeometry
    return wkb


if not CORE_AVAILABLE:

    # QgsUnitTypes constants
    mock_core.QgsUnitTypes.DistanceUnit.Meters = 0
    mock_core.QgsUnitTypes.toString = lambda x: "meters"

    mock_core.QgsFeature = MockQgsFeature
    mock_core.QgsField = MockQgsField
    mock_core.QgsFields = MockQgsFields
    mock_core.QgsFeatureRequest = MockQgsFeatureRequest
    mock_core.QgsSpatialIndex = MockQgsSpatialIndex
    mock_core.QgsSettings = MockQgsSettings
    mock_core.QgsCoordinateTransform = MockQgsCoordinateTransform
    mock_core.QgsRectangle = MockQgsRectangle
    mock_core.QgsVectorFileWriter = MagicMock()
    mock_core.QgsVectorFileWriter.NoError = 0
    mock_core.QgsMapSettings = MagicMock()
    mock_core.QgsMapRendererCustomPainterJob = MagicMock()

    mock_core.QgsProperty = MockQgsProperty
    mock_core.QgsPropertyCollection = MockQgsPropertyCollection
    mock_core.QgsLineString = MockQgsLineString
    mock_core.QgsPalLayerSettings = MockQgsPalLayerSettings
    mock_core.QgsTextFormat = MockQgsTextFormat
    mock_core.QgsVectorLayerSimpleLabeling = MockQgsVectorLayerSimpleLabeling
    mock_core.QgsSingleSymbolRenderer = MockQgsSingleSymbolRenderer
    mock_core.QgsLineSymbol = MockQgsLineSymbol
    mock_core.QgsMarkerSymbol = MockQgsMarkerSymbol

    class MockQgis:
        Critical = 2
        Warning = 1
        Info = 0
        LayerFilters = lambda x: x

        class LayerFilter:
            RasterLayer = 1
            PointLayer = 2
            LineLayer = 4
            PolygonLayer = 8
            All = 15

    mock_core.Qgis = MockQgis

    class MockQgsTask(MagicMock):
        CanCancel = 1

        def __init__(self, description="", flags=0):
            super().__init__()
            self._description = description
            self._flags = flags

    mock_core.QgsTask = MockQgsTask
    mock_core.QgsMessageLog = MagicMock()

    class MockQgsMapTool:
        def __init__(self, canvas):
            self.canvas = canvas

        def activate(self):
            pass

        def deactivate(self):
            pass

        def canvasReleaseEvent(self, e):
            pass

        def canvasMoveEvent(self, e):
            pass

        def keyPressEvent(self, e):
            pass

    mock_qgis.gui = mock_gui
    mock_gui.QgsMapTool = MockQgsMapTool
    mock_gui.QgsMapToolEmitPoint = MockQgsMapTool
    mock_gui.QgsMapToolPan = MockQgsMapTool

    class MockQgsRubberBand:
        def __init__(self, canvas, geometry_type=0):
            pass

        def addPoint(self, p, do_update=True):
            pass

        def reset(self, geometry_type=0):
            pass

        def show(self):
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

        def hide(self):
            pass

    class MockQgsVertexMarker:
        ICON_CIRCLE = 0
        ICON_CROSS = 1
        ICON_X = 2

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

    mock_gui.QgsRubberBand = MockQgsRubberBand
    mock_gui.QgsVertexMarker = MockQgsVertexMarker

    sys.modules["qgis.core"] = mock_core
    sys.modules["qgis.gui"] = mock_gui

    mock_qtcore = MagicMock()
    mock_qtcore.Qt.LeftButton = 1
    mock_qtcore.Qt.RightButton = 2
    mock_qtcore.Qt.Key_Return = 16777220
    mock_qtcore.Qt.Key_Enter = 16777221
    mock_qtcore.Qt.Key_Escape = 16777216
    mock_qtcore.Qt.CrossCursor = 2

    def mock_signal(*args, **kwargs):
        m = MagicMock()
        m.emit = MagicMock()
        return m

    mock_qtcore.pyqtSignal = mock_signal
    mock_qtcore.QObject = MagicMock
    mock_qtcore.QThread = MockQThread
    mock_qtcore.QCoreApplication = MockQApplication

    # Mock QgsMapCanvas as a class to avoid spec issues in type hints
    class MockQgsMapCanvas(MagicMock):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.scene = MagicMock()
            self.layers = MagicMock(return_value=[])

    mock_gui.QgsMapCanvas = MockQgsMapCanvas

    class MockQPoint:
        def __init__(self, x, y):
            self._x = x
            self._y = y

        def x(self):
            return self._x

        def y(self):
            return self._y

    sys.modules["qgis.PyQt"] = MagicMock()
    sys.modules["qgis.PyQt.QtCore"] = mock_qtcore
    sys.modules["qgis.PyQt.QtCore"].QPoint = MockQPoint
    sys.modules["qgis.PyQt.QtWidgets"] = mock_qtwidgets

    mock_gui_lib = MagicMock()

    # mock_gui_lib.QPainter = lambda *args: MagicMock()
    # Need QPainter to be a class that can be instantiated
    class MockQPainter(MagicMock):
        Antialiasing = 1

        def __init__(self, *args, **kwargs):
            # Strip positional args to avoid spec interpretation
            super().__init__(**kwargs)

    mock_gui_lib.QPainter = MockQPainter

    class MockQImage(MagicMock):
        Format_ARGB32 = 0

        def __init__(self, *args, **kwargs):
            # Strip positional args to avoid spec interpretation, but safely pass kwargs
            super().__init__(**kwargs)

    mock_gui_lib.QImage = MockQImage

    class MockQColor(MagicMock):
        def isValid(self):
            return True

        def darker(self, f=150):
            return self

        def setAlpha(self, a):
            pass

        def red(self):
            return 0

        def green(self):
            return 0

        def blue(self):
            return 0

        @staticmethod
        def fromHsv(h, s, v, a=255):
            return MockQColor()

    mock_gui_lib.QColor = MockQColor
    mock_gui_lib.QPen = MagicMock
    mock_gui_lib.QBrush = MagicMock
    sys.modules["qgis.PyQt.QtGui"] = mock_gui_lib

    class MockQRectF(MagicMock):
        def __init__(self, x=0, y=0, w=0, h=0):
            super().__init__()
            self._x, self._y, self._w, self._h = x, y, w, h

        def x(self):
            return self._x

        def y(self):
            return self._y

        def width(self):
            return self._w

        def height(self):
            return self._h

    mock_qtcore.QRectF = MockQRectF
    mock_qtcore.QSize = MagicMock

    sys.modules["qgis.PyQt.QtSvg"] = MagicMock()

    mock_processing = MagicMock()
    sys.modules["qgis.processing"] = mock_processing
    mock_qgis.processing = mock_processing

    # Also mock basic PyQt classes if needed by tests that don't need full QApp
    sys.modules["qgis.PyQt.QtCore"].QCoreApplication.translate = lambda c, t: t
    sys.modules["qgis.PyQt.QtCore"].QCoreApplication.installTranslator = lambda t: None
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
        # Reset globally shared mocks to prevent state leakage (StopIteration, etc.)
        from tests.base_test import mock_qtwidgets, mock_core, mock_gui

        # Resetting these ensures that any test modifying them (e.g., adding side_effects)
        # doesn't affect subsequent tests. We use return_value/side_effect = True to clear them.
        mock_qtwidgets.reset_mock(side_effect=True, return_value=True)
        mock_core.reset_mock(side_effect=True, return_value=True)
        mock_gui.reset_mock(side_effect=True, return_value=True)

        # Re-apply critical persistent mocks that were cleared by reset_mock
        mock_core.QgsProject.instance.side_effect = MockQgsProject.instance
        mock_core.QgsWkbTypes.geometryType.side_effect = mock_geometry_type
        mock_core.QgsWkbTypes.hasZ = lambda wkb: wkb >= 1000

        # Reset shared state in custom mock classes
        MockQgsProject.instance().clear()
        MockQgsSettings._shared_values.clear()

        # Restore critical module-level functions
        if "qgis.PyQt.QtCore" in sys.modules:
            sys.modules["qgis.PyQt.QtCore"].QCoreApplication.translate = lambda c, t: t
            sys.modules["qgis.PyQt.QtCore"].QCoreApplication.installTranslator = (
                lambda t: None
            )

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
