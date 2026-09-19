"""Spatial utilities (pure math)."""

from __future__ import annotations

import math


def calculate_line_azimuth(points: list[tuple[float, float]]) -> float:
    """Calculate the azimuth (compass bearing) of a line.

    Calculates the azimuth based on the first two points of the line.
    Returns 0 for points or single-vertex lines.

    Args:
        points: List of (x, y) tuples defining the line.

    Returns:
        Azimuth in degrees (0-360).

    """
    MIN_REQUIRED_POINTS = 2
    if len(points) < MIN_REQUIRED_POINTS:
        return 0

    p1 = points[0]
    p2 = points[1]
    azimuth = math.degrees(math.atan2(p2[0] - p1[0], p2[1] - p1[1]))
    if azimuth < 0:
        azimuth += 360
    return azimuth
