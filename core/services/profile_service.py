# /***************************************************************************
#  SecInterp - ProfileService
#                                  A QGIS plugin
#  Service for generating topographic profiles.
#                               -------------------
#         begin                : 2025-12-07
#         copyright            : (C) 2025 by Juan M Bernales
#         email                : juanbernales@gmail.com
#  ***************************************************************************/
#
# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

from typing import Optional

from qgis.core import QgsPointXY, QgsRasterLayer, QgsVectorLayer

from sec_interp.core import utils as scu
from sec_interp.core.exceptions import DataMissingError, GeometryError
from sec_interp.core.interfaces.profile_interface import IProfileService
from sec_interp.core.types import ProfileData
from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


class ProfileService(IProfileService):
    """Service for generating topographic profiles.

    This service handles the extraction of elevation data along a cross-section
    line by sampling a raster DEM.
    """

    def generate_topographic_profile(
        self,
        line_lyr: QgsVectorLayer,
        raster_lyr: QgsRasterLayer,
        band_number: int = 1,
        interval: Optional[float] = None,
    ) -> ProfileData:
        """Generate topographic profile data by sampling elevation along the section line.

        Args:
            line_lyr: The cross-section line layer.
            raster_lyr: The DEM/raster layer for elevation.
            band_number: Raster band to sample (default: 1).
            interval: Optional sampling interval. If None, uses raster resolution.

        Returns:
            A list of (distance, elevation) tuples representing the profile.

        Raises:
            DataMissingError: If line layer has no features.
            GeometryError: If line geometry is invalid.
        """
        line_feat = next(line_lyr.getFeatures(), None)
        if not line_feat:
            raise DataMissingError("Line layer has no features", {"layer": line_lyr.name()})

        geom = line_feat.geometry()
        if not geom or geom.isNull():
            raise GeometryError("Line geometry is not valid", {"layer": line_lyr.name()})

        da = scu.create_distance_area(line_lyr.crs())

        # Sample points using helper
        # For topographic profile, we measure from the start of the line
        points = scu.sample_elevation_along_line(
            geom, raster_lyr, band_number, da, interval=interval
        )

        # Convert QgsPointXY to tuples
        values = [(round(p.x(), 1), round(p.y(), 1)) for p in points]

        return values
