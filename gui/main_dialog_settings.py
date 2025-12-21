"""Settings management module for SecInterp main dialog.

This module handles persistence of user settings between sessions.
"""

from typing import TYPE_CHECKING
from qgis.core import QgsSettings

if TYPE_CHECKING:
    from .main_dialog import SecInterpDialog

class DialogSettingsManager:
    """Manages persistence of dialog settings."""

    def __init__(self, dialog: "SecInterpDialog"):
        """Initialize settings manager with reference to parent dialog."""
        self.dialog = dialog
        self.settings = QgsSettings()

    def load_settings(self) -> None:
        """Load user settings from previous session."""
        # Section parameters
        self.dialog.page_dem.scale_spin.setValue(
            self.settings.value("/SecInterp/scale", 500.0, type=float)
        )
        self.dialog.page_dem.vertexag_spin.setValue(
            self.settings.value("/SecInterp/vert_exag", 1.0, type=float)
        )
        self.dialog.page_section.buffer_spin.setValue(
            self.settings.value("/SecInterp/buffer_dist", 100.0, type=float)
        )
        self.dialog.page_struct.scale_spin.setValue(
            self.settings.value("/SecInterp/dip_scale_factor", 1.0, type=float)
        )

        # Output folder
        last_dir = self.settings.value("/SecInterp/last_output_dir", "")
        if last_dir:
            self.dialog.output_widget.setFilePath(last_dir)

        # Field selections from last session (optional, can be complex due to layer changes)
        # For now we focus on numeric scalars and paths

    def save_settings(self) -> None:
        """Save user settings for next session."""
        self.settings.setValue("/SecInterp/scale", self.dialog.page_dem.scale_spin.value())
        self.settings.setValue(
            "/SecInterp/vert_exag", self.dialog.page_dem.vertexag_spin.value()
        )
        self.settings.setValue(
            "/SecInterp/buffer_dist", self.dialog.page_section.buffer_spin.value()
        )
        self.settings.setValue(
            "/SecInterp/dip_scale_factor", self.dialog.page_struct.scale_spin.value()
        )
        self.settings.setValue(
            "/SecInterp/last_output_dir", self.dialog.output_widget.filePath()
        )
