from __future__ import annotations

"""Processing logic for Drillhole Intervals."""

from sec_interp.core import utils as scu
from sec_interp.core.domain import GeologySegment


class IntervalProcessor:
    """Handles interval interpolation."""

    def interpolate_hole_intervals(
        self,
        traj: list[tuple[float, float, float, float, float, float, float, float]],
        intervals: list[tuple[float, float, str]],
        buffer_width: float,
    ) -> list[GeologySegment]:
        """Interpolate intervals along a trajectory and return GeologySegments.

        Args:
            traj: The projected trajectory tuples (depth, x, y, z, dist_along, offset, nx, ny).
            intervals: List of (from, to, lith) tuples.
            buffer_width: Section buffer width.

        Returns:
            A list of GeologySegment objects.

        """
        if not intervals:
            return []

        rich_intervals = [
            (fd, td, {"unit": lith, "from": fd, "to": td}) for fd, td, lith in intervals
        ]
        # Scu returns (attr, points_2d, points_3d, points_3d_proj)
        tuples = scu.interpolate_intervals_on_trajectory(traj, rich_intervals, buffer_width)

        segments = []
        for attr, points_2d, points_3d, points_3d_proj in tuples:
            segments.append(
                GeologySegment(
                    unit_name=str(attr.get("unit", "Unknown")),
                    geometry_wkt=None,
                    attributes=attr,
                    points=points_2d,
                    points_3d=points_3d,
                    points_3d_projected=points_3d_proj,
                )
            )
        return segments
