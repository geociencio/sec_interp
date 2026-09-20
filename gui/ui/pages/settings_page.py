"""Settings page for Sec Interp plugin.

This page is a thin coordinator: it owns the tab container and delegates the
default (export), advanced (3D) and information forms to
:mod:`gui.ui.pages.settings`.
"""

from __future__ import annotations

import contextlib
from typing import Any

from qgis.core import QgsSettings
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from sec_interp.core.config import ConfigService
from sec_interp.logger_config import get_logger

from .base_page import BasePage
from .settings import AdvancedTab, DefaultTab, build_info_tab
from .settings.settings_persistence import load_settings, save_settings

logger = get_logger(__name__)


class SettingsPage(BasePage):
    """Page for managing plugin settings and restricted features."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the settings page."""
        self.settings = QgsSettings()
        self.config_service = ConfigService()
        super().__init__(QCoreApplication.translate("SettingsPage", "Plugin Settings"), parent)

    def _setup_ui(self) -> None:
        """Set up the tabbed settings interface."""
        super()._setup_ui()

        layout = self.group_box.layout()
        if layout is None:
            layout = QVBoxLayout(self.group_box)
            self.group_box.setLayout(layout)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        self.default_tab = DefaultTab()
        self.tab_widget.addTab(self.default_tab, self.tr("Default"))

        self.advanced_tab = AdvancedTab()
        self.tab_widget.addTab(self.advanced_tab, self.tr("Advanced"))

        self.info_tab = build_info_tab(self.tr)
        self.tab_widget.addTab(self.info_tab, self.tr("Plugin Information"))

        self._expose_tab_widgets()
        self._load_settings()

    def _expose_tab_widgets(self) -> None:
        """Expose tab widgets as page attributes for backward compatibility."""
        self.chk_exp_topo = self.default_tab.chk_exp_topo
        self.chk_exp_geol = self.default_tab.chk_exp_geol
        self.chk_exp_struct = self.default_tab.chk_exp_struct
        self.chk_exp_drill = self.default_tab.chk_exp_drill
        self.chk_exp_interp = self.default_tab.chk_exp_interp
        self.combo_format = self.default_tab.combo_format
        self.txt_naming = self.default_tab.txt_naming
        self.btn_reset_export = self.default_tab.btn_reset_export

        self.chk_enable_3d = self.advanced_tab.chk_enable_3d
        self.chk_3d_traces = self.advanced_tab.chk_3d_traces
        self.chk_3d_intervals = self.advanced_tab.chk_3d_intervals
        self.chk_3d_original = self.advanced_tab.chk_3d_original
        self.chk_3d_projected = self.advanced_tab.chk_3d_projected

    def _load_settings(self) -> None:
        """Load current state from QgsSettings."""
        load_settings(self.settings, self.default_tab, self.advanced_tab)

    def _reset_export_defaults(self) -> None:
        """Reset all export and 3D checkboxes to their default values."""
        self.default_tab.reset_to_defaults()
        self.advanced_tab.reset_to_defaults()

    def _on_settings_changed(self) -> None:
        """Save settings when they are changed."""
        save_settings(self.config_service, self.default_tab, self.advanced_tab)

    def get_data(self) -> dict[str, Any]:
        """Get the current settings.

        Returns:
            dict: Current settings.

        """
        data = self.default_tab.get_data()
        data.update(self.advanced_tab.get_data())
        return data

    def validate(self) -> tuple[bool, str]:
        """Validate settings.

        Returns:
            tuple[bool, str]: (is_valid, error_message)

        """
        return True, ""

    def connect_signals(self) -> None:
        """Connect internal signals for the settings page."""
        self.default_tab.changed.connect(self._on_settings_changed)
        self.advanced_tab.changed.connect(self._on_settings_changed)
        self.default_tab.connect_signals()
        self.advanced_tab.connect_signals()

    def disconnect_signals(self) -> None:
        """Disconnect all signals to prevent memory leaks."""
        self.default_tab.disconnect_signals()
        self.advanced_tab.disconnect_signals()
        with contextlib.suppress(TypeError, RuntimeError):
            self.default_tab.changed.disconnect(self._on_settings_changed)
        with contextlib.suppress(TypeError, RuntimeError):
            self.advanced_tab.changed.disconnect(self._on_settings_changed)
