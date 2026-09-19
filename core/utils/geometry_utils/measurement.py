"""Geometric measurement utilities for profile viewing."""

from __future__ import annotations

import math
from typing import Any


def project_point_onto_polyline(
    point: tuple[float, float],
    polyline: list[tuple[float, float]],
) -> tuple[float, tuple[float, float]]:
    """Project a point onto a polyline.

    Computes the nearest point on the polyline to ``point`` and the distance
    along the polyline (from its first vertex) to that nearest point. Uses only
    planar math, which is a valid approximation for projected (planar) CRS.

    Args:
        point: The (x, y) point to project.
        polyline: List of (x, y) vertices defining the line.

    Returns:
        A tuple ``(distance_along_line, nearest_point)``. Returns ``(0.0,
        point)`` for an empty polyline and ``(0.0, polyline[0])`` for a
        single-vertex polyline.

    """
    if not polyline:
        return 0.0, point
    if len(polyline) == 1:
        return 0.0, polyline[0]

    px, py = point
    best_dist_along = 0.0
    best_point = polyline[0]
    best_sq = float("inf")
    cumulative = 0.0

    for i in range(len(polyline) - 1):
        x1, y1 = polyline[i]
        x2, y2 = polyline[i + 1]
        dx = x2 - x1
        dy = y2 - y1
        seg_len = math.hypot(dx, dy)

        if seg_len == 0:
            nearest = (x1, y1)
            t = 0.0
        else:
            t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
            t = max(0.0, min(1.0, t))
            nearest = (x1 + t * dx, y1 + t * dy)

        sq = (px - nearest[0]) ** 2 + (py - nearest[1]) ** 2
        if sq < best_sq:
            best_sq = sq
            best_dist_along = cumulative + t * seg_len
            best_point = nearest

        cumulative += seg_len

    return best_dist_along, best_point


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
