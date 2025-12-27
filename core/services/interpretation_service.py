"""Service for projecting 2D section interpretations to 2.5D geometries."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Optional

from qgis.core import (
    QgsGeometry,
    QgsLineString,
    QgsPoint,
    QgsPointXY,
    QgsPolygon,
)

from sec_interp.core.exceptions import ValidationError
from sec_interp.core.types import InterpretationPolygon, InterpretationPolygon25D
from sec_interp.logger_config import get_logger


if TYPE_CHECKING:
    from qgis.core import QgsCoordinateReferenceSystem

logger = get_logger(__name__)


class InterpretationService:
    """Handles spatial projection of section interpretations to real-world coordinates."""

    def project_2d_to_25d(
        self,
        interpretation: InterpretationPolygon,
        section_line: QgsGeometry,
        crs: QgsCoordinateReferenceSystem,
        vertical_exag: float = 1.0,
    ) -> InterpretationPolygon25D:
        """Project a 2D profile interpretation to a georeferenced 2.5D geometry.

        Args:
            interpretation: The 2D interpretation data (dist, elev).
            section_line: The original 3D section line geometry in the map.
            crs: The CRS of the section line.
            vertical_exag: Vertical exaggeration factor used in the profile.

        Returns:
            An InterpretationPolygon25D object containing the projected geometry.

        Raises:
            ValidationError: If geometries are invalid or cannot be projected.
        """
        if not section_line or section_line.isNull():
            raise ValidationError("Invalid section line geometry.")

        if not interpretation.vertices_2d:
            raise ValidationError("Interpretation has no vertices.")

        line_length = section_line.length()
        points_25d = []

        # vertexAt(0) and the vertices iterator works for both LineString and MultiLineString
        # Use iterator to avoid version-specific vertexCount/nVertices issues
        vertices = list(section_line.vertices())
        if not vertices:
            raise ValidationError("Section line has no vertices.")
        p1 = vertices[0]
        p2 = vertices[-1]

        angle = math.atan2(p2.y() - p1.y(), p2.x() - p1.x())
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        for i, (dist, elev) in enumerate(interpretation.vertices_2d):
            # Clamp distance to line length
            clamped_dist = max(0.0, min(dist, line_length))

            # 1. Project Distance to X, Y linearly
            # Add a micro-offset (1cm) to half the points to give the polygon area
            # This makes it 'valid' for GEOS/QGIS without being visible to the user
            thickness = 0.01  # 1 cm
            offset_x = (sin_a * thickness) if i % 2 == 0 else 0
            offset_y = (-cos_a * thickness) if i % 2 == 0 else 0

            xtrsd = p1.x() + (cos_a * clamped_dist) + offset_x
            ytrsd = p1.y() + (sin_a * clamped_dist) + offset_y

            # 2. Map Elevation (removing exaggeration)
            true_elev = elev / vertical_exag if vertical_exag != 0 else elev

            # 3. Create 3D Point (X, Y, Z, M)
            p_25d = QgsPoint(xtrsd, ytrsd, true_elev, true_elev)
            points_25d.append(p_25d)

        if not points_25d:
            raise ValidationError("Failed to project any vertices.")

        # Create the final geometry
        if len(points_25d) < 3:
            raise ValidationError(f"Not enough points to create polygon: {len(points_25d)}")

        # Check if polygon is closed (compare only X, Y coordinates)
        first_pt = points_25d[0]
        last_pt = points_25d[-1]
        if not (first_pt.x() == last_pt.x() and first_pt.y() == last_pt.y()):
            points_25d.append(QgsPoint(first_pt.x(), first_pt.y(), first_pt.z(), first_pt.m()))

        ring = QgsLineString(points_25d)
        polygon = QgsPolygon()
        polygon.setExteriorRing(ring)

        geometry = QgsGeometry(polygon)

        if not geometry.isGeosValid():
            error_msg = geometry.lastError() if hasattr(geometry, "lastError") else "Unknown error"
            logger.warning(
                f"Projected geometry for '{interpretation.name}' is invalid. "
                f"Points: {len(points_25d)}, Error: {error_msg}"
            )
            logger.debug(f"2D Vertices: {interpretation.vertices_2d}")

            # Do NOT use buffer(0) as it strips Z coordinates.
            # The micro-offset added above should handle most area/validity issues.
            # We rely on makeValid() only if necessary.
            geometry = geometry.makeValid()

        return InterpretationPolygon25D(
            id=interpretation.id,
            name=interpretation.name,
            type=interpretation.type,
            geometry=geometry,
            attributes=interpretation.attributes.copy(),
            crs=crs,
        )

    def interpolate_point_on_line(
        self, distance: float, section_line: QgsGeometry
    ) -> Optional[QgsPointXY]:
        """Utility to get X,Y coordinates for a profile distance.

        Args:
            distance: Horizontal distance from start.
            section_line: Section line geometry.

        Returns:
            QgsPointXY or None.
        """
        if not section_line or section_line.isNull():
            return None

        line_length = section_line.length()
        clamped_dist = max(0.0, min(distance, line_length))

        geom_pt = section_line.interpolate(clamped_dist)
        return geom_pt.asPoint() if not geom_pt.isNull() else None
