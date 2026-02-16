"""Input management module for SecInterp main dialog.

Handles data aggregation and validation for the dialog UI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sec_interp.core.exceptions import ValidationError
from sec_interp.core.validation.project_validator import (
    ProjectValidator,
    ValidationParams,
)

if TYPE_CHECKING:
    from sec_interp.gui.main_dialog import SecInterpDialog


class DialogInputManager:
    """Manages dialog inputs, including data collection and validation."""

    def __init__(self, dialog: SecInterpDialog) -> None:
        """Initialize input manager.

        Args:
            dialog: The main dialog instance.

        """
        self.dialog = dialog
        self._setup_validation_rules()

    def _setup_validation_rules(self) -> None:
        """Define UI-level validation rules."""
        self.rules = {
            "dem": {
                "check": lambda p: bool(p.raster_layer),
                "message": self.dialog.tr("Raster DEM layer is required"),
            },
            "section": {
                "check": lambda p: bool(p.line_layer),
                "message": self.dialog.tr("Cross-section line layer is required"),
            },
            "output": {
                "check": lambda p: bool(p.output_path),
                "message": self.dialog.tr("Output directory path is required"),
            },
            "geology": {
                "check": lambda p: (
                    ProjectValidator.is_geology_complete(p) if p.outcrop_layer else True
                ),
                "message": self.dialog.tr("Geology configuration is incomplete"),
            },
            "structure": {
                "check": lambda p: (
                    ProjectValidator.is_structure_complete(p)
                    if p.struct_layer
                    else True
                ),
                "message": self.dialog.tr("Structure configuration is incomplete"),
            },
            "drillhole": {
                "check": lambda p: (
                    ProjectValidator.is_drillhole_complete(p)
                    if p.collar_layer
                    else True
                ),
                "message": self.dialog.tr("Drillhole configuration is incomplete"),
            },
        }

    # --- Data Collection ---

    def get_all_values(self) -> dict[str, Any]:
        """Get all UI values as a flat dictionary."""
        dem = self.dialog.page_dem.get_data()
        sect = self.dialog.page_section.get_data()
        geol = self.dialog.page_geology.get_data()
        stru = self.dialog.page_struct.get_data()
        dh = self.dialog.page_drillhole.get_data()

        return {
            "raster_layer": dem["raster_layer"],
            "selected_band": dem["selected_band"],
            "scale": dem["scale"],
            "vertexag": dem["vertexag"],
            "crossline_layer": sect["crossline_layer"],
            "buffer_distance": sect["buffer_distance"],
            "outcrop_layer": geol["outcrop_layer"],
            "outcrop_name_field": geol["outcrop_name_field"],
            "structural_layer": stru["structural_layer"],
            "dip_field": stru["dip_field"],
            "strike_field": stru["strike_field"],
            "dip_scale_factor": stru["dip_scale_factor"],
            "collar_layer_obj": dh["collar_layer"],
            "collar_id_field": dh["collar_id"],
            "collar_use_geometry": dh["use_geometry"],
            "collar_x_field": dh["collar_x"],
            "collar_y_field": dh["collar_y"],
            "collar_z_field": dh["collar_z"],
            "collar_depth_field": dh["collar_depth"],
            "survey_layer_obj": dh["survey_layer"],
            "survey_id_field": dh["survey_id"],
            "survey_depth_field": dh["survey_depth"],
            "survey_azim_field": dh["survey_azim"],
            "survey_incl_field": dh["survey_incl"],
            "interval_layer_obj": dh["interval_layer"],
            "interval_id_field": dh["interval_id"],
            "interval_from_field": dh["interval_from"],
            "interval_to_field": dh["interval_to"],
            "interval_lith_field": dh["interval_lith"],
            "output_path": self.dialog.output_widget.filePath(),
            **(
                self.dialog.page_settings.get_data()
                if hasattr(self.dialog, "page_settings")
                else {}
            ),
        }

    def get_validation_params(self) -> ValidationParams:
        """Collect current UI state into ValidationParams."""
        dem = self.dialog.page_dem.get_data()
        sect = self.dialog.page_section.get_data()
        geol = self.dialog.page_geology.get_data()
        stru = self.dialog.page_struct.get_data()
        dh = self.dialog.page_drillhole.get_data()

        return ValidationParams(
            raster_layer=dem["raster_layer"],
            band_number=dem["selected_band"],
            line_layer=sect["crossline_layer"],
            output_path=self.dialog.output_widget.filePath(),
            scale=dem["scale"],
            vert_exag=dem["vertexag"],
            buffer_dist=sect["buffer_distance"],
            outcrop_layer=geol["outcrop_layer"],
            outcrop_field=geol["outcrop_name_field"],
            struct_layer=stru["structural_layer"],
            struct_dip_field=stru["dip_field"],
            struct_strike_field=stru["strike_field"],
            dip_scale_factor=stru["dip_scale_factor"],
            collar_layer=dh["collar_layer"],
            collar_id=dh["collar_id"],
            collar_use_geom=dh["use_geometry"],
            collar_x=dh["collar_x"],
            collar_y=dh["collar_y"],
            survey_layer=dh["survey_layer"],
            survey_id=dh["survey_id"],
            survey_depth=dh["survey_depth"],
            survey_azim=dh["survey_azim"],
            survey_incl=dh["survey_incl"],
            interval_layer=dh["interval_layer"],
            interval_id=dh["interval_id"],
            interval_from=dh["interval_from"],
            interval_to=dh["interval_to"],
            interval_lith=dh["interval_lith"],
        )

    # --- Validation ---

    def validate_inputs(self) -> tuple[bool, str]:
        """Validate all inputs via core ProjectValidator."""
        params = self.get_validation_params()
        try:
            ProjectValidator.validate_all(params)
            return True, ""
        except ValidationError as e:
            return False, str(e)

    def validate_preview_requirements(self) -> tuple[bool, str]:
        """Validate minimum requirements for preview."""
        params = self.get_validation_params()
        try:
            ProjectValidator.validate_preview_requirements(params)
            return True, ""
        except ValidationError as e:
            return False, str(e)

    def is_section_valid(self, section: str) -> bool:
        """Check if a section is valid."""
        if section not in self.rules:
            return True
        params = self.get_validation_params()
        return self.rules[section]["check"](params)

    def get_section_error(self, section: str) -> str:
        """Get error message for a section."""
        if self.is_section_valid(section):
            return ""
        return self.rules[section]["message"]

    def can_preview(self) -> bool:
        """Check if basic preview requirements are met."""
        return self.is_section_valid("dem") and self.is_section_valid("section")

    def can_export(self) -> bool:
        """Check if export requirements are met."""
        return self.can_preview() and self.is_section_valid("output")
