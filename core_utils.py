# -*- coding: utf-8 -*-
"""
Core Utilities Module
"""

import math
from qgis.core import (
    QgsDistanceArea,
    QgsProject,
    QgsPointXY,
    QgsWkbTypes,
    QgsVectorFileWriter,
    QgsGeometry
)

def calculate_line_azimuth(line_geom):
    """Calculate the azimuth of a line."""
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
    """Calculate step size based on slope and raster resolution."""
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
    except Exception:
        # Fallback to simple resolution if geometry parsing fails
        pass
    return dist_step

def get_line_start_point(geometry):
    """Helper to get the start point of a line geometry."""
    if geometry.isMultipart():
        return geometry.asMultiPolyline()[0][0]
    else:
        return geometry.asPolyline()[0]

def create_distance_area(crs):
    """Helper to create and configure QgsDistanceArea."""
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
    """Helper to create a QgsVectorFileWriter."""
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

def calculate_apparent_dip(true_strike, true_dip, line_azimuth):
    """Convert true dip to apparent dip in section plane."""
    alpha = math.radians(true_strike)
    beta = math.radians(true_dip)
    theta = math.radians(line_azimuth)
    app_dip = math.degrees(
        math.atan(math.tan(beta) * math.sin(alpha - theta)))
    return app_dip
