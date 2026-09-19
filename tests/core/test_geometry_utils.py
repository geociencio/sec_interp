"""Tests for geometry utilities sub-modules (pure math)."""

from tests.base_test import BaseTestCase

from sec_interp.core.utils.geometry_utils.measurement import calculate_polyline_metrics
from sec_interp.core.utils.geometry_utils.optimization import PreviewOptimizer
from sec_interp.core.utils.geometry_utils.processing import (
    densify_line_points,
    interpolate_segment_points,
)


class TestGeometryMeasurement(BaseTestCase):
    """Tests for measurement.py"""

    def test_calculate_polyline_metrics_empty(self):
        """Test metrics for empty or short list of points."""
        self.assertEqual(calculate_polyline_metrics([])["point_count"], 0)
        self.assertEqual(calculate_polyline_metrics([(0, 0)])["point_count"], 1)

    def test_calculate_polyline_metrics_valid(self):
        """Test metrics calculation for a valid polyline."""
        points = [(0, 0), (3, 4)]  # 3-4-5 triangle
        metrics = calculate_polyline_metrics(points)

        self.assertAlmostEqual(metrics["total_distance"], 5.0)
        self.assertAlmostEqual(metrics["horizontal_distance"], 3.0)
        self.assertAlmostEqual(metrics["elevation_change"], 4.0)
        self.assertAlmostEqual(metrics["avg_slope"], 53.13, places=2)
        self.assertEqual(metrics["segment_count"], 1)


class TestGeometryOptimization(BaseTestCase):
    """Tests for optimization.py"""

    def test_preview_optimizer_decimate(self):
        """Test line decimation/simplification."""
        data = [(0, 0), (5, 0.1), (10, 0)]
        # Should return original if points <= max_points
        self.assertEqual(PreviewOptimizer.decimate(data, max_points=10), data)

        # Test decimation logic
        result = PreviewOptimizer.decimate(data, max_points=1)
        self.assertIsInstance(result, list)

    def test_calculate_curvature(self):
        """Test curvature calculation."""
        # Straight line
        data = [(0, 0), (10, 0), (20, 0)]
        curvatures = PreviewOptimizer.calculate_curvature(data)
        self.assertEqual(sum(curvatures), 0.0)

        # 90 degree turn
        data_turn = [(0, 0), (10, 0), (10, 10)]
        curvatures_turn = PreviewOptimizer.calculate_curvature(data_turn)
        self.assertAlmostEqual(curvatures_turn[1], 90.0)

    def test_adaptive_sample(self):
        """Test adaptive sampling heuristic."""
        data = [(i, 0) for i in range(100)]
        result = PreviewOptimizer.adaptive_sample(data, max_points=50)
        self.assertIsInstance(result, list)


class TestGeometryProcessing(BaseTestCase):
    """Tests for processing.py (pure math)."""

    def test_densify_line_points(self):
        """Test pure-math polyline densification."""
        result = densify_line_points([(0, 0), (10, 0)], 2.0)
        self.assertEqual(len(result), 6)  # 5 segments of length 2.0
        self.assertEqual(result[0], (0, 0))
        self.assertEqual(result[-1], (10, 0))

        self.assertEqual(densify_line_points([(0, 0), (1, 0)], 2.0), [(0, 0), (1, 0)])
        self.assertEqual(densify_line_points([(0, 0), (10, 0)], 0.0), [(0, 0), (10, 0)])
        self.assertEqual(densify_line_points([], 1.0), [])
        self.assertEqual(densify_line_points([(0, 0)], 1.0), [(0, 0)])

    def test_interpolate_segment_points(self):
        """Test distance-to-point conversion with interpolation."""
        grid = [(0.0, None, 100.0), (10.0, None, 110.0), (20.0, None, 120.0)]
        profile = [(0.0, 100.0), (10.0, 110.0), (20.0, 120.0)]

        points = interpolate_segment_points(5.0, 15.0, grid, profile, 0.001)

        self.assertEqual(len(points), 3)
        self.assertAlmostEqual(points[0][0], 5.0)
        self.assertAlmostEqual(points[0][1], 105.0)
        self.assertAlmostEqual(points[2][0], 15.0)
        self.assertAlmostEqual(points[2][1], 115.0)
