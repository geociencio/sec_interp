"""Project validation utilities (Orchestrator)."""
from dataclasses import dataclass
from qgis.core import QgsRasterLayer, QgsVectorLayer, QgsWkbTypes

from .layer_validator import (
    validate_raster_band,
    validate_layer_geometry,
    validate_layer_has_features,
    validate_structural_requirements,
    validate_field_exists,
)
from .path_validator import validate_output_path


def validate_reasonable_ranges(values: dict) -> list[str]:
    """Check for unreasonable parameter values."""
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
                f"⚠ Vertical exaggeration ({vert_exag}) is very low. "
                f"Profile may appear flattened."
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
    """Data container for all parameters that need validation."""
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


class ProjectValidator:
    """Orchestrates validation of project parameters independent of the GUI."""

    @staticmethod
    def validate_all(params: ValidationParams) -> tuple[bool, str]:
        """Validate all parameters."""
        errors = []

        # 1. Raster Layer
        if not params.raster_layer:
            errors.append("Raster DEM layer is required")
        elif params.band_number is not None:
            is_valid, error = validate_raster_band(params.raster_layer, params.band_number)
            if not is_valid:
                errors.append(error)

        # 2. Section Line
        if not params.line_layer:
            errors.append("Cross-section line layer is required")
        else:
            is_valid, error = validate_layer_geometry(params.line_layer, QgsWkbTypes.LineGeometry)
            if not is_valid:
                errors.append(error)
            
            is_valid, error = validate_layer_has_features(params.line_layer)
            if not is_valid:
                errors.append(error)

        # 3. Output Path
        if not params.output_path:
            errors.append("Output directory path is required")
        else:
            is_valid, error, _ = validate_output_path(params.output_path)
            if not is_valid:
                errors.append(error)

        # 4. Numeric Ranges
        if params.scale < 1:
            errors.append("Scale must be >= 1")
        if params.vert_exag < 0.1:
            errors.append("Vertical exaggeration must be >= 0.1")
        if params.buffer_dist < 0:
            errors.append("Buffer distance must be >= 0")
        if params.dip_scale_factor < 0.1:
            errors.append("Dip scale factor must be >= 0.1")

        # 5. Geology Inputs
        if params.outcrop_layer:
            is_valid, error = validate_layer_geometry(params.outcrop_layer, QgsWkbTypes.PolygonGeometry)
            if not is_valid:
                errors.append(error)
            else:
                is_valid, error = validate_layer_has_features(params.outcrop_layer)
                if not is_valid:
                    errors.append(error)
                
                if not params.outcrop_field:
                    errors.append("Geology unit field is required")
                else:
                    is_valid, error = validate_field_exists(params.outcrop_layer, params.outcrop_field)
                    if not is_valid:
                        errors.append(error)

        # 6. Structure Inputs
        if params.struct_layer:
            is_valid, error = validate_structural_requirements(
                params.struct_layer,
                params.struct_layer.name(),
                params.struct_dip_field,
                params.struct_strike_field
            )
            if not is_valid:
                errors.append(error)

        if errors:
            return False, "\n".join(errors)
        return True, ""

    @staticmethod
    def validate_preview_requirements(params: ValidationParams) -> tuple[bool, str]:
        """Validate minimum requirements for preview."""
        errors = []
        if not params.raster_layer:
            errors.append("Raster DEM layer is required")
        if not params.line_layer:
            errors.append("Cross-section line layer is required")
        
        if errors:
            return False, "\n".join(errors)
        return True, ""
