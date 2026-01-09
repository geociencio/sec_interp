"""Settings management module for SecInterp main dialog.

This module handles persistence of user settings between sessions.
"""

from typing import TYPE_CHECKING, Any

from sec_interp.logger_config import get_logger

from .main_dialog_config import DialogDefaults

if TYPE_CHECKING:
    pass

logger = get_logger(__name__)


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
        self._load_section_settings()
        self._load_dem_settings()
        self._load_geology_settings()
        self._load_structure_settings()
        self._load_drillhole_settings()
        self._load_output_settings()
        self._load_interpretation_settings()
        self._load_preview_settings()

        # Update all status indicators after bulk restoration
        self.dialog.status_manager.update_all()
        logger.info("Settings loaded successfully from Project/Global config")

    def _load_section_settings(self) -> None:
        """Load settings for the Section page."""
        p_sect = self.dialog.page_section
        self._restore_layer(p_sect.line_combo, "section_layer")
        buffer_dist = self._get_setting("buffer_dist")
        if buffer_dist is not None:
            p_sect.buffer_spin.setValue(float(buffer_dist))

    def _load_dem_settings(self) -> None:
        """Load settings for the DEM page."""
        p_dem = self.dialog.page_dem
        self._restore_layer(p_dem.raster_combo, "dem_layer")

        raster_layer = p_dem.raster_combo.currentLayer()
        if raster_layer:
            p_dem.band_combo.setLayer(raster_layer)

        band_idx = self._get_setting("dem_band")
        if band_idx is not None:
            p_dem.band_combo.setBand(int(band_idx))

        scale = self._get_setting("scale")
        if scale is not None:
            p_dem.scale_spin.setValue(float(scale))

        vert_exag = self._get_setting("vert_exag")
        if vert_exag is not None:
            p_dem.vertexag_spin.setValue(float(vert_exag))

        if raster_layer:
            p_dem.scale_spin.blockSignals(True)
            p_dem._update_resolution()
            p_dem.scale_spin.blockSignals(False)
            if scale is not None:
                p_dem.scale_spin.setValue(float(scale))

    def _load_geology_settings(self) -> None:
        """Load settings for the Geology page."""
        p_geol = self.dialog.page_geology
        self._restore_layer(p_geol.layer_combo, "geol_layer")
        geol_layer = p_geol.layer_combo.currentLayer()
        if geol_layer:
            p_geol.field_combo.setLayer(geol_layer)
        self._restore_field(p_geol.field_combo, "geol_field")

    def _load_structure_settings(self) -> None:
        """Load settings for the Structure page."""
        p_struct = self.dialog.page_struct
        self._restore_layer(p_struct.layer_combo, "struct_layer")
        struct_layer = p_struct.layer_combo.currentLayer()
        if struct_layer:
            p_struct.dip_combo.setLayer(struct_layer)
            p_struct.strike_combo.setLayer(struct_layer)
        self._restore_field(p_struct.dip_combo, "struct_dip_field")
        self._restore_field(p_struct.strike_combo, "struct_strike_field")
        dip_scale = self._get_setting("dip_scale_factor")
        if dip_scale is not None:
            p_struct.scale_spin.setValue(float(dip_scale))

    def _load_drillhole_settings(self) -> None:
        """Load settings for the Drillhole page."""
        dpage = self.dialog.page_drillhole
        self._restore_layer(dpage.c_layer, "dh_collar_layer")
        c_layer = dpage.c_layer.currentLayer()
        if c_layer:
            for w in [dpage.c_id, dpage.c_x, dpage.c_y, dpage.c_z, dpage.c_depth]:
                w.setLayer(c_layer)

        self._restore_field(dpage.c_id, "dh_collar_id")
        self._restore_check(dpage.chk_use_geom, "dh_use_geom")
        self._restore_field(dpage.c_x, "dh_collar_x")
        self._restore_field(dpage.c_y, "dh_collar_y")
        self._restore_field(dpage.c_z, "dh_collar_z")
        self._restore_field(dpage.c_depth, "dh_collar_depth")

        self._restore_layer(dpage.s_layer, "dh_survey_layer")
        s_layer = dpage.s_layer.currentLayer()
        if s_layer:
            for w in [dpage.s_id, dpage.s_depth, dpage.s_azim, dpage.s_incl]:
                w.setLayer(s_layer)
        self._restore_field(dpage.s_id, "dh_survey_id")
        self._restore_field(dpage.s_depth, "dh_survey_depth")
        self._restore_field(dpage.s_azim, "dh_survey_azim")
        self._restore_field(dpage.s_incl, "dh_survey_incl")

        self._restore_layer(dpage.i_layer, "dh_interval_layer")
        i_layer = dpage.i_layer.currentLayer()
        if i_layer:
            for w in [dpage.i_id, dpage.i_from, dpage.i_to, dpage.i_lith]:
                w.setLayer(i_layer)
        self._restore_field(dpage.i_id, "dh_interval_id")
        self._restore_field(dpage.i_from, "dh_interval_from")
        self._restore_field(dpage.i_to, "dh_interval_to")
        self._restore_field(dpage.i_lith, "dh_interval_lith")

    def _load_output_settings(self) -> None:
        """Load settings for output path."""
        last_dir = self._get_setting("last_output_dir")
        if last_dir:
            self.dialog.output_widget.setFilePath(str(last_dir))

    def _load_interpretation_settings(self) -> None:
        """Load settings for the Interpretation page."""
        p_interp = self.dialog.page_interpretation
        self._restore_check(p_interp.chk_inherit_geol, "interp_inherit_geol")
        self._restore_check(p_interp.chk_inherit_drill, "interp_inherit_drill")
        custom_fields_json = self._get_setting("interp_custom_fields")
        if custom_fields_json:
            try:
                import json

                fields = json.loads(custom_fields_json)
                p_interp.fields_table.setRowCount(0)
                for f in fields:
                    p_interp._add_field_row()
                    row = p_interp.fields_table.rowCount() - 1
                    p_interp.fields_table.item(row, 0).setText(f.get("name", ""))
                    p_interp.fields_table.cellWidget(row, 1).setCurrentText(f.get("type", "String"))
                    p_interp.fields_table.item(row, 2).setText(f.get("default", ""))
            except Exception as e:
                logger.warning(f"Failed to restore custom fields: {e}")

    def _load_preview_settings(self) -> None:
        """Load settings for the preview widget."""
        pw = self.dialog.preview_widget
        self._restore_check(pw.chk_topo, "show_topo")
        self._restore_check(pw.chk_geol, "show_geol")
        self._restore_check(pw.chk_struct, "show_struct")
        self._restore_check(pw.chk_drillholes, "show_drillholes")
        self._restore_check(pw.chk_interpretations, "show_interpretations")
        self._restore_check(pw.chk_auto_lod, "auto_lod")
        self._restore_check(pw.chk_adaptive_sampling, "adaptive_sampling")
        max_points = self._get_setting("max_points")
        if max_points is not None:
            pw.spin_max_points.setValue(int(max_points))

    def save_settings(self) -> None:
        """Save user settings for next session."""
        if not self.config:
            return

        self._save_section_settings()
        self._save_dem_settings()
        self._save_geology_settings()
        self._save_structure_settings()
        self._save_drillhole_settings()
        self._save_output_settings()
        self._save_interpretation_settings()
        self._save_preview_settings()

    def _save_section_settings(self) -> None:
        """Save settings for the Section page."""
        self._save_layer(self.dialog.page_section.line_combo, "section_layer")
        self._set_setting("buffer_dist", self.dialog.page_section.buffer_spin.value())

    def _save_dem_settings(self) -> None:
        """Save settings for the DEM page."""
        self._save_layer(self.dialog.page_dem.raster_combo, "dem_layer")
        self._set_setting("dem_band", self.dialog.page_dem.band_combo.currentBand())
        self._set_setting("scale", self.dialog.page_dem.scale_spin.value())
        self._set_setting("vert_exag", self.dialog.page_dem.vertexag_spin.value())

    def _save_geology_settings(self) -> None:
        """Save settings for the Geology page."""
        self._save_layer(self.dialog.page_geology.layer_combo, "geol_layer")
        self._save_field(self.dialog.page_geology.field_combo, "geol_field")

    def _save_structure_settings(self) -> None:
        """Save settings for the Structure page."""
        self._save_layer(self.dialog.page_struct.layer_combo, "struct_layer")
        self._save_field(self.dialog.page_struct.dip_combo, "struct_dip_field")
        self._save_field(self.dialog.page_struct.strike_combo, "struct_strike_field")
        self._set_setting("dip_scale_factor", self.dialog.page_struct.scale_spin.value())

    def _save_drillhole_settings(self) -> None:
        """Save settings for the Drillhole page."""
        dpage = self.dialog.page_drillhole
        self._save_layer(dpage.c_layer, "dh_collar_layer")
        self._save_field(dpage.c_id, "dh_collar_id")
        self._save_check(dpage.chk_use_geom, "dh_use_geom")
        self._save_field(dpage.c_x, "dh_collar_x")
        self._save_field(dpage.c_y, "dh_collar_y")
        self._save_field(dpage.c_z, "dh_collar_z")
        self._save_field(dpage.c_depth, "dh_collar_depth")

        self._save_layer(dpage.s_layer, "dh_survey_layer")
        self._save_field(dpage.s_id, "dh_survey_id")
        self._save_field(dpage.s_depth, "dh_survey_depth")
        self._save_field(dpage.s_azim, "dh_survey_azim")
        self._save_field(dpage.s_incl, "dh_survey_incl")

        self._save_layer(dpage.i_layer, "dh_interval_layer")
        self._save_field(dpage.i_id, "dh_interval_id")
        self._save_field(dpage.i_from, "dh_interval_from")
        self._save_field(dpage.i_to, "dh_interval_to")
        self._save_field(dpage.i_lith, "dh_interval_lith")

    def _save_output_settings(self) -> None:
        """Save output path settings."""
        self._set_setting("last_output_dir", self.dialog.output_widget.filePath())

    def _save_interpretation_settings(self) -> None:
        """Save settings for the Interpretation page."""
        p_interp = self.dialog.page_interpretation
        self._save_check(p_interp.chk_inherit_geol, "interp_inherit_geol")
        self._save_check(p_interp.chk_inherit_drill, "interp_inherit_drill")

        import json

        custom_fields = p_interp.get_data()["custom_fields"]
        self._set_setting("interp_custom_fields", json.dumps(custom_fields))

    def _save_preview_settings(self) -> None:
        """Save settings for the preview widget."""
        pw = self.dialog.preview_widget
        self._save_check(pw.chk_topo, "show_topo")
        self._save_check(pw.chk_geol, "show_geol")
        self._save_check(pw.chk_struct, "show_struct")
        self._save_check(pw.chk_drillholes, "show_drillholes")
        self._save_check(pw.chk_interpretations, "show_interpretations")
        self._save_check(pw.chk_auto_lod, "auto_lod")
        self._save_check(pw.chk_adaptive_sampling, "adaptive_sampling")
        self._set_setting("max_points", pw.spin_max_points.value())

    def reset_to_defaults(self) -> None:
        """Reset all dialog inputs to their default values."""
        # --- Section Page ---
        self.dialog.page_section.line_combo.setLayer(None)
        self.dialog.page_section.buffer_spin.setValue(float(DialogDefaults.BUFFER_DISTANCE))

        # --- DEM Page ---
        self.dialog.page_dem.raster_combo.setLayer(None)
        self.dialog.page_dem.band_combo.setBand(DialogDefaults.DEFAULT_BAND)
        self.dialog.page_dem.scale_spin.setValue(float(DialogDefaults.SCALE))
        self.dialog.page_dem.vertexag_spin.setValue(float(DialogDefaults.VERTICAL_EXAGGERATION))

        # --- Geology Page ---
        self.dialog.page_geology.layer_combo.setLayer(None)
        self.dialog.page_geology.field_combo.setField("")

        # --- Structure Page ---
        self.dialog.page_struct.layer_combo.setLayer(None)
        self.dialog.page_struct.dip_combo.setField("")
        self.dialog.page_struct.strike_combo.setField("")
        self.dialog.page_struct.scale_spin.setValue(float(DialogDefaults.DIP_SCALE_FACTOR))

        # --- Drillhole Page ---
        dpage = self.dialog.page_drillhole
        dpage.c_layer.setLayer(None)
        dpage.c_id.setField("")
        dpage.chk_use_geom.setChecked(True)
        dpage.c_x.setField("")
        dpage.c_y.setField("")
        dpage.c_z.setField("")
        dpage.c_depth.setField("")

        dpage.s_layer.setLayer(None)
        dpage.s_id.setField("")
        dpage.s_depth.setField("")
        dpage.s_azim.setField("")
        dpage.s_incl.setField("")

        dpage.i_layer.setLayer(None)
        dpage.i_id.setField("")
        dpage.i_from.setField("")
        dpage.i_to.setField("")
        dpage.i_lith.setField("")

        # Output folder
        self.dialog.output_widget.setFilePath("")

        # --- Interpretation Page ---
        self.dialog.page_interpretation.fields_table.setRowCount(0)
        self.dialog.page_interpretation.chk_inherit_geol.setChecked(True)
        self.dialog.page_interpretation.chk_inherit_drill.setChecked(True)

        # --- Preview Widget ---
        pw = self.dialog.preview_widget
        pw.chk_topo.setChecked(True)
        pw.chk_geol.setChecked(True)
        pw.chk_struct.setChecked(True)
        pw.chk_drillholes.setChecked(True)
        pw.chk_interpretations.setChecked(True)
        pw.chk_auto_lod.setChecked(False)
        pw.chk_adaptive_sampling.setChecked(True)
        pw.spin_max_points.setValue(1000)

    # --- Helper Methods ---
    def _parse_setting_value(self, val: Any) -> Any:
        """Parse string values back to appropriate Python types."""
        if val in (None, "", "None", "NULL"):
            return None

        val_str = str(val).lower()
        if val_str == "true":
            return True
        if val_str == "false":
            return False

        try:
            if "." in str(val):
                return float(val)
            return int(val)
        except ValueError:
            return val

    def _get_setting(self, key: str, default: Any = None) -> Any:
        """Get setting from Project (multiple scopes) first, then Global config."""
        # 1. Try Project (New Scope)
        val, ok = self.dialog.project.readEntry("SecInterp", key, "")
        if not ok or val in (None, "", "None", "NULL"):
            # 1b. Try Project (Legacy Scope)
            val, ok = self.dialog.project.readEntry("SecInterpUI", key, "")

        if ok and val not in (None, "", "None", "NULL"):
            parsed = self._parse_setting_value(val)
            if parsed is not None:
                logger.debug(f"Project setting hit: {key} = {parsed}")
                return parsed

        # 2. Try Global fallback
        if self.config:
            val = self.config.get(key, default)
            parsed = self._parse_setting_value(val)
            if parsed is not None:
                logger.debug(f"Global setting fallback: {key} = {parsed}")
                return parsed

        return default

    def _set_setting(self, key: str, value: Any) -> None:
        """Set setting in both Project and Global config."""
        if value is None:
            value = ""

        # 1. Save to Project
        self.dialog.project.writeEntry("SecInterp", key, str(value))
        logger.debug(f"Setting saved to project: {key} = {value}")

        # 2. Save to Global
        if self.config:
            self.config.set(key, value)

    def _save_layer(self, combo, key: str) -> None:
        """Save selected layer ID and Name."""
        layer = combo.currentLayer()
        if layer:
            self._set_setting(key, layer.id())
            self._set_setting(f"{key}_name", layer.name())
        else:
            self._set_setting(key, "")
            self._set_setting(f"{key}_name", "")

    def _restore_layer(self, combo, key: str) -> None:
        """Restore layer selection by ID or Name fallback."""
        layer_id = self._get_setting(key)
        layer_name = self._get_setting(f"{key}_name")

        if not layer_id and not layer_name:
            return

        layer = None
        # 1. Try by ID (most accurate for current project)
        if layer_id:
            layer = self.dialog.project.mapLayer(str(layer_id))

        # 2. Try by Name (fallback for cross-project or reloads)
        if not layer and layer_name:
            for lyr in self.dialog.project.mapLayers().values():
                if lyr.name() == layer_name:
                    layer = lyr
                    break

        if layer:
            logger.debug(f"Restoring layer: {key} -> {layer.name()}")
            # Block signals to prevent cascade overwrites (e.g. scale suggestion)
            combo.blockSignals(True)
            combo.setLayer(layer)
            combo.blockSignals(False)
        else:
            logger.debug(f"Failed to restore layer for {key}")

    def _save_field(self, combo, key: str) -> None:
        """Save selected field name."""
        self._set_setting(key, combo.currentField())

    def _restore_field(self, combo, key: str) -> None:
        """Restore field selection."""
        field = self._get_setting(key)
        if field:
            combo.setField(field)

    def _save_check(self, checkbox, key: str) -> None:
        """Save checkbox state."""
        self._set_setting(key, checkbox.isChecked())

    def _restore_check(self, checkbox, key: str) -> None:
        """Restore checkbox state."""
        checked = self._get_setting(key)
        if checked is not None and checked != "":
            checkbox.setChecked(bool(checked))
