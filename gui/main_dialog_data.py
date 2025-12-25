"""Data aggregation module for SecInterp main dialog.

This module handles aggregation of data from all dialog pages,
separating data collection logic from the main dialog class.
"""

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .main_dialog import SecInterpDialog


class DialogDataAggregator:
    """Aggregates data from all dialog pages.

    This class centralizes the logic for collecting and combining
    data from different pages into the flat dictionary format
    expected by the rest of the application.
    """

    def __init__(self, dialog: "sec_interp.gui.main_dialog.SecInterpDialog"):
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
