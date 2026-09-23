"""Sampling utilities (pure math)."""

from __future__ import annotations

import bisect

MIN_SMOOTHING_POINTS = 3


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


def smooth_profile_by_distance(
    data: list[tuple[float, float]],
    window_m: float,
    passes: int = 1,
) -> list[tuple[float, float]]:
    """Smooth a profile with a centered moving average over a distance window.

    Averages the elevation of every point within ``window_m / 2`` of each
    station. The first and last elevations are preserved so the ends do not
    drift. Returns the input unchanged when there is nothing to smooth or the
    window is non-positive.

    Args:
        data: List of (distance, elevation) tuples, sorted by distance.
        window_m: Window width in distance units (map units, e.g. metres).
        passes: Number of smoothing passes (>= 1).

    Returns:
        A new list of (distance, elevation) tuples of the same length.

    """
    if not data or window_m <= 0 or len(data) < MIN_SMOOTHING_POINTS:
        return [(float(d), float(e)) for d, e in data]

    result = [(float(d), float(e)) for d, e in data]
    half = window_m / 2.0

    for _ in range(max(1, int(passes))):
        distances = [p[0] for p in result]
        elevations = [p[1] for p in result]
        smoothed = list(elevations)

        left = 0
        right = 0
        running = 0.0
        for i in range(len(result)):
            low = distances[i] - half
            high = distances[i] + half
            while left < i and distances[left] < low:
                running -= elevations[left]
                left += 1
            right = max(right, left)
            while right < len(result) and distances[right] <= high:
                running += elevations[right]
                right += 1
            smoothed[i] = running / (right - left)

        smoothed[0] = elevations[0]
        smoothed[-1] = elevations[-1]
        result = [(distances[i], smoothed[i]) for i in range(len(result))]

    return result
