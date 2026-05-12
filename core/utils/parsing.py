"""Data parsing and conversion utilities."""

from __future__ import annotations

import re
from typing import Any


def _parse_quadrant_strike(part: str) -> float | None:
    """Parse a single part for quadrant strike notation."""
    # Regex for quadrant notation: N/S + angle + E/W
    # Use re.search to allow prefixes like "Strike: "
    match = re.search(r"([NS])\s*(\d+\.?\d*)\s*([EW])", part)
    if not match:
        return None

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

    # If already numeric, return correctly wrapped
    try:
        return float(value) % 360
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

    # Split by common delimiters: comma, slash, semicolon, vertical bar, or dash
    # We use a regex split to handle multiple delimiters
    parts = re.split(r"[,/\\;|]", text)
    parts = [p.strip() for p in parts if p.strip()]

    for part in parts:
        strike = _parse_quadrant_strike(part)
        if strike is not None:
            return strike

    # If it's a simple number after stripping noise, try parsing it as azimuth
    # but only if it's NOT followed by a dip-like cardinal direction (e.g. "45 SE")
    # or preceded by a "DIP:"-like label.
    if re.search(r"(?:DIP|BUZA|PEND)", text):
        return None

    numeric_match = re.search(r"(\d+\.?\d*)", text)
    if numeric_match:
        # Check if follow-up is a dip direction (NSEW 1-2 chars at end of word)
        # This prevents picking up "45" from "45 SE"
        if re.search(r"\d+\.?\d*\s+[NSEW]{1,2}(?!\w)", text):
            # But only if it's clearly a dip (like "45 SE") and not just "45"
            pass
        else:
            try:
                return float(numeric_match.group(1)) % 360
            except (ValueError, TypeError):
                pass

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

    # Split by common delimiters
    parts = re.split(r"[,/\\;|]", text)
    parts = [p.strip() for p in parts if p.strip()]

    for part in parts:
        # Avoid picking up Quadrant Strike notation (e.g., "N 45 E") as Dip
        # We look for N/S followed by number followed by E/W
        if re.search(r"[NS]\s*\d+\.?\d*\s*[EW]", part):
            continue

        # Case 2: full dip + direction.
        # Use re.search on the part to allow noise/prefixes
        # Ensure we match a number followed by a cardinal direction
        match = re.search(r"(\d+\.?\d*)\s*([NSEW]{1,2})", part)
        if match:
            dip, cardinal = match.groups()
            # Ensure it's not part of a quadrant strike (redundant but safe)
            # A dip direction like NE, SW, etc. or N, S, E, W
            # If the part has N/S before the number, it was caught above.
            dip_val = float(dip)
            dip_dir = cardinal_to_azimuth(cardinal)
            if dip_dir is not None:
                return dip_val, dip_dir

    # Try simple numeric extraction if no pattern matched
    # (Avoid strings that look like quadrant strike)
    if not re.search(r"[NS]\s*\d+\.?\d*", text):
        numeric_match = re.search(r"(\d+\.?\d*)", text)
        if numeric_match:
            try:
                return float(numeric_match.group(1)), None
            except (ValueError, TypeError):
                pass

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

    Ensures all values are converted to standard Python primitives to avoid
    threading issues with QVariant objects in QGIS 4/Qt6.

    Args:
        feature: The QgsFeature object.

    Returns:
        A dictionary mapping field names to sanitized attribute values.

    """
    if not feature or not hasattr(feature, "fields"):
        return {}

    names = feature.fields().names()
    raw_values = feature.attributes()
    sanitized = {}

    for name, val in zip(names, raw_values, strict=False):
        # Convert QVariant/NULL/etc to pure Python
        if val is None or str(val) == "NULL":
            sanitized[name] = None
        elif isinstance(val, int | float | str | bool):
            sanitized[name] = val
        else:
            # Fallback for complex types (dates, etc) to string
            sanitized[name] = str(val)

    return sanitized
