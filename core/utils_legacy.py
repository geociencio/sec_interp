"""Core Utilities Module."""

import math
import re

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsDistanceArea,
    QgsFeature,
    QgsFeatureRequest,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
    QgsSpatialIndex,
    QgsVectorFileWriter,
    QgsVectorLayer,
    QgsWkbTypes,
)

from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


def create_buffer_geometry(
    geometry: QgsGeometry,
    crs: QgsCoordinateReferenceSystem,
    distance: float,
    segments: int = 25,
) -> QgsGeometry:
    """Create buffer geometry using native QGIS processing algorithm.

    Uses native:buffer for better CRS handling and robustness compared to
    the manual QgsGeometry.buffer() method.

    Args:
        geometry: Input geometry to buffer
        crs: Coordinate reference system of the geometry
        distance: Buffer distance in CRS units
        segments: Number of segments to approximate curves (default: 25)

    Returns:
        QgsGeometry: Buffered geometry

    Raises:
        ValueError: If buffer creation fails or geometry is invalid
        RuntimeError: If processing algorithm fails

    Example:
        >>> line_geom = line_layer.geometry()
        >>> buffer_geom = create_buffer_geometry(line_geom, line_layer.crs(), 100.0)
    """
    from qgis import processing
    from qgis.core import QgsProcessingFeedback

    if not geometry or geometry.isNull():
        raise ValueError("Input geometry is null or invalid")

    # Determine geometry type for temporary layer
    geom_type_map = {
        QgsWkbTypes.PointGeometry: "Point",
        QgsWkbTypes.LineGeometry: "LineString",
        QgsWkbTypes.PolygonGeometry: "Polygon",
    }
    geom_type = geom_type_map.get(geometry.type(), "LineString")

    try:
        # Create temporary memory layer with the geometry
        temp_layer = QgsVectorLayer(geom_type, "temp_buffer", "memory")
        temp_layer.setCrs(crs)

        temp_feat = QgsFeature()
        temp_feat.setGeometry(geometry)
        temp_layer.dataProvider().addFeatures([temp_feat])

        # Create feedback for logging (silent mode)
        feedback = QgsProcessingFeedback()

        # Run native buffer algorithm
        logger.debug(
            f"Creating buffer: distance={distance} {crs.mapUnits()}, segments={segments}"
        )

        result = processing.run(
            "native:buffer",
            {
                "INPUT": temp_layer,
                "DISTANCE": distance,
                "SEGMENTS": segments,
                "END_CAP_STYLE": 0,  # Round
                "JOIN_STYLE": 0,  # Round
                "MITER_LIMIT": 2,
                "DISSOLVE": False,
                "OUTPUT": "memory:",
            },
            feedback=feedback,
        )

        # Extract buffer geometry from result
        buffer_layer = result["OUTPUT"]
        if buffer_layer.featureCount() == 0:
            raise ValueError("Buffer algorithm produced no features")

        # Get first feature's geometry
        buffer_feat = next(buffer_layer.getFeatures())
        buffer_geom = buffer_feat.geometry()

        if not buffer_geom or buffer_geom.isNull():
            raise ValueError("Buffer geometry is invalid")

        logger.debug("✓ Buffer created successfully using native algorithm")
        return buffer_geom

    except Exception as e:
        error_msg = f"Failed to create buffer using native algorithm: {e!s}"
        logger.exception(error_msg)
        raise RuntimeError(error_msg) from e


def filter_features_by_buffer(
    features_layer: QgsVectorLayer,
    buffer_geometry: QgsGeometry,
    buffer_crs: QgsCoordinateReferenceSystem,
) -> list[QgsFeature]:
    """Filter features that intersect with buffer using native algorithm.

    Uses native:extractbylocation with spatial indexing for efficient filtering.
    This is much faster than manual iteration with intersects() for large datasets
    because it uses an R-tree spatial index.

    Args:
        features_layer: Layer containing features to filter
        buffer_geometry: Buffer geometry to use for spatial filter
        buffer_crs: CRS of the buffer geometry

    Returns:
        list[QgsFeature]: List of features that intersect the buffer

    Raises:
        ValueError: If inputs are invalid
    """
    if not features_layer or not features_layer.isValid():
        raise ValueError("Invalid features layer")

    if not buffer_geometry or buffer_geometry.isNull():
        raise ValueError("Invalid buffer geometry")

    # 1. Build Spatial Index
    index = QgsSpatialIndex(features_layer.getFeatures())

    # 2. Get candidates using Bounding Box (Fast R-tree lookup)
    # intersects() returns list of feature IDs
    candidate_ids = index.intersects(buffer_geometry.boundingBox())

    # 3. Precise filtering
    filtered_features = []
    # Using QgsFeatureRequest with specific IDs is faster than iterating all
    if candidate_ids:
        request = QgsFeatureRequest().setFilterFids(candidate_ids)
        for feature in features_layer.getFeatures(request):
            if feature.geometry().intersects(buffer_geometry):
                filtered_features.append(feature)

    logger.debug(
        f"Spatial Index filtering: {len(candidate_ids)} candidates -> {len(filtered_features)} confirmed"
    )

    return filtered_features


