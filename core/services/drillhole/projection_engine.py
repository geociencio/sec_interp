from __future__ import annotations

"""Pure geometric projection logic for drillhole operations."""

from qgis.core import QgsDistanceArea, QgsGeometry, QgsPointXY


class ProjectionEngine:
    """Encapsulates geometric projection logic."""

    @staticmethod
    def project_point_to_line(
        pt: QgsPointXY,
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        da: QgsDistanceArea,
    ) -> tuple[float, float]:
        """Project point to line and return (dist_along, offset).

        Args:
            pt: The point to project.
            line_geom: The profile line geometry.
            line_start: The start point of the profile (dist=0).
            da: Distance area object for measurements.

        Returns:
            Tuple of (distance_along_line, offset_from_line).

        """
        collar_geom_pt = QgsGeometry.fromPointXY(pt)
        nearest_point_geom = line_geom.nearestPoint(collar_geom_pt)
        nearest_point = nearest_point_geom.asPoint()
        nearest_point_xy = QgsPointXY(nearest_point.x(), nearest_point.y())

        dist_along = da.measureLine(line_start, nearest_point_xy)
        offset = da.measureLine(pt, nearest_point_xy)
        return dist_along, offset
