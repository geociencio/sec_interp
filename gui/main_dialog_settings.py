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

        # Section parameters
        self.dialog.page_dem.scale_spin.setValue(self.config.get("scale"))
        self.dialog.page_dem.vertexag_spin.setValue(self.config.get("vert_exag"))
        self.dialog.page_section.buffer_spin.setValue(self.config.get("buffer_dist"))
        self.dialog.page_struct.scale_spin.setValue(self.config.get("dip_scale_factor"))

        # Output folder
        last_dir = self.config.get("last_output_dir")
        if last_dir:
            self.dialog.output_widget.setFilePath(last_dir)

    def save_settings(self) -> None:
        """Save user settings for next session."""
        if not self.config:
            return

        self.config.set("scale", self.dialog.page_dem.scale_spin.value())
        self.config.set("vert_exag", self.dialog.page_dem.vertexag_spin.value())
        self.config.set("buffer_dist", self.dialog.page_section.buffer_spin.value())
        self.config.set("dip_scale_factor", self.dialog.page_struct.scale_spin.value())
        self.config.set("last_output_dir", self.dialog.output_widget.filePath())
