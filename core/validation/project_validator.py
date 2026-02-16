"""Validation for QGIS project state and layer presence."""

from __future__ import annotations

from dataclasses import dataclass

from qgis.core import QgsRasterLayer, QgsVectorLayer, QgsWkbTypes

from .layer_validator import (
    validate_field_exists,
    validate_layer_geometry,
    validate_layer_has_features,
    validate_raster_band,
    validate_structural_requirements,
)
from .path_validator import validate_output_path
from .validation_helpers import ValidationContext, validate_reasonable_ranges

# validate_reasonable_ranges moved to validation_helpers.py
MIN_FLOAT_THRESHOLD = 0.1


@dataclass
class ValidationParams:
    """Data container for all parameters that need cross-layer validation."""

    raster_layer: str | QgsRasterLayer | None = None
    band_number: int | None = None
    line_layer: str | QgsVectorLayer | None = None
    output_path: str = ""
    scale: float = 1.0
    vert_exag: float = 1.0
    buffer_dist: float = 0.0
    outcrop_layer: str | QgsVectorLayer | None = None
    outcrop_field: str | None = None
    struct_layer: str | QgsVectorLayer | None = None
    struct_dip_field: str | None = None
    struct_strike_field: str | None = None
    dip_scale_factor: float = 1.0

    # Drillhole params
    collar_layer: str | QgsVectorLayer | None = None
    collar_id: str | None = None
    collar_use_geom: bool = True
    collar_x: str | None = None
    collar_y: str | None = None
    survey_layer: str | QgsVectorLayer | None = None
    survey_id: str | None = None
    survey_depth: str | None = None
    survey_azim: str | None = None
    survey_incl: str | None = None
    interval_layer: str | QgsVectorLayer | None = None
    interval_id: str | None = None
    interval_from: str | None = None
    interval_to: str | None = None
    interval_lith: str | None = None


