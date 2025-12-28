"""Settings management module for SecInterp main dialog.

This module handles persistence of user settings between sessions.
"""

from typing import TYPE_CHECKING

from qgis.core import QgsSettings


if TYPE_CHECKING:
    from .main_dialog import SecInterpDialog


class DialogSettingsManager:
    """Manages persistence of dialog settings."""

    def __init__(self, dialog: "sec_interp.gui.main_dialog.SecInterpDialog"):
        """Initialize settings manager with reference to parent dialog.

        Args:
            dialog: The :class:`sec_interp.gui.main_dialog.SecInterpDialog` instance
        """
        self.dialog = dialog
        # Access config service through the plugin instance controller
        # Safety check for tests where plugin_instance might be mock or None
        self.config = None
        if hasattr(self.dialog, "plugin_instance") and self.dialog.plugin_instance:
            self.config = self.dialog.plugin_instance.controller.config_service

    def load_settings(self) -> None:
        """Load user settings from previous session."""
        if not self.config:
            return

        # --- Section Page ---
        self._restore_layer(self.dialog.page_section.line_combo, "section_layer")
        buffer_dist = self.config.get("buffer_dist")
        if buffer_dist is not None:
            self.dialog.page_section.buffer_spin.setValue(float(buffer_dist))

        # --- DEM Page ---
        self._restore_layer(self.dialog.page_dem.raster_combo, "dem_layer")
        # Band is trickier as it depends on layer load, try direct index for now
        band_idx = int(self.config.get("dem_band", 1))
        # Note: band combo might need reset if layer changes asynchronously
        self.dialog.page_dem.band_combo.setBand(band_idx)

        scale = self.config.get("scale")
        if scale is not None:
            self.dialog.page_dem.scale_spin.setValue(float(scale))

        vert_exag = self.config.get("vert_exag")
        if vert_exag is not None:
            self.dialog.page_dem.vertexag_spin.setValue(float(vert_exag))

        # --- Geology Page ---
        self._restore_layer(self.dialog.page_geology.layer_combo, "geol_layer")
        self._restore_field(self.dialog.page_geology.field_combo, "geol_field")

        # --- Structure Page ---
        self._restore_layer(self.dialog.page_struct.layer_combo, "struct_layer")
        self._restore_field(self.dialog.page_struct.dip_combo, "struct_dip_field")
        self._restore_field(self.dialog.page_struct.strike_combo, "struct_strike_field")

        dip_scale = self.config.get("dip_scale_factor")
        if dip_scale is not None:
            self.dialog.page_struct.scale_spin.setValue(float(dip_scale))

        # --- Drillhole Page ---
        dpage = self.dialog.page_drillhole
        # Collar
        self._restore_layer(dpage.c_layer, "dh_collar_layer")
        self._restore_field(dpage.c_id, "dh_collar_id")
        self._restore_check(dpage.chk_use_geom, "dh_use_geom")
        self._restore_field(dpage.c_x, "dh_collar_x")
        self._restore_field(dpage.c_y, "dh_collar_y")
        self._restore_field(dpage.c_z, "dh_collar_z")
        self._restore_field(dpage.c_depth, "dh_collar_depth")

        # Survey
        self._restore_layer(dpage.s_layer, "dh_survey_layer")
        self._restore_field(dpage.s_id, "dh_survey_id")
        self._restore_field(dpage.s_depth, "dh_survey_depth")
        self._restore_field(dpage.s_azim, "dh_survey_azim")
        self._restore_field(dpage.s_incl, "dh_survey_incl")

        # Interval
        self._restore_layer(dpage.i_layer, "dh_interval_layer")
        self._restore_field(dpage.i_id, "dh_interval_id")
        self._restore_field(dpage.i_from, "dh_interval_from")
        self._restore_field(dpage.i_to, "dh_interval_to")
        self._restore_field(dpage.i_lith, "dh_interval_lith")

        # Output folder
        last_dir = self.config.get("last_output_dir")
        if last_dir:
            self.dialog.output_widget.setFilePath(last_dir)

    def save_settings(self) -> None:
        """Save user settings for next session."""
        if not self.config:
            return

        # --- Section Page ---
        self._save_layer(self.dialog.page_section.line_combo, "section_layer")
        self.config.set("buffer_dist", self.dialog.page_section.buffer_spin.value())

        # --- DEM Page ---
        self._save_layer(self.dialog.page_dem.raster_combo, "dem_layer")
        self.config.set("dem_band", self.dialog.page_dem.band_combo.currentBand())
        self.config.set("scale", self.dialog.page_dem.scale_spin.value())
        self.config.set("vert_exag", self.dialog.page_dem.vertexag_spin.value())

        # --- Geology Page ---
        self._save_layer(self.dialog.page_geology.layer_combo, "geol_layer")
        self._save_field(self.dialog.page_geology.field_combo, "geol_field")

        # --- Structure Page ---
        self._save_layer(self.dialog.page_struct.layer_combo, "struct_layer")
        self._save_field(self.dialog.page_struct.dip_combo, "struct_dip_field")
        self._save_field(self.dialog.page_struct.strike_combo, "struct_strike_field")
        self.config.set("dip_scale_factor", self.dialog.page_struct.scale_spin.value())

        # --- Drillhole Page ---
        dpage = self.dialog.page_drillhole
        # Collar
        self._save_layer(dpage.c_layer, "dh_collar_layer")
        self._save_field(dpage.c_id, "dh_collar_id")
        self._save_check(dpage.chk_use_geom, "dh_use_geom")
        self._save_field(dpage.c_x, "dh_collar_x")
        self._save_field(dpage.c_y, "dh_collar_y")
        self._save_field(dpage.c_z, "dh_collar_z")
        self._save_field(dpage.c_depth, "dh_collar_depth")

        # Survey
        self._save_layer(dpage.s_layer, "dh_survey_layer")
        self._save_field(dpage.s_id, "dh_survey_id")
        self._save_field(dpage.s_depth, "dh_survey_depth")
        self._save_field(dpage.s_azim, "dh_survey_azim")
        self._save_field(dpage.s_incl, "dh_survey_incl")

        # Interval
        self._save_layer(dpage.i_layer, "dh_interval_layer")
        self._save_field(dpage.i_id, "dh_interval_id")
        self._save_field(dpage.i_from, "dh_interval_from")
        self._save_field(dpage.i_to, "dh_interval_to")
        self._save_field(dpage.i_lith, "dh_interval_lith")

        # Output folder
        self.config.set("last_output_dir", self.dialog.output_widget.filePath())

    # --- Helper Methods ---

    def _save_layer(self, combo, key: str) -> None:
        """Save selected layer ID."""
        layer = combo.currentLayer()
        if layer:
            self.config.set(key, layer.id())
        else:
            self.config.set(key, "")

    def _restore_layer(self, combo, key: str) -> None:
        """Restore layer selection by ID."""
        layer_id = self.config.get(key)
        if layer_id:
            combo.setLayer(self.dialog.project.mapLayer(layer_id))

    def _save_field(self, combo, key: str) -> None:
        """Save selected field name."""
        self.config.set(key, combo.currentField())

    def _restore_field(self, combo, key: str) -> None:
        """Restore field selection."""
        field = self.config.get(key)
        if field:
            combo.setField(field)

    def _save_check(self, checkbox, key: str) -> None:
        """Save checkbox state."""
        self.config.set(key, checkbox.isChecked())

    def _restore_check(self, checkbox, key: str) -> None:
        """Restore checkbox state."""
        checked = self.config.get(key)
        if checked is not None:
            checkbox.setChecked(bool(checked))
