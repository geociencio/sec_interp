"""Processing logic for Outcrop intersections."""

from __future__ import annotations

from typing import Any

from qgis.core import (
    QgsDistanceArea,
    QgsFeatureRequest,
    QgsGeometry,
    QgsPointXY,
    QgsVectorLayer,
)
from sec_interp.core.domain import GeologySegment
from sec_interp.core.utils.geometry_utils.extraction import extract_lines_from_geometry
from sec_interp.core.utils.geometry_utils.processing import (
    calculate_segment_range,
    interpolate_segment_points,
)


class OutcropProcessor:
    """Handles extraction and intersection of outcrop features."""

    def extract_outcrop_data(
        self,
        line_geom: QgsGeometry,
        outcrop_lyr: QgsVectorLayer,
        outcrop_name_field: str,
    ) -> list[dict[str, Any]]:
        """Extract outcrop features intersecting the line bounding box (detached)."""
        outcrop_data = []
        line_bbox = line_geom.boundingBox()
        request = QgsFeatureRequest().setFilterRect(line_bbox)

        for feature in outcrop_lyr.getFeatures(request):
            if not feature.hasGeometry():
                continue

            attrs = dict(
                zip(feature.fields().names(), feature.attributes(), strict=False)
            )
            try:
                unit_name = str(feature[outcrop_name_field])
            except KeyError:
                unit_name = "Unknown"

            outcrop_data.append(
                {
                    "wkt": feature.geometry().asWkt(),
                    "attrs": attrs,
                    "unit_name": unit_name,
                }
            )
        return outcrop_data

    def process_detached_intersection(
        self,
        geom: QgsGeometry,
        attrs: dict[str, Any],
        unit_name: str,
        line_start: QgsPointXY,
        da: QgsDistanceArea,
        master_grid_dists: list[tuple[float, QgsPointXY, float]],
        master_profile_data: list[tuple[float, float]],
        tolerance: float,
    ) -> list[GeologySegment]:
        """Process a detached intersection geometry to extract geology segments."""
        if not geom or geom.isNull():
            return []

        geometries = extract_lines_from_geometry(geom)
        if not geometries:
            return []

        segments = []
        for seg_geom in geometries:
            segment = self.create_segment_from_geometry(
                seg_geom,
                attrs,
                unit_name,
                line_start,
                da,
                master_grid_dists,
                master_profile_data,
                tolerance,
            )
            if segment:
                segments.append(segment)

        return segments

    def create_segment_from_geometry(
        self,
        seg_geom: QgsGeometry,
        attributes: dict[str, Any],
        unit_name: str,
        line_start: QgsPointXY,
        da: QgsDistanceArea,
        master_grid_dists: list[tuple[float, QgsPointXY, float]],
        master_profile_data: list[tuple[float, float]],
        tolerance: float,
    ) -> GeologySegment | None:
        """Create a GeologySegment from a geometry part by sampling elevations."""
        rng = calculate_segment_range(seg_geom, line_start, da)
        if not rng:
            return None

        dist_start, dist_end = rng
        segment_points = interpolate_segment_points(
            dist_start, dist_end, master_grid_dists, master_profile_data, tolerance
        )

        return GeologySegment(
            unit_name=unit_name,
            geometry_wkt=(
                seg_geom.asWkt() if seg_geom and not seg_geom.isNull() else None
            ),
            attributes=attributes,
            points=[(float(d), float(e)) for d, e in segment_points],
        )
