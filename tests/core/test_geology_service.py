"""Tests for Geology Service."""

from tests.base_test import BaseTestCase

from sec_interp.core.domain.task_inputs import GeologyContext, OutcropSegments
from sec_interp.core.services.geology_service import GeologyService
from sec_interp.core.utils.geometry_utils.processing import interpolate_segment_points


class TestGeologyService(BaseTestCase):
    """Tests for GeologyService."""

    def setUp(self):
        super().setUp()
        self.service = GeologyService()

    def _build_context(self, outcrops):
        """Build a detached context with a flat master profile (0-20 m)."""
        master_profile = [(0.0, 100.0), (10.0, 110.0), (20.0, 120.0)]
        master_grid = [
            (0.0, (0.0, 0.0), 100.0),
            (10.0, (10.0, 0.0), 110.0),
            (20.0, (20.0, 0.0), 120.0),
        ]
        return GeologyContext(
            master_profile_data=master_profile,
            master_grid_dists=master_grid,
            outcrops=outcrops,
        )

    def test_build_segments_empty_returns_empty_list(self):
        """build_segments with no outcrops should return an empty list."""
        result = self.service.build_segments(self._build_context([]))
        self.assertEqual(result, [])

    def test_build_segments_single_outcrop(self):
        """A single outcrop segment should produce a GeologySegment."""
        outcrops = [
            OutcropSegments(
                unit_name="Unit A",
                attributes={"age": "Miocene"},
                segments=[(5.0, 15.0, "LINESTRING(5 0, 15 0)")],
            )
        ]
        result = self.service.build_segments(self._build_context(outcrops))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].unit_name, "Unit A")
        self.assertEqual(result[0].attributes["age"], "Miocene")

    def test_build_segments_sorted_by_distance(self):
        """Segments should be sorted by their first point's distance."""
        outcrops = [
            OutcropSegments("Unit B", {}, [(10.0, 15.0, "wkt")]),
            OutcropSegments("Unit A", {}, [(0.0, 5.0, "wkt")]),
        ]
        result = self.service.build_segments(self._build_context(outcrops))

        self.assertEqual([s.unit_name for s in result], ["Unit A", "Unit B"])

    def test_convert_to_segment_points(self):
        """Test distance to point conversion with interpolation."""
        grid = [(0.0, None, 100.0), (10.0, None, 110.0), (20.0, None, 120.0)]
        profile = [(0.0, 100.0), (10.0, 110.0), (20.0, 120.0)]

        # Segment from 5 to 15
        points = interpolate_segment_points(5.0, 15.0, grid, profile, 0.001)

        self.assertEqual(len(points), 3)  # (5, 105), (10, 110), (15, 115)
        self.assertAlmostEqual(points[0][0], 5.0)
        self.assertAlmostEqual(points[0][1], 105.0)
        self.assertAlmostEqual(points[2][0], 15.0)
        self.assertAlmostEqual(points[2][1], 115.0)
