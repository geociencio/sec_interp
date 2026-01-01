"""Settings page for Sec Interp plugin."""

from qgis.core import QgsSettings
from qgis.PyQt.QtWidgets import QCheckBox, QVBoxLayout, QLabel

from .base_page import BasePage


class SettingsPage(BasePage):
    """Page for managing plugin settings and restricted features."""

    def __init__(self, parent=None):
        """Initialize the settings page."""
        super().__init__(self.tr("Plugin Settings"), parent)
        self.settings = QgsSettings()

    def _setup_ui(self):
        """Set up the UI for settings."""
        super()._setup_ui()

        # Group box layout was defined as None in BasePage, we need to initialize it
        v_layout = QVBoxLayout()
        self.group_box.setLayout(v_layout)

        # Restricted Features Section
        v_layout.addWidget(QLabel("<b>Restricted Features (Pro/Premium)</b>"))

        self.chk_enable_3d = QCheckBox(self.tr("Enable 3D Interpretation Export"))
        self.chk_enable_3d.setToolTip(
            self.tr("Enables the generation of 3D Shapefiles (.shp) during export.")
        )

        # Load current state from QgsSettings
        enabled_3d = self.settings.value("sec_interp/enable_3d", False, type=bool)
        self.chk_enable_3d.setChecked(enabled_3d)

        # Connect signal to save automatically or we can handle it in a save method
        self.chk_enable_3d.stateChanged.connect(self._on_settings_changed)

        v_layout.addWidget(self.chk_enable_3d)

        # General Info
        v_layout.addSpacing(20)
        v_layout.addWidget(QLabel("<b>Plugin Information</b>"))
        v_layout.addWidget(QLabel(self.tr("Sec Interp v2.4.0")))
        v_layout.addWidget(QLabel(self.tr("Developed by Juan M Bernales")))

    def _on_settings_changed(self):
        """Save settings when they are changed."""
        self.settings.setValue("sec_interp/enable_3d", self.chk_enable_3d.isChecked())

    def get_data(self) -> dict:
        """Get the current settings.

        Returns:
            dict: Current settings.

        """
        return {
            "enable_3d": self.chk_enable_3d.isChecked(),
        }

    def validate(self) -> tuple[bool, str]:
        """Validate settings.

        Returns:
            tuple[bool, str]: (is_valid, error_message)

        """
        return True, ""
