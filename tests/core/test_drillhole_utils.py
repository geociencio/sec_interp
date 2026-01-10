"""Tests for drillhole utilities."""

import math
from tests.base_test import BaseTestCase
from qgis.core import (
    QgsPointXY,
    QgsGeometry,
    QgsDistanceArea,
    QgsCoordinateReferenceSystem,
)

from sec_interp.core.utils.drillhole import (
    calculate_drillhole_trajectory,
    project_trajectory_to_section,
    interpolate_intervals_on_trajectory,
)


class TestCalculateDrillholeTrajectory(BaseTestCase):
    """Tests for calculate_drillhole_trajectory function."""

    def setUp(self):
        super().setUp()
        self.collar_point = QgsPointXY(1000.0, 2000.0)
        self.collar_z = 100.0

    def test_vertical_hole_no_survey(self):
        """Test vertical hole with no survey data but total depth."""
        trajectory = calculate_drillhole_trajectory(
            self.collar_point,
            self.collar_z,
            [],
            section_azimuth=0.0,
            densify_step=10.0,
            total_depth=50.0,
        )

        # Should have collar + densified points
        self.assertGreater(len(trajectory), 1)
        # First point is collar
        self.assertEqual(trajectory[0][0], 0.0)
        self.assertAlmostEqual(trajectory[0][1], 1000.0)
        self.assertAlmostEqual(trajectory[0][2], 2000.0)
        self.assertAlmostEqual(trajectory[0][3], 100.0)

    def test_empty_survey_no_depth(self):
        """Test empty survey with no total depth returns empty."""
        trajectory = calculate_drillhole_trajectory(
            self.collar_point,
            self.collar_z,
            [],
            section_azimuth=0.0,
        )

        self.assertEqual(len(trajectory), 0)

    def test_single_survey_point_vertical(self):
        """Test single survey point with vertical inclination."""
        survey_data = [(50.0, 0.0, -90.0)]  # 50m depth, vertical down

        trajectory = calculate_drillhole_trajectory(
            self.collar_point,
            self.collar_z,
            survey_data,
            section_azimuth=0.0,
            densify_step=10.0,
        )

        # Should have collar + densified points to 50m
        self.assertGreater(len(trajectory), 1)

        # Last point should be at 50m depth
        last_point = trajectory[-1]
        self.assertAlmostEqual(last_point[0], 50.0, places=1)

        # For vertical hole, X and Y should remain constant
        self.assertAlmostEqual(last_point[1], 1000.0, places=1)
        self.assertAlmostEqual(last_point[2], 2000.0, places=1)

        # Z should decrease by 50m
        self.assertAlmostEqual(last_point[3], 50.0, places=1)

    def test_inclined_hole(self):
        """Test inclined drillhole trajectory."""
        # 45° inclination (from vertical), 90° azimuth (East)
        survey_data = [(50.0, 90.0, -45.0)]

        trajectory = calculate_drillhole_trajectory(
            self.collar_point,
            self.collar_z,
            survey_data,
            section_azimuth=0.0,
            densify_step=10.0,
        )

        self.assertGreater(len(trajectory), 1)

        # Last point should have moved East (positive X) and down (negative Z)
        last_point = trajectory[-1]
        self.assertGreater(last_point[1], 1000.0)  # X increased (East)
        self.assertLess(last_point[3], 100.0)  # Z decreased (down)

    def test_multiple_survey_points(self):
        """Test trajectory with multiple survey points."""
        survey_data = [
            (20.0, 0.0, -90.0),  # Vertical to 20m
            (50.0, 90.0, -45.0),  # Then inclined East to 50m
        ]

        trajectory = calculate_drillhole_trajectory(
            self.collar_point,
            self.collar_z,
            survey_data,
            section_azimuth=0.0,
            densify_step=5.0,
        )

        self.assertGreater(len(trajectory), 5)

        # Check that depths are increasing
        depths = [p[0] for p in trajectory]
        self.assertEqual(depths, sorted(depths))

    def test_extrapolation_beyond_last_survey(self):
        """Test extrapolation when total_depth exceeds last survey."""
        survey_data = [(30.0, 0.0, -90.0)]

        trajectory = calculate_drillhole_trajectory(
            self.collar_point,
            self.collar_z,
            survey_data,
            section_azimuth=0.0,
            densify_step=10.0,
            total_depth=60.0,  # Extrapolate to 60m
        )

        # Should have points beyond 30m
        last_point = trajectory[-1]
        self.assertAlmostEqual(last_point[0], 60.0, places=1)

    def test_densification_step(self):
        """Test that densification step affects number of points."""
        survey_data = [(50.0, 0.0, -90.0)]

        # Coarse densification
        trajectory_coarse = calculate_drillhole_trajectory(
            self.collar_point,
            self.collar_z,
            survey_data,
            section_azimuth=0.0,
            densify_step=25.0,
        )

        # Fine densification
        trajectory_fine = calculate_drillhole_trajectory(
            self.collar_point,
            self.collar_z,
            survey_data,
            section_azimuth=0.0,
            densify_step=5.0,
        )

        # Fine should have more points
        self.assertGreater(len(trajectory_fine), len(trajectory_coarse))

    def test_skip_invalid_survey_depth(self):
        """Test that survey points with depth <= previous are skipped."""
        survey_data = [
            (20.0, 0.0, -90.0),
            (15.0, 90.0, -45.0),  # Invalid: depth less than previous
            (40.0, 0.0, -90.0),
        ]

        trajectory = calculate_drillhole_trajectory(
            self.collar_point,
            self.collar_z,
            survey_data,
            section_azimuth=0.0,
            densify_step=10.0,
        )

        # Should still work, skipping invalid point
        self.assertGreater(len(trajectory), 1)


