"""Complex Data Transfer Objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sec_interp.core.exceptions import ValidationError
from sec_interp.core.performance_metrics import MetricsCollector

from .entities import (
    GeologyData,
    ProfileData,
    StructureData,
)


@dataclass
class PreviewParams:
    """Consolidated parameters for profile generation and preview.

    Attributes:
        raster_layer: QGIS layer ID for DEM sampling.
        line_layer: QGIS layer ID for the section orientation.
        band_num: Raster band number to use for elevation.
        buffer_dist: Search buffer for projecting data onto the section.
        outcrop_layer: Optional layer ID with geological outcrops.
        outcrop_name_field: Field name for geological unit names.
        struct_layer: Optional layer ID with structural measurements.
        dip_field: Field name for dip values.
        strike_field: Field name for strike/azimuth values.
        dip_scale_factor: Visual scale factor for dip lines.
        collar_layer: Optional layer ID with drillhole collars.
        collar_id_field: Field name for drillhole IDs in collar layer.
        collar_use_geometry: Whether to use layer geometry for collar coordinates.
        collar_x_field: Field name for X coordinate.
        collar_y_field: Field name for Y coordinate.
        collar_z_field: Field name for Z coordinate.
        collar_depth_field: Field name for total hole depth.
        survey_layer: Optional layer ID with drillhole surveys.
        survey_id_field: Field name for drillhole IDs in survey layer.
        survey_depth_field: Field name for downhole depth in survey.
        survey_azim_field: Field name for azimuth in survey.
        survey_incl_field: Field name for inclination in survey.
        interval_layer: Optional layer ID with drillhole intervals.
        interval_id_field: Field name for drillhole IDs in interval layer.
        interval_from_field: Field name for 'from' depth.
        interval_to_field: Field name for 'to' depth.
        interval_lith_field: Field name for lithology code/name.
        max_points: Max number of points for simplified preview (LOD).
        canvas_width: Width of the preview canvas in pixels.
        auto_lod: Whether to automatically adjust LOD based on canvas width.

    """

    raster_layer: str
    line_layer: str
    band_num: int
    buffer_dist: float = 100.0

    # Geology params
    outcrop_layer: str | None = None
    outcrop_name_field: str | None = None

    # Structure params
    struct_layer: str | None = None
    dip_field: str | None = None
    strike_field: str | None = None
    dip_scale_factor: float = 1.0

    # Drillhole params
    collar_layer: str | None = None
    collar_id_field: str | None = None
    collar_use_geometry: bool = True
    collar_x_field: str | None = None
    collar_y_field: str | None = None
    collar_z_field: str | None = None
    collar_depth_field: str | None = None
    survey_layer: str | None = None
    survey_id_field: str | None = None
    survey_depth_field: str | None = None
    survey_azim_field: str | None = None
    survey_incl_field: str | None = None
    interval_layer: str | None = None
    interval_id_field: str | None = None
    interval_from_field: str | None = None
    interval_to_field: str | None = None
    interval_lith_field: str | None = None

    # LOD Params
    max_points: int = 1000
    canvas_width: int = 800
    auto_lod: bool = True

    def validate(self) -> None:
        """Perform native validation of parameters.

        Raises:
            ValidationError: If critical parameters are missing or invalid.

        """
        self._validate_core_params()
        self._validate_geology_params()
        self._validate_structure_params()
        self._validate_drillhole_params()

    def _validate_core_params(self) -> None:
        """Validate core raster and line layer IDs."""
        if not self.raster_layer:
            raise ValidationError("Raster layer ID is missing.")
        if not self.line_layer:
            raise ValidationError("Section line layer ID is missing.")
        if self.band_num < 1:
            raise ValidationError(f"Invalid band number: {self.band_num}")
        if self.buffer_dist < 0:
            raise ValidationError(f"Buffer distance cannot be negative: {self.buffer_dist}")

    def _validate_geology_params(self) -> None:
        """Validate geology specific parameters."""
        if self.outcrop_layer and not self.outcrop_name_field:
            raise ValidationError("Outcrop layer selected but no name field provided.")

    def _validate_structure_params(self) -> None:
        """Validate structure specific parameters."""
        if self.struct_layer and (not self.dip_field or not self.strike_field):
            raise ValidationError("Structural layer selected but dip/strike fields missing.")

    def _validate_drillhole_params(self) -> None:
        """Validate drillhole specific parameters."""
        if self.collar_layer:
            if not self.collar_id_field:
                raise ValidationError("Collar layer selected but no ID field provided.")
            self._validate_survey_params()
            self._validate_interval_params()

    def _validate_survey_params(self) -> None:
        """Validate drillhole survey parameters."""
        if self.survey_layer:
            required = [
                self.survey_id_field,
                self.survey_depth_field,
                self.survey_azim_field,
                self.survey_incl_field,
            ]
            if not all(required):
                raise ValidationError("Survey layer selected but some required fields are missing.")

    def _validate_interval_params(self) -> None:
        """Validate drillhole interval parameters for consistency and field existence."""
        if self.interval_layer:
            required = [
                self.interval_id_field,
                self.interval_from_field,
                self.interval_to_field,
                self.interval_lith_field,
            ]
            if not all(required):
                raise ValidationError(
                    "Interval layer selected but some required fields are missing."
                )


@dataclass
class PreviewResult:
    """Consolidated result set from profile generation.

    Attributes:
        topo: Sampled topographic profile data.
        geol: List of geological unit segments.
        struct: List of projected structural measurements.
        drillhole: Processed drillhole projection data.
        metrics: Performance metrics collector for the generation cycle.
        buffer_dist: Buffer distance used for this result.

    """

    topo: ProfileData | None = None
    geol: GeologyData | None = None
    struct: StructureData | None = None
    drillhole: Any | None = None
    metrics: MetricsCollector = field(default_factory=MetricsCollector)
    buffer_dist: float = 0.0

    def get_elevation_range(self) -> tuple[float, float]:
        """Calculate the global minimum and maximum elevation across all active layers.

        Scans topography, geology, structural measurements, and drillhole data
        to find the absolute vertical bounds.

        Returns:
            A tuple containing (min_elevation, max_elevation).

        """
        elevations = []
        if self.topo:
            elevations.extend(p[1] for p in self.topo)

        elevations.extend(self._get_geol_elevations())
        elevations.extend(self._get_struct_elevations())
        elevations.extend(self._get_drillhole_elevations())

        if not elevations:
            return 0.0, 0.0
        return min(elevations), max(elevations)

    def _get_geol_elevations(self) -> list[float]:
        """Extract elevations from geology data."""
        if not self.geol:
            return []
        return [p[1] for segment in self.geol for p in segment.points]

    def _get_struct_elevations(self) -> list[float]:
        """Extract elevations from structural data points.

        Returns:
            List of elevation values (Z).

        """
        if not self.struct:
            return []
        return [m.elevation for m in self.struct]

    def _get_drillhole_elevations(self) -> list[float]:
        """Extract elevations from drillhole data using DrillholeProjection entities."""
        if not self.drillhole:
            return []

        elevations = []
        for hole_proj in self.drillhole:
            # hole_proj is a DrillholeProjection object
            if hole_proj.points_3d:
                elevations.extend(p.z for p in hole_proj.points_3d)
            if hole_proj.segments:
                for seg in hole_proj.segments:
                    elevations.extend(p[1] for p in seg.points)
        return elevations

    def get_distance_range(self) -> tuple[float, float]:
        """Calculate the horizontal distance range based on topography.

        Uses the first and last points of the sampled topography as the
        authoritative horizontal bounds of the section.

        Returns:
            A tuple containing (min_distance, max_distance).

        """
        if not self.topo:
            return 0.0, 0.0
        return self.topo[0][0], self.topo[-1][0]
