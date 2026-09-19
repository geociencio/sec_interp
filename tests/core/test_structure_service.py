"""Tests for Structure Service."""

from unittest.mock import MagicMock
from tests.base_test import BaseTestCase

from sec_interp.core.services.structure_service import StructureService


class TestStructureService(BaseTestCase):
    """Tests for StructureService."""

    def setUp(self):
        super().setUp()
        self.service = StructureService()

        # A horizontal E–W section line from (0, 0) to (100, 0).
        self.line_points = [(0.0, 0.0), (100.0, 0.0)]

    def test_project_structures_success(self):
        """Test full structure projection."""
        struct_data = [
            {
                "point": (50.0, 5.0),
                "attributes": {"dip": 45.0, "strike": 90.0},
            }
        ]

        results = self.service.project_structures(
            line_points=self.line_points,
            struct_data=struct_data,
            elevation_sampler=lambda x, y: 150.0,
            line_az=0.0,
            dip_field="dip",
            strike_field="strike",
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].distance, 50.0)
        self.assertEqual(results[0].elevation, 150.0)
        self.assertEqual(results[0].original_dip, 45.0)

    def test_project_structures_sorts_by_distance(self):
        """Projected measurements should be sorted by station distance."""
        struct_data = [
            {"point": (80.0, 0.0), "attributes": {"dip": 45.0, "strike": 90.0}},
            {"point": (20.0, 0.0), "attributes": {"dip": 45.0, "strike": 90.0}},
        ]

        results = self.service.project_structures(
            line_points=self.line_points,
            struct_data=struct_data,
            elevation_sampler=lambda x, y: 100.0,
            line_az=0.0,
            dip_field="dip",
            strike_field="strike",
        )

        self.assertEqual([r.distance for r in results], [20.0, 80.0])

    def test_project_structures_skips_missing_point(self):
        """Items without a point should be skipped gracefully."""
        struct_data = [
            {"attributes": {"dip": 45.0, "strike": 90.0}},
            {"point": (50.0, 0.0), "attributes": {"dip": 45.0, "strike": 90.0}},
        ]

        results = self.service.project_structures(
            line_points=self.line_points,
            struct_data=struct_data,
            elevation_sampler=lambda x, y: 100.0,
            line_az=0.0,
            dip_field="dip",
            strike_field="strike",
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].distance, 50.0)

    def test_parse_structural_data(self):
        """Test strike/dip parsing and apparent dip calculation."""
        attributes = {"dip": "45", "strike": "090"}
        data = self.service._parse_structural_data(attributes, "strike", "dip", 0.0)
        self.assertIsNotNone(data)
        strike, dip, app_dip = data
        self.assertEqual(strike, 90.0)
        self.assertEqual(dip, 45.0)

    def test_elevation_sampler_called_with_projected_point(self):
        """The elevation sampler should receive the projected (x, y)."""
        sampler = MagicMock(return_value=123.0)
        struct_data = [{"point": (50.0, 5.0), "attributes": {"dip": 45.0, "strike": 90.0}}]

        self.service.project_structures(
            line_points=self.line_points,
            struct_data=struct_data,
            elevation_sampler=sampler,
            line_az=0.0,
            dip_field="dip",
            strike_field="strike",
        )

        # (50, 5) projects onto (50, 0) on the horizontal line.
        sampler.assert_called_once_with(50.0, 0.0)
