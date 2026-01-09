"""Settings page for Sec Interp plugin."""

from qgis.core import QgsSettings
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QLabel,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .base_page import BasePage


class SettingsPage(BasePage):
    """Page for managing plugin settings and restricted features."""

    def __init__(self, parent=None):
        """Initialize the settings page."""
        self.settings = QgsSettings()
        # Ensure we have all necessary widgets
        self.tab_widget = None
        self.chk_enable_3d = None
        super().__init__(QCoreApplication.translate("SettingsPage", "Plugin Settings"), parent)

    def _setup_ui(self):
        """Set up the UI for settings using Tabs."""
        super()._setup_ui()

        # Handle existing layout in group_box (similar to DrillholePage logic)
        if self.group_box.layout():
            QWidget().setLayout(self.group_box.layout())
            layout = self.group_box.layout()
        else:
            layout = QVBoxLayout(self.group_box)
            self.group_box.setLayout(layout)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # -- Tab 1: Default --
        self.default_tab = QWidget()
        self._setup_default_tab(self.default_tab)
        self.tab_widget.addTab(self.default_tab, self.tr("Default"))

        # -- Tab 2: Advanced --
        self.advanced_tab = QWidget()
        self._setup_advanced_tab(self.advanced_tab)
        self.tab_widget.addTab(self.advanced_tab, self.tr("Advanced"))

        # -- Tab 3: Plugin Information --
        self.info_tab = QWidget()
        self._setup_info_tab(self.info_tab)
        self.tab_widget.addTab(self.info_tab, self.tr("Plugin Information"))

        # Load settings after UI setup
        self._load_settings()

    def _setup_default_tab(self, parent_widget: QWidget) -> None:
        """Set up Default tab."""
        layout = QVBoxLayout(parent_widget)

        layout.addWidget(QLabel("<b>Export Selection (Save)</b>"))
        layout.addWidget(
            QLabel(self.tr("<i>Select which data to generate when clicking Save.</i>"))
        )

        self.chk_exp_topo = QCheckBox(self.tr("Topographic Profile"))
        self.chk_exp_geol = QCheckBox(self.tr("Geological Profile"))
        self.chk_exp_struct = QCheckBox(self.tr("Structural Data"))
        self.chk_exp_drill = QCheckBox(self.tr("Drillhole Data"))
        self.chk_exp_interp = QCheckBox(self.tr("Interpretations (2D)"))

        for chk in [
            self.chk_exp_topo,
            self.chk_exp_geol,
            self.chk_exp_struct,
            self.chk_exp_drill,
            self.chk_exp_interp,
        ]:
            chk.setChecked(True)  # Default True
            chk.stateChanged.connect(self._on_settings_changed)
            layout.addWidget(chk)

        layout.addStretch()

    def _setup_advanced_tab(self, parent_widget: QWidget) -> None:
        """Set up Advanced tab (Restricted Features)."""
        layout = QVBoxLayout(parent_widget)

        layout.addWidget(QLabel("<b>Advanced Features</b>"))

        self.chk_enable_3d = QCheckBox(self.tr("Enable 3D Interpretation Export"))
        self.chk_enable_3d.setToolTip(
            self.tr("Enables the generation of 3D Shapefiles (.shp) during export.")
        )
        self.chk_enable_3d.stateChanged.connect(self._on_settings_changed)
        layout.addWidget(self.chk_enable_3d)

        layout.addStretch()

    def _setup_info_tab(self, parent_widget: QWidget) -> None:
        """Set up Plugin Information tab."""
        layout = QVBoxLayout(parent_widget)

        layout.addWidget(QLabel("<b>Plugin Information</b>"))
        layout.addWidget(QLabel(self.tr("Sec Interp v2.6.0")))
        layout.addWidget(QLabel(self.tr("Developed by Juan M Bernales")))
        layout.addWidget(QLabel(self.tr("Contact: juanbernales@gmail.com")))

        layout.addStretch()

    def _load_settings(self):
        """Load current state from QgsSettings."""
        # Advanced
        enabled_3d = self.settings.value("sec_interp/enable_3d", False, type=bool)
        if self.chk_enable_3d:
            self.chk_enable_3d.setChecked(enabled_3d)

        # Default (Export Selection)
        if hasattr(self, "chk_exp_topo"):
            self.chk_exp_topo.setChecked(
                self.settings.value("sec_interp/exp_topo", True, type=bool)
            )
            self.chk_exp_geol.setChecked(
                self.settings.value("sec_interp/exp_geol", True, type=bool)
            )
            self.chk_exp_struct.setChecked(
                self.settings.value("sec_interp/exp_struct", True, type=bool)
            )
            self.chk_exp_drill.setChecked(
                self.settings.value("sec_interp/exp_drill", True, type=bool)
            )
            self.chk_exp_interp.setChecked(
                self.settings.value("sec_interp/exp_interp", True, type=bool)
            )

    def _on_settings_changed(self):
        """Save settings when they are changed."""
        # Advanced
        if self.chk_enable_3d:
            self.settings.setValue("sec_interp/enable_3d", self.chk_enable_3d.isChecked())

        # Default
        if hasattr(self, "chk_exp_topo"):
            self.settings.setValue("sec_interp/exp_topo", self.chk_exp_topo.isChecked())
            self.settings.setValue("sec_interp/exp_geol", self.chk_exp_geol.isChecked())
            self.settings.setValue("sec_interp/exp_struct", self.chk_exp_struct.isChecked())
            self.settings.setValue("sec_interp/exp_drill", self.chk_exp_drill.isChecked())
            self.settings.setValue("sec_interp/exp_interp", self.chk_exp_interp.isChecked())

    def get_data(self) -> dict:
        """Get the current settings.

        Returns:
            dict: Current settings.

        """
        return {
            "enable_3d": self.chk_enable_3d.isChecked() if self.chk_enable_3d else False,
            "exp_topo": self.chk_exp_topo.isChecked() if hasattr(self, "chk_exp_topo") else True,
            "exp_geol": self.chk_exp_geol.isChecked() if hasattr(self, "chk_exp_geol") else True,
            "exp_struct": self.chk_exp_struct.isChecked()
            if hasattr(self, "chk_exp_struct")
            else True,
            "exp_drill": self.chk_exp_drill.isChecked() if hasattr(self, "chk_exp_drill") else True,
            "exp_interp": self.chk_exp_interp.isChecked()
            if hasattr(self, "chk_exp_interp")
            else True,
        }

    def validate(self) -> tuple[bool, str]:
        """Validate settings.

        Returns:
            tuple[bool, str]: (is_valid, error_message)

        """
        return True, ""
