"""Specialized validators for project components (QGIS-agnostic)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sec_interp.core.utils.i18n import TranslatableMixin
from sec_interp.core.validation.layer_metadata import GEOMETRY_LINE, KIND_RASTER

from .base_validator import IValidator
from .layer_validator import (
    validate_layer_geometry,
    validate_layer_has_features,
    validate_raster_band,
    validate_structural_requirements,
)
from .validation_helpers import (
    DependencyRule,
    validate_dependencies,
    validate_reasonable_ranges,
)

if TYPE_CHECKING:
    from .project_validator import ValidationParams
    from .validation_helpers import ValidationContext


class SectionValidator(IValidator):
    """Validates section line requirements."""

    def validate(self, params: ValidationParams, context: ValidationContext) -> None:
        """Validate cross-section line layer requirements."""
        if not params.line_layer:
            context.add_error("Cross-section line layer is required", "line_layer")
            return

        metadata = params.line_layer
        if not metadata.is_valid:
            context.add_error("Cross-section line layer not found in project", "line_layer")
            return

        is_valid, error = validate_layer_geometry(metadata, GEOMETRY_LINE)
        if not is_valid:
            context.add_error(error, "line_layer")

        is_valid, error = validate_layer_has_features(metadata)
        if not is_valid:
            context.add_error(error, "line_layer")


class DEMValidator(IValidator):
    """Validates Raster DEM requirements."""

    def validate(self, params: ValidationParams, context: ValidationContext) -> None:
        """Validate Raster DEM requirements."""
        if not params.raster_layer:
            context.add_error("Raster DEM layer is required", "raster_layer")
            return

        metadata = params.raster_layer
        if not metadata.is_valid:
            context.add_error("Raster DEM layer not found in project", "raster_layer")
            return

        if metadata.kind != KIND_RASTER:
            context.add_error("Raster DEM layer must be a raster layer", "raster_layer")
            return

        if params.band_number is not None:
            is_valid, error = validate_raster_band(metadata, params.band_number)
            if not is_valid:
                context.add_error(error, "band_number")


class GeologyValidator(IValidator):
    """Validates Geology layer and field requirements."""

    def validate(self, params: ValidationParams, context: ValidationContext) -> None:
        """Validate Geology layer and field requirements."""
        if not params.outcrop_layer:
            return

        metadata = params.outcrop_layer
        if not metadata.is_valid:
            context.add_error("Geology layer not found in project", "outcrop_layer")
            return

        from .layer_validator import validate_geology_requirements

        validate_geology_requirements(metadata, params.outcrop_field, context)


class StructureValidator(IValidator):
    """Validates Structural measurements requirements."""

    def validate(self, params: ValidationParams, context: ValidationContext) -> None:
        """Validate Structural measurements requirements."""
        if not params.struct_layer:
            return

        metadata = params.struct_layer
        if not metadata.is_valid:
            context.add_error("Structural layer not found in project", "struct_layer")
            return

        validate_structural_requirements(
            metadata,
            params.struct_dip_field,
            params.struct_strike_field,
            context,
        )


class DrillholeValidator(IValidator):
    """Validates complex Drillhole data dependencies."""

    def validate(self, params: ValidationParams, context: ValidationContext) -> None:
        """Validate complex Drillhole data dependencies."""
        has_collar = bool(params.collar_layer)
        has_survey = bool(params.survey_layer)
        has_interval = bool(params.interval_layer)

        if not (has_collar or has_survey or has_interval):
            return

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

        # Survey Rules
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


class OutputValidator(IValidator, TranslatableMixin):
    """Validates output path and range requirements."""

    def validate(self, params: ValidationParams, context: ValidationContext) -> None:
        """Validate output path and range requirements."""
        if params.output_path:
            from .path_validator import validate_safe_output_path

            is_valid, error, _ = validate_safe_output_path(params.output_path, must_exist=False)
            if not is_valid:
                context.add_error(error, "output_path")

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

        MIN_FLOAT_THRESHOLD = 0.1
        if params.scale < 1:
            context.add_error(self.tr("Scale must be >= 1"), "scale")
        if params.vert_exag < MIN_FLOAT_THRESHOLD:
            context.add_error(
                self.tr("Vertical exaggeration must be >= 0.1"),
                "vert_exag",
            )
        if params.buffer_dist < 0:
            context.add_error(self.tr("Buffer distance must be >= 0"), "buffer_dist")
        if params.dip_scale_factor < MIN_FLOAT_THRESHOLD:
            context.add_error(
                self.tr("Dip scale factor must be >= 0.1"),
                "dip_scale_factor",
            )
