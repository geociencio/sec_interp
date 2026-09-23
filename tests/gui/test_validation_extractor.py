"""Tests for the validation extraction adapter (extent/pixel extraction)."""

from unittest.mock import MagicMock

from tests.base_test import BaseTestCase
from tests.mocks.qgis_core import (
    MockQgsCoordinateReferenceSystem,
    MockQgsRectangle,
)

from sec_interp.gui.adapters.validation_extractor import extract_raster_metadata


def _raster_layer(extent, pixel=1.0, crs=None):
    layer = MagicMock()
    layer.name.return_value = "DEM"
    layer.isValid.return_value = True
    layer.bandCount.return_value = 1
    layer.crs.return_value = crs or MockQgsCoordinateReferenceSystem("EPSG:4326")
    layer.extent.return_value = extent
    layer.rasterUnitsPerPixelX.return_value = pixel
    return layer


class TestRasterMetadataExtraction(BaseTestCase):
    """Raster metadata carries extent and pixel size for CRS checks."""

    def test_populates_extent_and_pixel(self):
        layer = _raster_layer(MockQgsRectangle(-99.0, 22.7, -98.99, 23.0), pixel=0.000138)

        metadata = extract_raster_metadata(layer)

        self.assertAlmostEqual(metadata.extent_xmin, -99.0)
        self.assertAlmostEqual(metadata.extent_ymin, 22.7)
        self.assertAlmostEqual(metadata.extent_xmax, -98.99)
        self.assertAlmostEqual(metadata.extent_ymax, 23.0)
        self.assertAlmostEqual(metadata.pixel_size_x, 0.000138)

    def test_empty_extent_is_left_as_none(self):
        extent = MagicMock()
        extent.isEmpty.return_value = True
        layer = _raster_layer(extent)

        metadata = extract_raster_metadata(layer)

        self.assertIsNone(metadata.extent_xmin)
        self.assertIsNone(metadata.extent_xmax)
