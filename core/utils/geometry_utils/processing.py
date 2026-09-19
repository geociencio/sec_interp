"""Geometry processing utilities (pure math)."""

from __future__ import annotations

import math
from typing import Any


def densify_line_points(
    points: list[tuple[float, float]], interval: float
) -> list[tuple[float, float]]:
    """Densify a polyline by inserting intermediate vertices.

    Ensures no segment is longer than ``interval``. Returns the input unchanged
    if it has fewer than two points or the interval is non-positive.

    Args:
        points: List of (x, y) tuples.
        interval: Maximum segment length (in the same units as the points).

    Returns:
        Densified list of (x, y) tuples.

    """
    if not points or interval <= 0:
        return points

    result = [points[0]]
    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i + 1]

        seg_len = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        if seg_len == 0:
            continue

        num_segments = max(1, math.ceil(seg_len / interval))
        for j in range(1, num_segments):
            t = j / num_segments
            result.append((p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1])))
        result.append(p2)

    return result


def interpolate_segment_points(
    dist_start: float,
    dist_end: float,
    master_grid_dists: list[tuple[float, Any, float]],  # (dist, point, elev)
    master_profile_data: list[tuple[float, float]],  # (dist, elev)
    tolerance: float,
) -> list[tuple[float, float]]:
    """Convert boundary distances into a list of points with sampled elevations.

    Includes the start/end points and any intermediate grid points from the
    master profile that fall within the specified distance range.

    Args:
        dist_start: Start distance along section.
        dist_end: End distance along section.
        master_grid_dists: Full grid of coordinates and elevations.
        master_profile_data: Topography profile (dist, elevation).
        tolerance: Distance tolerance for grid inclusions.

    Returns:
        List of (distance, elevation) tuples defining the segment profile.

    """
    from sec_interp.core.utils.sampling import interpolate_elevation

    # Get Inner Grid Points
    inner_points = [
        (d, e) for d, _, e in master_grid_dists if dist_start + tolerance < d < dist_end - tolerance
    ]

    # Interpolate Boundary Elevations
    elev_start = interpolate_elevation(master_profile_data, dist_start)
    elev_end = interpolate_elevation(master_profile_data, dist_end)

    return [(dist_start, elev_start), *inner_points, (dist_end, elev_end)]
