"""Service for projecting 2D section interpretations to 2.5D geometries."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from qgis.core import (
    QgsGeometry,
    QgsLineString,
    QgsPoint,
    QgsPolygon,
    QgsPointXY,
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

        for dist, elev in interpretation.vertices_2d:
            # Clamp distance to line length to avoid interpolation errors
            clamped_dist = max(0.0, min(dist, line_length))
            
            # 1. Project Distance to X, Y
            # QgsGeometry.interpolate returns a point geometry at distance
            geom_pt = section_line.interpolate(clamped_dist)
            if geom_pt.isNull():
                logger.warning(f"Could not interpolate point at distance {clamped_dist}")
                continue
            
            p_xy = geom_pt.asPoint()
            
            # 2. Map Elevation to M (removing exaggeration if applied)
            m_coord = elev / vertical_exag if vertical_exag != 0 else elev
            
            # 3. Create 2.5D Point (X, Y, M)
            # QgsPoint supports X, Y, Z, M. We use M for elevation as per plan.
            p_25d = QgsPoint(p_xy.x(), p_xy.y(), 0.0, m_coord)
            points_25d.append(p_25d)

        if not points_25d:
            raise ValidationError("Failed to project any vertices.")

        # Create the final geometry
        # Currently we assume interpretation is a Polygon
        # We ensure it's closed for a polygon (only check X, Y)
        if len(points_25d) < 3:
            raise ValidationError(f"Not enough points to create polygon: {len(points_25d)}")
            
        # Check if polygon is closed (compare only X, Y coordinates)
        first_pt = points_25d[0]
        last_pt = points_25d[-1]
        if not (first_pt.x() == last_pt.x() and first_pt.y() == last_pt.y()):
            # Close the polygon by duplicating the first point with all coordinates
            points_25d.append(QgsPoint(first_pt.x(), first_pt.y(), first_pt.z(), first_pt.m()))

        ring = QgsLineString(points_25d)
        polygon = QgsPolygon()
        polygon.setExteriorRing(ring)
        
        geometry = QgsGeometry(polygon)
        
        if not geometry.isGeosValid():
            error_msg = geometry.lastError() if hasattr(geometry, 'lastError') else "Unknown error"
            logger.warning(
                f"Projected geometry for '{interpretation.name}' is invalid. "
                f"Points: {len(points_25d)}, Error: {error_msg}"
            )
            # Try to get more details
            logger.debug(f"First point: {points_25d[0].asWkt()}, Last point: {points_25d[-1].asWkt()}")

        return InterpretationPolygon25D(
            id=interpretation.id,
            name=interpretation.name,
            type=interpretation.type,
            geometry=geometry,
            attributes=interpretation.attributes.copy(),
            crs=crs,
        )

    def interpolate_point_on_line(
        self, 
        distance: float, 
        section_line: QgsGeometry
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
