# -*- coding: utf-8 -*-
"""
Core Utilities Module
"""

import math
import re
from qgis.core import (
    QgsDistanceArea,
    QgsProject,
    QgsPointXY,
    QgsWkbTypes,
    QgsVectorFileWriter,
    QgsGeometry
)

def calculate_line_azimuth(line_geom):
    """Calculate the azimuth of a line.
    
    Args:
        line_geom (QgsGeometry): The line geometry to calculate azimuth for.
        
    Returns:
        float: Azimuth in degrees (0-360). Returns 0 for points or invalid lines.
    """
    if line_geom.wkbType() == QgsWkbTypes.Point:
        return 0  # Points have no azimuth
    elif line_geom.wkbType() == QgsWkbTypes.LineString:
        line = line_geom.asPolyline()
        if len(line) < 2:
            return 0
        # Calculate azimuth of first segment (from first to second point)
        p1 = line[0]
        p2 = line[1]
        azimuth = math.degrees(math.atan2(p2.x() - p1.x(), p2.y() - p1.y()))
        # Convert to compass bearing (0-360)
        if azimuth < 0:
            azimuth += 360
        return azimuth
    else:
        # For other geometry types, return a default value
        return 0

def calculate_step_size(geom, raster_lyr):
    """Calculate step size based on slope and raster resolution.
    
    Ensures that sampling occurs at approximately one pixel intervals,
    accounting for the slope of the line relative to the raster grid.
    
    Args:
        geom (QgsGeometry): The geometry to sample along.
        raster_lyr (QgsRasterLayer): The raster layer being sampled.
        
    Returns:
        float: Calculated step size in map units.
    """
    # Get raster resolution
    res = raster_lyr.rasterUnitsPerPixelX()

    # Calculate step size based on slope to ensure 1 pixel sampling
    dist_step = res
    try:
        if geom.isMultipart():
            parts = geom.asMultiPolyline()
            line_pts = parts[0] if parts else []
        else:
            line_pts = geom.asPolyline()

        if line_pts and len(line_pts) >= 2:
            p1 = line_pts[0]
            p2 = line_pts[-1]
            dx = abs(p2.x() - p1.x())
            dy = abs(p2.y() - p1.y())
            if max(dx, dy) > 0:
                dist_step = geom.length() * res / max(dx, dy)
    except (ValueError, TypeError):
        # Fallback to simple resolution if geometry parsing fails
        pass
    return dist_step

def get_line_start_point(geometry):
    """Helper to get the start point of a line geometry.
    
    Args:
        geometry (QgsGeometry): The geometry to get start point from.
        
    Returns:
        QgsPointXY: The starting point of the line.
    """
    if geometry.isMultipart():
        return geometry.asMultiPolyline()[0][0]
    else:
        return geometry.asPolyline()[0]

def create_distance_area(crs):
    """Helper to create and configure QgsDistanceArea.
    
    Args:
        crs (QgsCoordinateReferenceSystem): The CRS to use for calculations.
        
    Returns:
        QgsDistanceArea: Configured distance area object.
    """
    da = QgsDistanceArea()
    da.setSourceCrs(crs, QgsProject.instance().transformContext())
    da.setEllipsoid(crs.ellipsoidAcronym())
    return da

def sample_elevation_along_line(geometry, raster_layer, band_number, distance_area, reference_point=None):
    """Helper to sample elevation values along a line geometry.
    
    Args:
        geometry: QgsGeometry (LineString) to sample along.
        raster_layer: QgsRasterLayer to sample from.
        band_number: Raster band number.
        distance_area: QgsDistanceArea for distance calculations.
        reference_point: Optional QgsPointXY to measure distance from. 
                         If None, distance is measured from the start of the geometry.
                         
    Returns:
        List of QgsPointXY(distance, elevation).
    """
    dist_step = calculate_step_size(geometry, raster_layer)
    length = geometry.length()
    current_dist = 0.0
    points = []
    
    start_pt = reference_point if reference_point else geometry.interpolate(0).asPoint()

    while current_dist <= length:
        pt = geometry.interpolate(current_dist).asPoint()
        
        # Calculate distance for X axis
        if reference_point:
            dist_from_start = distance_area.measureLine(reference_point, pt)
        else:
            dist_from_start = distance_area.measureLine(start_pt, pt)

        val, ok = raster_layer.dataProvider().sample(pt, band_number)
        elev = val if ok else 0.0
        points.append(QgsPointXY(dist_from_start, elev))
        current_dist += dist_step
        
    return points

def create_shapefile_writer(output_path, crs, fields, geometry_type=QgsWkbTypes.LineString):
    """Helper to create a QgsVectorFileWriter.
    
    Args:
        output_path (Path or str): Path where shapefile will be created.
        crs (QgsCoordinateReferenceSystem): CRS for the shapefile.
        fields (QgsFields): Fields definition for the shapefile.
        geometry_type (QgsWkbTypes.GeometryType): Geometry type (default: LineString).
        
    Returns:
        QgsVectorFileWriter: Initialized writer object.
        
    Raises:
        Exception: If writer creation fails.
    """
    writer = QgsVectorFileWriter(
        str(output_path),
        "UTF-8",
        fields,
        geometry_type,
        crs,
        "ESRI Shapefile"
    )
    
    if writer.hasError() != QgsVectorFileWriter.NoError:
        raise Exception(f"Error creating shapefile {output_path}: {writer.errorMessage()}")
        
    return writer

