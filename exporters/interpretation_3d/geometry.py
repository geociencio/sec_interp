"""2D-to-3D projection helpers for interpretation polygons."""

from __future__ import annotations

import math
from typing import Any

from qgis.core import (
    QgsGeometry,
    QgsLineString,
    QgsPoint,
    QgsPointXY,
    QgsPolygon,
)

from sec_interp.exporters.interpretation_3d.fields import make_fields_obj
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)

MIN_VALID_POLYGON_VERTICES = 4
MIN_REQUIRED_FOR_CLOSURE = 2


def calculate_section_geometry(
    section_line: QgsGeometry,
) -> tuple[float, float, float]:
    """Calculate origin and azimuth from the section line."""
    if section_line.isMultipart():
        line_points = section_line.asMultiPolyline()[0]
    else:
        line_points = section_line.asPolyline()

    p1 = line_points[0]
    p2 = line_points[-1]
    dx = p2.x() - p1.x()
    dy = p2.y() - p1.y()
    azimuth = math.atan2(dy, dx)

    logger.info(
        f"Section Plane: Origin({p1.x():.2f}, {p1.y():.2f}), "
        f"Azimuth({math.degrees(azimuth):.2f} deg)"
    )
    return p1.x(), p1.y(), azimuth


def create_3d_rings(
    poly_2d: list[list[QgsPointXY]],
    origin_x: float,
    origin_y: float,
    azimuth: float,
    vert_exag: float,
) -> list[QgsLineString]:
    """Transform 2D rings to 3D LineStrings."""
    rings_3d = []
    cos_a = math.cos(azimuth)
    sin_a = math.sin(azimuth)

    for ring_2d in poly_2d:
        points_3d = []
        for point_2d in ring_2d:
            east = origin_x + (point_2d.x() * cos_a)
            north = origin_y + (point_2d.x() * sin_a)
            elev = point_2d.y() / vert_exag
            points_3d.append(QgsPoint(east, north, elev))
        rings_3d.append(QgsLineString(points_3d))
    return rings_3d


def project_to_3d_features(
    geom_2d: QgsGeometry,
    polygon: Any,
    fields: list,
    origin_x: float,
    origin_y: float,
    azimuth: float,
    custom_keys: list[str],
    vert_exag: float = 1.0,
) -> list[Any]:
    """Project a 2D geometry (potentially MultiPolygon) to 3D features."""
    from qgis.core import QgsFeature

    projected_features = []
    polygons_2d = geom_2d.asMultiPolygon() if geom_2d.isMultipart() else [geom_2d.asPolygon()]

    for poly_2d in polygons_2d:
        rings_3d = create_3d_rings(poly_2d, origin_x, origin_y, azimuth, vert_exag)
        if not rings_3d:
            continue

        polygon_3d = QgsPolygon()
        polygon_3d.setExteriorRing(rings_3d[0])
        for i in range(1, len(rings_3d)):
            polygon_3d.addInteriorRing(rings_3d[i])

        feature = QgsFeature()
        feature.setFields(make_fields_obj(fields))
        feature.setAttribute("id", polygon.id)
        feature.setAttribute("name", polygon.name)
        feature.setAttribute("type", polygon.type)
        feature.setAttribute("color", polygon.color)
        feature.setAttribute("created_at", polygon.created_at)
        for key in custom_keys:
            feature.setAttribute(key, str(polygon.attributes.get(key, "")))
        feature.setGeometry(QgsGeometry(polygon_3d))
        projected_features.append(feature)

    return projected_features


def prepare_2d_geometry(polygon: Any) -> QgsGeometry | None:
    """Prepare and validate 2D geometry from polygon vertices."""
    vertices = get_unique_vertices(polygon.vertices_2d)
    if not vertices:
        return None

    vertices = ensure_closed_polygon(vertices)
    if len(vertices) < MIN_VALID_POLYGON_VERTICES:
        logger.warning(f"Polygon {polygon.id} has insufficient unique vertices. Skipping.")
        return None

    qgs_points_3d = [QgsPoint(x, y, 0.0) for x, y in vertices]
    polygon_2d = QgsPolygon()
    polygon_2d.setExteriorRing(QgsLineString(qgs_points_3d))
    geom_2d = QgsGeometry(polygon_2d)
    if not geom_2d.isGeosValid():
        logger.info(f"Correcting 2D geometry for polygon {polygon.id}")
        geom_2d = geom_2d.makeValid()
    return geom_2d


def get_unique_vertices(vertices_2d: Any) -> list:
    """Deduplicate consecutive vertices."""
    raw_list = list(vertices_2d)
    if not raw_list:
        return []

    dedup: list[Any] = []
    for vertex in raw_list:
        if not dedup or vertex != dedup[-1]:
            dedup.append(vertex)
    return dedup


def ensure_closed_polygon(vertices: list) -> list:
    """Ensure the polygon vertices are closed."""
    if len(vertices) > MIN_REQUIRED_FOR_CLOSURE and vertices[0] != vertices[-1]:
        return [*vertices, vertices[0]]
    return vertices


def collect_projected_features(
    interpretations: list[Any],
    fields: list,
    sorted_keys: list[str],
    origin_x: float,
    origin_y: float,
    azimuth: float,
) -> list[Any]:
    """Project every valid interpretation polygon to 3D features."""
    features = []
    for polygon in interpretations:
        geom_2d = prepare_2d_geometry(polygon)
        if not geom_2d:
            continue
        features.extend(
            project_to_3d_features(
                geom_2d,
                polygon,
                fields,
                origin_x,
                origin_y,
                azimuth,
                sorted_keys,
                vert_exag=1.0,
            )
        )
    return features
