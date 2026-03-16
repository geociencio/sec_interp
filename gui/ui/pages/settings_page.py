"""Settings page for Sec Interp plugin."""

from __future__ import annotations

import contextlib

from qgis.core import QgsSettings
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from sec_interp.core.utils.metadata_reader import read_plugin_metadata
from sec_interp.logger_config import get_logger

from .base_page import BasePage

logger = get_logger(__name__)


class SettingsPage(BasePage):
    """Page for managing plugin settings and restricted features."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the settings page."""
        self.settings = QgsSettings()
        # Ensure we have all necessary widgets
        self.tab_widget = None
        self.chk_enable_3d = None
        super().__init__(QCoreApplication.translate("SettingsPage", "Plugin Settings"), parent)

    def _setup_ui(self) -> None:
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

        layout.addWidget(QLabel(self.tr("<b>Export Selection (Save)</b>")))
        layout.addWidget(
            QLabel(self.tr("<i>Select which data to generate when clicking Save.</i>"))
        )

        self.chk_exp_topo = QCheckBox(self.tr("Topographic Profile"))
        self.chk_exp_geol = QCheckBox(self.tr("Geological Profile"))
        self.chk_exp_struct = QCheckBox(self.tr("Structural Data"))
        self.chk_exp_drill = QCheckBox(self.tr("Drillhole Data"))
        self.chk_exp_interp = QCheckBox(self.tr("Interpretations (2D)"))

        layout.addWidget(self.chk_exp_topo)
        layout.addWidget(self.chk_exp_geol)
        layout.addWidget(self.chk_exp_struct)
        layout.addWidget(self.chk_exp_drill)
        layout.addWidget(self.chk_exp_interp)

        # General Export settings
        layout.addWidget(QLabel(self.tr("<br><b>Export Format & Naming</b>")))

        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel(self.tr("Default Vector Format:")))
        self.combo_format = QComboBox()
        self.combo_format.addItems(["Shapefile", "GeoPackage", "DXF"])
        format_layout.addWidget(self.combo_format)
        format_layout.addStretch()
        layout.addLayout(format_layout)

        naming_layout = QHBoxLayout()
        naming_layout.addWidget(QLabel(self.tr("Naming Pattern:")))
        self.txt_naming = QLineEdit()
        self.txt_naming.setPlaceholderText("{filename}_{profile}")
        self.txt_naming.setToolTip(
            self.tr("Pattern for exported files. Use {filename} and {profile} as placeholders.")
        )
        naming_layout.addWidget(self.txt_naming)
        layout.addLayout(naming_layout)

        # Reset button
        btn_layout = QHBoxLayout()
        self.btn_reset_export = QPushButton(self.tr("Reset to defaults"))
        self.btn_reset_export.setToolTip(
            self.tr("Re-enables all export options and resets format settings.")
        )
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_reset_export)
        layout.addLayout(btn_layout)

        layout.addStretch()

    def _setup_advanced_tab(self, parent_widget: QWidget) -> None:
        """Set up Advanced tab (Restricted Features)."""
        layout = QVBoxLayout(parent_widget)

        layout.addWidget(QLabel(self.tr("<b>Advanced Features</b>")))

        self.chk_enable_3d = QCheckBox(self.tr("Enable 3D Interpretation Export"))
        self.chk_enable_3d.setToolTip(
            self.tr("Enables the generation of 3D Shapefiles (.shp) during export.")
        )
        layout.addWidget(self.chk_enable_3d)

        # -- Drillhole 3D Export --
        layout.addWidget(QLabel(self.tr("<br><b>Drillhole 3D Export Options</b>")))
        self.chk_3d_traces = QCheckBox(self.tr("Export 3D Traces"))
        self.chk_3d_intervals = QCheckBox(self.tr("Export 3D Intervals"))
        self.chk_3d_original = QCheckBox(self.tr("Use Original Coordinates (Real 3D)"))
        self.chk_3d_projected = QCheckBox(self.tr("Use Projected Coordinates (Section Plane)"))

        layout.addWidget(self.chk_3d_traces)
        layout.addWidget(self.chk_3d_intervals)
        layout.addWidget(self.chk_3d_original)
        layout.addWidget(self.chk_3d_projected)

        layout.addStretch()

    def _setup_info_tab(self, parent_widget: QWidget) -> None:
        """Set up Plugin Information tab."""
        layout = QVBoxLayout(parent_widget)

        try:
            metadata = read_plugin_metadata()

            layout.addWidget(QLabel(self.tr("<b>Plugin Information</b>")))
            layout.addWidget(QLabel(self.tr(f"{metadata['name']} v{metadata['version']}")))
            layout.addWidget(QLabel(self.tr(f"Developed by {metadata['author']}")))
            layout.addWidget(QLabel(self.tr(f"Contact: {metadata['email']}")))

            if metadata.get("homepage"):
                # Add clickable documentation link
                doc_label = QLabel(
                    f"<a href='{metadata['homepage']}'>{self.tr('Documentation')}</a>"
                )
                doc_label.setOpenExternalLinks(True)
                layout.addWidget(doc_label)

        except (FileNotFoundError, ValueError) as e:
            logger.warning(f"Metadata read error: {e}")
            layout.addWidget(QLabel(self.tr("<b>Plugin Information</b>")))
            layout.addWidget(QLabel(self.tr("Sec Interp (version unavailable)")))
            layout.addWidget(QLabel(self.tr("Metadata missing")))

        layout.addStretch()

    def _load_settings(self) -> None:
        """Load current state from QgsSettings."""
        # Advanced
        enabled_3d = self.settings.value("SecInterp/enable_3d", False, type=bool)
        if self.chk_enable_3d:
            self.chk_enable_3d.setChecked(enabled_3d)

        # Default (Export Selection)
        if hasattr(self, "chk_exp_topo"):
            self.chk_exp_topo.setChecked(self.settings.value("SecInterp/exp_topo", True, type=bool))
            self.chk_exp_geol.setChecked(self.settings.value("SecInterp/exp_geol", True, type=bool))
            self.chk_exp_struct.setChecked(
                self.settings.value("SecInterp/exp_struct", True, type=bool)
            )
            self.chk_exp_drill.setChecked(
                self.settings.value("SecInterp/exp_drill", True, type=bool)
            )
            self.chk_exp_interp.setChecked(
                self.settings.value("SecInterp/exp_interp", True, type=bool)
            )

        if hasattr(self, "combo_format"):
            default_fmt = self.settings.value("SecInterp/export_format", "Shapefile", type=str)
            index = self.combo_format.findText(default_fmt)
            if index >= 0:
                self.combo_format.setCurrentIndex(index)

        if hasattr(self, "txt_naming"):
            self.txt_naming.setText(
                self.settings.value("SecInterp/export_naming", "{filename}_{profile}", type=str)
            )

        # Drillhole 3D
        if hasattr(self, "chk_3d_traces"):
            self.chk_3d_traces.setChecked(
                self.settings.value("SecInterp/drill_3d_traces", True, type=bool)
            )
            self.chk_3d_intervals.setChecked(
                self.settings.value("SecInterp/drill_3d_intervals", True, type=bool)
            )
            self.chk_3d_original.setChecked(
                self.settings.value("SecInterp/drill_3d_original", True, type=bool)
            )
            self.chk_3d_projected.setChecked(
                self.settings.value("SecInterp/drill_3d_projected", False, type=bool)
            )

    def _reset_export_defaults(self) -> None:
        """Reset all export checkboxes to their default values (all enabled)."""
        defaults = {
            "chk_exp_topo": True,
            "chk_exp_geol": True,
            "chk_exp_struct": True,
            "chk_exp_drill": True,
            "chk_exp_interp": True,
            "chk_enable_3d": False,
            "chk_3d_traces": True,
            "chk_3d_intervals": True,
            "chk_3d_original": True,
            "chk_3d_projected": False,
        }
        for attr, value in defaults.items():
            widget = getattr(self, attr, None)
            if widget is not None:
                widget.setChecked(value)

        if hasattr(self, "combo_format"):
            index = self.combo_format.findText("Shapefile")
            if index >= 0:
                self.combo_format.setCurrentIndex(index)

        if hasattr(self, "txt_naming"):
            self.txt_naming.setText("{filename}_{profile}")
        # _on_settings_changed is triggered automatically by stateChanged signals
        logger.info("Export options reset to defaults.")

    def _on_settings_changed(self) -> None:
        """Save settings when they are changed."""
        # Advanced
        if self.chk_enable_3d:
            self.settings.setValue("SecInterp/enable_3d", self.chk_enable_3d.isChecked())

        # Default
        if hasattr(self, "chk_exp_topo"):
            self.settings.setValue("SecInterp/exp_topo", self.chk_exp_topo.isChecked())
            self.settings.setValue("SecInterp/exp_geol", self.chk_exp_geol.isChecked())
            self.settings.setValue("SecInterp/exp_struct", self.chk_exp_struct.isChecked())
            self.settings.setValue("SecInterp/exp_drill", self.chk_exp_drill.isChecked())
            self.settings.setValue("SecInterp/exp_interp", self.chk_exp_interp.isChecked())

        if hasattr(self, "combo_format"):
            self.settings.setValue("SecInterp/export_format", self.combo_format.currentText())

        if hasattr(self, "txt_naming"):
            self.settings.setValue("SecInterp/export_naming", self.txt_naming.text())

        # Drillhole 3D
        if hasattr(self, "chk_3d_traces"):
            self.settings.setValue("SecInterp/drill_3d_traces", self.chk_3d_traces.isChecked())
            self.settings.setValue(
                "SecInterp/drill_3d_intervals", self.chk_3d_intervals.isChecked()
            )
            self.settings.setValue("SecInterp/drill_3d_original", self.chk_3d_original.isChecked())
            self.settings.setValue(
                "SecInterp/drill_3d_projected", self.chk_3d_projected.isChecked()
            )

    def get_data(self) -> dict[str, Any]:
        """Get the current settings.

        Returns:
            dict: Current settings.

        """
        return {
            "enable_3d": (self.chk_enable_3d.isChecked() if self.chk_enable_3d else False),
            "exp_topo": (self.chk_exp_topo.isChecked() if hasattr(self, "chk_exp_topo") else True),
            "exp_geol": (self.chk_exp_geol.isChecked() if hasattr(self, "chk_exp_geol") else True),
            "exp_struct": (
                self.chk_exp_struct.isChecked() if hasattr(self, "chk_exp_struct") else True
            ),
            "exp_drill": (
                self.chk_exp_drill.isChecked() if hasattr(self, "chk_exp_drill") else True
            ),
            "exp_interp": (
                self.chk_exp_interp.isChecked() if hasattr(self, "chk_exp_interp") else True
            ),
            "drill_3d_traces": (
                self.chk_3d_traces.isChecked() if hasattr(self, "chk_3d_traces") else True
            ),
            "drill_3d_intervals": (
                self.chk_3d_intervals.isChecked() if hasattr(self, "chk_3d_intervals") else True
            ),
            "drill_3d_original": (
                self.chk_3d_original.isChecked() if hasattr(self, "chk_3d_original") else True
            ),
            "drill_3d_projected": (
                self.chk_3d_projected.isChecked() if hasattr(self, "chk_3d_projected") else False
            ),
            "export_format": (
                self.combo_format.currentText() if hasattr(self, "combo_format") else "Shapefile"
            ),
            "export_naming": (
                self.txt_naming.text() if hasattr(self, "txt_naming") else "{filename}_{profile}"
            ),
        }

    def validate(self) -> tuple[bool, str]:
        """Validate settings.

        Returns:
            tuple[bool, str]: (is_valid, error_message)

        """
        return True, ""

    def connect_signals(self) -> None:
        """Connect internal signals for the settings page."""
        # Default tab
        self.chk_exp_topo.stateChanged.connect(self._on_settings_changed)
        self.chk_exp_geol.stateChanged.connect(self._on_settings_changed)
        self.chk_exp_struct.stateChanged.connect(self._on_settings_changed)
        self.chk_exp_drill.stateChanged.connect(self._on_settings_changed)
        self.chk_exp_interp.stateChanged.connect(self._on_settings_changed)
        self.btn_reset_export.clicked.connect(self._reset_export_defaults)

        if hasattr(self, "combo_format"):
            self.combo_format.currentIndexChanged.connect(self._on_settings_changed)
        if hasattr(self, "txt_naming"):
            self.txt_naming.textChanged.connect(self._on_settings_changed)

        # Advanced tab
        self.chk_enable_3d.stateChanged.connect(self._on_settings_changed)
        self.chk_3d_traces.stateChanged.connect(self._on_settings_changed)
        self.chk_3d_intervals.stateChanged.connect(self._on_settings_changed)
        self.chk_3d_original.stateChanged.connect(self._on_settings_changed)
        self.chk_3d_projected.stateChanged.connect(self._on_settings_changed)

    def disconnect_signals(self) -> None:
        """Disconnect all signals to prevent memory leaks."""
        with contextlib.suppress(TypeError, RuntimeError):
            self.chk_exp_topo.stateChanged.disconnect(self._on_settings_changed)
        with contextlib.suppress(TypeError, RuntimeError):
            self.chk_exp_geol.stateChanged.disconnect(self._on_settings_changed)
        with contextlib.suppress(TypeError, RuntimeError):
            self.chk_exp_struct.stateChanged.disconnect(self._on_settings_changed)
        with contextlib.suppress(TypeError, RuntimeError):
            self.chk_exp_drill.stateChanged.disconnect(self._on_settings_changed)
        with contextlib.suppress(TypeError, RuntimeError):
            self.chk_exp_interp.stateChanged.disconnect(self._on_settings_changed)
        with contextlib.suppress(TypeError, RuntimeError):
            self.chk_enable_3d.stateChanged.disconnect(self._on_settings_changed)
        with contextlib.suppress(TypeError, RuntimeError):
            self.chk_3d_traces.stateChanged.disconnect(self._on_settings_changed)
        with contextlib.suppress(TypeError, RuntimeError):
            self.chk_3d_intervals.stateChanged.disconnect(self._on_settings_changed)
        with contextlib.suppress(TypeError, RuntimeError):
            self.chk_3d_original.stateChanged.disconnect(self._on_settings_changed)
        with contextlib.suppress(TypeError, RuntimeError):
            self.chk_3d_projected.stateChanged.disconnect(self._on_settings_changed)
        with contextlib.suppress(TypeError, RuntimeError):
            self.btn_reset_export.clicked.disconnect(self._reset_export_defaults)
        with contextlib.suppress(TypeError, RuntimeError):
            if hasattr(self, "combo_format"):
                self.combo_format.currentIndexChanged.disconnect(self._on_settings_changed)
        with contextlib.suppress(TypeError, RuntimeError):
            if hasattr(self, "txt_naming"):
                self.txt_naming.textChanged.disconnect(self._on_settings_changed)
