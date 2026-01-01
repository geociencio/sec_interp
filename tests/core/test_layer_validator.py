"""Tests for layer validation utilities."""

from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase, MockQgsProject
from qgis.core import (
    QgsVectorLayer,
    QgsRasterLayer,
    QgsWkbTypes,
    QgsCoordinateReferenceSystem,
    QgsMapLayer
)

from sec_interp.core.validation.layer_validator import (
    validate_layer_exists,
    validate_layer_has_features,
    validate_layer_geometry,
    validate_raster_band,
    validate_structural_requirements,
    validate_crs_compatibility
)
from sec_interp.core.types import FieldType


class TestLayerValidator(BaseTestCase):
    """Tests for layer_validator.py"""

    def setUp(self):
        super().setUp()
        # Reset MockQgsProject instance
        MockQgsProject._instance = None
        self.project = MockQgsProject.instance()

    def test_validate_layer_exists_none(self):
        """Test validation with None layer name."""
        is_valid, msg, lyr = validate_layer_exists(None)
        self.assertFalse(is_valid)
        self.assertEqual(msg, "Layer name is required")

    def test_validate_layer_exists_by_id(self):
        """Test layer lookup by ID."""
        layer = QgsVectorLayer()
        layer.id = MagicMock(return_value="layer1")
        layer.isValid = MagicMock(return_value=True)
        self.project.addMapLayer(layer)

        is_valid, msg, lyr = validate_layer_exists("layer1")
        self.assertTrue(is_valid)
        self.assertEqual(lyr, layer)

    def test_validate_layer_exists_by_name(self):
        """Test layer lookup by name."""
        layer = QgsVectorLayer()
        layer.id = MagicMock(return_value="id123")
        layer.name = MagicMock(return_value="My Layer")
        layer.isValid = MagicMock(return_value=True)
        self.project.addMapLayer(layer)

        is_valid, msg, lyr = validate_layer_exists("My Layer")
        self.assertTrue(is_valid)
        self.assertEqual(lyr, layer)

    def test_validate_layer_exists_not_found(self):
        """Test case where layer is not in project."""
        # Ensure project is empty
        self.project._layers = {}
        is_valid, msg, lyr = validate_layer_exists("Missing")
        self.assertFalse(is_valid)
        self.assertIn("not found", msg)

    def test_validate_layer_has_features(self):
        """Test feature count validation."""
        layer = QgsVectorLayer()
        layer.featureCount = MagicMock(return_value=5)

        is_valid, msg = validate_layer_has_features(layer)
        self.assertTrue(is_valid)

        layer.featureCount = MagicMock(return_value=0)
        layer.name = MagicMock(return_value="Empty")
        is_valid, msg = validate_layer_has_features(layer)
        self.assertFalse(is_valid)
        self.assertIn("has no features", msg)

    def test_validate_layer_geometry(self):
        """Test geometry type validation."""
        layer = QgsVectorLayer()
        # PointGeometry = 0
        layer.wkbType = MagicMock(return_value=QgsWkbTypes.Point)

        is_valid, msg = validate_layer_geometry(layer, QgsWkbTypes.PointGeometry)
        self.assertTrue(is_valid)

        # Mismatch
        is_valid, msg = validate_layer_geometry(layer, QgsWkbTypes.LineGeometry)
        self.assertFalse(is_valid)
        self.assertIn("Found Point, but expected Line", msg)

    def test_validate_raster_band(self):
        """Test raster band validation."""
        layer = QgsRasterLayer()
        layer.bandCount = MagicMock(return_value=1)

        is_valid, msg = validate_raster_band(layer, 1)
        self.assertTrue(is_valid)

        is_valid, msg = validate_raster_band(layer, 2)
        self.assertFalse(is_valid)
        self.assertIn("invalid", msg)

    def test_validate_structural_requirements(self):
        """Test structural layer requirements."""
        layer = QgsVectorLayer()
        layer.isValid = MagicMock(return_value=True)
        layer.wkbType = MagicMock(return_value=QgsWkbTypes.Point)

        # Mock field validation
        with patch("sec_interp.core.validation.layer_validator.validate_field_exists", return_value=(True, "")), \
             patch("sec_interp.core.validation.layer_validator.validate_field_type", return_value=(True, "")):

            is_valid, msg = validate_structural_requirements(layer, "Struct", "dip", "strike")
            self.assertTrue(is_valid)

    def test_validate_crs_compatibility(self):
        """Test CRS compatibility warning."""
        lyr1 = QgsVectorLayer()
        lyr1.isValid = MagicMock(return_value=True)
        crs1 = MagicMock()
        crs1.authid.return_value = "EPSG:4326"
        lyr1.crs = MagicMock(return_value=crs1)

        lyr2 = QgsVectorLayer()
        lyr2.isValid = MagicMock(return_value=True)
        crs2 = MagicMock()
        crs2.authid.return_value = "EPSG:3857"
        lyr2.crs = MagicMock(return_value=crs2)

        is_valid, msg = validate_crs_compatibility([lyr1, lyr2])
        self.assertFalse(is_valid)
        self.assertIn("CRS mismatch detected", msg)

        # Consistent CRS
        lyr2.crs = MagicMock(return_value=crs1)
        is_valid, msg = validate_crs_compatibility([lyr1, lyr2])
        self.assertTrue(is_valid)
