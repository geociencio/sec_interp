"""Base test class and mocks for unittest migration."""

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock


class MockQgsBase:
    """Base class for non-mock QGIS objects to provide standard methods."""

    def isNull(self):
        return False

    def isValid(self):
        return True

    def constGet(self):
        return self

    def get(self):
        return self


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
        # Use a real value but allow it to be a mock if needed
        self._name_val = (
            args[1] if len(args) > 1 else "MockLayer" if len(args) > 0 else ""
        )
        self.name = MagicMock(side_effect=lambda: self._name_val)
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

        # Simple URI parsing for fields: "Point?field=id:integer&field=name:string"
        if "?" in path:
            params = path.split("?")[1].split("&")
            for p in params:
                if p.startswith("field="):
                    f_info = p.split("=")[1].split(":")
                    f_name = f_info[0]
                    from qgis.PyQt.QtCore import QMetaType

                    f_type = QMetaType.Type.QString
                    if len(f_info) > 1:
                        if "int" in f_info[1]:
                            f_type = QMetaType.Type.Int
                        elif "double" in f_info[1] or "float" in f_info[1]:
                            f_type = QMetaType.Type.Double
                    self._internal_fields.append(MockQgsField(f_name, f_type))


class MockQgsRasterLayer(MockQgsMapLayer):
    pass


