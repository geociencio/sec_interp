"""Data parsing and conversion utilities."""

from __future__ import annotations

import re
from typing import Any


def parse_strike(value: Any) -> float | None:
    """Parse a strike value from various formats into an azimuth (0-360).

    Supports numeric values, strings, and quadrant notation (e.g., "N 30 E", "S 45 W").
    Also handles combined strike/dip strings by splitting them.

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

    # Normalize value: remove degree symbols and typos
    text = (
        str(value)
        .replace("°", "")
        .replace("º", "")
        .replace("ø", "")
        .replace("O", "")
        .strip()
        .upper()
    )

    # If combined notation with comma, try the parts
    parts = [text]
    if "," in text:
        parts = [p.strip() for p in text.split(",")]

    for part in parts:
        # Regex for quadrant notation: N/S + angle + E/W
        # Use re.match on the part to ensure it starts with N or S
        match = re.match(r"([NS])\s*(\d+\.?\d*)\s*([EW])", part)
        if match:
            d1, ang, d2 = match.groups()
            ang = float(ang)
            strike = 0.0
            if d1 == "N" and d2 == "E":
                strike = ang
            elif d1 == "N" and d2 == "W":
                strike = 360 - ang
            elif d1 == "S" and d2 == "E":
                strike = 180 - ang
            elif d1 == "S" and d2 == "W":
                strike = 180 + ang
            return strike % 360

    return None


def parse_dip(value: Any) -> tuple[float | None, float | None]:
    """Parse a dip value from various formats.

    Supports numeric dip ("45") and field notation with direction ("45 NE", "22 SW").
    Also supports finding the dip part in combined strings (e.g. "N30E, 45NW").

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
        .replace("ø", "")
        .replace("O", "")
        .strip()
        .upper()
    )

    # Case 1: numeric only (integer or decimal) - needs exact match on full string
    numeric_only = re.match(r"^(\d+\.?\d*)$", text)
    if numeric_only:
        return float(text), None

    # Handle combined notation by splitting
    parts = [text]
    if "," in text:
        parts = [p.strip() for p in text.split(",")]

    for part in parts:
        # Case 2: full dip + direction.
        # Use re.match on the part to ensure it starts with the number (dip)
        match = re.match(r"(\d+\.?\d*)\s*([NSEW]{1,2})", part)
        if match:
            dip, cardinal = match.groups()
            dip = float(dip)
            dip_dir = cardinal_to_azimuth(cardinal)
            if dip_dir is not None:
                return dip, dip_dir

    return None, None


def cardinal_to_azimuth(text: str) -> float | None:
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


def extract_feature_attributes(feature: Any) -> dict[str, Any]:
    """Extract attributes from a QgsFeature into a pure Python dictionary.

    Args:
        feature: The QgsFeature object.

    Returns:
        A dictionary mapping field names to attribute values.

    """
    if not feature or not hasattr(feature, "fields"):
        return {}
    return dict(zip(feature.fields().names(), feature.attributes(), strict=False))
