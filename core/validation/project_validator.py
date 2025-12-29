"""Validation for QGIS project state and layer presence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Union

from qgis.core import QgsRasterLayer, QgsVectorLayer, QgsWkbTypes

from sec_interp.core.exceptions import ValidationError

from .layer_validator import (
    validate_field_exists,
    validate_layer_geometry,
    validate_layer_has_features,
    validate_raster_band,
    validate_structural_requirements,
)
from .path_validator import validate_output_path


def validate_reasonable_ranges(values: dict[str, Any]) -> list[str]:
    """Check for unreasonable or potentially erroneous parameter values.

    This function does not return hard errors, but a list of warning strings
    to inform the user about extreme values (e.g., vertical exaggeration > 10).

    Args:
        values: Dictionary containing parameter names and their current values.

    Returns:
        A list of warning messages. If empty, all values are reasonable.

    """
    warnings = []

    # Vertical exaggeration
    try:
        vert_exag = float(values.get("vert_exag", 1.0))
        if vert_exag > 10:
            warnings.append(
                f"⚠ Vertical exaggeration ({vert_exag}) is very high. "
                f"Values > 10 may distort the profile significantly."
            )
        elif vert_exag < 0.1:
            warnings.append(
                f"⚠ Vertical exaggeration ({vert_exag}) is very low. Profile may appear flattened."
            )
        elif vert_exag <= 0:
            warnings.append(f"❌ Vertical exaggeration ({vert_exag}) must be positive.")
    except (ValueError, TypeError):
        pass

    # Buffer distance
    try:
        buffer = float(values.get("buffer", 0))
        if buffer > 5000:
            warnings.append(
                f"⚠ Buffer distance ({buffer}m) is very large. "
                f"This may include distant structures not relevant to the section."
            )
        elif buffer < 0:
            warnings.append(f"❌ Buffer distance ({buffer}m) cannot be negative.")
    except (ValueError, TypeError):
        pass

    # Dip scale
    try:
        dip_scale = float(values.get("dip_scale", 1.0))
        if dip_scale > 5:
            warnings.append(
                f"⚠ Dip scale ({dip_scale}) is very high. "
                f"Dip symbols may overlap and obscure the profile."
            )
        elif dip_scale <= 0:
            warnings.append(f"❌ Dip scale ({dip_scale}) must be positive.")
    except (ValueError, TypeError):
        pass

    return warnings


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
    """Orchestrates validation of project parameters independent of the GUI."""

    @staticmethod
    def validate_all(params: ValidationParams) -> bool:
        """Perform a comprehensive validation of all project parameters.

        Args:
            params: The parameters to validate.

        Returns:
            True if all checks passed.

        Raises:
            ValidationError: If any validation check fails.

        """
        errors: list[str] = []

        # Decomposed validation steps
        ProjectValidator._validate_dem(params, errors)
        ProjectValidator._validate_section(params, errors)
        ProjectValidator._validate_output(params, errors)
        ProjectValidator._validate_numeric_ranges(params, errors)
        ProjectValidator._validate_geology(params, errors)
        ProjectValidator._validate_structural(params, errors)

        if errors:
            raise ValidationError("\n".join(errors))
        return True

    @staticmethod
    def _validate_dem(params: ValidationParams, errors: list[str]) -> None:
        """Validate Raster DEM layer."""
        if not params.raster_layer:
            errors.append("Raster DEM layer is required")
        elif params.band_number is not None:
            is_valid, error = validate_raster_band(params.raster_layer, params.band_number)
            if not is_valid:
                errors.append(error)

    @staticmethod
    def _validate_section(params: ValidationParams, errors: list[str]) -> None:
        """Validate Cross-section line layer."""
        if not params.line_layer:
            errors.append("Cross-section line layer is required")
            return

        is_valid, error = validate_layer_geometry(params.line_layer, QgsWkbTypes.LineGeometry)
        if not is_valid:
            errors.append(error)

        is_valid, error = validate_layer_has_features(params.line_layer)
        if not is_valid:
            errors.append(error)

    @staticmethod
    def _validate_output(params: ValidationParams, errors: list[str]) -> None:
        """Validate output path."""
        if not params.output_path:
            errors.append("Output directory path is required")
        else:
            is_valid, error, _ = validate_output_path(params.output_path)
            if not is_valid:
                errors.append(error)

    @staticmethod
    def _validate_numeric_ranges(params: ValidationParams, errors: list[str]) -> None:
        """Validate numeric parameter ranges."""
        checks = [
            (params.scale < 1, "Scale must be >= 1"),
            (params.vert_exag < 0.1, "Vertical exaggeration must be >= 0.1"),
            (params.buffer_dist < 0, "Buffer distance must be >= 0"),
            (params.dip_scale_factor < 0.1, "Dip scale factor must be >= 0.1"),
        ]
        for condition, msg in checks:
            if condition:
                errors.append(msg)

    @staticmethod
    def _validate_geology(params: ValidationParams, errors: list[str]) -> None:
        """Validate Geology Inputs."""
        if not params.outcrop_layer:
            return

        is_valid, error = validate_layer_geometry(params.outcrop_layer, QgsWkbTypes.PolygonGeometry)
        if not is_valid:
            errors.append(error)
            return

        is_valid, error = validate_layer_has_features(params.outcrop_layer)
        if not is_valid:
            errors.append(error)

        if not params.outcrop_field:
            errors.append("Geology unit field is required")
        else:
            is_valid, error = validate_field_exists(params.outcrop_layer, params.outcrop_field)
            if not is_valid:
                errors.append(error)

    @staticmethod
    def _validate_structural(params: ValidationParams, errors: list[str]) -> None:
        """Validate Structural Inputs."""
        if not params.struct_layer:
            return

        is_valid, error = validate_structural_requirements(
            params.struct_layer,
            params.struct_layer.name(),
            params.struct_dip_field,
            params.struct_strike_field,
        )
        if not is_valid:
            errors.append(error)

    @staticmethod
    def validate_preview_requirements(params: ValidationParams) -> bool:
        """Validate only the minimum requirements needed to generate a preview.

        Args:
            params: The parameters containing at least raster and line layers.

        Returns:
            True if the core preview can be generated.

        Raises:
            ValidationError: Description of missing core components.

        """
        errors = []
        if not params.raster_layer:
            errors.append("Raster DEM layer is required")
        if not params.line_layer:
            errors.append("Cross-section line layer is required")

        if errors:
            raise ValidationError("\n".join(errors))
        return True

    @staticmethod
    def is_drillhole_complete(params: ValidationParams) -> bool:
        """Check if required fields are filled if drillhole layers are selected."""
        if not params.collar_layer or not params.collar_id:
            return False

        if not params.collar_use_geom and not (params.collar_x and params.collar_y):
            return False

        # If Survey Layer selected, check its fields
        if params.survey_layer and not all(
            [
                params.survey_id,
                params.survey_depth,
                params.survey_azim,
                params.survey_incl,
            ]
        ):
            return False

        # If Interval Layer selected, check its fields
        if params.interval_layer:
            return all(
                [
                    params.interval_id,
                    params.interval_from,
                    params.interval_to,
                    params.interval_lith,
                ]
            )

        return True

    @staticmethod
    def is_geology_complete(params: ValidationParams) -> bool:
        """Check if geology requirements are met."""
        return bool(params.outcrop_layer and params.outcrop_field)

    @staticmethod
    def is_structure_complete(params: ValidationParams) -> bool:
        """Check if structural requirements are met."""
        return bool(params.struct_layer and params.struct_dip_field and params.struct_strike_field)