def densify_line_by_interval(
    geometry: QgsGeometry,
    interval: float,
) -> QgsGeometry:
    """Densify line geometry by adding vertices at regular intervals.

    Uses native:densifygeometriesgivenaninterval for precise vertex placement.
    This is simpler and more accurate than manual interpolation loops.

    Args:
        geometry: Line geometry to densify
        interval: Distance between vertices in geometry units

    Returns:
        QgsGeometry: Densified line geometry with vertices at regular intervals

    Raises:
        ValueError: If geometry is invalid or not a line
        RuntimeError: If densification algorithm fails

    Example:
        >>> line_geom = line_layer.geometry()
        >>> interval = raster_layer.rasterUnitsPerPixelX()
        >>> densified = densify_line_by_interval(line_geom, interval)
        >>> points = densified.asPolyline()  # Now has vertices at regular intervals
    """
    from qgis import processing
    from qgis.core import QgsProcessingFeedback

    if not geometry or geometry.isNull():
        raise ValueError("Input geometry is null or invalid")

    if geometry.type() != QgsWkbTypes.LineGeometry:
        raise ValueError("Geometry must be a LineString")

    try:
        # Create temporary layer with geometry
        temp_layer = QgsVectorLayer("LineString", "temp_densify", "memory")
        temp_feat = QgsFeature()
        temp_feat.setGeometry(geometry)
        temp_layer.dataProvider().addFeatures([temp_feat])

        # Create feedback for logging
        feedback = QgsProcessingFeedback()

        logger.debug(f"Densifying line with interval={interval:.2f}")

        # Run densification algorithm
        result = processing.run(
            "native:densifygeometriesgivenaninterval",
            {
                "INPUT": temp_layer,
                "INTERVAL": interval,
                "OUTPUT": "memory:",
            },
            feedback=feedback,
        )

        # Extract densified geometry
        densified_layer = result["OUTPUT"]
        if densified_layer.featureCount() == 0:
            raise ValueError("Densification produced no features")

        densified_feat = next(densified_layer.getFeatures())
        densified_geom = densified_feat.geometry()

        if not densified_geom or densified_geom.isNull():
            raise ValueError("Densified geometry is invalid")

        # Get vertex count for logging
        if densified_geom.isMultipart():
            vertex_count = sum(len(part) for part in densified_geom.asMultiPolyline())
        else:
            vertex_count = len(densified_geom.asPolyline())

        logger.debug(f"✓ Densification complete: {vertex_count} vertices")
        return densified_geom

    except Exception as e:
        error_msg = f"Failed to densify line: {e!s}"
        logger.exception(error_msg)
        raise RuntimeError(error_msg) from e


def calculate_line_azimuth(line_geom):
    """Calculate the azimuth of a line.

    Args:
        line_geom (QgsGeometry): The line geometry to calculate azimuth for.

    Returns:
        float: Azimuth in degrees (0-360). Returns 0 for points or invalid lines.
    """
    if line_geom.wkbType() == QgsWkbTypes.Point:
        return 0  # Points have no azimuth

    if line_geom.wkbType() == QgsWkbTypes.LineString:
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

    # For other geometry types, return a default value
    return 0


