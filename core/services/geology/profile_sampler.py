from __future__ import annotations

"""Sampling logic for Master Profile elevations."""

from qgis.core import QgsDistanceArea, QgsGeometry, QgsPointXY, QgsRasterLayer
from sec_interp.core import utils as scu
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class ProfileSampler:
    """Handles densification and elevation sampling for the profile line."""

    def generate_master_profile(
        self,
        line_geom: QgsGeometry,
        raster_lyr: QgsRasterLayer,
        band_number: int,
        da: QgsDistanceArea,
        line_start: QgsPointXY,
    ) -> tuple[list[tuple[float, float]], list[tuple[float, QgsPointXY, float]]]:
        """Generate master profile data (grid points and elevations).

        Densifies the section line and samples elevations from the DEM.

        Args:
            line_geom: Section line geometry.
            raster_lyr: Elevation raster layer.
            band_number: Raster band to sample.
            da: Distance calculator.
            line_start: Section start point.

        Returns:
            Tuple containing:
            - List of (distance, elevation) tuples.
            - List of (distance, point, elevation) tuples.

        """
        grid_points = self._get_densified_grid_points(line_geom, raster_lyr)
        return self._sample_elevation_at_points(
            grid_points, raster_lyr, band_number, da, line_start
        )

    def _get_densified_grid_points(
        self, line_geom: QgsGeometry, raster_lyr: QgsRasterLayer
    ) -> list[QgsPointXY]:
        """Densify line and extract vertices based on raster resolution."""
        try:
            interval = raster_lyr.rasterUnitsPerPixelX()
            master_densified = scu.densify_line_by_interval(line_geom, interval)
            return scu.get_line_vertices(master_densified)
        except (AttributeError, ValueError, TypeError) as e:
            logger.warning(f"Failed to densify line, using original vertices: {e}")
            return scu.get_line_vertices(line_geom)

    def _sample_elevation_at_points(
        self,
        points: list[QgsPointXY],
        raster_lyr: QgsRasterLayer,
        band_number: int,
        da: QgsDistanceArea,
        line_start: QgsPointXY,
    ) -> tuple[list[tuple[float, float]], list[tuple[float, QgsPointXY, float]]]:
        """Sample elevation from raster at provided points and calculate distances."""
        master_profile_data = []
        master_grid_dists = []
        current_dist = 0.0

        for i, pt in enumerate(points):
            if i > 0:
                current_dist += da.measureLine(points[i - 1], pt)

            val, ok = raster_lyr.dataProvider().sample(pt, band_number)
            elev = val if ok else 0.0

            master_profile_data.append((current_dist, elev))
            master_grid_dists.append((current_dist, pt, elev))

        return master_profile_data, master_grid_dists