class TestProjectTrajectoryToSection(BaseTestCase):
    """Tests for project_trajectory_to_section function."""

    def setUp(self):
        super().setUp()
        # Create a simple East-West section line
        self.line_start = QgsPointXY(0.0, 0.0)
        self.line_end = QgsPointXY(100.0, 0.0)
        self.line_geom = QgsGeometry.fromPolylineXY([self.line_start, self.line_end])

        # Setup distance area
        self.distance_area = QgsDistanceArea()
        crs = QgsCoordinateReferenceSystem("EPSG:32633")  # UTM zone 33N
        self.distance_area.setSourceCrs(crs, None)

    def test_project_single_point_on_line(self):
        """Test projecting a single point that lies on the section line."""
        trajectory = [
            (0.0, 50.0, 0.0, 100.0, 0.0, 0.0),  # Point at (50, 0) on the line
        ]

        projected = project_trajectory_to_section(
            trajectory,
            self.line_geom,
            self.line_start,
            self.distance_area,
        )

        self.assertEqual(len(projected), 1)
        depth, x, y, z, dist_along, offset = projected[0]

        # Should be at distance 50 along line
        self.assertAlmostEqual(dist_along, 50.0, places=0)
        # Offset should be ~0 (on the line)
        self.assertAlmostEqual(offset, 0.0, places=0)

    def test_project_point_offset_from_line(self):
        """Test projecting a point offset from the section line."""
        trajectory = [
            (0.0, 50.0, 10.0, 100.0, 0.0, 0.0),  # Point at (50, 10), 10m North of line
        ]

        projected = project_trajectory_to_section(
            trajectory,
            self.line_geom,
            self.line_start,
            self.distance_area,
        )

        self.assertEqual(len(projected), 1)
        depth, x, y, z, dist_along, offset = projected[0]

        # Should project to distance ~50 along line
        self.assertAlmostEqual(dist_along, 50.0, places=0)
        # Offset should be ~10m
        self.assertAlmostEqual(offset, 10.0, places=0)

    def test_project_multiple_points(self):
        """Test projecting multiple trajectory points."""
        trajectory = [
            (0.0, 0.0, 0.0, 100.0, 0.0, 0.0),
            (10.0, 25.0, 5.0, 90.0, 0.0, 0.0),
            (20.0, 50.0, 0.0, 80.0, 0.0, 0.0),
            (30.0, 75.0, -5.0, 70.0, 0.0, 0.0),
        ]

        projected = project_trajectory_to_section(
            trajectory,
            self.line_geom,
            self.line_start,
            self.distance_area,
        )

        self.assertEqual(len(projected), 4)

        # Check that distances along section are increasing
        distances = [p[4] for p in projected]
        self.assertEqual(distances, sorted(distances))


