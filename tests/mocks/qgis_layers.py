"""QGIS Layer mocks."""

from unittest.mock import MagicMock
from .qgis_base import MockQObject
from .qgis_core import MockQgsCoordinateReferenceSystem, MockQgsRectangle
from .qgis_features import MockQgsFields, MockQgsField


class MockQgsMapLayer(MockQObject):
    """Mock implementation for QgsMapLayer."""

    VectorLayer = 0
    RasterLayer = 1

    class LayerType:
        """Layer type constants."""

        VectorLayer = 0
        RasterLayer = 1
        PluginLayer = 2
        MeshLayer = 3
        VectorTileLayer = 4
        PointCloudLayer = 5
        AnnotationLayer = 6

    def __init__(self, *args, **kwargs):
        """Initialize the mock map layer."""
        super().__init__(*args, **kwargs)
        self._dataProvider = MagicMock()
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

        self._provider = MagicMock()
        self._dataProvider.return_value = self._provider
        self.dataProvider = self._dataProvider
        self._internal_fields = MockQgsFields()
        self._provider.addAttributes.side_effect = self._add_attributes
        self._provider.addFeatures.side_effect = self._add_features
        self._features = []

        self._provider.sample.return_value = (100.0, True)
        self._provider.identify.return_value = MagicMock()
        self._provider.identify().isValid.return_value = True
        self._provider.identify().results.return_value = {1: 100.0}

        self._crs = MockQgsCoordinateReferenceSystem()

    def crs(self):
        """Get the layer CRS."""
        return self._crs

    def fields(self):
        """Get the layer fields."""
        return self._internal_fields

    def _add_attributes(self, fields):
        """Add attributes to the internal fields (mock side effect)."""
        for f in fields:
            self._internal_fields.append(f)
        return True

    def _add_features(self, features):
        """Add features to the layer (mock side effect)."""
        self._features.extend(features)
        self.getFeatures.return_value = iter(self._features)
        return True

    def isValid(self):
        """Check if the layer is valid."""
        return True

    def featureCount(self):
        """Get the number of features."""
        return len(self._features)

    def setCrs(self, crs):
        """Set the layer CRS."""
        pass

    def dataProvider(self):
        """Get the data provider."""
        return self._dataProvider

    def updateFields(self):
        """Update fields."""
        pass

    def rasterUnitsPerPixelX(self):
        """Get raster units per pixel X."""
        return 1.0

    def source(self):
        """Get the layer source."""
        return "mock_source"

    def updateExtents(self):
        """Update layer extents."""
        pass

    def setLabeling(self, labeling):
        """Set layer labeling."""
        pass

    def setLabelsEnabled(self, enabled):
        """Set if labels are enabled."""
        self._labels_enabled = enabled

    def saveNamedStyle(self, path):
        """Save named style to path."""
        return "Success", True

    def labelsEnabled(self):
        """Check if labels are enabled."""
        return getattr(self, "_labels_enabled", False)

    def wkbType(self):
        """Get WKB type."""
        return 3

    def extent(self):
        """Get the layer extent."""
        return MockQgsRectangle(0, 0, 100, 100)


class MockQgsVectorLayer(MockQgsMapLayer):
    """Mock implementation for QgsVectorLayer."""

    def __init__(self, path="path", name="layer", provider="memory", options=None):
        """Initialize the mock vector layer mapping path attributes to fields."""
        super().__init__(path, name)
        if "?" in path:
            params = path.split("?")[1].split("&")
            for p in params:
                if p.startswith("field="):
                    f_info = p.split("=")[1].split(":")
                    f_name = f_info[0]
                    # Direct check instead of QMetaType for simplicity in mocks
                    f_type = 10  # String
                    if len(f_info) > 1:
                        if "int" in f_info[1]:
                            f_type = 2
                        elif "double" in f_info[1] or "float" in f_info[1]:
                            f_type = 6
                    self._internal_fields.append(MockQgsField(f_name, f_type))


class MockQgsRasterLayer(MockQgsMapLayer):
    """Mock implementation for QgsRasterLayer."""

    pass
