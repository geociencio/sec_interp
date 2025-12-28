"""Geology Utilities Module.

Geological calculations and structural geology operations.
"""

import math


def calculate_apparent_dip(
    true_strike: float, true_dip: float, line_azimuth: float
) -> float:
    """Convert true dip to apparent dip in section plane.

    The apparent dip is the inclination of a plane measured in a direction
    not perpendicular to the strike. In a vertical cross-section, the
    apparent dip depends on the angle between the strike of the plane
    and the azimuth of the cross-section line.

    Formula:
        tan(apparent_dip) = tan(true_dip) * sin(alpha)

        Where alpha is the angle between the strike of the plane and the
        direction of the cross-section (section azimuth).
        alpha = strike - section_azimuth

    Args:
        true_strike: Strike of the geological plane (0-360 degrees).
        true_dip: True dip of the geological plane (0-90 degrees).
        line_azimuth: Azimuth of the cross-section line (0-360 degrees).

    Returns:
        Apparent dip in degrees. Positive values indicate dip, negative values
        might occur depending on quadrant but are typically normalized.
    """
    alpha = math.radians(true_strike)
    beta = math.radians(true_dip)
    theta = math.radians(line_azimuth)
    app_dip = math.degrees(math.atan(math.tan(beta) * math.sin(alpha - theta)))
    return app_dip
