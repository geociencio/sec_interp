"""QGIS lifecycle and action/toolbar wiring for the SecInterp plugin."""

from __future__ import annotations

import contextlib
from typing import Any

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class PluginLifecycleMixin:
    """Menu/toolbar actions and unload/cleanup lifecycle."""

    def add_action(
        self,
        icon_path: str,
        text: str,
        callback: Any,
        enabled_flag: bool = True,
        add_to_menu: bool = True,
        add_to_toolbar: bool = True,
        status_tip: str | None = None,
        whats_this: str | None = None,
        parent: Any = None,
    ) -> QAction:
        """Add a toolbar icon to the toolbar.

        Args:
            icon_path: Path to the icon for this action.
            text: Text shown in menu items for this action.
            callback: Function called when the action is triggered.
            enabled_flag: Whether the action is enabled by default.
            add_to_menu: Whether the action is added to the menu.
            add_to_toolbar: Whether the action is added to the toolbar.
            status_tip: Optional popup text on hover.
            whats_this: Optional status-bar text on hover.
            parent: Parent widget for the new action.

        Returns:
            The created QAction (also appended to ``self.actions``).

        """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self) -> None:  # noqa: N802
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = str(self.plugin_dir / "icon.png")
        self.add_action(
            icon_path,
            text=self.tr("Geological data extraction"),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )
        self.first_start = True

    def run(self) -> None:
        """Run method that performs all the real work."""
        if not self.dlg:
            from qgis.PyQt.QtWidgets import QMessageBox

            QMessageBox.critical(
                self.iface.mainWindow(),
                self.tr("Initialization Error"),
                self.tr("The plugin dialog failed to initialize. Please check the logs."),
            )
            return

        if self.first_start:
            self.first_start = False
            if self.preview_renderer:
                self.preview_renderer.canvas = self.dlg.preview_widget.canvas
            self.dlg.accepted.connect(self.process_data)

        if hasattr(self.dlg, "signal_manager"):
            self.dlg.signal_manager.connect_all()

        self.dlg._load_interpretations()
        self.dlg._load_user_settings()
        self.dlg.show()
        self.dlg.exec()

    def process_data(self, inputs: dict[str, Any] | None = None) -> tuple[Any, Any, Any] | None:
        """Process profile data by delegating to the dialog's preview manager.

        Args:
            inputs: Pre-validated inputs (optional)

        Returns:
            Tuple of (profile_data, geol_data, struct_data) or None

        """
        if hasattr(self, "dlg") and self.dlg:
            success, message = self.dlg.preview_manager.generate_preview()
            if not success:
                logger.warning(f"Data processing failed: {message}")
                return None

            cache = self.dlg.preview_manager.cached_data
            return cache["topo"], cache["geol"], cache["struct"]

        return None

    def unload(self) -> None:
        """Remove the plugin menu item and icon from QGIS GUI."""
        self.disconnect_signals()

        for action in self.actions:
            self.iface.removePluginMenu(self.tr("&Sec Interp"), action)
            self.iface.removeToolBarIcon(action)

        if self.toolbar:
            with contextlib.suppress(Exception):
                self.iface.mainWindow().removeToolBar(self.toolbar)
            del self.toolbar
            self.toolbar = None

    def disconnect_signals(self) -> None:
        """Disconnect all signals to prevent memory leaks."""
        self._disconnect_actions()
        self._disconnect_dialog()
        self.disconnect_layer_notifications()

    def _disconnect_actions(self) -> None:
        """Disconnect plugin actions."""
        for action in self.actions:
            if action:
                with contextlib.suppress(TypeError, RuntimeError):
                    action.triggered.disconnect()

    def _disconnect_dialog(self) -> None:
        """Disconnect dialog connections."""
        if hasattr(self, "dlg") and self.dlg:
            with contextlib.suppress(TypeError, RuntimeError):
                self.dlg.accepted.disconnect(self.process_data)

            if hasattr(self.dlg, "cleanup"):
                with contextlib.suppress(Exception):
                    self.dlg.cleanup()
