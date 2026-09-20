"""Delegation/proxy mixin for the SecInterp main dialog."""

from __future__ import annotations

from typing import Any

from qgis.core import Qgis

from sec_interp.core.domain import InterpretationPolygon
from sec_interp.gui.main_dialog_utils import DialogEntityManager
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class DialogFacadeMixin:
    """Thin proxies that delegate to the dialog's specialized managers."""

    def toggle_measure_tool(self, checked: bool) -> None:
        """Toggle measurement tool via tool_manager."""
        self.tool_manager.toggle_measure_tool(checked)

    def update_measurement_display(self, metrics: dict[str, Any]) -> None:
        """Display measurement results from multi-point tool via tool_manager."""
        self.tool_manager.update_measurement_display(metrics)

    def toggle_interpretation_tool(self, checked: bool) -> None:
        """Toggle interpretation tool via tool_manager."""
        self.tool_manager.toggle_interpretation_tool(checked)

    def on_interpretation_finished(self, interpretation: InterpretationPolygon) -> None:
        """Handle finalized interpretation polygon."""
        self.interpretation_manager.handle_interpretation_finished(interpretation)

    @property
    def interpretations(self) -> list[InterpretationPolygon]:
        """Proxy to interpretations in the manager for backward compatibility."""
        return self.interpretation_manager.interpretations

    @interpretations.setter
    def interpretations(self, value: list[InterpretationPolygon]) -> None:
        """Set interpretations in the manager."""
        self.interpretation_manager.interpretations = value

    def update_preview_checkbox_states(self) -> None:
        """Enable or disable preview checkboxes via state_manager."""
        self.state_manager.update_preview_checkbox_states()

    def update_button_state(self) -> None:
        """Enable or disable buttons via state_manager."""
        self.state_manager.update_button_state()

    def get_selected_values(self) -> dict[str, Any]:
        """Get the selected values from the dialog.

        Returns:
            Dictionary with all dialog values in legacy flat format

        """
        return self.input_manager.get_all_values()

    def get_preview_options(self) -> dict[str, Any]:
        """Return the state of preview layer checkboxes.

        Returns:
            dict: Keys 'show_topo', 'show_geol', 'show_struct' with boolean values.

        """
        return {
            "show_topo": bool(self.preview_widget.chk_topo.isChecked()),
            "show_geol": bool(self.preview_widget.chk_geol.isChecked()),
            "show_struct": bool(self.preview_widget.chk_struct.isChecked()),
            "show_drillholes": bool(self.preview_widget.chk_drillholes.isChecked()),
            "show_interpretations": bool(self.preview_widget.chk_interpretations.isChecked()),
            "show_legend": bool(self.preview_widget.chk_legend.isChecked()),
            "max_points": self.preview_widget.spin_max_points.value(),
            "auto_lod": self.preview_widget.chk_auto_lod.isChecked(),
            "use_adaptive_sampling": bool(self.preview_widget.chk_adaptive_sampling.isChecked()),
        }

    def update_preview_from_checkboxes(self) -> None:
        """Update preview when checkboxes change via PreviewManager."""
        self.preview_manager.update_from_checkboxes()

    def preview_profile_handler(self) -> None:
        """Generate a quick preview and auto-save settings on success."""
        success, message = self.preview_manager.generate_preview()
        if success:
            self.state_manager.save_settings()

        if not success and message:
            self.push_message(self.tr("Preview Error"), message, level=Qgis.MessageLevel.Warning)

    def export_preview(self) -> None:
        """Export the current preview to a file using ExportManager."""
        self.export_manager.export_preview()

    def accept_handler(self) -> None:
        """Handle the accept button click event."""
        self.state_manager.save_settings()

        if self.iface is None:
            self.accept()
            return

        if not self.validate_inputs():
            return

        self.interpretation_manager.save_interpretations()
        self.accept()

    def reject_handler(self) -> None:
        """Handle the reject button click event."""
        self._save_on_close = False
        self.close()

    def clear_cache_handler(self) -> None:
        """Clear cached data and notify user."""
        if hasattr(self, "plugin_instance") and self.plugin_instance:
            self.plugin_instance.controller.data_cache.clear()
            if hasattr(self, "tool_manager"):
                self.tool_manager.measure_tool.reset()
            self.preview_widget.results_text.append(
                self.tr("✓ Cache cleared - next preview will re-process data")
            )
            logger.info("Cache cleared by user")
        else:
            self.preview_widget.results_text.append(self.tr("⚠ Cache not available"))

    def reset_defaults_handler(self) -> None:
        """Reset all dialog inputs via state_manager."""
        self.state_manager.reset_to_defaults()

    def _populate_field_combobox(self, source_combobox: Any, target_combobox: Any) -> None:
        """Populate a combobox with field names."""
        DialogEntityManager.populate_field_combobox(source_combobox, target_combobox)

    def get_layer_names_by_type(self, layer_type) -> list[str]:
        """Get layer names by type."""
        return DialogEntityManager.get_layer_names_by_type(layer_type)

    def get_layer_names_by_geometry(self, geometry_type) -> list[str]:
        """Get layer names by geometry."""
        return DialogEntityManager.get_layer_names_by_geometry(geometry_type)

    def getThemeIcon(self, name: str) -> Any:
        """Get a theme icon via DialogEntityManager."""
        return DialogEntityManager.get_theme_icon(name)

    def _load_interpretations(self) -> None:
        """Load interpretations via interpretation_manager."""
        self.interpretation_manager.load_interpretations()

    def _save_interpretations(self) -> None:
        """Save interpretations via interpretation_manager."""
        self.interpretation_manager.save_interpretations()

    def _load_user_settings(self) -> None:
        """Load user settings via state_manager."""
        self.state_manager.load_settings()

    def _save_user_settings(self) -> None:
        """Save user settings via state_manager."""
        self.state_manager.save_settings()