def prepare_profile_context(line_lyr):
    """Prepare common context for profile operations.
    
    Args:
        line_lyr (QgsVectorLayer): The cross-section line layer.
        
    Returns:
        tuple: (line_geom, line_start, distance_area)
            - line_geom (QgsGeometry): The geometry of the section line.
            - line_start (QgsPointXY): The starting point of the line.
            - distance_area (QgsDistanceArea): Configured distance area object.
            
    Raises:
        ValueError: If layer has no features or invalid geometry.
    """
    line_feat = next(line_lyr.getFeatures(), None)
    if not line_feat:
        raise ValueError("Line layer has no features")
    
    line_geom = line_feat.geometry()
    if not line_geom or line_geom.isNull():
        raise ValueError("Line geometry is not valid")
    
    line_start = get_line_start_point(line_geom)
    da = create_distance_area(line_lyr.crs())
    
    return line_geom, line_start, da

def calculate_apparent_dip(true_strike, true_dip, line_azimuth):
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
        true_strike (float): Strike of the geological plane (0-360 degrees).
        true_dip (float): True dip of the geological plane (0-90 degrees).
        line_azimuth (float): Azimuth of the cross-section line (0-360 degrees).
        
    Returns:
        float: Apparent dip in degrees. Positive values indicate dip, 
               negative values might occur depending on quadrant but are 
               typically normalized.
    """
    alpha = math.radians(true_strike)
    beta = math.radians(true_dip)
    theta = math.radians(line_azimuth)
    app_dip = math.degrees(
        math.atan(math.tan(beta) * math.sin(alpha - theta)))
    return app_dip

# Preview rendering utilities

def calculate_bounds(topo_data, geol_data=None):
    """Calculate min/max bounds for all data.
    
    Args:
        topo_data (list): List of (distance, elevation) tuples for topography.
        geol_data (list, optional): List of (distance, elevation, name) tuples for geology.
        
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
        'min_d': min_d - d_range * 0.05,
        'max_d': max_d + d_range * 0.05,
        'min_e': min_e - e_range * 0.05,
        'max_e': max_e + e_range * 0.05
    }

def create_coordinate_transform(bounds, view_w, view_h, margin, vert_exag=1.0):
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
    data_w = bounds['max_d'] - bounds['min_d']
    data_h = bounds['max_e'] - bounds['min_e']
    
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
        x = margin + (dist - bounds['min_d']) * scale_x
        y = view_h - margin - (elev - bounds['min_e']) * scale_y
        return x, y
    
    return transform

def calculate_interval(data_range):
    """Calculate nice interval for axis labels.
    
    Args:
        data_range (float): The total range of data values.
        
    Returns:
        float: A 'nice' interval (e.g., 1, 2, 5, 10, etc.) for grid lines.
    """
    magnitude = 10 ** math.floor(math.log10(data_range))
    normalized = data_range / magnitude
    
    if normalized < 2:
        return magnitude * 0.5
    elif normalized < 5:
        return magnitude
    else:
        return magnitude * 2

def interpolate_elevation(topo_data, distance):
    """Interpolate elevation at given distance.
    
    Args:
        topo_data (list): List of (distance, elevation) tuples.
        distance (float): Distance at which to interpolate elevation.
        
    Returns:
        float: Interpolated elevation value.
    """
    if not topo_data:
        return 0

    # Find nearest points
    for i in range(len(topo_data) - 1):
        dist1, elev1 = topo_data[i]
        dist2, elev2 = topo_data[i + 1]
        # Interpolate elevation
        if dist1 <= distance <= dist2:
            ratio = (distance - dist1) / (dist2 - dist1)
            return elev1 + (elev2 - elev1) * ratio
    
    # Return last elevation if distance is beyond last point
    return topo_data[-1][1] if topo_data else 0

"""
Utilities for parsing geological structural measurements.

Supports:
- Numeric strike/dip (e.g. strike=345, dip=22)
- Field notation (e.g. "N 15° W", "22° SW")
"""

# ------------------------------------
#  STRIKE PARSER
# ------------------------------------
def parse_strike(value):
    """
    Accepts:
        - Numeric azimuth (string or int)
        - Quadrant notation ("N 30° E", "S 15° W")
    Returns:
        strike in azimuth degrees (0–360)
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


# ------------------------------------
#  DIP PARSER
# ------------------------------------
def parse_dip(value):
    """
    Accepts:
        - Numeric dip: "22", "45.5", "30.0"
        - Field notation: "22° SW", "45 NE", "10 S"
    Returns:
        (dip_angle, dip_direction_azimuth)
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


# ------------------------------------
#  Helper for converting cardinal directions to azimuth
# ------------------------------------
def cardinal_to_azimuth(text):
    """
    Converts:
        N, NE, E, SE, S, SW, W, NW
    Returns:
        0–360 azimuth
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

    return table.get(text, None)