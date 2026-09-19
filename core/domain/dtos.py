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
        raster_layer: Resolved DEM raster layer object for sampling.
        line_layer: Resolved section line layer object.
        band_num: Raster band number to use for elevation.
        buffer_dist: Search buffer for projecting data onto the section.
        outcrop_layer: Optional resolved geological outcrop layer object.
        outcrop_name_field: Field name for geological unit names.
        struct_layer: Optional resolved structural measurements layer object.
        dip_field: Field name for dip values.
        strike_field: Field name for strike/azimuth values.
        dip_scale_factor: Visual scale factor for dip lines.
        collar_layer: Optional resolved drillhole collar layer object.
        collar_id_field: Field name for drillhole IDs in collar layer.
        collar_use_geometry: Whether to use layer geometry for collar coordinates.
        collar_x_field: Field name for X coordinate.
        collar_y_field: Field name for Y coordinate.
        collar_z_field: Field name for Z coordinate.
        collar_depth_field: Field name for total hole depth.
        survey_layer: Optional resolved drillhole survey layer object.
        survey_id_field: Field name for drillhole IDs in survey layer.
        survey_depth_field: Field name for downhole depth in survey.
        survey_azim_field: Field name for azimuth in survey.
        survey_incl_field: Field name for inclination in survey.
        interval_layer: Optional resolved drillhole interval layer object.
        interval_id_field: Field name for drillhole IDs in interval layer.
        interval_from_field: Field name for 'from' depth.
        interval_to_field: Field name for 'to' depth.
        interval_lith_field: Field name for lithology code/name.
        max_points: Max number of points for simplified preview (LOD).
        canvas_width: Width of the preview canvas in pixels.
        auto_lod: Whether to automatically adjust LOD based on canvas width.

    """

    raster_layer: Any
    line_layer: Any
    band_num: int
    buffer_dist: float = 100.0

    # Geology params
    outcrop_layer: Any | None = None
    outcrop_name_field: str | None = None

    # Structure params
    struct_layer: Any | None = None
    dip_field: str | None = None
    strike_field: str | None = None
    dip_scale_factor: float = 1.0

    # Drillhole params
    collar_layer: Any | None = None
    collar_id_field: str | None = None
    collar_use_geometry: bool = True
    collar_x_field: str | None = None
    collar_y_field: str | None = None
    collar_z_field: str | None = None
    collar_depth_field: str | None = None
    survey_layer: Any | None = None
    survey_id_field: str | None = None
    survey_depth_field: str | None = None
    survey_azim_field: str | None = None
    survey_incl_field: str | None = None
    interval_layer: Any | None = None
    interval_id_field: str | None = None
    interval_from_field: str | None = None
    interval_to_field: str | None = None
    interval_lith_field: str | None = None

    # LOD Params
    max_points: int = 1000
    canvas_width: int = 800
    auto_lod: bool = True

    def validate(self) -> None:
        """Perform native validation of primitive parameters.

        Layer validation is performed separately by the GUI via
        ``ProjectValidator`` using detached ``LayerMetadata``.

        Raises:
            ValueError: If primitive parameters are missing or invalid.

        """
        # Basic type and range validation
        if not isinstance(self.buffer_dist, int | float) or self.buffer_dist < 0:
            raise ValueError("Buffer distance must be a non-negative number")

        if not isinstance(self.band_num, int) or self.band_num < 1:
            raise ValueError("Band number must be a positive integer")


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
        elevations: list[float] = []
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

        elevations: list[float] = []
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
