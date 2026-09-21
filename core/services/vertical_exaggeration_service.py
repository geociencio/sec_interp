"""Adaptive Vertical Exaggeration Service.

This module calculates the optimal vertical exaggeration (VE) for a
cross-section from its geometric properties (elevation vs. distance range)
and structural measurement density. It is QGIS-agnostic and thread-safe.

Algorithm reference: ``docs/plans/implementation_plan_adaptive_ve_v3.8.0.md``.
"""

# /***************************************************************************
#  SecInterp - VerticalExaggerationService
#                                  A QGIS plugin
#  Service for adaptive vertical exaggeration calculation.
#                               -------------------
#         begin                : 2026-09-21
#         copyright            : (C) 2026 by Juan M Bernales
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

from sec_interp.core.domain import ProfileData, StructureData
from sec_interp.core.domain.dtos import PreviewResult
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class VerticalExaggerationService:
    """Calculate adaptive vertical exaggeration for section profiles.

    The service derives an optimal VE from the profile aspect ratio
    (``elevation_range / distance_range``) modulated by the structural
    measurement density, clamped to ``[MIN_VERT_EXAG, MAX_VERT_EXAG]``.

    All inputs are primitive domain types; the service holds no state and
    is safe to use from background threads.
    """

    DEFAULT_VERT_EXAG = 1.0
    MIN_VERT_EXAG = 0.5
    MAX_VERT_EXAG = 20.0

    # Aspect-ratio (elevation_range / distance_range) thresholds and base VE
    ASPECT_EXPRESSIVE = 0.5
    ASPECT_MODERATE = 0.1
    ASPECT_FLAT = 0.02
    BASE_EXPRESSIVE = 1.0
    BASE_MODERATE = 2.0
    BASE_LOW = 5.0
    BASE_FLAT = 10.0

    # Structural density (measurements per map unit) thresholds and multipliers
    DENSITY_DENSE = 0.1
    DENSITY_SPARSE = 0.01
    MULT_DENSE = 0.7
    MULT_NEUTRAL = 1.0
    MULT_SPARSE = 1.3

    def calculate(
        self,
        topo: ProfileData | None,
        struct: StructureData | None,
    ) -> float:
        """Calculate the adaptive VE from topography and structural data.

        Args:
            topo: Sampled topographic profile as ``(distance, elevation)``
                tuples. Empty or ``None`` returns ``DEFAULT_VERT_EXAG``.
            struct: Projected structural measurements. ``None`` or empty
                applies a neutral density multiplier (1.0).

        Returns:
            Adaptive vertical exaggeration rounded to 1 decimal, within
            ``[MIN_VERT_EXAG, MAX_VERT_EXAG]``.

        """
        if not topo:
            logger.debug("Adaptive VE: empty topo, using default %.1f", self.DEFAULT_VERT_EXAG)
            return self.DEFAULT_VERT_EXAG

        dist_range = self._distance_range(topo)
        if dist_range <= 0:
            logger.debug("Adaptive VE: zero distance range, using default")
            return self.DEFAULT_VERT_EXAG

        elev_range = self._elevation_range(topo, struct)
        base = self._aspect_base(elev_range / dist_range)
        mult = self._density_multiplier(self._structural_density(struct, dist_range))

        ve = round(self._clamp(base * mult), 1)
        logger.debug(
            "Adaptive VE: elev_range=%.1f dist_range=%.1f base=%.1f mult=%.1f -> %.1f",
            elev_range,
            dist_range,
            base,
            mult,
            ve,
        )
        return ve

    def calculate_from_result(self, result: PreviewResult) -> float:
        """Calculate the adaptive VE from a consolidated preview result.

        Only synchronous layers (topography and structures) are considered;
        asynchronous layers (geology, drillholes) are intentionally excluded
        to keep the VE stable across async re-renders (plan v3.8.0, §5.1).

        Args:
            result: Consolidated preview result.

        Returns:
            Adaptive vertical exaggeration (see :meth:`calculate`).

        """
        return self.calculate(result.topo, result.struct)

    def _distance_range(self, topo: ProfileData) -> float:
        """Return the horizontal distance covered by the profile.

        Uses the first and last sampled points as the authoritative bounds,
        consistent with ``PreviewResult.get_distance_range()``.
        """
        return topo[-1][0] - topo[0][0]

    def _elevation_range(
        self,
        topo: ProfileData,
        struct: StructureData | None,
    ) -> float:
        """Return the vertical range across topography and structures."""
        elevations = [p[1] for p in topo]
        if struct:
            elevations.extend(m.elevation for m in struct)
        return max(elevations) - min(elevations)

    def _structural_density(
        self,
        struct: StructureData | None,
        dist_range: float,
    ) -> float | None:
        """Return structural measurements per map unit, or None if absent."""
        if not struct:
            return None
        return len(struct) / dist_range

    def _aspect_base(self, aspect_ratio: float) -> float:
        """Map the elevation/distance aspect ratio to a base VE.

        A nearly flat profile (ratio <= 0.02) needs strong exaggeration to
        make structures visible; an already expressive profile (ratio > 0.5)
        needs none.
        """
        if aspect_ratio > self.ASPECT_EXPRESSIVE:
            return self.BASE_EXPRESSIVE
        if aspect_ratio > self.ASPECT_MODERATE:
            return self.BASE_MODERATE
        if aspect_ratio > self.ASPECT_FLAT:
            return self.BASE_LOW
        return self.BASE_FLAT

    def _density_multiplier(self, density: float | None) -> float:
        """Map structural density to a VE multiplier.

        Dense structural sections are damped (x0.7) to avoid clutter;
        sparse sections are boosted (x1.3).
        """
        if density is None:
            return self.MULT_NEUTRAL
        if density > self.DENSITY_DENSE:
            return self.MULT_DENSE
        if density > self.DENSITY_SPARSE:
            return self.MULT_NEUTRAL
        return self.MULT_SPARSE

    def _clamp(self, value: float) -> float:
        """Clamp the VE to the supported adaptive range."""
        return max(self.MIN_VERT_EXAG, min(self.MAX_VERT_EXAG, value))
