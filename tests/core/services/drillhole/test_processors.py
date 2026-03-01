"""Tests for Drillhole Processors."""

import unittest
from unittest.mock import MagicMock

from qgis.core import QgsPointXY, QgsGeometry
from sec_interp.core.services.drillhole.collar_processor import CollarProcessor
from sec_interp.core.services.drillhole.survey_processor import SurveyProcessor
from sec_interp.core.services.drillhole.interval_processor import IntervalProcessor
from sec_interp.tests.base_test import BaseTestCase


class TestSurveyProcessor(BaseTestCase):
    """Test suite for SurveyProcessor."""

    def setUp(self):
        super().setUp()
        self.processor = SurveyProcessor()

    def test_determine_final_depth(self):
        """Test final depth calculation logic."""
        # Case 1: All sources available
        given = 100.0
        surveys = [(120.0, 45, 90)]
        intervals = [(0, 150.0, "LithA")]
        self.assertEqual(
            self.processor.determine_final_depth(given, surveys, intervals), 150.0
        )

        # Case 2: Only given depth
        self.assertEqual(self.processor.determine_final_depth(200.0, [], []), 200.0)

        # Case 3: Only survey deeper
        self.assertEqual(
            self.processor.determine_final_depth(50.0, [(80.0, 0, 0)], []), 80.0
        )


class TestIntervalProcessor(BaseTestCase):
    """Test suite for IntervalProcessor."""

    def setUp(self):
        super().setUp()
        self.processor = IntervalProcessor()

    def test_interpolate_hole_intervals_empty(self):
        """Test with no intervals."""
        self.assertEqual(self.processor.interpolate_hole_intervals([], [], 1.0), [])

    def test_interpolate_hole_intervals_basic(self):
        """Test basic interpolation call (mocking scu)."""
        traj = [(0.0, 0, 0, 0, 0, 0, 1, 0), (10.0, 0, 0, -10, 10, 0, 1, 0)]
        intervals = [(0, 5.0, "LithA")]

        # We check that it returns GeologySegments
        results = self.processor.interpolate_hole_intervals(traj, intervals, 2.0)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].unit_name, "LithA")
        self.assertEqual(results[0].attributes["from"], 0)


class TestCollarProcessor(BaseTestCase):
    """Test suite for CollarProcessor."""

    def setUp(self):
        super().setUp()
        self.processor = CollarProcessor()

    def test_build_coordinate_map(self):
        """Test building hole_id -> QgsPointXY map."""
        collar_data = [
            {"id": "H1", "attributes": {"x": 100, "y": 200}},
            {"id": "H2", "attributes": {"x": 150, "y": 250}},
        ]
        coord_map = self.processor.build_coordinate_map(
            collar_data, use_geometry=False, collar_x_field="x", collar_y_field="y"
        )

        self.assertEqual(len(coord_map), 2)
        self.assertIsInstance(coord_map["H1"], QgsPointXY)
        self.assertEqual(coord_map["H1"].x(), 100)
        self.assertEqual(coord_map["H2"].y(), 250)

    def test_extract_point_agnostic_dict(self):
        """Test point extraction from dict."""
        data = {"attributes": {"x": 123, "y": 456}}
        pt = self.processor.extract_point_agnostic(
            data, is_dict=True, use_geom=False, x_f="x", y_f="y"
        )
        self.assertEqual(pt.x(), 123)
        self.assertEqual(pt.y(), 456)

    def test_extract_depth_agnostic(self):
        """Test depth extraction."""
        data = {"attributes": {"depth": 150.5}}
        depth = self.processor._extract_depth_agnostic(data, True, "depth")
        self.assertEqual(depth, 150.5)

        # Missing field should return 0
        self.assertEqual(self.processor._extract_depth_agnostic({}, True, "miss"), 0.0)


if __name__ == "__main__":
    unittest.main()
