"""State management module for SecInterp main dialog.

Handles both visual status (indicators, button enablement) and
persistence (saving/loading settings).
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from qgis.PyQt.QtWidgets import QDialogButtonBox

from sec_interp.logger_config import get_logger

from .main_dialog_config import DialogDefaults

if TYPE_CHECKING:
    from sec_interp.gui.main_dialog import SecInterpDialog

logger = get_logger(__name__)


class StateManager:
    """Manages the state of the dialog, including UI status and settings persistence."""

    def __init__(self, dialog: SecInterpDialog) -> None:
        """Initialize state manager.

        Args:
            dialog: The main dialog instance.

        """
        self.dialog = dialog
        self.config = None
        if hasattr(self.dialog, "plugin_instance") and self.dialog.plugin_instance:
            self.config = self.dialog.plugin_instance.controller.config_service

        # Icons for status indicators
        self._warning_icon = None
        self._success_icon = None

    # --- UI Status Management ---

    def setup_indicators(self) -> None:
        """Set up required field indicators with warning icons."""
        self._warning_icon = self.dialog.getThemeIcon("mMessageLogCritical.svg")
        self._success_icon = self._success_icon = self.dialog.getThemeIcon("mIconSuccess.svg")

        # Initial update
        self.update_raster_status()
        self.update_section_status()

    def update_all(self) -> None:
        """Update all UI status components."""
        self.update_button_state()
        self.update_preview_checkbox_states()
        self.update_raster_status()
        self.update_section_status()

    def update_preview_checkbox_states(self) -> None:
        """Enable or disable preview checkboxes based on input validity."""
        im = self.dialog.input_manager
        has_section = im.is_section_valid("section")
        has_dem = im.is_section_valid("dem")

        pw = self.dialog.preview_widget
        pw.chk_topo.setEnabled(has_dem and has_section)
        pw.chk_geol.setEnabled(im.is_section_valid("geology") and has_section)
        pw.chk_struct.setEnabled(im.is_section_valid("structure") and has_section)
        pw.chk_drillholes.setEnabled(im.is_section_valid("drillhole") and has_section)

    def update_button_state(self) -> None:
        """Enable or disable buttons based on input validity."""
        im = self.dialog.input_manager
        can_preview = im.can_preview()

        self.dialog.preview_widget.btn_preview.setEnabled(can_preview)
        self.dialog.button_box.button(QDialogButtonBox.Ok).setEnabled(can_preview)

        if hasattr(self.dialog, "btn_save"):
            self.dialog.btn_save.setEnabled(im.can_export())

    def update_raster_status(self) -> None:
        """Update raster layer status icon."""
        if not self._warning_icon:
            return
        im = self.dialog.input_manager
        label = self.dialog.page_dem.lbl_raster_status
        if im.is_section_valid("dem"):
            label.setPixmap(self._success_icon.pixmap(16, 16))
            label.setToolTip(self.dialog.tr("Raster layer selected"))
        else:
            label.setPixmap(self._warning_icon.pixmap(16, 16))
            label.setToolTip(im.get_section_error("dem"))

    def update_section_status(self) -> None:
        """Update section line status icon."""
        if not self._warning_icon:
            return
        im = self.dialog.input_manager
        label = self.dialog.page_section.lbl_section_status
        if im.is_section_valid("section"):
            label.setPixmap(self._success_icon.pixmap(16, 16))
            label.setToolTip(self.dialog.tr("Section line selected"))
        else:
            label.setPixmap(self._warning_icon.pixmap(16, 16))
            label.setToolTip(im.get_section_error("section"))

    # --- Settings Persistence ---

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
        self.update_all()
        logger.info("Settings loaded successfully from Project/Global config")

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

    def reset_to_defaults(self) -> None:
        """Reset all dialog inputs to their default values."""
        self._reset_pages()
        self._reset_preview()
        self._reset_tools()

        self.dialog.preview_widget.results_text.append(
            self.dialog.tr("✓ Form reset to default values")
        )
        logger.info("Dialog reset to defaults by user")

    # --- Private Load/Save/Reset logic (omitted for brevity in thinking, but will fully implement) ---
    def _load_section_settings(self) -> None:
        p_sect = self.dialog.page_section
        self._restore_layer(p_sect.line_combo, "section_layer")
        buffer_dist = self._get_setting("buffer_dist")
        if buffer_dist is not None:
            p_sect.buffer_spin.setValue(float(buffer_dist))

    def _load_dem_settings(self) -> None:
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
        p_geol = self.dialog.page_geology
        self._restore_layer(p_geol.layer_combo, "geol_layer")
        geol_layer = p_geol.layer_combo.currentLayer()
        if geol_layer:
            p_geol.field_combo.setLayer(geol_layer)
        self._restore_field(p_geol.field_combo, "geol_field")

    def _load_structure_settings(self) -> None:
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
        last_dir = self._get_setting("last_output_dir")
        if last_dir:
            self.dialog.output_widget.setFilePath(str(last_dir))

    def _load_interpretation_settings(self) -> None:
        p_interp = self.dialog.page_interpretation
        self._restore_check(p_interp.chk_inherit_geol, "interp_inherit_geol")
        self._restore_check(p_interp.chk_inherit_drill, "interp_inherit_drill")
        custom_fields_json = self._get_setting("interp_custom_fields")
        if custom_fields_json:
            try:
                fields = json.loads(custom_fields_json)
                p_interp.fields_table.setRowCount(0)
                for f in fields:
                    p_interp._add_field_row()
                    row = p_interp.fields_table.rowCount() - 1
                    p_interp.fields_table.item(row, 0).setText(f.get("name", ""))
                    p_interp.fields_table.cellWidget(row, 1).setCurrentText(f.get("type", "String"))
                    p_interp.fields_table.item(row, 2).setText(f.get("default", ""))
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"Failed to restore custom fields: {e}")

    def _load_preview_settings(self) -> None:
        pw = self.dialog.preview_widget
        for chk, key in [
            (pw.chk_topo, "show_topo"),
            (pw.chk_geol, "show_geol"),
            (pw.chk_struct, "show_struct"),
            (pw.chk_drillholes, "show_drillholes"),
            (pw.chk_interpretations, "show_interpretations"),
            (pw.chk_legend, "show_legend"),
            (pw.chk_auto_lod, "auto_lod"),
            (pw.chk_adaptive_sampling, "adaptive_sampling"),
        ]:
            self._restore_check(chk, key)
        max_points = self._get_setting("max_points")
        if max_points is not None:
            pw.spin_max_points.setValue(int(max_points))

    def _save_section_settings(self) -> None:
        self._save_layer(self.dialog.page_section.line_combo, "section_layer")
        self._set_setting("buffer_dist", self.dialog.page_section.buffer_spin.value())

    def _save_dem_settings(self) -> None:
        self._save_layer(self.dialog.page_dem.raster_combo, "dem_layer")
        self._set_setting("dem_band", self.dialog.page_dem.band_combo.currentBand())
        self._set_setting("scale", self.dialog.page_dem.scale_spin.value())
        self._set_setting("vert_exag", self.dialog.page_dem.vertexag_spin.value())

    def _save_geology_settings(self) -> None:
        self._save_layer(self.dialog.page_geology.layer_combo, "geol_layer")
        self._save_field(self.dialog.page_geology.field_combo, "geol_field")

    def _save_structure_settings(self) -> None:
        self._save_layer(self.dialog.page_struct.layer_combo, "struct_layer")
        self._save_field(self.dialog.page_struct.dip_combo, "struct_dip_field")
        self._save_field(self.dialog.page_struct.strike_combo, "struct_strike_field")
        self._set_setting("dip_scale_factor", self.dialog.page_struct.scale_spin.value())

    def _save_drillhole_settings(self) -> None:
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
        self._set_setting("last_output_dir", self.dialog.output_widget.filePath())

    def _save_interpretation_settings(self) -> None:
        p_interp = self.dialog.page_interpretation
        self._save_check(p_interp.chk_inherit_geol, "interp_inherit_geol")
        self._save_check(p_interp.chk_inherit_drill, "interp_inherit_drill")
        custom_fields = p_interp.get_data()["custom_fields"]
        self._set_setting("interp_custom_fields", json.dumps(custom_fields))

    def _save_preview_settings(self) -> None:
        pw = self.dialog.preview_widget
        for chk, key in [
            (pw.chk_topo, "show_topo"),
            (pw.chk_geol, "show_geol"),
            (pw.chk_struct, "show_struct"),
            (pw.chk_drillholes, "show_drillholes"),
            (pw.chk_interpretations, "show_interpretations"),
            (pw.chk_legend, "show_legend"),
            (pw.chk_auto_lod, "auto_lod"),
            (pw.chk_adaptive_sampling, "adaptive_sampling"),
        ]:
            self._save_check(chk, key)
        self._set_setting("max_points", pw.spin_max_points.value())

    def _reset_pages(self) -> None:
        self.dialog.page_section.line_combo.setLayer(None)
        self.dialog.page_section.buffer_spin.setValue(float(DialogDefaults.BUFFER_DISTANCE))
        self.dialog.page_dem.raster_combo.setLayer(None)
        self.dialog.page_dem.band_combo.setBand(DialogDefaults.DEFAULT_BAND)
        self.dialog.page_dem.scale_spin.setValue(float(DialogDefaults.SCALE))
        self.dialog.page_dem.vertexag_spin.setValue(float(DialogDefaults.VERTICAL_EXAGGERATION))
        self.dialog.page_geology.layer_combo.setLayer(None)
        self.dialog.page_geology.field_combo.setField("")
        self.dialog.page_struct.layer_combo.setLayer(None)
        self.dialog.page_struct.dip_combo.setField("")
        self.dialog.page_struct.strike_combo.setField("")
        self.dialog.page_struct.scale_spin.setValue(float(DialogDefaults.DIP_SCALE_FACTOR))
        dpage = self.dialog.page_drillhole
        for combo in [dpage.c_layer, dpage.s_layer, dpage.i_layer]:
            combo.setLayer(None)
        dpage.chk_use_geom.setChecked(True)
        self.dialog.output_widget.setFilePath("")
        self.dialog.page_interpretation.fields_table.setRowCount(0)
        self.dialog.page_interpretation.chk_inherit_geol.setChecked(True)
        self.dialog.page_interpretation.chk_inherit_drill.setChecked(True)

    def _reset_preview(self) -> None:
        pw = self.dialog.preview_widget
        for chk in [
            pw.chk_topo,
            pw.chk_geol,
            pw.chk_struct,
            pw.chk_drillholes,
            pw.chk_interpretations,
            pw.chk_legend,
            pw.chk_adaptive_sampling,
        ]:
            chk.setChecked(True)
        pw.chk_auto_lod.setChecked(False)
        pw.spin_max_points.setValue(1000)

    def _reset_tools(self) -> None:
        if hasattr(self.dialog, "tool_manager"):
            self.dialog.tool_manager.measure_tool.reset()
        if hasattr(self.dialog, "interpretations"):
            self.dialog.interpretations = []
            if hasattr(self.dialog, "_save_interpretations"):
                self.dialog._save_interpretations()

    # --- Persistence Helpers ---

    def _get_setting(self, key: str, default: Any = None) -> Any:
        val, ok = self.dialog.project.readEntry("SecInterp", key, "")
        if not ok or val in (None, "", "None", "NULL"):
            val, ok = self.dialog.project.readEntry("SecInterpUI", key, "")
        if ok and val not in (None, "", "None", "NULL"):
            parsed = self._parse_setting_value(val)
            if parsed is not None:
                return parsed
        if self.config:
            try:
                val = self.config.get(key, default)
                parsed = self._parse_setting_value(val)
                if parsed is not None:
                    return parsed
            except Exception:
                pass
        return default

    def _set_setting(self, key: str, value: Any) -> None:
        if value is None:
            value = ""
        self.dialog.project.writeEntry("SecInterp", key, str(value))
        if self.config:
            self.config.set(key, value)

    def _parse_setting_value(self, val: Any) -> Any:
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
        except (ValueError, TypeError):
            return val

    def _save_layer(self, combo, key: str) -> None:
        layer = combo.currentLayer()
        if layer:
            self._set_setting(key, layer.id())
            self._set_setting(f"{key}_name", layer.name())
        else:
            self._set_setting(key, "")
            self._set_setting(f"{key}_name", "")

    def _restore_layer(self, combo, key: str) -> None:
        layer_id = self._get_setting(key)
        layer_name = self._get_setting(f"{key}_name")
        if not layer_id and not layer_name:
            return
        layer = None
        if layer_id:
            layer = self.dialog.project.mapLayer(str(layer_id))
        if not layer and layer_name:
            for lyr in self.dialog.project.mapLayers().values():
                if lyr.name() == layer_name:
                    layer = lyr
                    break
        if layer:
            combo.blockSignals(True)
            combo.setLayer(layer)
            combo.blockSignals(False)

    def _save_field(self, combo, key: str) -> None:
        self._set_setting(key, combo.currentField())

    def _restore_field(self, combo, key: str) -> None:
        field = self._get_setting(key)
        if field:
            combo.setField(field)

    def _save_check(self, checkbox, key: str) -> None:
        self._set_setting(key, checkbox.isChecked())

    def _restore_check(self, checkbox, key: str) -> None:
        checked = self._get_setting(key)
        if checked is not None and checked != "":
            checkbox.setChecked(bool(checked))