def calculate_step_size(geom, raster_lyr):
    """Calculate step size based on slope and raster resolution.

    .. deprecated::
        Use densify_line_by_interval() instead for better precision and simpler code.
        This function is kept for backward compatibility but may be removed in future versions.

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


def sample_elevation_along_line(
    geometry, raster_layer, band_number, distance_area, reference_point=None
):
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
    # Densify line at raster resolution
    interval = raster_layer.rasterUnitsPerPixelX()
    try:
        densified_geom = densify_line_by_interval(geometry, interval)
    except (ValueError, RuntimeError):
        # Fallback to original geometry if densification fails
        densified_geom = geometry

    # Get vertices from densified geometry
    if densified_geom.isMultipart():
        vertices = densified_geom.asMultiPolyline()[0]
    else:
        vertices = densified_geom.asPolyline()

    points = []
    start_pt = reference_point if reference_point else vertices[0]

    # Sample elevation at each vertex
    for pt in vertices:
        # Calculate distance for X axis
        if reference_point:
            dist_from_start = distance_area.measureLine(reference_point, pt)
        else:
            dist_from_start = distance_area.measureLine(start_pt, pt)

        val, ok = raster_layer.dataProvider().sample(pt, band_number)
        elev = val if ok else 0.0
        points.append(QgsPointXY(dist_from_start, elev))

    return points


def create_shapefile_writer(
    output_path, crs, fields, geometry_type=QgsWkbTypes.LineString
):
    """Helper to create a QgsVectorFileWriter.

    Args:
        output_path (Path or str): Path where shapefile will be created.
        crs (QgsCoordinateReferenceSystem): CRS for the shapefile.
        fields (QgsFields): Fields definition for the shapefile.
        geometry_type (QgsWkbTypes.GeometryType): Geometry type (default: LineString).

    Returns:
        QgsVectorFileWriter: Initialized writer object.

    Raises:
        IOError: If writer creation fails.
    """
    # Use new static create method for QGIS 3.38+
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "ESRI Shapefile"
    options.fileEncoding = "UTF-8"

    writer = QgsVectorFileWriter.create(
        str(output_path),
        fields,
        geometry_type,
        crs,
        QgsProject.instance().transformContext(),
        options,
    )

    if writer.hasError() != QgsVectorFileWriter.NoError:
        raise OSError(
            f"Error creating shapefile {output_path}: {writer.errorMessage()}"
        )

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
    app_dip = math.degrees(math.atan(math.tan(beta) * math.sin(alpha - theta)))
    return app_dip


def show_user_message(parent, title, message, level="warning"):
    """Show message box with consistent styling and automatic logging.

    Args:
        parent: Parent widget (usually dialog or main window)
        title: Message box title
        message: Message content
        level: Message level - "warning", "info", "error", "critical"

    Returns:
        QMessageBox.StandardButton for "question" level, None otherwise

    Example:
        show_user_message(self.dlg, "Error", "Invalid input", "warning")
    """
    from qgis.PyQt.QtWidgets import QMessageBox

    from sec_interp.logger_config import get_logger

    logger = get_logger(__name__)

    # Log the message
    if level in {"error", "critical"}:
        logger.error(f"{title}: {message}")
    elif level == "warning":
        logger.warning(f"{title}: {message}")
    else:
        logger.info(f"{title}: {message}")

    # Show message box
    if level == "warning":
        QMessageBox.warning(parent, title, message)
    elif level == "info":
        QMessageBox.information(parent, title, message)
    elif level in {"error", "critical"}:
        QMessageBox.critical(parent, title, message)
    elif level == "question":
        return QMessageBox.question(
            parent, title, message, QMessageBox.Yes | QMessageBox.No
        )


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
        "min_d": min_d - d_range * 0.05,
        "max_d": max_d + d_range * 0.05,
        "min_e": min_e - e_range * 0.05,
        "max_e": max_e + e_range * 0.05,
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

    if normalized < 5:
        return magnitude

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


# Utilities for parsing geological structural measurements.
#
# Supports:
# - Numeric strike/dip (e.g. strike=345, dip=22)
# - Field notation (e.g. "N 15° W", "22° SW")


# ------------------------------------
#  STRIKE PARSER
# ------------------------------------
def parse_strike(value):
    """Accepts:
        - Numeric azimuth (string or int)
        - Quadrant notation ("N 30° E", "S 15° W").

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
    """Accepts:
        - Numeric dip: "22", "45.5", "30.0"
        - Field notation: "22° SW", "45 NE", "10 S"
    Returns:
        (dip_angle, dip_direction_azimuth).
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
    """Converts:
        N, NE, E, SE, S, SW, W, NW
    Returns:
        0–360 azimuth.
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
