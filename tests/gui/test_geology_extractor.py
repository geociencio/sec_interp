"""Tests for geology master-profile smoothing in GeologyExtractor."""

from __future__ import annotations

import math
from unittest.mock import MagicMock

from tests.base_test import BaseTestCase
from tests.mocks.qgis_core import MockQgsCoordinateReferenceSystem
from tests.mocks.qgis_geometry import MockQgsGeometry, MockQgsPointXY

from sec_interp.gui.adapters.geology_extractor import GeologyExtractor


def _raster(crs, sample_side_effect):
    raster = MagicMock()
    raster.isValid.return_value = True
    raster.crs.return_value = crs
    raster.rasterUnitsPerPixelX.return_value = 10.0
    raster.rasterUnitsPerPixelY.return_value = 10.0
    raster.dataProvider.return_value.sample.side_effect = sample_side_effect
    return raster


def _distance_area(crs):
    da = MagicMock()
    da.sourceCrs.return_value = crs
    da.measureLine.side_effect = lambda a, b: math.hypot(b.x() - a.x(), b.y() - a.y())
    return da


def _spike_sampler(peak_x: float = 50.0):
    return lambda pt, band: (100.0 if abs(pt.x() - peak_x) < 1e-6 else 10.0, True)


class TestGeologyMasterProfileSmoothing(BaseTestCase):
    """The master profile follows the smoothing window."""

    def setUp(self) -> None:
        super().setUp()
        self.extractor = GeologyExtractor()
        self.crs = MockQgsCoordinateReferenceSystem("EPSG:32614")
        self.line = MockQgsGeometry.fromWkt("LINESTRING(0 0, 100 0)")
        self.start = MockQgsPointXY(0.0, 0.0)

    def _run(self, window: float):
        raster = _raster(self.crs, _spike_sampler())
        return self.extractor._generate_master_profile(
            self.line,
            raster,
            1,
            _distance_area(self.crs),
            self.start,
            smoothing_window_m=window,
        )

    def test_zero_window_keeps_raw_spike(self) -> None:
        """With no smoothing the spike is preserved."""
        profile, _grid = self._run(0.0)
        self.assertAlmostEqual(max(e for _, e in profile), 100.0)

    def test_window_attenuates_spike(self) -> None:
        """A smoothing window lowers the spike and keeps the distance axis."""
        profile, grid = self._run(50.0)
        self.assertLess(max(e for _, e in profile), 100.0)
        self.assertGreater(max(e for _, e in profile), 10.0)

        # grid elevations mirror the (smoothed) profile, same order/distances
        self.assertEqual([d for d, _ in profile], [d for d, _, _ in grid])
        self.assertEqual(
            [e for _, e in profile], [e for _, _, e in grid]
        )
