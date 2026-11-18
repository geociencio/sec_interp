"""Unit tests for the QGIS-free SectionFrame."""

from __future__ import annotations

import math

from sec_interp.core.domain import SectionFrame
from tests.base_test import BaseTestCase


class TestSectionFrame(BaseTestCase):
    """SectionFrame must map profile coordinates deterministically."""

    def test_east_heading(self) -> None:
        frame = SectionFrame.from_endpoints(1000, 2000, 1100, 2000, "EPSG:32614")

        self.assertAlmostEqual(frame.length, 100.0)
        self.assertAlmostEqual(frame.azimuth_deg, 0.0)
        self.assertEqual(frame.to_map(10, 50), (1010.0, 2000.0, 50.0))

    def test_north_heading(self) -> None:
        frame = SectionFrame.from_endpoints(1000, 2000, 1000, 2100, "EPSG:32614")

        self.assertAlmostEqual(frame.azimuth_deg, 90.0)
        east, north, elev = frame.to_map(10, 50)
        self.assertAlmostEqual(east, 1000.0)
        self.assertAlmostEqual(north, 2010.0)
        self.assertAlmostEqual(elev, 50.0)

    def test_vertical_exaggeration_is_metadata(self) -> None:
        frame = SectionFrame.from_endpoints(0, 0, 100, 0, "EPSG:32614", vertical_exaggeration=5.0)

        self.assertEqual(frame.vertical_exaggeration, 5.0)
        self.assertEqual(frame.to_map(10, 20)[2], 20.0)

    def test_azimuth_degrees(self) -> None:
        frame = SectionFrame.from_endpoints(0, 0, 0, 10)
        self.assertAlmostEqual(frame.azimuth_deg, math.degrees(math.pi / 2))

    def test_rejects_zero_length(self) -> None:
        with self.assertRaises(ValueError):
            SectionFrame.from_endpoints(1, 2, 1, 2)

    def test_rejects_invalid_metadata(self) -> None:
        with self.assertRaises(ValueError):
            SectionFrame(0, 0, 0, "EPSG:32614", length=0)
        with self.assertRaises(ValueError):
            SectionFrame(0, 0, 0, "EPSG:32614", length=10, vertical_exaggeration=0)
        with self.assertRaises(ValueError):
            SectionFrame(0, 0, math.nan, "EPSG:32614", length=10)

    def test_rejects_non_finite_map_input(self) -> None:
        frame = SectionFrame.from_endpoints(0, 0, 10, 0)
        with self.assertRaises(ValueError):
            frame.to_map(math.inf, 10)
