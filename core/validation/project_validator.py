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


@dataclass
class ValidationParams:
    """Data container for all parameters that need cross-layer validation."""

    raster_layer: QgsRasterLayer | None = None
    band_number: int | None = None
    line_layer: QgsVectorLayer | None = None
    output_path: str = ""
    scale: float = 1.0
    vert_exag: float = 1.0
    buffer_dist: float = 0.0
    outcrop_layer: QgsVectorLayer | None = None
    outcrop_field: str | None = None
    struct_layer: QgsVectorLayer | None = None
    struct_dip_field: str | None = None
    struct_strike_field: str | None = None
    dip_scale_factor: float = 1.0

    # Drillhole params
    collar_layer: QgsVectorLayer | None = None
    collar_id: str | None = None
    collar_use_geom: bool = True
    collar_x: str | None = None
    collar_y: str | None = None
    survey_layer: QgsVectorLayer | None = None
    survey_id: str | None = None
    survey_depth: str | None = None
    survey_azim: str | None = None
    survey_incl: str | None = None
    interval_layer: QgsVectorLayer | None = None
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
    def validate_all(params: ValidationParams) -> bool:
        """Perform a comprehensive validation of all project parameters.

        Args:
            params: The parameters to validate.

        Returns:
            True if all checks passed.

        Raises:
            ValidationError: If any validation check fails (contains list of errors).

        """
        # Level 2 Validation: Business Context Accumulation
        context = ValidationContext()

        # Phase 1: Critical Structural Checks (Dependencies)
        # Assuming DEM and Section are critical for any operation
        ProjectValidator._validate_dem(params, context)
        ProjectValidator._validate_section(params, context)
        ProjectValidator._validate_output(params, context)

        # Stop here if critical foundations are missing?
        # For now, we continue to gather as much info as possible unless it crashes.

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
        elif params.band_number is not None:
            is_valid, error = validate_raster_band(params.raster_layer, params.band_number)
            if not is_valid:
                context.add_error(error, "band_number")

    @staticmethod
    def _validate_section(params: ValidationParams, context: ValidationContext) -> None:
        """Validate Cross-section line layer."""
        if not params.line_layer:
            context.add_error("Cross-section line layer is required", "line_layer")
            return

        is_valid, error = validate_layer_geometry(params.line_layer, QgsWkbTypes.LineGeometry)
        if not is_valid:
            context.add_error(error, "line_layer")

        is_valid, error = validate_layer_has_features(params.line_layer)
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
    def _validate_numeric_ranges(params: ValidationParams, context: ValidationContext) -> None:
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
        if params.vert_exag < 0.1:
            context.add_error("Vertical exaggeration must be >= 0.1", "vert_exag")
        if params.buffer_dist < 0:
            context.add_error("Buffer distance must be >= 0", "buffer_dist")
        if params.dip_scale_factor < 0.1:
            context.add_error("Dip scale factor must be >= 0.1", "dip_scale_factor")

    @staticmethod
    def _validate_geology(params: ValidationParams, context: ValidationContext) -> None:
        """Validate Geology Inputs using Dependency Rules."""
        # Rule: If outcrop layer is present, field is required.
        if params.outcrop_layer:
            # Check geometry
            is_valid, error = validate_layer_geometry(
                params.outcrop_layer, QgsWkbTypes.PolygonGeometry
            )
            if not is_valid:
                context.add_error(error, "outcrop_layer")

            # Check features
            is_valid, error = validate_layer_has_features(params.outcrop_layer)
            if not is_valid:
                context.add_error(error, "outcrop_layer")

            # Check field dependency
            if not params.outcrop_field:
                context.add_error(
                    "Geology unit field is required when geology layer is selected",
                    "outcrop_field",
                )
            else:
                is_valid, error = validate_field_exists(params.outcrop_layer, params.outcrop_field)
                if not is_valid:
                    context.add_error(error, "outcrop_field")

    @staticmethod
    def _validate_structural(params: ValidationParams, context: ValidationContext) -> None:
        """Validate Structural Inputs."""
        if params.struct_layer:
            is_valid, error = validate_structural_requirements(
                params.struct_layer,
                params.struct_layer.name(),
                params.struct_dip_field,
                params.struct_strike_field,
            )
            if not is_valid:
                context.add_error(error, "struct_layer")

    @staticmethod
    def _validate_drillholes(params: ValidationParams, context: ValidationContext) -> None:
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
        if not params.struct_layer or not params.struct_dip_field or not params.struct_strike_field:
            return False
        context = ValidationContext()
        ProjectValidator._validate_structural(params, context)
        return not context.has_errors
