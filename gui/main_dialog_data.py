"""Data aggregation module for SecInterp main dialog.

This module handles aggregation of data from all dialog pages,
separating data collection logic from the main dialog class.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sec_interp.core.validation.project_validator import ValidationParams

if TYPE_CHECKING:
    pass


class DialogDataAggregator:
    """Aggregates data from all dialog pages.

    This class centralizes the logic for collecting and combining
    data from different pages into the flat dictionary format
    expected by the rest of the application.
    """

    def __init__(self, dialog: sec_interp.gui.main_dialog.SecInterpDialog):
        """Initialize data aggregator.

        Args:
            dialog: The :class:`sec_interp.gui.main_dialog.SecInterpDialog` instance

        """
        self.dialog = dialog

    def get_all_values(self) -> dict:
        """Get all values from pages as flat dictionary.

        Returns:
            Dictionary with all dialog values in legacy flat format

        """
        return {
            **self._get_dem_values(),
            **self._get_section_values(),
            **self._get_geology_values(),
            **self._get_structure_values(),
            **self._get_drillhole_values(),
            **self._get_settings_values(),
            "output_path": self.dialog.output_widget.filePath(),
        }

    def _get_dem_values(self) -> dict:
        """Get DEM page values.

        Returns:
            Dictionary with raster layer, band, scale, and vertical exaggeration

        """
        dem_data = self.dialog.page_dem.get_data()
        return {
            "raster_layer": dem_data["raster_layer"],
            "selected_band": dem_data["selected_band"],
            "scale": dem_data["scale"],
            "vertexag": dem_data["vertexag"],
        }

    def _get_section_values(self) -> dict:
        """Get section page values.

        Returns:
            Dictionary with cross-line layer and buffer distance

        """
        section_data = self.dialog.page_section.get_data()
        return {
            "crossline_layer": section_data["crossline_layer"],
            "buffer_distance": section_data["buffer_distance"],
        }

    def _get_geology_values(self) -> dict:
        """Get geology page values.

        Returns:
            Dictionary with outcrop layer and name field

        """
        geology_data = self.dialog.page_geology.get_data()
        return {
            "outcrop_layer": geology_data["outcrop_layer"],
            "outcrop_name_field": geology_data["outcrop_name_field"],
        }

    def _get_structure_values(self) -> dict:
        """Get structure page values.

        Returns:
            Dictionary with structural layer, dip/strike fields, and scale factor

        """
        structure_data = self.dialog.page_struct.get_data()
        return {
            "structural_layer": structure_data["structural_layer"],
            "dip_field": structure_data["dip_field"],
            "strike_field": structure_data["strike_field"],
            "dip_scale_factor": structure_data["dip_scale_factor"],
        }

    def _get_drillhole_values(self) -> dict:
        """Get drillhole page values.

        Returns:
            Dictionary with collar, survey, and interval layer data

        """
        drillhole_data = self.dialog.page_drillhole.get_data()

        # Map DrillholePage keys to Controller keys
        return {
            "collar_layer_obj": drillhole_data["collar_layer"],
            "collar_id_field": drillhole_data["collar_id"],
            "collar_use_geometry": drillhole_data["use_geometry"],
            "collar_x_field": drillhole_data["collar_x"],
            "collar_y_field": drillhole_data["collar_y"],
            "collar_z_field": drillhole_data["collar_z"],
            "collar_depth_field": drillhole_data["collar_depth"],
            "survey_layer_obj": drillhole_data["survey_layer"],
            "survey_id_field": drillhole_data["survey_id"],
            "survey_depth_field": drillhole_data["survey_depth"],
            "survey_azim_field": drillhole_data["survey_azim"],
            "survey_incl_field": drillhole_data["survey_incl"],
            "interval_layer_obj": drillhole_data["interval_layer"],
            "interval_id_field": drillhole_data["interval_id"],
            "interval_from_field": drillhole_data["interval_from"],
            "interval_to_field": drillhole_data["interval_to"],
            "interval_lith_field": drillhole_data["interval_lith"],
        }

    def _get_settings_values(self) -> dict:
        """Get settings page values.

        Returns:
            Dictionary with settings values

        """
        # Ensure we don't fail if page_settings is not fully initialized in tests
        if hasattr(self.dialog, "page_settings"):
            return self.dialog.page_settings.get_data()
        return {}

    def get_validation_params(self) -> ValidationParams:
        """Collect current dialog state into a ValidationParams object.

        Returns:
            ValidationParams populated with current UI selections.

        """
        dem = self.dialog.page_dem.get_data()
        sect = self.dialog.page_section.get_data()
        geol = self.dialog.page_geology.get_data()
        stru = self.dialog.page_struct.get_data()
        dh = self.dialog.page_drillhole.get_data()

        return ValidationParams(
            # Core
            raster_layer=dem["raster_layer"],
            band_number=dem["selected_band"],
            line_layer=sect["crossline_layer"],
            output_path=self.dialog.output_widget.filePath(),
            scale=dem["scale"],
            vert_exag=dem["vertexag"],
            buffer_dist=sect["buffer_distance"],
            # Geology
            outcrop_layer=geol["outcrop_layer"],
            outcrop_field=geol["outcrop_name_field"],
            # Structure
            struct_layer=stru["structural_layer"],
            struct_dip_field=stru["dip_field"],
            struct_strike_field=stru["strike_field"],
            dip_scale_factor=stru["dip_scale_factor"],
            # Drillhole
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
