"""Profile extraction adapter (Extract phase).

Bridges the QGIS object world and the QGIS-agnostic core layer for topographic
profiles. It reads the section line and samples elevations from a DEM raster,
returning a plain ``ProfileData`` list of ``(distance, elevation)`` tuples.
"""

from __future__ import annotations

from qgis.core import QgsRasterLayer, QgsVectorLayer
from qgis.PyQt.QtCore import QCoreApplication

from sec_interp.core.domain import ProfileData
from sec_interp.core.exceptions import DataMissingError, GeometryError
from sec_interp.gui.adapters import geometry


class ProfileExtractor:
    """Extract topographic profile data from QGIS layers into primitives."""

    def tr(self, message: str) -> str:
        """Translate a message using QCoreApplication."""
        return QCoreApplication.translate("ProfileExtractor", message)  # type: ignore[no-any-return]

    def calculate_lod_interval(self, line_lyr: QgsVectorLayer, canvas_width: int) -> float | None:
        """Compute the LOD sampling interval from the section line length.

        Args:
            line_lyr: The cross-section line layer.
            canvas_width: Current width of the preview canvas in pixels.

        Returns:
            The sampling interval, or None if the line length is unavailable.

        """
        line_feat = next(line_lyr.getFeatures(), None)
        if not line_feat:
            return None
        line_geom = line_feat.geometry()
        if not line_geom or line_geom.isNull():
            return None

        line_len = line_geom.length()
        max_pts = max(200, int(canvas_width * 2))
        return line_len / max_pts if max_pts > 0 else None

    def extract_profile(
        self,
        line_lyr: QgsVectorLayer,
        raster_lyr: QgsRasterLayer,
        band_number: int = 1,
        interval: float | None = None,
    ) -> ProfileData:
        """Sample elevation along a section line into a detached profile.

        Args:
            line_lyr: The cross-section line layer.
            raster_lyr: The DEM/raster layer for elevation.
            band_number: Raster band to sample (default: 1).
            interval: Optional sampling interval. If None, uses raster resolution.

        Returns:
            A list of ``(distance, elevation)`` tuples representing the profile.

        Raises:
            DataMissingError: If the line layer has no features.
            GeometryError: If the line geometry is invalid.

        """
        line_feat = next(line_lyr.getFeatures(), None)
        if not line_feat:
            raise DataMissingError(
                self.tr("Line layer has no features"), {"layer": line_lyr.name()}
            )

        geom = line_feat.geometry()
        if not geom or geom.isNull():
            raise GeometryError(self.tr("Line geometry is not valid"), {"layer": line_lyr.name()})

        da = geometry.create_distance_area(line_lyr.crs())

        points = geometry.sample_elevation_along_line(
            geom, raster_lyr, band_number, da, interval=interval
        )

        return [(round(p.x(), 1), round(p.y(), 1)) for p in points]