class MockQgsGeometry(MockQgsBase):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._polyline = []
        self._polygons = []
        self._point = MockQgsPointXY()
        self._wkb_type = 2  # Default LineString
        self._wkt = None

        if args:
            arg = args[0]
            if isinstance(arg, MockQgsGeometry):
                self._polyline = list(arg._polyline)
                self._wkb_type = arg._wkb_type
                self._point = MockQgsPointXY(arg._point.x(), arg._point.y())
                self._polygons = [list(r) for r in arg._polygons]
                self._wkt = arg._wkt
            elif "MockQgsPolygon" in str(type(arg)):
                self._polygons = arg._rings
                self._wkb_type = 3  # Default Polygon
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
    def fromPolygonXY(rings):
        geom = MockQgsGeometry()
        geom._polygons = rings
        geom._wkb_type = 3  # Polygon
        return geom

    @staticmethod
    def fromPolylineXY(points):
        geom = MockQgsGeometry()
        geom._polyline = points
        geom._wkb_type = 2  # LineString
        return geom

    @staticmethod
    def fromPolylineZ(points):
        geom = MockQgsGeometry()
        geom._polyline = points
        geom._wkb_type = 1002  # LineStringZ
        return geom

    @staticmethod
    def fromPolygonZ(rings):
        geom = MockQgsGeometry()
        geom._polygons = rings
        geom._wkb_type = 1003  # PolygonZ
        return geom

    @staticmethod
    def fromPolyline(points):
        if points and (hasattr(points[0], "z") or hasattr(points[0], "_z")):
            return MockQgsGeometry.fromPolylineZ(points)
        return MockQgsGeometry.fromPolylineXY(points)

    @staticmethod
    def fromPointXY(point):
        geom = MockQgsGeometry()
        geom._point = point
        geom._wkb_type = 1
        return geom

    @staticmethod
    def fromWkt(wkt):
        geom = MockQgsGeometry()
        geom._wkt = wkt
        if "LINESTRING" in wkt.upper():
            geom._wkb_type = 2
        elif "POLYGON" in wkt.upper():
            geom._wkb_type = 3
        elif "POINT" in wkt.upper():
            geom._wkb_type = 1
        return geom

    def asWkt(self):
        if self._wkt:
            return self._wkt
        if self._wkb_type in [1, 1001]:
            return f"POINT({self._point.x()} {self._point.y()})"
        if self._polyline:
            pts = ", ".join([f"{p.x()} {p.y()}" for p in self._polyline])
            return f"LINESTRING ({pts})"
        return "GEOMETRYCOLLECTION EMPTY"

    def vertices(self):
        if self._polyline:
            return self._polyline
        if self._wkt and "LINESTRING" in self._wkt.upper():
            try:
                content = self._wkt.upper().split("(")[1].split(")")[0]
                pts = []
                for pair in content.split(","):
                    coords = pair.strip().split()
                    pts.append(MockQgsPointXY(float(coords[0]), float(coords[1])))
                return pts
            except Exception:
                return []
        if self._wkb_type in [1, 1001]:
            return [self._point]
        return []

    def asPolyline(self):
        return self.vertices()

    def asPolygon(self):
        return self._polygons

    def is3D(self):
        return self._wkb_type >= 1000

    def wkbType(self):
        return self._wkb_type

    def pointN(self, n):
        pts = self._polyline if self._polyline else self.vertices()
        if 0 <= n < len(pts):
            return pts[n]
        return None

    def asMultiPolygon(self):
        return [self._polygons]

    def asMultiPolyline(self):
        return [self._polyline]

    def intersection(self, other):
        return self.clone()

    def intersects(self, other):
        return True

    def isEmpty(self):
        return not (self._polyline or self._polygons or self._wkt)

    def isNull(self):
        return False

    def isMultipart(self):
        return False

    def isGeosValid(self):
        return True

    def clone(self):
        new_geom = MockQgsGeometry()
        new_geom._polyline = list(self._polyline)
        new_geom._polygons = [list(r) for r in self._polygons]
        new_geom._point = MockQgsPointXY(self._point.x(), self._point.y())
        new_geom._wkb_type = self._wkb_type
        new_geom._wkt = self._wkt
        return new_geom

    def centroid(self):
        p = self._point
        if self._polyline:
            p = self._polyline[0]
        elif self._polygons and self._polygons[0]:
            p = self._polygons[0][0]
        return MockQgsGeometry.fromPointXY(p)

    def makeValid(self):
        return self

    def wkbType(self):
        return self._wkb_type

    def is3D(self):
        return self._wkb_type >= 1000

    def asPoint(self):
        return self._point

    def type(self):
        # 0: Point, 1: Line, 2: Polygon
        if self._wkb_type in [1, 1001]:
            return 0
        if self._wkb_type in [2, 1002, 4, 1004]:
            return 1
        if self._wkb_type in [3, 1003, 6, 1006]:
            return 2
        return 4

    def length(self):
        verts = self.vertices()
        if len(verts) < 2:
            return 0.0
        total = 0.0
        for i in range(len(verts) - 1):
            p1, p2 = verts[i], verts[i + 1]
            total += ((p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2) ** 0.5
        return total

    def interpolate(self, distance):
        return MockQgsGeometry.fromPointXY(MockQgsPointXY(distance, 0.0))

    def lineLocatePoint(self, point_geom):
        if isinstance(point_geom, MockQgsGeometry):
            return point_geom.asPoint().x()
        return 0.0

    def nearestPoint(self, other):
        if self.type() == 1 and self.vertices():
            verts = self.vertices()
            if all(pt.y() == 0 for pt in verts):
                try:
                    other_pt = other.asPoint()
                    return MockQgsGeometry.fromPointXY(
                        MockQgsPointXY(other_pt.x(), 0.0)
                    )
                except AttributeError:
                    pass
        return other

    def simplify(self, tolerance):
        return self

    def buffer(self, distance, segments):
        geom = MockQgsGeometry()
        geom._wkb_type = 3  # Polygon
        # Add dummy vertices to make it non-empty
        geom._polygons = [
            [
                MockQgsPointXY(0, 0),
                MockQgsPointXY(1, 1),
                MockQgsPointXY(0, 1),
                MockQgsPointXY(0, 0),
            ]
        ]
        return geom

    def densifyByDistance(self, distance):
        return self

    def boundingBox(self):
        verts = self.vertices()
        if not verts:
            return MagicMock()
        min_x = min(p.x() for p in verts)
        max_x = max(p.x() for p in verts)
        min_y = min(p.y() for p in verts)
        max_y = max(p.y() for p in verts)
        box = MagicMock()
        box.width.return_value = max_x - min_x
        box.height.return_value = max_y - min_y
        box.xMinimum.return_value = min_x
        box.xMaximum.return_value = max_x
        box.yMinimum.return_value = min_y
        box.yMaximum.return_value = max_y
        return box

    def transform(self, transform):
        pass
        # Mock transformation: does nothing for now
        pass

    def vertexAt(self, index):
        if self._wkb_type == 1 or self._wkb_type == 1001:  # Point / PointZ
            return self._point

        # For lines and polygons, try to extract point
        all_pts = []
        if self._polyline:
            all_pts = self._polyline
        elif self._polygons and self._polygons[0]:
            # Exterior ring
            ring = self._polygons[0]
            if hasattr(ring, "points"):
                all_pts = ring.points()
            else:
                all_pts = ring

        if 0 <= index < len(all_pts):
            return all_pts[index]

        return MockQgsPoint(0, 0, 0)


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
        if isinstance(x, (MockQgsPoint, MockQgsPointXY)):
            self._x, self._y, self._z = x.x(), x.y(), getattr(x, "z", lambda: 0)()
        elif isinstance(x, (tuple, list)):
            self._x, self._y = float(x[0]), float(x[1])
            self._z = float(x[2]) if len(x) > 2 else 0.0
        else:
            self._x, self._y, self._z = float(x), float(y), float(z)

    def x(self):
        return self._x

    def y(self):
        return self._y

    def z(self):
        return self._z

    def setX(self, x):
        self._x = float(x)

    def setY(self, y):
        self._y = float(y)

    def setZ(self, z):
        self._z = float(z)

    def __iter__(self):
        yield self._x
        yield self._y


class MockQgsPointXY(MockQgsPoint):
    def __init__(self, x=0, y=0):
        if isinstance(x, (MockQgsPoint, MockQgsPointXY)):
            super().__init__(x.x(), x.y(), 0)
        else:
            super().__init__(x, y, 0)

    def distance(self, other):
        return ((self._x - other.x()) ** 2 + (self._y - other.y()) ** 2) ** 0.5

    def azimuth(self, other):
        import math

        dx = other.x() - self._x
        dy = other.y() - self._y
        angle = math.degrees(math.atan2(dx, dy))
        if angle < 0:
            angle += 360
        return angle

    def compare(self, other, epsilon=1e-6):
        return self.distance(other) < epsilon


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

    def setDestinationCrs(self, crs, context):
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

    def indexFromName(self, name):
        return self.indexOf(name)

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
        self._window_title = title

    def windowTitle(self):
        return getattr(self, "_window_title", "")

    def property(self, name):
        return getattr(self, f"_prop_{name}", None)

    def setProperty(self, name, value):
        setattr(self, f"_prop_{name}", value)
        return True

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

    def setIcon(self, icon):
        pass

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


import types

# --- 1. Utility Classes and Functions for Mocking ---


class ModuleProxy(types.ModuleType):
    """A stable module proxy that holds Mock classes and delegates to an internal MagicMock."""

    def __init__(self, name):
        super().__init__(name)
        self._mock = MagicMock(name=name)

    def __getattr__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            # Fallback to the internal mock for any dynamic attributes
            return getattr(self._mock, name)

    def __setattr__(self, name, value):
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            # Store stable attributes directly on the module-like proxy
            super().__setattr__(name, value)

    def reset_mock(self, *args, **kwargs):
        self._mock.reset_mock(*args, **kwargs)


def mock_geometry_type(wkb):
    """Calculates the QGIS geometry type from WKB code."""
    if wkb == 1:
        return 0  # PointGeometry
    if wkb == 2:
        return 1  # LineGeometry
    if wkb in [3, 1003]:
        return 2  # PolygonGeometry
    return wkb


class MockSignal:
    def __init__(self, *args, **kwargs):
        self._slots = []
        self.emit = MagicMock(side_effect=self._emit_to_slots)
        self.connect = MagicMock(side_effect=self._connect_slot)
        self.disconnect = MagicMock()

    def _connect_slot(self, slot):
        self._slots.append(slot)

    def _emit_to_slots(self, *args, **kwargs):
        for slot in self._slots:
            try:
                slot(*args, **kwargs)
            except Exception:
                pass


def mock_signal(*args, **kwargs):
    return MockSignal(*args, **kwargs)


# --- 2. Define Stable Mock Classes ---


class MockQgsWkbTypes:
    Point, LineString, Polygon = 1, 2, 3
    PointZ, LineStringZ, PolygonZ = 1001, 1002, 1003
    MultiPoint, MultiLineString, MultiPolygon = 4, 5, 6
    MultiPointZ, MultiLineStringZ, MultiPolygonZ = 1004, 1005, 1006
    Point25D, LineString25D, Polygon25D = 1001, 1002, 1003

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


class MockQPoint:
    def __init__(self, x, y):
        self._x, self._y = x, y

    def x(self):
        return self._x

    def y(self):
        return self._y


class MockQgsMapCanvas(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene = MagicMock()
        self.layers = MagicMock(return_value=[])


class MockQPainter(MagicMock):
    Antialiasing = 1

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)


class MockQImage(MagicMock):
    Format_ARGB32 = 0

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)


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


