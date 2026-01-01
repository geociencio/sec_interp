"""Tests for rendering utilities."""

from tests.base_test import BaseTestCase
from sec_interp.core.utils.rendering import (
    calculate_bounds,
    create_coordinate_transform,
    calculate_interval,
)


class TestCalculateBounds(BaseTestCase):
    """Tests for calculate_bounds function."""

    def test_calculate_bounds_topo_only(self):
        """Test bounds calculation with only topography data."""
        topo_data = [(0.0, 100.0), (100.0, 150.0), (200.0, 120.0)]
        bounds = calculate_bounds(topo_data)

        # min_d=0, max_d=200, range=200, padding=10
        self.assertAlmostEqual(bounds["min_d"], -10.0)
        self.assertAlmostEqual(bounds["max_d"], 210.0)

        # min_e=100, max_e=150, range=50, padding=2.5
        self.assertAlmostEqual(bounds["min_e"], 97.5)
        self.assertAlmostEqual(bounds["max_e"], 152.5)

    def test_calculate_bounds_with_geol(self):
        """Test bounds calculation with both topography and geology data."""
        from sec_interp.core.types import GeologySegment
        from unittest.mock import MagicMock

        topo_data = [(0.0, 100.0), (100.0, 150.0)]

        # GeologySegment takes unit_name, geometry, attributes, points
        geol_data = [
            GeologySegment("Unit A", MagicMock(), {}, [(50.0, 80.0), (150.0, 60.0)]),
            GeologySegment("Unit B", MagicMock(), {}, [(200.0, 40.0), (250.0, 20.0)]),
        ]

        bounds = calculate_bounds(topo_data, geol_data)

        # min_d=0, max_d=250, range=250, padding=12.5
        self.assertAlmostEqual(bounds["min_d"], -12.5)
        self.assertAlmostEqual(bounds["max_d"], 262.5)

        # min_e=20, max_e=150, range=130, padding=6.5
        self.assertAlmostEqual(bounds["min_e"], 13.5)
        self.assertAlmostEqual(bounds["max_e"], 156.5)

    def test_calculate_bounds_division_by_zero(self):
        """Test bounds calculation with zero range data."""
        topo_data = [(100.0, 50.0)]
        bounds = calculate_bounds(topo_data)

        self.assertGreater(bounds["max_d"], bounds["min_d"])
        self.assertGreater(bounds["max_e"], bounds["min_e"])


class TestCoordinateTransform(BaseTestCase):
    """Tests for create_coordinate_transform function."""

    def test_transform_linear(self):
        """Test basic linear transformation."""
        bounds = {"min_d": 0.0, "max_d": 100.0, "min_e": 0.0, "max_e": 100.0}
        view_w, view_h, margin = 1000, 1000, 100

        transform = create_coordinate_transform(bounds, view_w, view_h, margin)

        # Center point
        x, y = transform(50.0, 50.0)
        self.assertAlmostEqual(x, 500.0)
        self.assertAlmostEqual(y, 500.0)

        # Top-left of data (min_d, max_e)
        x, y = transform(0.0, 100.0)
        self.assertAlmostEqual(x, 100.0)
        self.assertAlmostEqual(y, 100.0)

        # Bottom-right of data (max_d, min_e)
        x, y = transform(100.0, 0.0)
        self.assertAlmostEqual(x, 900.0)
        self.assertAlmostEqual(y, 900.0)

    def test_transform_vertical_exaggeration(self):
        """Test transformation with vertical exaggeration."""
        bounds = {"min_d": 0.0, "max_d": 100.0, "min_e": 0.0, "max_e": 100.0}
        view_w, view_h, margin = 1000, 1000, 100

        # vert_exag = 2.0
        transform = create_coordinate_transform(bounds, view_w, view_h, margin, vert_exag=2.0)

        # Margin is 100, view_h is 1000. Data max_e=100 transforms to margin=100.
        # Data min_e=0 transforms to view_h-margin = 900.
        # But wait, scale_y = base_scale * vert_exag.
        # data_w = 100, data_h = 100.
        # pot_x = (1000-200)/100 = 8.
        # pot_y = (1000-200)/100 = 8.
        # base_scale = 8.
        # scale_x = 8.
        # scale_y = 16.

        # elev=50: y = 1000 - 100 - (50 - 0) * 16 = 900 - 800 = 100.
        x, y = transform(50.0, 50.0)
        self.assertAlmostEqual(x, 500.0)
        self.assertAlmostEqual(y, 100.0)


class TestCalculateInterval(BaseTestCase):
    """Tests for calculate_interval function."""

    def test_calculate_interval_various_ranges(self):
        """Test interval calculation for various data ranges."""
        self.assertEqual(calculate_interval(150), 50.0)
        self.assertEqual(calculate_interval(350), 100.0)
        self.assertEqual(calculate_interval(800), 200.0)
        self.assertEqual(calculate_interval(1500), 500.0)
        self.assertEqual(calculate_interval(15), 5.0)