class ProjectValidator:
    """Orchestrates validation of project parameters independent of the GUI.

    Level 2: Business Logic Validation.
    Uses ValidationContext to accumulate errors and verify cross-field dependencies.
    """

    @staticmethod
    def _resolve_layer(layer_ref: Any) -> Any:
        """Resolve layer ID or object to a QgsMapLayer."""
        from qgis.core import QgsProject

        if not isinstance(layer_ref, str) or not layer_ref:
            return layer_ref

        return QgsProject.instance().mapLayer(str(layer_ref))

    @staticmethod
    def validate_all(params: ValidationParams) -> bool:
        """Perform a comprehensive validation of all project parameters."""
        # Level 2 Validation: Business Context Accumulation
        context = ValidationContext()

        # Phase 1: Critical Structural Checks (Dependencies)
        # Assuming DEM and Section are critical for any operation
        ProjectValidator._validate_dem(params, context)
        ProjectValidator._validate_section(params, context)
        ProjectValidator._validate_output(params, context)

        # Phase 2: Numeric Ranges & Business Rules
        ProjectValidator._validate_numeric_ranges(params, context)
        ProjectValidator._validate_geology(params, context)
        ProjectValidator._validate_structural(params, context)

        # Phase 3: Drillhole dependencies (Complex)
        ProjectValidator._validate_drillholes(params, context)

        # Raise accumulated errors
        context.raise_if_errors()
        return True

    @staticmethod
    def _validate_dem(params: ValidationParams, context: ValidationContext) -> None:
        """Validate Raster DEM layer."""
        if not params.raster_layer:
            context.add_error("Raster DEM layer is required", "raster_layer")
        else:
            raster_lyr = ProjectValidator._resolve_layer(params.raster_layer)
            if not raster_lyr:
                context.add_error(
                    "Raster DEM layer not found in project", "raster_layer"
                )
            elif params.band_number is not None:
                is_valid, error = validate_raster_band(raster_lyr, params.band_number)
                if not is_valid:
                    context.add_error(error, "band_number")

    @staticmethod
    def _validate_section(params: ValidationParams, context: ValidationContext) -> None:
        """Validate Cross-section line layer."""
        if not params.line_layer:
            context.add_error("Cross-section line layer is required", "line_layer")
            return

        line_lyr = ProjectValidator._resolve_layer(params.line_layer)
        if not line_lyr:
            context.add_error(
                "Cross-section line layer not found in project", "line_layer"
            )
            return

        is_valid, error = validate_layer_geometry(line_lyr, QgsWkbTypes.LineGeometry)
        if not is_valid:
            context.add_error(error, "line_layer")

        is_valid, error = validate_layer_has_features(line_lyr)
        if not is_valid:
            context.add_error(error, "line_layer")

    @staticmethod
    def _validate_output(params: ValidationParams, context: ValidationContext) -> None:
        """Validate output path."""
        if not params.output_path:
            context.add_error("Output directory path is required", "output_path")
        else:
            is_valid, error, _ = validate_output_path(params.output_path)
            if not is_valid:
                context.add_error(error, "output_path")

    @staticmethod
    def _validate_numeric_ranges(
        params: ValidationParams, context: ValidationContext
    ) -> None:
        """Validate numeric parameter ranges."""
        # Level 1 logic might handle simple types, but business rules (Project Level) check context consistency here.
        # Warnings are accumulated too.
        warnings = validate_reasonable_ranges(
            {
                "vert_exag": params.vert_exag,
                "scale": params.scale,
                "buffer": params.buffer_dist,
                "dip_scale": params.dip_scale_factor,
            }
        )
        for warn in warnings:
            context.add_warning(warn)

        if params.scale < 1:
            context.add_error("Scale must be >= 1", "scale")
        if params.vert_exag < MIN_FLOAT_THRESHOLD:
            context.add_error("Vertical exaggeration must be >= 0.1", "vert_exag")
        if params.buffer_dist < 0:
            context.add_error("Buffer distance must be >= 0", "buffer_dist")
        if params.dip_scale_factor < MIN_FLOAT_THRESHOLD:
            context.add_error("Dip scale factor must be >= 0.1", "dip_scale_factor")

    @staticmethod
    def _validate_geology(params: ValidationParams, context: ValidationContext) -> None:
        """Validate Geology Inputs using Dependency Rules."""
        # Rule: If outcrop layer is present, field is required.
        if params.outcrop_layer:
            outcrop_lyr = ProjectValidator._resolve_layer(params.outcrop_layer)
            if not outcrop_lyr:
                context.add_error("Geology layer not found in project", "outcrop_layer")
                return

            # Check geometry
            is_valid, error = validate_layer_geometry(
                outcrop_lyr, QgsWkbTypes.PolygonGeometry
            )
            if not is_valid:
                context.add_error(error, "outcrop_layer")

            # Check features
            is_valid, error = validate_layer_has_features(outcrop_lyr)
            if not is_valid:
                context.add_error(error, "outcrop_layer")

            # Check field dependency
            if not params.outcrop_field:
                context.add_error(
                    "Geology unit field is required when geology layer is selected",
                    "outcrop_field",
                )
            else:
                is_valid, error = validate_field_exists(
                    outcrop_lyr, params.outcrop_field
                )
                if not is_valid:
                    context.add_error(error, "outcrop_field")

    @staticmethod
    def _validate_structural(
        params: ValidationParams, context: ValidationContext
    ) -> None:
        """Validate Structural Inputs."""
        if params.struct_layer:
            struct_lyr = ProjectValidator._resolve_layer(params.struct_layer)
            if not struct_lyr:
                context.add_error(
                    "Structural layer not found in project", "struct_layer"
                )
                return

            is_valid, error = validate_structural_requirements(
                struct_lyr,
                struct_lyr.name(),
                params.struct_dip_field,
                params.struct_strike_field,
            )
            if not is_valid:
                context.add_error(error, "struct_layer")

    @staticmethod
    def _validate_drillholes(
        params: ValidationParams, context: ValidationContext
    ) -> None:
        """Validate Drillhole Complex Dependencies (Level 2)."""
        from sec_interp.core.validation.validation_helpers import (
            DependencyRule,
            validate_dependencies,
        )

        # Helper to simplify rules
        has_collar = bool(params.collar_layer)
        has_survey = bool(params.survey_layer)
        has_interval = bool(params.interval_layer)

        # Collar Rules
        if has_collar:
            if not params.collar_id:
                context.add_error("Collar ID field is required", "collar_id")

            if not params.collar_use_geom:
                if not params.collar_x:
                    context.add_error(
                        "Collar X field is required (when not using geometry)",
                        "collar_x",
                    )
                if not params.collar_y:
                    context.add_error(
                        "Collar Y field is required (when not using geometry)",
                        "collar_y",
                    )

        # Survey Rules (Depend on Collar effectively for a valid project, but here we validate internal consistency)
        if has_survey:
            rules = [
                DependencyRule(
                    lambda: True,
                    lambda: bool(params.survey_id),
                    "Survey ID field is required",
                    "survey_id",
                ),
                DependencyRule(
                    lambda: True,
                    lambda: bool(params.survey_depth),
                    "Survey Depth field is required",
                    "survey_depth",
                ),
                DependencyRule(
                    lambda: True,
                    lambda: bool(params.survey_azim),
                    "Survey Azimuth field is required",
                    "survey_azim",
                ),
                DependencyRule(
                    lambda: True,
                    lambda: bool(params.survey_incl),
                    "Survey Inclination field is required",
                    "survey_incl",
                ),
            ]
            validate_dependencies(rules, context)

        # Interval Rules
        if has_interval:
            rules = [
                DependencyRule(
                    lambda: True,
                    lambda: bool(params.interval_id),
                    "Interval ID field is required",
                    "interval_id",
                ),
                DependencyRule(
                    lambda: True,
                    lambda: bool(params.interval_from),
                    "Interval From field is required",
                    "interval_from",
                ),
                DependencyRule(
                    lambda: True,
                    lambda: bool(params.interval_to),
                    "Interval To field is required",
                    "interval_to",
                ),
                DependencyRule(
                    lambda: True,
                    lambda: bool(params.interval_lith),
                    "Interval Lithology field is required",
                    "interval_lith",
                ),
            ]
            validate_dependencies(rules, context)

    @staticmethod
    def validate_preview_requirements(params: ValidationParams) -> bool:
        """Validate only the minimum requirements needed to generate a preview."""
        context = ValidationContext()
        if not params.raster_layer:
            context.add_error("Raster DEM layer is required")
        if not params.line_layer:
            context.add_error("Cross-section line layer is required")

        context.raise_if_errors()
        return True

    # Legacy helper methods for GUI checks (kept for backward compatibility with check_completeness methods)
    # Ideally these should delegate to the context logic, but for simple booleans, direct checks are fine.

    @staticmethod
    def is_drillhole_complete(params: ValidationParams) -> bool:
        """Check if required fields are filled if drillhole layers are selected.

        Args:
            params: The parameters to check.

        Returns:
            True if drillhole configuration is complete and consistent.

        """
        # Basic presence check
        if not params.collar_layer or not params.collar_id:
            return False

        # Internal consistency check
        context = ValidationContext()
        ProjectValidator._validate_drillholes(params, context)
        return not context.has_errors

    @staticmethod
    def is_dem_complete(params: ValidationParams) -> bool:
        """Check if DEM configuration is complete.

        Args:
            params: Parameters to check.

        Returns:
            bool: True if valid.

        """
        if not params.raster_layer:
            return False
        context = ValidationContext()
        ProjectValidator._validate_dem(params, context)
        return not context.has_errors

    @staticmethod
    def is_geology_complete(params: ValidationParams) -> bool:
        """Check if geology configuration is complete.

        Args:
            params: Parameters to check.

        Returns:
            bool: True if valid.

        """
        if not params.outcrop_layer or not params.outcrop_field:
            return False
        context = ValidationContext()
        ProjectValidator._validate_geology(params, context)
        return not context.has_errors

    @staticmethod
    def is_structure_complete(params: ValidationParams) -> bool:
        """Check if structural configuration is complete.

        Args:
            params: Parameters to check.

        Returns:
            bool: True if valid.

        """
        if (
            not params.struct_layer
            or not params.struct_dip_field
            or not params.struct_strike_field
        ):
            return False
        context = ValidationContext()
        ProjectValidator._validate_structural(params, context)
        return not context.has_errors
