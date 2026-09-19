"""Pure geometric projection logic for drillhole operations."""

from __future__ import annotations

import math

from sec_interp.core.utils.geometry_utils.measurement import project_point_onto_polyline


class ProjectionEngine:
    """Encapsulates geometric projection logic (pure math)."""

    @staticmethod
    def project_point_to_line(
        pt: tuple[float, float],
        line_points: list[tuple[float, float]],
    ) -> tuple[float, float]:
        """Project point to line and return (dist_along, offset).

        Args:
            pt: The (x, y) point to project.
            line_points: Section line vertices as ``(x, y)`` tuples.

        Returns:
            Tuple of (distance_along_line, offset_from_line).

        """
        dist_along, nearest = project_point_onto_polyline(pt, line_points)
        offset = math.hypot(pt[0] - nearest[0], pt[1] - nearest[1])
        return dist_along, offset