class TestInterpolateIntervalsOnTrajectory(BaseTestCase):
    """Tests for interpolate_intervals_on_trajectory function."""

    def test_single_interval_all_points_in_buffer(self):
        """Test single interval with all points within buffer."""
        trajectory = [
            (0.0, 0.0, 0.0, 100.0, 0.0, 0.0),
            (10.0, 10.0, 0.0, 90.0, 10.0, 0.5),
            (20.0, 20.0, 0.0, 80.0, 20.0, 1.0),
        ]

        intervals = [
            (0.0, 20.0, "Unit A"),
        ]

        segments = interpolate_intervals_on_trajectory(
            trajectory,
            intervals,
            buffer_width=5.0,
        )

        self.assertEqual(len(segments), 1)
        attribute, points = segments[0]
        self.assertEqual(attribute, "Unit A")
        self.assertEqual(len(points), 3)

    def test_interval_partial_points_in_buffer(self):
        """Test interval with some points outside buffer."""
        trajectory = [
            (0.0, 0.0, 0.0, 100.0, 0.0, 0.0),
            (10.0, 10.0, 0.0, 90.0, 10.0, 2.0),
            (20.0, 20.0, 0.0, 80.0, 20.0, 10.0),  # Outside buffer
        ]

        intervals = [
            (0.0, 20.0, "Unit A"),
        ]

        segments = interpolate_intervals_on_trajectory(
            trajectory,
            intervals,
            buffer_width=5.0,
        )

        self.assertEqual(len(segments), 1)
        attribute, points = segments[0]
        # Only 2 points should be included (last one outside buffer)
        self.assertEqual(len(points), 2)

    def test_multiple_intervals(self):
        """Test multiple geological intervals."""
        trajectory = [
            (0.0, 0.0, 0.0, 100.0, 0.0, 0.0),
            (10.0, 10.0, 0.0, 90.0, 10.0, 0.5),
            (20.0, 20.0, 0.0, 80.0, 20.0, 0.5),
            (30.0, 30.0, 0.0, 70.0, 30.0, 0.5),
        ]

        intervals = [
            (0.0, 15.0, "Unit A"),
            (15.0, 30.0, "Unit B"),
        ]

        segments = interpolate_intervals_on_trajectory(
            trajectory,
            intervals,
            buffer_width=5.0,
        )

        self.assertEqual(len(segments), 2)

        # Check first interval
        attr_a, points_a = segments[0]
        self.assertEqual(attr_a, "Unit A")
        self.assertGreater(len(points_a), 0)

        # Check second interval
        attr_b, points_b = segments[1]
        self.assertEqual(attr_b, "Unit B")
        self.assertGreater(len(points_b), 0)

    def test_interval_no_points_in_range(self):
        """Test interval with no trajectory points in depth range."""
        trajectory = [
            (0.0, 0.0, 0.0, 100.0, 0.0, 0.0),
            (10.0, 10.0, 0.0, 90.0, 10.0, 0.5),
        ]

        intervals = [
            (50.0, 100.0, "Unit C"),  # No points in this depth range
        ]

        segments = interpolate_intervals_on_trajectory(
            trajectory,
            intervals,
            buffer_width=5.0,
        )

        # Should return empty list or segment with no points
        self.assertEqual(len(segments), 0)

    def test_points_format(self):
        """Test that returned points have correct format (distance, elevation)."""
        trajectory = [
            (0.0, 0.0, 0.0, 100.0, 5.0, 0.0),
            (10.0, 10.0, 0.0, 90.0, 15.0, 0.5),
        ]

        intervals = [
            (0.0, 10.0, "Unit A"),
        ]

        segments = interpolate_intervals_on_trajectory(
            trajectory,
            intervals,
            buffer_width=5.0,
        )

        attribute, points = segments[0]

        # Check point format
        for point in points:
            self.assertEqual(len(point), 2)
            dist_along, elevation = point
            self.assertIsInstance(dist_along, (int, float))
            self.assertIsInstance(elevation, (int, float))
