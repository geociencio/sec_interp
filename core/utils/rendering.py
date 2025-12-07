# -*- coding: utf-8 -*-
"""
Rendering Utilities Module

Visualization and coordinate transformation utilities for profile rendering.
"""

import math


def calculate_bounds(topo_data: list, geol_data: list = None) -> dict:
    """Calculate min/max bounds for all data.

    Args:
        topo_data: List of (distance, elevation) tuples for topography.
        geol_data: List of (distance, elevation, name) tuples for geology.

    Returns:
        dict: Dictionary containing 'min_d', 'max_d', 'min_e', 'max_e' with 5% padding.
    """
    dists = [p[0] for p in topo_data]
    elevs = [p[1] for p in topo_data]

    if geol_data:
        dists.extend([p[0] for p in geol_data])
        elevs.extend([p[1] for p in geol_data])

    min_d, max_d = min(dists), max(dists)
    min_e, max_e = min(elevs), max(elevs)

    # Avoid division by zero
    if max_d == min_d:
        max_d = min_d + 100
    if max_e == min_e:
        max_e = min_e + 10

    # Add 5% padding
    d_range = max_d - min_d
    e_range = max_e - min_e

    return {
        "min_d": min_d - d_range * 0.05,
        "max_d": max_d + d_range * 0.05,
        "min_e": min_e - e_range * 0.05,
        "max_e": max_e + e_range * 0.05,
    }


def create_coordinate_transform(bounds: dict, view_w: int, view_h: int, margin: int, vert_exag: float = 1.0):
    """Create coordinate transformation function.

    Args:
        bounds: Dictionary with min_d, max_d, min_e, max_e
        view_w: View width in pixels
        view_h: View height in pixels
        margin: Margin in pixels
        vert_exag: Vertical exaggeration factor (default 1.0 = no exaggeration, i.e., 1:1 scale)

    Returns:
        Function that transforms (distance, elevation) to (x, y) screen coordinates
    """
    data_w = bounds["max_d"] - bounds["min_d"]
    data_h = bounds["max_e"] - bounds["min_e"]

    # Calculate potential scales for each axis
    potential_scale_x = (view_w - 2 * margin) / data_w
    potential_scale_y = (view_h - 2 * margin) / data_h

    # Use the smaller scale as the base to ensure everything fits
    # This gives us a 1:1 aspect ratio when vert_exag = 1.0
    base_scale = min(potential_scale_x, potential_scale_y)

    # Apply base scale to both axes
    scale_x = base_scale
    scale_y = base_scale * vert_exag  # Apply vertical exaggeration

    def transform(dist, elev):
        x = margin + (dist - bounds["min_d"]) * scale_x
        y = view_h - margin - (elev - bounds["min_e"]) * scale_y
        return x, y

    return transform


def calculate_interval(data_range: float) -> float:
    """Calculate nice interval for axis labels.

    Args:
        data_range: The total range of data values.

    Returns:
        float: A 'nice' interval (e.g., 1, 2, 5, 10, etc.) for grid lines.
    """
    magnitude = 10 ** math.floor(math.log10(data_range))
    normalized = data_range / magnitude

    if normalized < 2:
        return magnitude * 0.5
    
    if normalized < 5:
        return magnitude
        
    return magnitude * 2
