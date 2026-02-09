"""QGIS Core utility mocks."""

from unittest.mock import MagicMock
from .qgis_base import MockQgsBase


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

    def setDestinationCrs(self, crs, context=None):
        return self


class MockQgsRectangle(MockQgsBase):
    def __init__(self, xmin=0, ymin=0, xmax=0, ymax=0):
        super().__init__()
        self._xmin, self._ymin, self._xmax, self._ymax = xmin, ymin, xmax, ymax

    def xMinimum(self):
        return self._xmin

    def yMinimum(self):
        return self._ymin

    def xMaximum(self):
        return self._xmax

    def yMaximum(self):
        return self._ymax

    def width(self):
        return self._xmax - self._xmin

    def height(self):
        return self._ymax - self._ymin

    def combineExtentWith(self, other):
        self._xmin = min(self._xmin, other.xMinimum())
        self._ymin = min(self._ymin, other.yMinimum())
        self._xmax = max(self._xmax, other.xMaximum())
        self._ymax = max(self._ymax, other.yMaximum())


class MockQgsProject(MockQgsBase):
    _instance = None

    def __init__(self):
        super().__init__()
        self._layers = {}
        self._settings = {}

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = MockQgsProject()
        return cls._instance

    def mapLayers(self):
        return self._layers

    def mapLayer(self, layer_id):
        return self._layers.get(layer_id)

    def mapLayersByName(self, name):
        return [l for l in self._layers.values() if l.name() == name]

    def addMapLayer(self, layer, addToLegend=True):
        self._layers[layer.id()] = layer
        return layer

    def removeMapLayer(self, layer_id):
        if layer_id in self._layers:
            del self._layers[layer_id]
        elif hasattr(layer_id, "id"):  # In case a layer object is passed
            lid = layer_id.id()
            if lid in self._layers:
                del self._layers[lid]

    def crs(self):
        return MockQgsCoordinateReferenceSystem()

    def transformContext(self):
        return MagicMock()

    def readEntry(self, scope, key, default=""):
        val = self._settings.get(f"{scope}/{key}", default)
        return val, True

    def writeEntry(self, scope, key, value):
        self._settings[f"{scope}/{key}"] = value
        return True, True

    def clear(self):
        self._layers.clear()
        self._settings.clear()


class MockQgsSettings(MockQgsBase):
    _shared_values = {}

    def __init__(self):
        super().__init__()

    def value(self, key, default=None, type=None):
        return self._shared_values.get(key, default)

    def setValue(self, key, value):
        self._shared_values[key] = value

    def beginGroup(self, group):
        pass

    def endGroup(self):
        pass

    def contains(self, key):
        return key in self._shared_values
