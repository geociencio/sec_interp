"""Parsing Utilities Module.

Parsing of geological structural measurements (strike/dip).
Supports numeric and field notation formats.
"""

import re


def parse_strike(value):
    """Parse strike value from various formats.

    Accepts:
        - Numeric azimuth (string or int)
        - Quadrant notation ("N 30° E", "S 15° W")

    Returns:
        strike in azimuth degrees (0–360) or None if invalid
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


def parse_dip(value):
    """Parse dip value from various formats.

    Accepts:
        - Numeric dip: "22", "45.5", "30.0"
        - Field notation: "22° SW", "45 NE", "10 S"

    Returns:
        tuple: (dip_angle, dip_direction_azimuth) or (None, None) if invalid
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


def cardinal_to_azimuth(text: str):
    """Convert cardinal direction to azimuth.

    Converts: N, NE, E, SE, S, SW, W, NW

    Returns:
        0–360 azimuth or None if invalid
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
