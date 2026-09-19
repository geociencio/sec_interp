"""Geology Data Processing Service.

This module handles the pure computation of geological unit segments along a
cross-section, using detached data extracted by the GUI ``GeologyExtractor``
adapter. It is QGIS-agnostic.
"""

# /***************************************************************************
#  SecInterp - GeologyService
#                                  A QGIS plugin
#  Service for generating geological profiles.
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

from typing import Any

from sec_interp.core.domain import GeologyData, GeologySegment
from sec_interp.core.domain.task_inputs import GeologyContext
from sec_interp.core.interfaces.geology_interface import IGeologyService
from sec_interp.core.performance_metrics import performance_monitor
from sec_interp.core.utils.geometry_utils.processing import interpolate_segment_points
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class GeologyService(IGeologyService):
    """Service for generating geological profiles (pure computation)."""

    @performance_monitor
    def build_segments(self, context: GeologyContext, feedback: Any | None = None) -> GeologyData:
        """Build geological segments from a detached context.

        Interpolates segment elevations along the master profile and builds
        :class:`GeologySegment` objects, sorted by distance along the section.

        Args:
            context: Fully-detached geology data from ``GeologyExtractor``.
            feedback: Optional feedback object for progress/cancellation.

        Returns:
            GeologyData: Sorted list of geological segments.

        """
        segments: list[GeologySegment] = []
        total = len(context.outcrops)

        for i, outcrop in enumerate(context.outcrops):
            if feedback and feedback.isCanceled():
                return []

            for dist_start, dist_end, wkt in outcrop.segments:
                segment_points = interpolate_segment_points(
                    dist_start,
                    dist_end,
                    context.master_grid_dists,
                    context.master_profile_data,
                    context.tolerance,
                )
                segments.append(
                    GeologySegment(
                        unit_name=outcrop.unit_name,
                        geometry_wkt=wkt,
                        attributes=outcrop.attributes,
                        points=[(float(d), float(e)) for d, e in segment_points],
                    )
                )

            if feedback:
                feedback.setProgress((i / total) * 100)

        segments.sort(key=lambda x: x.points[0][0] if x.points else 0)
        return segments
