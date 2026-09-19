"""Sampling utilities (pure math)."""

from __future__ import annotations

import bisect


def interpolate_elevation(topo_data: list[tuple[float, float]], distance: float) -> float:
    """Interpolate elevation at a given distance along the topography profile.

    Uses linear interpolation between the two nearest sampled points.

    Args:
        topo_data: List of (distance, elevation) tuples.
        distance: Horizontal distance along the section.

    Returns:
        The interpolated elevation value (Z) at that distance.

    """
    if not topo_data:
        return 0.0

    # Extract distances for bisect
    distances = [pt[0] for pt in topo_data]

    # Find the insertion point
    idx = bisect.bisect_left(distances, distance)

    if idx == 0:
        return topo_data[0][1]
    if idx >= len(topo_data):
        return topo_data[-1][1]

    # Interpolate
    dist1, elev1 = topo_data[idx - 1]
    dist2, elev2 = topo_data[idx]

    if dist2 == dist1:
        return elev1

    ratio = (distance - dist1) / (dist2 - dist1)
    return elev1 + (elev2 - elev1) * ratio
