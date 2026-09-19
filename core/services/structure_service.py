"""Structure Data Processing Service.

This module handles the calculation of apparent dips and projection
of structural measurements (planes, lines) onto the section plane.
"""

# /***************************************************************************
#  SecInterp - StructureService
#                                  A QGIS plugin
#  Service for projecting structural measurements.
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
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from sec_interp.core import utils as scu
from sec_interp.core.domain import StructureData, StructureMeasurement
from sec_interp.core.interfaces.structure_interface import IStructureService
from sec_interp.core.utils.geometry_utils.measurement import project_point_onto_polyline
from sec_interp.core.utils.i18n import TranslatableMixin
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class StructureService(IStructureService, TranslatableMixin):
    """Service for projecting structural measurements onto cross-sections.

    This service receives pre-extracted structural data (from the GUI's
    ``StructureExtractor``) and performs the pure-math projection and apparent
    dip calculations. It is QGIS-agnostic.
    """

    def project_structures(
        self,
        line_points: list[tuple[float, float]],
        struct_data: list[dict[str, Any]],
        elevation_sampler: Callable[[float, float], float],
        line_az: float,
        dip_field: str,
        strike_field: str,
    ) -> StructureData:
        """Project detached structural measurements onto the section plane.

        Calculates stations (distance along section), elevations from the
        injected sampler, and apparent dips based on the section orientation.

        Args:
            line_points: Section line vertices as ``(x, y)`` tuples.
            struct_data: List of detached structures
                (``{"point": (x, y), "attributes": {...}}``).
            elevation_sampler: Callable returning elevation at ``(x, y)``.
            line_az: Section azimuth in degrees.
            dip_field: Field name for dip angle.
            strike_field: Field name for strike azimuth.

        Returns:
            StructureData: Sorted list of projected StructureMeasurement objects.

        """
        projected_structs = []

        for item in struct_data:
            measurement = self._process_single_structure(
                item,
                line_points,
                elevation_sampler,
                line_az,
                dip_field,
                strike_field,
            )
            if measurement:
                projected_structs.append(measurement)

        # Sort by distance
        projected_structs.sort(key=lambda x: x.distance)

        logger.info(self.tr("Processed {0} structural measurements").format(len(projected_structs)))
        return projected_structs

    def _process_single_structure(
        self,
        data: dict[str, Any],
        line_points: list[tuple[float, float]],
        elevation_sampler: Callable[[float, float], float],
        line_az: float,
        dip_field: str,
        strike_field: str,
    ) -> StructureMeasurement | None:
        """Process a single structure from detached data.

        Projects the measurement point onto the section line and calculates
        geological properties.

        Args:
            data: Detached structure data (``{"point", "attributes"}``).
            line_points: Section line vertices as ``(x, y)`` tuples.
            elevation_sampler: Callable sampling elevation at ``(x, y)``.
            line_az: Section azimuth.
            dip_field: Dip field.
            strike_field: Strike field.

        Returns:
            StructureMeasurement or None if projection fails.

        """
        point = data.get("point")
        if point is None:
            return None

        # Project point onto line to get true station distance
        proj_dist, proj_pt = project_point_onto_polyline(point, line_points)

        elev = elevation_sampler(proj_pt[0], proj_pt[1])

        parsed_data = self._parse_structural_data(
            data.get("attributes", {}), strike_field, dip_field, line_az
        )
        if not parsed_data:
            return None

        strike, dip_angle, app_dip = parsed_data

        # Create object
        return StructureMeasurement(
            distance=round(proj_dist, 1),
            elevation=round(elev, 1),
            apparent_dip=round(app_dip, 1),
            original_dip=dip_angle,
            original_strike=strike,
            attributes=data.get("attributes", {}),
        )

    def _parse_structural_data(
        self,
        attributes: dict[str, Any],
        strike_field: str,
        dip_field: str,
        line_az: float,
    ) -> tuple[float, float, float] | None:
        """Parse strike and dip attributes and calculate apparent dip.

        Args:
            attributes: Feature attributes dictionary.
            strike_field: Name of the strike field.
            dip_field: Name of the dip field.
            line_az: Azimuth of the section line.

        Returns:
            Tuple (strike, dip, apparent_dip) or None if parsing fails.

        """
        try:
            strike_raw = attributes.get(strike_field)
            dip_raw = attributes.get(dip_field)
        except (AttributeError, KeyError):
            return None

        strike = scu.parse_strike(strike_raw)
        dip_angle, _ = scu.parse_dip(dip_raw)

        if strike is None or dip_angle is None:
            return None

        MAX_STRIKE = 360
        MAX_DIP_ANGLE = 90

        # Validate ranges
        if not (0 <= strike <= MAX_STRIKE) or not (0 <= dip_angle <= MAX_DIP_ANGLE):
            return None

        app_dip = scu.calculate_apparent_dip(strike, dip_angle, line_az)
        return strike, dip_angle, app_dip
