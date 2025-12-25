from __future__ import annotations

import re
from typing import Any, Optional


def parse_strike(value: Any) -> Optional[float]:
    """Parse a strike value from various formats into an azimuth (0-360).

    Supports numeric values, strings, and quadrant notation (e.g., "N 30 E", "S 45 W").

    Args:
        value: The raw strike value (string, int, float, or None).

    Returns:
        Strike in azimuth degrees (0-360) or None if parsing fails.
    """
    if value is None:
        return None

    # If already numeric, return directly
    try:
        return float(value)
    except (ValueError, TypeError):
        pass

    # Normalize value
    text = (
        str(value)
        .replace("°", "")
        .replace("º", "")
        .replace("ø", "")  # Support for alternative degree symbol
        .strip()
        .upper()
    )

    # Regex for quadrant notation: N/S + angle + E/W
    # Supports integers and decimals for the angle
    match = re.match(r"([NS])\s*(\d+\.?\d*)\s*([EW])", text)
    if not match:
        return None  # invalid notation

    d1, ang, d2 = match.groups()
    ang = float(ang)

    # Quadrant rules
    strike = 0  # Initialize to prevent NameError
    if d1 == "N" and d2 == "E":
        strike = ang
    elif d1 == "N" and d2 == "W":
        strike = 360 - ang
    elif d1 == "S" and d2 == "E":
        strike = 180 - ang
    elif d1 == "S" and d2 == "W":
        strike = 180 + ang

    return strike % 360


def parse_dip(value: Any) -> tuple[Optional[float], Optional[float]]:
    """Parse a dip value from various formats.

    Supports numeric dip ("45") and field notation with direction ("45 NE", "22 SW").

    Args:
        value: The raw dip value.

    Returns:
        A tuple of (dip_angle, dip_direction_azimuth). Values are None if
        parsing fails.
    """
    if value is None:
        return None, None

    text = (
        str(value)
        .replace("°", "")
        .replace("º", "")
        .replace("ø", "")  # Support for alternative degree symbol
        .strip()
        .upper()
    )

    # Case 1: numeric only (integer or decimal)
    numeric_only = re.match(r"^(\d+\.?\d*)$", text)
    if numeric_only:
        return float(text), None

    # Case 2: full dip + direction
    match = re.match(r"(\d+\.?\d*)\s*([NSEW]{1,2})", text)
    if not match:
        return None, None

    dip, cardinal = match.groups()
    dip = float(dip)

    dip_dir = cardinal_to_azimuth(cardinal)

    return dip, dip_dir


def cardinal_to_azimuth(text: str) -> Optional[float]:
    """Convert a cardinal direction string to its equivalent azimuth.

    Supports: N, NE, E, SE, S, SW, W, NW.

    Args:
        text: The cardinal direction string.

    Returns:
        The azimuth in degrees (0-360), or None if invalid.
    """
    table = {
        "N": 0,
        "NE": 45,
        "E": 90,
        "SE": 135,
        "S": 180,
        "SW": 225,
        "W": 270,
        "NW": 315,
    }

    return table.get(text)
