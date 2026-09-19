"""Tests for layer validation utilities (QGIS-agnostic)."""

from unittest.mock import patch
from tests.base_test import BaseTestCase

from sec_interp.core.validation.layer_validator import (
    validate_layer_has_features,
    validate_layer_geometry,
    validate_raster_band,
    validate_structural_requirements,
    validate_crs_compatibility,
)
from sec_interp.core.validation.layer_metadata import (
    GEOMETRY_LINE,
    GEOMETRY_POINT,
    KIND_RASTER,
    KIND_VECTOR,
    LayerMetadata,
)


def _vector_metadata(geometry_type=GEOMETRY_POINT, feature_count=5):
    return LayerMetadata(
        name="Layer",
        is_valid=True,
        kind=KIND_VECTOR,
        geometry_type=geometry_type,
        feature_count=feature_count,
    )


class TestLayerValidator(BaseTestCase):
    """Tests for layer_validator.py"""

    def test_validate_layer_has_features(self):
        """Test feature count validation."""
        metadata = _vector_metadata(feature_count=5)
        self.assertTrue(validate_layer_has_features(metadata)[0])

        empty = _vector_metadata(feature_count=0)
        is_valid, msg = validate_layer_has_features(empty)
        self.assertFalse(is_valid)
        self.assertIn("has no features", msg)

    def test_validate_layer_geometry(self):
        """Test geometry type validation."""
        metadata = _vector_metadata(geometry_type=GEOMETRY_POINT)
        self.assertTrue(validate_layer_geometry(metadata, GEOMETRY_POINT)[0])

        is_valid, msg = validate_layer_geometry(metadata, GEOMETRY_LINE)
        self.assertFalse(is_valid)
        self.assertIn("Found Point, but expected Line", msg)

    def test_validate_raster_band(self):
        """Test raster band validation."""
        metadata = LayerMetadata(
            name="Raster", is_valid=True, kind=KIND_RASTER, band_count=1
        )
        self.assertTrue(validate_raster_band(metadata, 1)[0])

        is_valid, msg = validate_raster_band(metadata, 2)
        self.assertFalse(is_valid)
        self.assertIn("invalid", msg)

    def test_validate_structural_requirements(self):
        """Test structural layer requirements."""
        metadata = _vector_metadata(geometry_type=GEOMETRY_POINT)

        with (
            patch(
                "sec_interp.core.validation.layer_validator.validate_field_exists",
                return_value=(True, ""),
            ),
            patch(
                "sec_interp.core.validation.layer_validator.validate_field_type",
                return_value=(True, ""),
            ),
        ):
            is_valid, msg = validate_structural_requirements(
                metadata, "dip", "strike"
            )
            self.assertTrue(is_valid)

    def test_validate_crs_compatibility(self):
        """Test CRS compatibility warning."""
        lyr1 = _vector_metadata()
        lyr1.crs_authid = "EPSG:4326"
        lyr2 = _vector_metadata()
        lyr2.crs_authid = "EPSG:3857"

        is_valid, msg = validate_crs_compatibility([lyr1, lyr2])
        self.assertFalse(is_valid)
        self.assertIn("CRS mismatch detected", msg)

        lyr2.crs_authid = "EPSG:4326"
        is_valid, msg = validate_crs_compatibility([lyr1, lyr2])
        self.assertTrue(is_valid)
