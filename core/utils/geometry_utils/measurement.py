"""Measurement calculation utilities for profile viewing."""

import math
from typing import Any

from qgis.core import QgsPointXY


def calculate_polyline_metrics(points: list[QgsPointXY]) -> dict[str, Any]:
    """Calculate comprehensive measurement metrics from a list of points.

    Args:
        points: List of QgsPointXY points defining the polyline on the profile plane.

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
    if len(points) < 2:
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

        dx = abs(p2.x() - p1.x())
        dy = p2.y() - p1.y()
        seg_dist = math.sqrt(dx * dx + dy * dy)

        total_dist += seg_dist
        total_dx += dx

        segments.append(
            {
                "distance": seg_dist,
                "dx": dx,
                "dy": dy,
                "start": (p1.x(), p1.y()),
                "end": (p2.x(), p2.y()),
            }
        )

    # Total elevation change (first to last point)
    elevation_change = points[-1].y() - points[0].y()

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
