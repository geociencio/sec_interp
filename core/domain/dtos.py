"""Complex Data Transfer Objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

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
        """Perform native validation using ProjectValidator to avoid duplication.

        Raises:
            ValidationError: If critical parameters are missing or invalid.

        """
        from sec_interp.core.validation.project_validator import (
            ProjectValidator,
            ValidationParams,
        )

        # Basic type and range validation before calling ProjectValidator
        if not isinstance(self.buffer_dist, int | float) or self.buffer_dist < 0:
            raise ValueError("Buffer distance must be a non-negative number")

        if not isinstance(self.band_num, int) or self.band_num < 1:
            raise ValueError("Band number must be a positive integer")

        val_params = ValidationParams(
            raster_layer=self.raster_layer,
            band_number=self.band_num,
            line_layer=self.line_layer,
            buffer_dist=float(self.buffer_dist),
            outcrop_layer=self.outcrop_layer,
            outcrop_field=self.outcrop_name_field,
            struct_layer=self.struct_layer,
            struct_dip_field=self.dip_field,
            struct_strike_field=self.strike_field,
            dip_scale_factor=self.dip_scale_factor,
            collar_layer=self.collar_layer,
            collar_id=self.collar_id_field,
            collar_use_geom=self.collar_use_geometry,
            collar_x=self.collar_x_field,
            collar_y=self.collar_y_field,
            survey_layer=self.survey_layer,
            survey_id=self.survey_id_field,
            survey_depth=self.survey_depth_field,
            survey_azim=self.survey_azim_field,
            survey_incl=self.survey_incl_field,
            interval_layer=self.interval_layer,
            interval_id=self.interval_id_field,
            interval_from=self.interval_from_field,
            interval_to=self.interval_to_field,
            interval_lith=self.interval_lith_field,
        )
        ProjectValidator.validate_all(val_params)


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
