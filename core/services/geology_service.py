"""Geology Data Processing Service.

This module handles the extraction and projection of geological boundaries
and unit segments from map layers to the cross-section plane.
"""

from __future__ import annotations

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
from typing import Any

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsDistanceArea,
    QgsGeometry,
    QgsPointXY,
    QgsRasterLayer,
    QgsVectorLayer,
)

from sec_interp.core import utils as scu
from sec_interp.core.domain import GeologyData, GeologySegment, GeologyTaskInput
from sec_interp.core.exceptions import DataMissingError, GeometryError
from sec_interp.core.interfaces.geology_interface import IGeologyService
from sec_interp.core.performance_metrics import performance_monitor
from sec_interp.core.services.geology.outcrop_processor import OutcropProcessor
from sec_interp.core.services.geology.profile_sampler import ProfileSampler
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class GeologyService(IGeologyService):
    """Service for generating geological profiles."""

    def __init__(self) -> None:
        """Initialize service with specialized processors.

        The service delegates the heavy lifting of elevation sampling and
        outcrop extraction to specialized sub-components.
        """
        self.profile_sampler = ProfileSampler()
        self.outcrop_processor = OutcropProcessor()

    @performance_monitor
    def generate_geological_profile(
        self,
        line_lyr: QgsVectorLayer,
        raster_lyr: QgsRasterLayer,
        outcrop_lyr: QgsVectorLayer,
        outcrop_name_field: str,
        band_number: int = 1,
    ) -> GeologyData:
        """Generate geological profile data by intersecting the section line with outcrop polygons.

        Extracts geological unit intersections along the cross-section line,
        calculates elevations from the DEM, and returns a list of segments.

        Args:
            line_lyr: The QGIS vector layer representing the cross-section line.
            raster_lyr: The Digital Elevation Model (DEM) raster layer.
            outcrop_lyr: The QGIS vector layer containing geological outcrop polygons.
            outcrop_name_field: The attribute field name for geological unit names.
            band_number: The raster band to use for elevation sampling (default 1).

        Returns:
            GeologyData: A list of `GeologySegment` objects, sorted by distance along the section.

        Raises:
            DataMissingError: If the line layer has no features.
            GeometryError: If the line geometry is invalid.
            ProcessingError: If the intersection processing fails.

        """
        task_input = self.prepare_task_input(
            line_lyr, raster_lyr, outcrop_lyr, outcrop_name_field, band_number
        )
        return self.process_task_data(task_input)

    def prepare_task_input(
        self,
        line_lyr: QgsVectorLayer,
        raster_lyr: QgsRasterLayer,
        outcrop_lyr: QgsVectorLayer,
        outcrop_name_field: str,
        band_number: int = 1,
    ) -> GeologyTaskInput:
        """Prepare detached domain data for background task execution.

        Extracts all necessary geometric and attribute data from QGIS layers
        to create a serializable input for asynchronous processing.

        Args:
            line_lyr: The cross-section line vector layer.
            raster_lyr: The elevation raster layer.
            outcrop_lyr: The geological outcrop vector layer.
            outcrop_name_field: Field name for geological units.
            band_number: Raster band for elevation sampling.

        Returns:
            GeologyTaskInput: Detached data ready for processing.

        """
        self._validate_inputs(line_lyr, raster_lyr, outcrop_lyr, outcrop_name_field, band_number)

        line_geom, line_start = self._extract_line_info(line_lyr)
        crs = line_lyr.crs()
        da = scu.create_distance_area(crs)

        # 1. Generate Master Profile Data (needs Raster access)
        master_profile_data, master_grid_dists_raw = self.profile_sampler.generate_master_profile(
            line_geom, raster_lyr, band_number, da, line_start
        )

        # Convert master_grid_dists to domain types (dist, (x, y), elev)
        master_grid_dists = [(d, (pt.x(), pt.y()), e) for d, pt, e in master_grid_dists_raw]

        # 2. Extract Outcrop Data (needs Vector access)
        outcrop_data = []
        if outcrop_lyr:
            outcrop_data = self.outcrop_processor.extract_outcrop_data(
                line_geom, outcrop_lyr, outcrop_name_field
            )

        return GeologyTaskInput(
            line_geometry_wkt=line_geom.asWkt(),
            line_start_x=line_start.x(),
            line_start_y=line_start.y(),
            crs_authid=crs.authid(),
            master_profile_data=master_profile_data,
            master_grid_dists=master_grid_dists,
            outcrop_data=outcrop_data,
            outcrop_name_field=outcrop_name_field,
        )

    def _validate_inputs(
        self,
        line_lyr: QgsVectorLayer,
        raster_lyr: QgsRasterLayer,
        outcrop_lyr: QgsVectorLayer,
        outcrop_name_field: str,
        band_number: int,
    ) -> None:
        """Validate input layers and parameters for correctness.

        Checks layer validity, raster band range, and field existence.

        Args:
            line_lyr: Section line layer.
            raster_lyr: Raster layer.
            outcrop_lyr: Outcrop layer.
            outcrop_name_field: Unit field name.
            band_number: Targeted raster band.

        Raises:
            DataMissingError: If a layer is invalid.
            ValidationError: If parameters are out of range or missing.

        """
        from sec_interp.core.exceptions import ValidationError

        # 1. Layer Validity
        for lyr, name in [
            (line_lyr, "Line layer"),
            (raster_lyr, "Raster layer"),
        ]:
            if not lyr or not lyr.isValid():
                raise DataMissingError(
                    f"Invalid layer: {name}. Please check input layers.",
                    {"layer": name},
                )

        if outcrop_lyr and not outcrop_lyr.isValid():
            raise DataMissingError(
                "Invalid layer: Outcrop layer. Please check input layers.",
                {"layer": "Outcrop layer"},
            )

        # 2. Band Validation
        if band_number < 1:
            raise ValidationError("Band number must be positive.")

        if band_number > raster_lyr.bandCount():
            raise ValidationError(
                f"Band number {band_number} exceeds raster band count ({raster_lyr.bandCount()})."
            )

        # 3. Field Validation
        if outcrop_lyr:
            idx = outcrop_lyr.fields().indexFromName(outcrop_name_field)
            if idx == -1:
                raise ValidationError(f"Field '{outcrop_name_field}' not found in outcrop layer.")

    def process_task_data(
        self, task_input: GeologyTaskInput, feedback: Any | None = None
    ) -> GeologyData:
        """Process geological data in a thread-safe way (Domain-Pure logic).

        Intersects the section line with detached outcrop geometries and
        assigns elevations sampled from the master profile.

        Args:
            task_input: Detached data for processing.
            feedback: Optional QgsFeedback for progress tracking.

        Returns:
            GeologyData: Sorted list of geological segments.

        """
        # Reconstruct necessary tools from IDs/Strings
        crs = QgsCoordinateReferenceSystem(task_input.crs_authid)
        da = scu.create_distance_area(crs)
        line_geom = QgsGeometry.fromWkt(task_input.line_geometry_wkt)
        line_start = QgsPointXY(task_input.line_start_x, task_input.line_start_y)

        segments = []
        total = len(task_input.outcrop_data)

        for i, item in enumerate(task_input.outcrop_data):
            if feedback and feedback.isCanceled():
                return []

            new_segments = self._process_single_outcrop(item, line_geom, line_start, da, task_input)
            segments.extend(new_segments)

            if feedback:
                feedback.setProgress((i / total) * 100)

        # Sort by start distance
        segments.sort(key=lambda x: x.points[0][0] if x.points else 0)
        return segments

    def _process_detached_intersection(
        self,
        geom: QgsGeometry,
        attrs: dict[str, Any],
        unit_name: str,
        line_start: QgsPointXY,
        da: QgsDistanceArea,
        master_grid_dists: list[tuple[float, QgsPointXY, float]],
        master_profile_data: list[tuple[float, float]],
        tolerance: float,
    ) -> list[GeologySegment]:
        """Process a detached intersection geometry to extract geology segments."""
        return self.outcrop_processor.process_detached_intersection(
            geom,
            attrs,
            unit_name,
            line_start,
            da,
            master_grid_dists,
            master_profile_data,
            tolerance,
        )

    def _process_single_outcrop(
        self,
        item: dict[str, Any],
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        da: QgsDistanceArea,
        task_input: GeologyTaskInput,
    ) -> list[GeologySegment]:
        """Process a single outcrop feature intersection.

        Args:
            item: Detached outcrop dictionary (wkt, attrs, unit_name).
            line_geom: Master section geometry.
            line_start: Section start point.
            da: Distance calculator.
            task_input: Full task input for context.

        Returns:
            List of GeologySegment objects for this feature.

        """
        outcrop_geom = QgsGeometry.fromWkt(item["wkt"])
        intersection = line_geom.intersection(outcrop_geom)

        if intersection.isEmpty():
            return []

        return self._process_detached_intersection(
            intersection,
            item["attrs"],
            item["unit_name"],
            line_start,
            da,
            task_input.master_grid_dists,
            task_input.master_profile_data,
            task_input.tolerance,
        )

    def _create_segment_from_geometry(
        self,
        seg_geom: QgsGeometry,
        attributes: dict[str, Any],
        unit_name: str,
        line_start: QgsPointXY,
        da: QgsDistanceArea,
        master_grid_dists: list[tuple[float, QgsPointXY, float]],
        master_profile_data: list[tuple[float, float]],
        tolerance: float,
    ) -> GeologySegment | None:
        """Create a GeologySegment from a geometry part by sampling elevations."""
        return self.outcrop_processor.create_segment_from_geometry(
            seg_geom,
            attributes,
            unit_name,
            line_start,
            da,
            master_grid_dists,
            master_profile_data,
            tolerance,
        )

    def _extract_line_info(self, line_lyr: QgsVectorLayer) -> tuple[QgsGeometry, QgsPointXY]:
        """Extract geometry and start point from the line layer.

        Args:
            line_lyr: The vector layer containing the section line.

        Returns:
            A tuple containing (line_geometry, start_point).

        Raises:
            DataMissingError: If layer has no features.
            GeometryError: If geometry is invalid.

        """
        line_feat = next(line_lyr.getFeatures(), None)
        if not line_feat:
            raise DataMissingError("Line layer has no features", {"layer": line_lyr.name()})

        line_geom = line_feat.geometry()
        if not line_geom or line_geom.isNull():
            raise GeometryError("Line geometry is not valid", {"layer": line_lyr.name()})

        if line_geom.isMultipart():
            line_start = line_geom.asMultiPolyline()[0][0]
        else:
            line_start = line_geom.asPolyline()[0]

        return line_geom, line_start
