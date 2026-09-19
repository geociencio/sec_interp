"""Geometric measurement utilities for profile viewing."""

from __future__ import annotations

import math
from typing import Any


def calculate_polyline_metrics(points: list[tuple[float, float]]) -> dict[str, Any]:
    """Calculate comprehensive measurement metrics from a list of points.

    Args:
        points: List of (x, y) tuples defining the polyline on the profile plane.

    Returns:
        Dictionary containing:
            - total_distance: Accumulated 2D distance along all segments.
            - horizontal_distance: Total horizontal distance (X span).
            - elevation_change: Total elevation change (Y span from first to last).
            - avg_slope: Average slope in degrees.
            - segment_count: Number of segments.
            - segments: List of segment details with distance, dx, and dy.
            - point_count: Number of points.

    """
    MIN_POINTS_REQUIRED = 2
    if len(points) < MIN_POINTS_REQUIRED:
        return {
            "total_distance": 0.0,
            "horizontal_distance": 0.0,
            "elevation_change": 0.0,
            "avg_slope": 0.0,
            "segment_count": 0,
            "segments": [],
            "point_count": len(points),
        }

    total_dist = 0.0
    total_dx = 0.0
    segments = []

    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i + 1]

        dx = abs(p2[0] - p1[0])
        dy = p2[1] - p1[1]
        seg_dist = math.sqrt(dx * dx + dy * dy)

        total_dist += seg_dist
        total_dx += dx

        segments.append(
            {
                "distance": seg_dist,
                "dx": dx,
                "dy": dy,
                "start": (p1[0], p1[1]),
                "end": (p2[0], p2[1]),
            }
        )

    # Total elevation change (first to last point)
    elevation_change = points[-1][1] - points[0][1]

    # Average slope
    avg_slope = 0.0
    if total_dx > 0:
        avg_slope = math.degrees(math.atan(abs(elevation_change) / total_dx))

    return {
        "total_distance": total_dist,
        "horizontal_distance": total_dx,
        "elevation_change": elevation_change,
        "avg_slope": avg_slope,
        "segment_count": len(segments),
        "segments": segments,
        "point_count": len(points),
    }
