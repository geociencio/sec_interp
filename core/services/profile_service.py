"""/***************************************************************************
 SecInterp - ProfileService
                                 A QGIS plugin
 Service for generating topographic profiles.
                              -------------------
        begin                : 2025-12-07
        copyright            : (C) 2025 by Juan M Bernales
        email                : juanbernales@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.core import QgsRasterLayer, QgsVectorLayer

from sec_interp.core import utils as scu
from sec_interp.core.types import ProfileData
from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


class ProfileService:
    """Service for generating topographic profiles.

    This service handles the extraction of elevation data along a cross-section
    line by sampling a raster DEM.
    """

    def generate_topographic_profile(
        self,
        line_lyr: QgsVectorLayer,
        raster_lyr: QgsRasterLayer,
        band_number: int = 1,
    ) -> ProfileData:
        """Generate topographic profile data by sampling elevation along the section line.

        This function returns the profile data as a list of tuples.

        Args:
            line_lyr: The cross-section line layer.
            raster_lyr: The DEM/raster layer for elevation.
            band_number: Raster band to sample (default: 1).

        Returns:
            List of (distance, elevation) tuples.

        Raises:
            ValueError: If line layer has no features or invalid geometry.
        """
        line_feat = next(line_lyr.getFeatures(), None)
        if not line_feat:
            raise ValueError("Line layer has no features")

        geom = line_feat.geometry()
        if not geom or geom.isNull():
            raise ValueError("Line geometry is not valid")

        da = scu.create_distance_area(line_lyr.crs())

        # Sample points using helper
        # For topographic profile, we measure from the start of the line
        points = scu.sample_elevation_along_line(geom, raster_lyr, band_number, da)

        # Convert QgsPointXY to tuples
        values = [(round(p.x(), 1), round(p.y(), 1)) for p in points]

        return values
