"""Tests for the GUI geometry adapter (CRS-aware sampling safety)."""

from unittest.mock import MagicMock, patch

from sec_interp.gui.adapters import geometry
from tests.base_test import BaseTestCase
from tests.mocks.qgis_core import MockQgsCoordinateReferenceSystem


class _ScalingTransform:
    """Fake transform that scales X to simulate degrees -> metres conversion."""

    def __init__(self, src_crs=None, dest_crs=None, context=None, factor=1000.0):
        self._factor = factor

    def transform(self, point):
        return geometry.QgsPointXY(point.x() * self._factor, point.y())


class TestRasterResolutionInCrs(BaseTestCase):
    """The DEM pixel size must be expressed in the target CRS units."""

    def _raster(self, res, crs):
        raster = MagicMock()
        raster.rasterUnitsPerPixelX.return_value = res
        raster.crs.return_value = crs
        center = MagicMock()
        center.x.return_value = 0.0
        center.y.return_value = 0.0
        raster.extent.return_value.center.return_value = center
        return raster

    def test_same_crs_returns_raw_resolution(self):
        """Matching CRSs need no transform: raw pixel size is used."""
        crs = MockQgsCoordinateReferenceSystem("EPSG:32614")
        raster = self._raster(10.0, crs)

        result = geometry.raster_resolution_in_crs(raster, crs)

        self.assertEqual(result, 10.0)

    def test_different_crs_transforms_resolution(self):
        """A different CRS is transformed before being used as interval."""
        raster = self._raster(0.000138, MockQgsCoordinateReferenceSystem("EPSG:4326"))
        target = MockQgsCoordinateReferenceSystem("EPSG:32614")

        with patch.object(geometry, "QgsCoordinateTransform", _ScalingTransform):
            result = geometry.raster_resolution_in_crs(raster, target)

        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 0.138)

    def test_invalid_resolution_returns_none(self):
        """Zero/negative pixel sizes yield None so a fallback can be used."""
        raster = self._raster(0.0, MockQgsCoordinateReferenceSystem("EPSG:4326"))
        target = MockQgsCoordinateReferenceSystem("EPSG:32614")

        self.assertIsNone(geometry.raster_resolution_in_crs(raster, target))


class TestResolveSamplingInterval(BaseTestCase):
    """Fallbacks keep the interval positive when the resolution is unusable."""

    def test_uses_raster_resolution_when_available(self):
        raster = MagicMock()
        raster.rasterUnitsPerPixelX.return_value = 5.0

        result = geometry.resolve_sampling_interval(MagicMock(), raster, None)

        self.assertEqual(result, 5.0)

    def test_falls_back_to_geometry_length(self):
        raster = MagicMock()
        raster.rasterUnitsPerPixelX.return_value = 0.0
        line = MagicMock()
        line.length.return_value = 10_000.0

        result = geometry.resolve_sampling_interval(line, raster, None)

        self.assertAlmostEqual(result, 2.0)


class TestBuildSamplingTransform(BaseTestCase):
    """Sampling points must be reprojected when line and raster CRSs differ."""

    def test_matching_crs_needs_no_transform(self):
        crs = MockQgsCoordinateReferenceSystem("EPSG:4326")
        raster = MagicMock()
        raster.crs.return_value = crs

        self.assertIsNone(geometry.build_sampling_transform(crs, raster))

    def test_different_crs_builds_transform(self):
        raster = MagicMock()
        raster.crs.return_value = MockQgsCoordinateReferenceSystem("EPSG:4326")

        transform = geometry.build_sampling_transform(
            MockQgsCoordinateReferenceSystem("EPSG:32614"), raster
        )

        self.assertIsNotNone(transform)

    def test_unknown_line_crs_needs_no_transform(self):
        raster = MagicMock()
        raster.crs.return_value = MockQgsCoordinateReferenceSystem("EPSG:4326")

        self.assertIsNone(geometry.build_sampling_transform(None, raster))
