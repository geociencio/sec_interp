"""Tests for CRS-aware elevation sampling in StructureExtractor."""

from unittest.mock import MagicMock, patch

from tests.base_test import BaseTestCase
from tests.mocks.qgis_core import MockQgsCoordinateReferenceSystem
from tests.mocks.qgis_geometry import MockQgsPointXY

from sec_interp.gui.adapters import structure_extractor
from sec_interp.gui.adapters.structure_extractor import StructureExtractor


class _OffsetTransform:
    """Fake transform that offsets points, to observe reprojection."""

    def transform(self, point):
        return MockQgsPointXY(point.x() + 10.0, point.y() + 20.0)


def _raster(value=250.0, crs=None):
    raster = MagicMock()
    raster.isValid.return_value = True
    raster.crs.return_value = crs or MockQgsCoordinateReferenceSystem("EPSG:4326")
    ident = MagicMock()
    ident.isValid.return_value = True
    ident.results.return_value = {1: value}
    raster.dataProvider.return_value.identify.return_value = ident
    return raster


class TestMakeElevationSampler(BaseTestCase):
    """Structural points must be reprojected into the raster CRS before sampling."""

    def test_same_crs_samples_without_transform(self):
        raster = _raster(value=123.0)
        line = MagicMock()
        line.crs.return_value = raster.crs.return_value

        sampler = StructureExtractor().make_elevation_sampler(raster, line, 1)

        self.assertEqual(sampler(10.0, 20.0), 123.0)

    def test_different_crs_reprojects_before_sampling(self):
        raster = _raster(value=300.0, crs=MockQgsCoordinateReferenceSystem("EPSG:4326"))
        line = MagicMock()
        line.crs.return_value = MockQgsCoordinateReferenceSystem("EPSG:32614")

        with patch.object(
            structure_extractor.geometry,
            "build_sampling_transform",
            return_value=_OffsetTransform(),
        ):
            sampler = StructureExtractor().make_elevation_sampler(raster, line, 1)
            result = sampler(10.0, 20.0)

        called_point = raster.dataProvider().identify.call_args.args[0]
        self.assertEqual((called_point.x(), called_point.y()), (20.0, 40.0))
        self.assertEqual(result, 300.0)

    def test_invalid_raster_returns_zero(self):
        raster = MagicMock()
        raster.isValid.return_value = False

        sampler = StructureExtractor().make_elevation_sampler(raster, None, 1)

        self.assertEqual(sampler(0.0, 0.0), 0.0)
