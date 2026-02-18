"""Validation for QGIS project state and layer presence."""

from __future__ import annotations

from dataclasses import dataclass

from qgis.core import QgsRasterLayer, QgsVectorLayer
from qgis.PyQt.QtCore import QCoreApplication

from .validation_helpers import ValidationContext

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
    def tr(message: str) -> str:
        """Translate a message using QCoreApplication."""
        return QCoreApplication.translate("ProjectValidator", message)

    @classmethod
    def validate_all(cls, params: ValidationParams) -> bool:
        """Perform a comprehensive validation of all project parameters."""
        from .pipeline import ValidationPipeline
        from .project_validators import (
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
        from .project_validators import DEMValidator, SectionValidator

        context = ValidationContext()
        pipeline = ValidationPipeline([SectionValidator(), DEMValidator()])
        pipeline.execute(params, context)
        context.raise_if_errors()
        return True

    # --- Compatibility Helpers / Legacy Proxies ---

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

    @staticmethod
    def _resolve_layer(layer_ref: Any) -> Any:
        """Resolve layer ID or object to a QgsMapLayer."""
        from qgis.core import QgsMapLayer, QgsProject

        if isinstance(layer_ref, QgsMapLayer):
            return layer_ref
        if isinstance(layer_ref, str) and layer_ref:
            return QgsProject.instance().mapLayer(layer_ref)
        return None
