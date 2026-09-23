"""Validation for project state and layer presence (QGIS-agnostic)."""

from __future__ import annotations

from dataclasses import dataclass

from sec_interp.core.validation.layer_metadata import LayerMetadata

from .validation_helpers import ValidationContext

# validate_reasonable_ranges moved to validation_helpers.py
MIN_FLOAT_THRESHOLD = 0.1


@dataclass
class ValidationParams:
    """Data container for all parameters that need cross-layer validation.

    Layers are held as detached :class:`LayerMetadata` produced by the GUI
    ``ValidationExtractor`` adapter.
    """

    raster_layer: LayerMetadata | None = None
    band_number: int | None = None
    line_layer: LayerMetadata | None = None
    line_vertex_count: int | None = None
    line_length: float | None = None
    output_path: str = ""
    scale: float = 1.0
    vert_exag: float = 1.0
    buffer_dist: float = 0.0
    outcrop_layer: LayerMetadata | None = None
    outcrop_field: str | None = None
    struct_layer: LayerMetadata | None = None
    struct_dip_field: str | None = None
    struct_strike_field: str | None = None
    dip_scale_factor: float = 1.0

    # Drillhole params
    collar_layer: LayerMetadata | None = None
    collar_id: str | None = None
    collar_use_geom: bool = True
    collar_x: str | None = None
    collar_y: str | None = None
    survey_layer: LayerMetadata | None = None
    survey_id: str | None = None
    survey_depth: str | None = None
    survey_azim: str | None = None
    survey_incl: str | None = None
    interval_layer: LayerMetadata | None = None
    interval_id: str | None = None
    interval_from: str | None = None
    interval_to: str | None = None
    interval_lith: str | None = None


class ProjectValidator:
    """Orchestrates validation of project parameters independent of the GUI.

    Level 2: Business Logic Validation.
    Uses ValidationContext to accumulate errors and verify cross-field dependencies.
    """

    @classmethod
    def validate_all(cls, params: ValidationParams) -> bool:
        """Perform a comprehensive validation of all project parameters."""
        from .pipeline import ValidationPipeline
        from .project_validators import (
            CrsPlausibilityValidator,
            DEMValidator,
            DrillholeValidator,
            GeologyValidator,
            OutputValidator,
            SectionValidator,
            StructureValidator,
        )

        context = ValidationContext()
        pipeline = ValidationPipeline(
            [
                SectionValidator(),
                DEMValidator(),
                CrsPlausibilityValidator(),
                GeologyValidator(),
                StructureValidator(),
                DrillholeValidator(),
                OutputValidator(),
            ]
        )

        pipeline.execute(params, context)
        context.raise_if_errors()
        return True

    @classmethod
    def validate_preview_requirements(cls, params: ValidationParams) -> bool:
        """Validate only the minimum requirements needed to generate a preview."""
        from .pipeline import ValidationPipeline
        from .project_validators import (
            CrsPlausibilityValidator,
            DEMValidator,
            SectionValidator,
        )

        context = ValidationContext()
        pipeline = ValidationPipeline(
            [SectionValidator(), DEMValidator(), CrsPlausibilityValidator()]
        )
        pipeline.execute(params, context)
        context.raise_if_errors()
        return True

    # --- Compatibility Helpers / Legacy Proxies ---

    @classmethod
    def crs_compatibility_warning(cls, params: ValidationParams) -> str:
        """Return a CRS-mismatch warning for the configured layers, or ``""``.

        Non-blocking: QGIS reprojects on the fly, but a mismatch can degrade
        accuracy (and, for rasters, sampling intervals expressed in the wrong
        CRS). The first valid configured layer is used as reference, so the DEM
        (if present) leads the comparison.
        """
        from .layer_validator import validate_crs_compatibility

        metadata = [
            params.raster_layer,
            params.line_layer,
            params.outcrop_layer,
            params.struct_layer,
            params.collar_layer,
            params.survey_layer,
            params.interval_layer,
        ]
        is_compatible, message = validate_crs_compatibility([m for m in metadata if m is not None])
        return "" if is_compatible else message

    @classmethod
    def crs_plausibility_error(cls, params: ValidationParams) -> str:
        """Return a blocking message for mislabelled-CRS suspects, or ``""``.

        Best-effort heuristic on layer extents (see ``crs_plausibility``). A
        wrong CRS label produces silently wrong profiles, so it is treated as a
        hard error rather than a warning.
        """
        from .crs_plausibility import configured_layer_metadata, implausible_crs_reason

        reasons = [
            implausible_crs_reason(metadata) for metadata in configured_layer_metadata(params)
        ]
        return "\n".join(reason for reason in reasons if reason)

    @classmethod
    def is_drillhole_complete(cls, params: ValidationParams) -> bool:
        """Check if required fields are filled if drillhole layers are selected."""
        if not params.collar_layer or not params.collar_id:
            return False

        from .project_validators import DrillholeValidator

        context = ValidationContext()
        DrillholeValidator().validate(params, context)
        return not context.has_errors

    @classmethod
    def section_geometry_error(cls, params: ValidationParams) -> str:
        """Return the section-line geometry error, or an empty string.

        Shared by the core pipeline and the GUI gating (semaphore / preview
        enablement) so both stay on the same rule.
        """
        from .project_validators import section_line_geometry_error

        return section_line_geometry_error(params)

    @classmethod
    def is_dem_complete(cls, params: ValidationParams) -> bool:
        """Check if DEM configuration is complete."""
        if not params.raster_layer:
            return False

        from .project_validators import DEMValidator

        context = ValidationContext()
        DEMValidator().validate(params, context)
        return not context.has_errors

    @classmethod
    def is_geology_complete(cls, params: ValidationParams) -> bool:
        """Check if geology configuration is complete."""
        if not params.outcrop_layer or not params.outcrop_field:
            return False

        from .project_validators import GeologyValidator

        context = ValidationContext()
        GeologyValidator().validate(params, context)
        return not context.has_errors

    @classmethod
    def is_structure_complete(cls, params: ValidationParams) -> bool:
        """Check if structural configuration is complete."""
        if not params.struct_layer or not params.struct_dip_field or not params.struct_strike_field:
            return False

        from .project_validators import StructureValidator

        context = ValidationContext()
        StructureValidator().validate(params, context)
        return not context.has_errors
