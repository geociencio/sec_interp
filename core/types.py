from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Optional, Protocol, runtime_checkable

from qgis.core import QgsGeometry, QgsPointXY, QgsRasterLayer, QgsVectorLayer

from sec_interp.core.exceptions import ConfigurationError, ValidationError
from sec_interp.core.performance_metrics import MetricsCollector


class FieldType(IntEnum):
    """Core-safe field types mapping to QVariant.Type values.

    This allows the core module to perform type validation WITHOUT
    direct dependencies on PyQt components.
    """

    NULL = 0
    BOOL = 1
    INT = 2
    DOUBLE = 6
    STRING = 10
    LONG_LONG = 4
    DATE = 14
    DATE_TIME = 16


# Profile data types (Initial aliases)
ProfilePoints = list[tuple[float, float]]
GeologyPoints = list[tuple[float, float, str]]
StructurePoints = list[tuple[float, float]]

# Layer collections
LayerDict = dict[str, QgsVectorLayer]
"""Dictionary mapping layer names to QgsVectorLayer objects."""

# Settings and configuration
SettingsDict = dict[str, Any]
"""Dictionary of plugin settings and configuration values."""

ExportSettings = dict[str, Any]
"""Dictionary of export configuration parameters."""

# Validation results
ValidationResult = tuple[bool, str]
"""Tuple of (is_valid, error_message) from validation functions."""

# Point data
PointList = list[QgsPointXY]
"""List of QgsPointXY objects."""



@dataclass
class StructureMeasurement:
    """Represents a projected structural measurement on the section plane.

    Attributes:
        distance: Horizontal distance from the start of the profile.
        elevation: Elevation (Z) at the projected point.
        apparent_dip: Dip angle relative to the section plane.
        original_dip: True dip measured in the field.
        original_strike: True strike (azimuth) measured in the field.
        attributes: Dictionary containing original feature attributes.
    """

    distance: float
    elevation: float
    apparent_dip: float
    original_dip: float
    original_strike: float
    attributes: dict[str, Any]


@dataclass
class GeologySegment:
    """Represents a geological unit segment along the profile.

    Attributes:
        unit_name: Name of the geological unit.
        geometry: QGIS geometry of the segment.
        attributes: Dictionary containing original feature attributes.
        points: Sampled points (distance, elevation) representing the segment boundary.
    """

    unit_name: str
    geometry: QgsGeometry  # Forward reference
    attributes: dict[str, Any]
    points: list[tuple[float, float]]


# Final type aliases for processed data
StructureData = list[StructureMeasurement]
GeologyData = list[GeologySegment]
ProfileData = list[tuple[float, float]]