# --- 3. Initialize Proxies and Modules ---

mock_core = ModuleProxy("qgis.core")
mock_gui = ModuleProxy("qgis.gui")
mock_qtwidgets = ModuleProxy("qgis.PyQt.QtWidgets")
mock_qtcore = ModuleProxy("qgis.PyQt.QtCore")
mock_qtgui = ModuleProxy("qgis.PyQt.QtGui")
mock_processing = MagicMock(name="processing")


def restore_mocks():
    """Re-assigns all stable mock classes to their respective proxies."""
    if os.environ.get("FORCE_MOCKS", "1") == "0":
        return

    # Qt Widgets
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
    mock_qtwidgets.QMainWindow = MockQWidget

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
    mock_core.QgsProperty = MockQgsProperty
    mock_core.QgsPropertyCollection = MockQgsPropertyCollection
    mock_core.QgsPalLayerSettings = MockQgsPalLayerSettings
    mock_core.QgsTextFormat = MockQgsTextFormat
    mock_core.QgsVectorLayerSimpleLabeling = MockQgsVectorLayerSimpleLabeling
    mock_core.QgsSingleSymbolRenderer = MockQgsSingleSymbolRenderer
    mock_core.QgsLineSymbol = MockQgsLineSymbol
    mock_core.QgsMarkerSymbol = MockQgsMarkerSymbol
    mock_core.QgsTask = MockQgsTask
    mock_core.Qgis = MockQgis
    mock_core.QgsWkbTypes = MockQgsWkbTypes

    # Specialized logic for unit types and message logs
    if not hasattr(mock_core, "QgsUnitTypes"):
        mock_core.QgsUnitTypes = MagicMock(name="QgsUnitTypes")
    mock_core.QgsUnitTypes.DistanceUnit.Meters = 0
    mock_core.QgsUnitTypes.toString = lambda x: "meters"

    if not hasattr(mock_core, "QgsMessageLog"):
        mock_core.QgsMessageLog = MagicMock(name="QgsMessageLog")

    # Gui
    mock_gui.QgsMapTool = MockQgsMapTool
    mock_gui.QgsMapToolEmitPoint = MockQgsMapTool
    mock_gui.QgsMapToolPan = MockQgsMapTool
    mock_gui.QgsRubberBand = MockQgsRubberBand
    mock_gui.QgsVertexMarker = MockQgsVertexMarker
    mock_gui.QgsMapCanvas = MockQgsMapCanvas

    # QtCore
    mock_qtcore.QPoint = MockQPoint
    mock_qtcore.QRectF = MockQRectF
    mock_qtcore.QSize = MagicMock
    mock_qtcore.Qt.LeftButton = 1
    mock_qtcore.Qt.RightButton = 2
    mock_qtcore.Qt.Key_Return, mock_qtcore.Qt.Key_Enter = 16777220, 16777221
    mock_qtcore.Qt.Key_Escape = 16777216
    mock_qtcore.Qt.CrossCursor = 2
    mock_qtcore.pyqtSignal = mock_signal
    mock_qtcore.QObject = MagicMock
    mock_qtcore.QThread = MockQThread
    mock_qtcore.QCoreApplication = MockQApplication
    mock_qtcore.QCoreApplication.translate = lambda c, t: t
    mock_qtcore.QCoreApplication.installTranslator = lambda t: None

    # QtGui
    mock_qtgui.QPainter = MockQPainter
    mock_qtgui.QImage = MockQImage
    mock_qtgui.QColor = MockQColor
    mock_qtgui.QPen = MagicMock
    mock_qtgui.QBrush = MagicMock

    # Specialized mocks (MagicMock based) - RESET instead of REASSIGN
    def get_or_reset(module, name):
        if not hasattr(module, name):
            setattr(module, name, MagicMock(name=name))
        m = getattr(module, name)
        if hasattr(m, "reset_mock"):
            m.reset_mock()
        return m

    qgs_project = get_or_reset(mock_core, "QgsProject")
    qgs_project.instance.side_effect = MockQgsProject.instance

    writer = get_or_reset(mock_core, "QgsVectorFileWriter")
    writer.NoError = 0

    def create_real_writer(
        output_path, fields, geometry_type, crs, transform_context, options
    ):
        """Mock writer that creates actual shapefile-like files for testing."""
        import os

        base_path = os.path.splitext(output_path)[0]

        # Create immediate files to simulate successful export
        def mock_addFeature(feature):
            return True

        def mock_flushBuffer():
            pass

        # Create mock writer object that actually creates files on first feature add
        mock_writer = MagicMock()
        mock_writer.hasError.return_value = 0
        mock_writer.errorMessage.return_value = ""
        mock_writer.addFeature.side_effect = mock_addFeature
        mock_writer.flushBuffer.side_effect = mock_flushBuffer

        # Immediately create files since export will succeed
        def create_files_now():
            # Create main .shp file
            with open(output_path, "w") as f:
                f.write("# Mock shapefile created for testing\n")

            # Create supporting files including .qml for tests that need it
            for ext in [".shx", ".dbf", ".prj", ".qml"]:
                support_path = base_path + ext
                with open(support_path, "w") as f:
                    if ext == ".prj":
                        f.write(
                            'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","4326"]]'
                        )
                    elif ext == ".qml":
                        f.write(
                            '<!DOCTYPE qgis PUBLIC "http://mrcc.com/qgis.dtd" "SYSTEM">\n<qgis version="3.28.0-Firenze"></qgis>\n'
                        )
                    else:
                        f.write(f"# Mock {ext} file for testing\n")

        # Create files immediately to simulate successful export
        create_files_now()

        return mock_writer

    writer.create.side_effect = create_real_writer
    writer.writeAsVectorFormatV3.return_value = (0, "", "", "")


