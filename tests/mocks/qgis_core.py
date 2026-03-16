"""QGIS Core utility mocks."""

from unittest.mock import MagicMock
from .qgis_base import MockQgsBase


class MockQgsCoordinateReferenceSystem(MockQgsBase):
    """Mock implementation for QgsCoordinateReferenceSystem."""

    def __init__(self, authid="EPSG:4326"):
        """Initialize the mock CRS with the given authority ID."""
        super().__init__()
        self._authid = authid

    def authid(self):
        """Get the authority ID."""
        return self._authid

    def ellipsoidAcronym(self):
        """Get the ellipsoid acronym."""
        return "WGS84"

    def isValid(self):
        """Check if the CRS is valid."""
        return True


class MockQgsCoordinateTransform(MockQgsBase):
    """Mock implementation for QgsCoordinateTransform."""

    def __init__(self, src_crs=None, dest_crs=None, project=None):
        """Initialize the mock transform."""
        super().__init__()

    def transform(self, geom):
        """Transform the geometry (no-op in mock)."""
        return geom


class MockQgsSpatialIndex:
    """Mock implementation for QgsSpatialIndex."""

    def __init__(self, features=None):
        """Initialize the mock spatial index."""
        if features:
            self._fids = [
                f.id() if hasattr(f, "id") else i for i, f in enumerate(features)
            ]
        else:
            self._fids = []

    def intersects(self, rect):
        """Perform intersection query (returns all IDs in mock for simplicity)."""
        return self._fids


class MockQgsFeatureRequest:
    """Mock implementation for QgsFeatureRequest."""

    NoGeometry = 1

    def setFilterFids(self, fids):
        """Set filter FIDs."""
        return self

    def setFilterExpression(self, expr):
        """Set filter expression."""
        return self

    def setDestinationCrs(self, crs, context):
        """Set destination CRS."""
        self._dest_crs = crs
        return self

    def destinationCrs(self):
        """Get destination CRS."""
        return getattr(self, "_dest_crs", None)

    def setFilterRect(self, rect):
        """Set filter rectangle."""
        self._rect = rect
        return self

    def filterRect(self):
        """Get filter rectangle."""
        return getattr(self, "_rect", None)

    def setFilterRect(self, rect):
        """Set filter rectangle."""
        return self

    def setFilterExpression(self, expression):
        """Set filter expression."""
        return self

    def setSubsetOfAttributes(self, attributes, fields):
        """Set subset of attributes."""
        return self

    def setDestinationCrs(self, crs, context=None):
        """Set destination CRS."""
        return self


class MockQgsRectangle(MockQgsBase):
    """Mock implementation for QgsRectangle."""

    def __init__(self, xmin=0, ymin=0, xmax=0, ymax=0):
        """Initialize the mock rectangle."""
        super().__init__()
        self._xmin, self._ymin, self._xmax, self._ymax = xmin, ymin, xmax, ymax

    def xMinimum(self):
        """Get minimum X coordinate."""
        return self._xmin

    def yMinimum(self):
        """Get minimum Y coordinate."""
        return self._ymin

    def xMaximum(self):
        """Get maximum X coordinate."""
        return self._xmax

    def yMaximum(self):
        """Get maximum Y coordinate."""
        return self._ymax

    def width(self):
        """Get rectangle width."""
        return self._xmax - self._xmin

    def height(self):
        """Get rectangle height."""
        return self._ymax - self._ymin

    def combineExtentWith(self, other):
        """Combine this extent with another extent."""
        self._xmin = min(self._xmin, other.xMinimum())
        self._ymin = min(self._ymin, other.yMinimum())
        self._xmax = max(self._xmax, other.xMaximum())
        self._ymax = max(self._ymax, other.yMaximum())


class MockQgsProject(MockQgsBase):
    """Mock implementation for QgsProject (Singleton)."""

    _instance = None

    def __init__(self):
        """Initialize the mock project."""
        super().__init__()
        self._layers = {}
        self._settings = {}

    @classmethod
    def instance(cls):
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = MockQgsProject()
        return cls._instance

    def mapLayers(self):
        """Get all map layers."""
        return self._layers

    def mapLayer(self, layer_id):
        """Get map layer by ID."""
        return self._layers.get(layer_id)

    def mapLayersByName(self, name):
        """Get map layers by name."""
        return [l for l in self._layers.values() if l.name() == name]

    def addMapLayer(self, layer, addToLegend=True):
        """Add a map layer to the project."""
        self._layers[layer.id()] = layer
        return layer

    def removeMapLayer(self, layer_id):
        """Remove a map layer from the project."""
        if layer_id in self._layers:
            del self._layers[layer_id]
        elif hasattr(layer_id, "id"):  # In case a layer object is passed
            lid = layer_id.id()
            if lid in self._layers:
                del self._layers[lid]

    def crs(self):
        """Get the project CRS."""
        return MockQgsCoordinateReferenceSystem()

    def transformContext(self):
        """Get dummy transform context."""
        return MagicMock()

    def readEntry(self, scope, key, default=""):
        """Read entry from project settings."""
        val = self._settings.get(f"{scope}/{key}", default)
        return val, True

    def writeEntry(self, scope, key, value):
        """Write entry to project settings."""
        self._settings[f"{scope}/{key}"] = value
        return True, True

    def clear(self):
        """Clear all layers and settings (internal use)."""
        self._layers.clear()
        self._settings.clear()


class MockQgsSettings(MockQgsBase):
    """Mock implementation for QgsSettings (Shared state)."""

    _shared_values = {}

    def __init__(self):
        """Initialize mock settings."""
        super().__init__()

    def value(self, key, default=None, type=None):
        """Get value for key."""
        return self._shared_values.get(key, default)

    def setValue(self, key, value):
        """Set value for key."""
        self._shared_values[key] = value

    def beginGroup(self, group):
        """Begin group (no-op in mock)."""
        pass

    def endGroup(self):
        """End group (no-op in mock)."""
        pass

    def sync(self):
        """Sync settings (no-op in mock)."""
        pass

    def contains(self, key):
        """Check if settings contain key."""
        return key in self._shared_values

    def remove(self, key):
        """Remove key from settings."""
        if key in self._shared_values:
            del self._shared_values[key]


class MockQgsDistanceArea(MockQgsBase):
    """Mock implementation for QgsDistanceArea."""

    def __init__(self):
        """Initialize the mock distance area."""
        super().__init__()
        self._ellipsoid = "WGS84"

    def setEllipsoid(self, ellipsoid):
        """Set ellipsoid."""
        self._ellipsoid = ellipsoid

    def ellipsoid(self):
        """Get ellipsoid."""
        return self._ellipsoid

    def measureLine(self, p1, p2):
        """Measure distance between two points (Euclidean in mock)."""
        import math

        return math.sqrt((p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2)