@dataclass
class PreviewParams:
    """Consolidated parameters for profile generation and preview.

    Attributes:
        raster_layer: QGIS raster layer for DEM sampling.
        line_layer: QGIS vector layer for the section orientation.
        band_num: Raster band number to use for elevation.
        buffer_dist: Search buffer for projecting data onto the section.
        outcrop_layer: Optional vector layer with geological outcrops.
        outcrop_name_field: Field name for geological unit names.
        struct_layer: Optional vector layer with structural measurements.
        dip_field: Field name for dip values.
        strike_field: Field name for strike/azimuth values.
        dip_scale_factor: Visual scale factor for dip lines.
        collar_layer: Optional vector layer with drillhole collars.
        collar_id_field: Field name for drillhole IDs in collar layer.
        collar_use_geometry: Whether to use layer geometry for collar coordinates.
        collar_x_field: Field name for X coordinate.
        collar_y_field: Field name for Y coordinate.
        collar_z_field: Field name for Z coordinate.
        collar_depth_field: Field name for total hole depth.
        survey_layer: Optional vector layer with drillhole surveys.
        survey_id_field: Field name for drillhole IDs in survey layer.
        survey_depth_field: Field name for downhole depth in survey.
        survey_azim_field: Field name for azimuth in survey.
        survey_incl_field: Field name for inclination in survey.
        interval_layer: Optional vector layer with drillhole intervals.
        interval_id_field: Field name for drillhole IDs in interval layer.
        interval_from_field: Field name for 'from' depth.
        interval_to_field: Field name for 'to' depth.
        interval_lith_field: Field name for lithology code/name.
        max_points: Max number of points for simplified preview (LOD).
        canvas_width: Width of the preview canvas in pixels.
        auto_lod: Whether to automatically adjust LOD based on canvas width.
    """

    raster_layer: QgsRasterLayer
    line_layer: QgsVectorLayer
    band_num: int
    buffer_dist: float = 100.0

    # Geology params
    outcrop_layer: Optional[QgsVectorLayer] = None
    outcrop_name_field: Optional[str] = None

    # Structure params
    struct_layer: Optional[QgsVectorLayer] = None
    dip_field: Optional[str] = None
    strike_field: Optional[str] = None
    dip_scale_factor: float = 1.0

    # Drillhole params
    collar_layer: Optional[QgsVectorLayer] = None
    collar_id_field: Optional[str] = None
    collar_use_geometry: bool = True
    collar_x_field: Optional[str] = None
    collar_y_field: Optional[str] = None
    collar_z_field: Optional[str] = None
    collar_depth_field: Optional[str] = None
    survey_layer: Optional[QgsVectorLayer] = None
    survey_id_field: Optional[str] = None
    survey_depth_field: Optional[str] = None
    survey_azim_field: Optional[str] = None
    survey_incl_field: Optional[str] = None
    interval_layer: Optional[QgsVectorLayer] = None
    interval_id_field: Optional[str] = None
    interval_from_field: Optional[str] = None
    interval_to_field: Optional[str] = None
    interval_lith_field: Optional[str] = None

    # LOD Params
    max_points: int = 1000
    canvas_width: int = 800
    auto_lod: bool = True

    def validate(self) -> None:
        """Perform native validation of parameters.

        Raises:
            ValidationError: If critical parameters are missing or invalid.
        """
        if not self.raster_layer or not self.raster_layer.isValid():
            raise ValidationError("Raster layer is missing or invalid.")
        if not self.line_layer or not self.line_layer.isValid():
            raise ValidationError("Section line layer is missing or invalid.")
        if self.band_num < 1:
            raise ValidationError(f"Invalid band number: {self.band_num}")
        if self.buffer_dist < 0:
            raise ValidationError(f"Buffer distance cannot be negative: {self.buffer_dist}")

        # Dependent validation
        if self.outcrop_layer and self.outcrop_layer.isValid() and not self.outcrop_name_field:
            raise ValidationError("Outcrop layer selected but no name field provided.")

        if self.struct_layer and self.struct_layer.isValid() and (not self.dip_field or not self.strike_field):
            raise ValidationError("Structural layer selected but dip/strike fields missing.")

        if self.collar_layer and self.collar_layer.isValid() and not self.collar_id_field:
            raise ValidationError("Collar layer selected but no ID field provided.")

        if self.survey_layer and self.survey_layer.isValid() and not all([self.survey_id_field, self.survey_depth_field, self.survey_azim_field, self.survey_incl_field]):
            raise ValidationError("Survey layer selected but some required fields are missing.")

        if self.interval_layer and self.interval_layer.isValid() and not all([self.interval_id_field, self.interval_from_field, self.interval_to_field, self.interval_lith_field]):
            raise ValidationError("Interval layer selected but some required fields are missing.")


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

    topo: Optional[ProfileData] = None
    geol: Optional[GeologyData] = None
    struct: Optional[StructureData] = None
    drillhole: Optional[Any] = None
    metrics: MetricsCollector = field(default_factory=MetricsCollector)
    buffer_dist: float = 0.0

    def get_elevation_range(self) -> tuple[float, float]:
        """Calculate the global minimum and maximum elevation across all layers.

        Returns:
            A tuple containing (min_elevation, max_elevation).
        """
        elevations = []
        if self.topo:
            elevations.extend(p[1] for p in self.topo)
        if self.geol:
            for segment in self.geol:
                elevations.extend(p[1] for p in segment.points)
        if self.struct:
            elevations.extend(m.elevation for m in self.struct)
        if self.drillhole:
            for _, trace, segments in self.drillhole:
                if trace:
                    elevations.extend(p[1] for p in trace)
                if segments:
                    for seg in segments:
                        elevations.extend(p[1] for p in seg.points)

        if not elevations:
            return 0.0, 0.0
        return min(elevations), max(elevations)

    def get_distance_range(self) -> tuple[float, float]:
        """Calculate the horizontal distance range based on topography.

        Returns:
            A tuple containing (min_distance, max_distance).
        """
        if not self.topo:
            return 0.0, 0.0
        return self.topo[0][0], self.topo[-1][0]