def apply_mock_patches():
    """Apply mock patches to sys.modules for unit testing."""
    import types

    global qgis_pkg, pyqt_pkg

    if not hasattr(sys.modules, "qgis_pkg"):
        qgis_pkg = types.ModuleType("qgis")
        qgis_pkg.__path__ = []

    if not hasattr(sys.modules, "pyqt_pkg"):
        pyqt_pkg = types.ModuleType("qgis.PyQt")
        pyqt_pkg.__path__ = []

    sys.modules["qgis"] = qgis_pkg
    sys.modules["qgis.core"] = mock_core
    sys.modules["qgis.gui"] = mock_gui
    qgis_pkg.core, qgis_pkg.gui = mock_core, mock_gui

    sys.modules["qgis.PyQt"] = pyqt_pkg
    qgis_pkg.PyQt = pyqt_pkg

    sys.modules["qgis.PyQt.QtWidgets"] = mock_qtwidgets
    sys.modules["qgis.PyQt.QtCore"] = mock_qtcore
    sys.modules["qgis.PyQt.QtGui"] = mock_qtgui
    pyqt_pkg.QtWidgets, pyqt_pkg.QtCore, pyqt_pkg.QtGui = (
        mock_qtwidgets,
        mock_qtcore,
        mock_qtgui,
    )

    sys.modules["qgis.PyQt.QtSvg"] = MagicMock()
    sys.modules["processing"] = mock_processing
    sys.modules["qgis.processing"] = mock_processing
    qgis_pkg.processing = mock_processing
    restore_mocks()


