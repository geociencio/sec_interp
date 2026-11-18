"""2D-to-3D projection helpers for interpretation polygons."""

from __future__ import annotations

from typing import Any

from qgis.core import (
    QgsGeometry,
    QgsLineString,
    QgsPoint,
    QgsPointXY,
    QgsPolygon,
)

from sec_interp.core.domain.section_frame import SectionFrame
from sec_interp.exporters.interpretation_3d.fields import make_fields_obj
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)

MIN_VALID_POLYGON_VERTICES = 4
MIN_REQUIRED_FOR_CLOSURE = 2


def build_section_frame(
    section_line: QgsGeometry,
    crs_authid: str = "",
) -> SectionFrame:
    """Build the shared section frame from a line geometry.

    Args:
        section_line: Two-vertex (or multi-part) section line.
        crs_authid: CRS authority identifier for the exported layers.

    Returns:
        A validated section frame.

    Raises:
        ValueError: If the line has fewer than two points or is degenerate.

    """
    line_points = (
        section_line.asMultiPolyline()[0]
        if section_line.isMultipart()
        else section_line.asPolyline()
    )
    if len(line_points) < MIN_REQUIRED_FOR_CLOSURE:
        raise ValueError("section line must contain at least two points")

    p1 = line_points[0]
    p2 = line_points[-1]
    frame = SectionFrame.from_endpoints(
        p1.x(),
        p1.y(),
        p2.x(),
        p2.y(),
        crs_authid=crs_authid,
    )
    logger.info(
        f"Section Plane: Origin({frame.origin_x:.2f}, {frame.origin_y:.2f}), "
        f"Azimuth({frame.azimuth_deg:.2f} deg), Length({frame.length:.2f})"
    )
    return frame


def calculate_section_geometry(
    section_line: QgsGeometry,
) -> tuple[float, float, float]:
    """Calculate origin and azimuth from the section line.

    Kept for callers that still consume the legacy tuple API.
    """
    frame = build_section_frame(section_line)
    return frame.origin_x, frame.origin_y, frame.azimuth_rad


def create_3d_rings(
    poly_2d: list[list[QgsPointXY]],
    frame: SectionFrame,
) -> list[QgsLineString]:
    """Transform 2D rings to 3D LineStrings using the section frame."""
    rings_3d: list[QgsLineString] = []
    for ring_2d in poly_2d:
        points_3d = [QgsPoint(*frame.to_map(point_2d.x(), point_2d.y())) for point_2d in ring_2d]
        rings_3d.append(QgsLineString(points_3d))
    return rings_3d


def project_to_3d_features(
    geom_2d: QgsGeometry,
    polygon: Any,
    fields: list,
    frame: SectionFrame,
    custom_keys: list[str],
) -> list[Any]:
    """Project a 2D geometry (potentially MultiPolygon) to 3D features."""
    from qgis.core import QgsFeature

    projected_features = []
    polygons_2d = geom_2d.asMultiPolygon() if geom_2d.isMultipart() else [geom_2d.asPolygon()]

    for poly_2d in polygons_2d:
        rings_3d = create_3d_rings(poly_2d, frame)
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
    frame: SectionFrame,
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
                frame,
                sorted_keys,
            )
        )
    return features