def remove_mock_patches():
    """Remove mock patches from sys.modules to allow real QGIS usage."""
    for m in list(sys.modules.keys()):
        if m.startswith("qgis") or m == "processing":
            del sys.modules[m]


# Initial check
try:
    import qgis.core

    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False

# Initial setup
if not CORE_AVAILABLE or os.environ.get("FORCE_MOCKS", "1") == "1":
    apply_mock_patches()
else:
    restore_mocks()


# --- 6. Base Test Case Implementation ---


class BaseTestCase(unittest.TestCase):
    """Base test case providing environment management and shared data properties."""

    @classmethod
    def setUpClass(cls):
        """Ensure mocks are applied for unit tests."""
        if CORE_AVAILABLE and os.environ.get("FORCE_MOCKS", "1") == "1":
            apply_mock_patches()

    def setUp(self):
        """Set up temporary test directory and reset shared mock states."""
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.test_dir)

        # Reset custom shared mock states BEFORE each test
        MockQgsProject.instance().clear()
        MockQgsSettings._shared_values.clear()

    def tearDown(self):
        """Clean up test directory and perform surgical mock resets."""
        if hasattr(self, "test_dir") and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

        # Reset Proxy mocks to clear call history without destroying attributes
        mock_qtwidgets.reset_mock()
        mock_core.reset_mock()
        mock_gui.reset_mock()
        mock_qtcore.reset_mock()
        mock_qtgui.reset_mock()

        # Re-assign stable classes in case they were polluted by direct assignments
        restore_mocks()

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
