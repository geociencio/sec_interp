"""Main Dialog Module.

Contains the SecInterpDialog class which is the primary UI for the plugin.
Message/error handling, lifecycle cleanup and manager proxies live in the
``dialog_*_mixin`` modules.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qgis.core import Qgis, QgsProject
from qgis.PyQt.QtCore import QSettings, QUrl
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtWidgets import QDialogButtonBox, QPushButton

from sec_interp.gui.dialog_facade_mixin import DialogFacadeMixin
from sec_interp.gui.dialog_lifecycle_mixin import DialogLifecycleMixin
from sec_interp.gui.dialog_message_mixin import DialogMessageMixin
from sec_interp.gui.utils import show_user_message
from sec_interp.logger_config import get_logger

from .dialog_export_manager import ExportManager
from .dialog_input_manager import InputManager
from .dialog_interpretation_manager import InterpretationManager
from .dialog_preview_manager import PreviewManager
from .dialog_signal_manager import SignalManager
from .dialog_state_manager import StateManager
from .dialog_tool_manager import NavigationManager, ToolManager
from .legend_widget import LegendWidget
from .preview_layer_factory import PreviewLayerFactory
from .preview_state import PreviewCache, RenderState
from .ui.main_window import SecInterpMainWindow

logger = get_logger(__name__)


class _NoOpMessageBar:
    """Safe no-op messagebar when iface is not available."""

    def pushMessage(self, *_args, **_kwargs) -> None:
        """No-op implementation of pushMessage."""
        return None


class SecInterpDialog(
    DialogLifecycleMixin,
    DialogMessageMixin,
    DialogFacadeMixin,
    SecInterpMainWindow,
):
    """Dialog for the SecInterp QGIS plugin.

    This dialog provides the user interface and helper methods to populate
    combo boxes with layers from the current QGIS project (raster and vector
    layers filtered by geometry type). It also exposes the interface and
    plugin instance for interaction with the host application.

    Attributes:
        iface (QgsInterface): The QGIS interface instance.
        plugin_instance (SecInterp): The plugin instance that created this dialog.
        messagebar (QgsMessageBar): The message bar widget for notifications.

    """

    def __init__(self, iface=None, plugin_instance=None, parent=None) -> None:
        """Initialize the dialog."""
        super().__init__(iface, parent)

        self.iface = iface
        self.plugin_instance = plugin_instance
        self.project = QgsProject.instance()

        if self.iface is None:
            self.messagebar = _NoOpMessageBar()
        else:
            self.messagebar = self.iface.messageBar()

        self._init_managers()

        self.legend_widget = LegendWidget(self.preview_widget.canvas)

        self.render_state = RenderState()

        self.clear_cache_btn = QPushButton(self.tr("Clear Cache"))
        self.clear_cache_btn.setToolTip(self.tr("Clear cached data to force re-processing."))
        self.button_box.addButton(self.clear_cache_btn, QDialogButtonBox.ButtonRole.ActionRole)

        self.reset_defaults_btn = QPushButton(self.tr("Reset Defaults"))
        self.reset_defaults_btn.setToolTip(self.tr("Reset all inputs to their default values."))
        self.button_box.addButton(self.reset_defaults_btn, QDialogButtonBox.ButtonRole.ActionRole)

        self.tool_manager.initialize_tools()

        self.signal_manager = SignalManager(
            self,
            self.preview_manager,
            self.export_manager,
            self.tool_manager,
            self.state_manager,
        )
        self.signal_manager.connect_all()

        self.state_manager.update_all()
        self.state_manager.load_settings()

        self._save_on_close = True

    def _init_managers(self) -> None:
        """Initialize all manager instances."""
        from sec_interp.core.services.preview_service import PreviewService

        from .dialog_dependencies import Pages

        preview_cache = PreviewCache()
        pages = Pages(
            dem=self.page_dem,
            section=self.page_section,
            geology=self.page_geology,
            structure=self.page_struct,
            drillhole=self.page_drillhole,
            settings=self.page_settings,
        )

        self.input_manager = InputManager(pages, self.output_widget, self.tr)
        self.state_manager = StateManager(self)
        self.preview_manager = PreviewManager(
            self, PreviewService(self.plugin_instance.controller), cache=preview_cache
        )
        self.export_manager = ExportManager(self)
        self.state_manager.setup_indicators()
        self.interpretation_manager = InterpretationManager(self, cache=preview_cache)
        self.interpretation_manager.load_interpretations()
        self.tool_manager = ToolManager(
            self.preview_widget.canvas,
            self.preview_widget,
            self.tr,
            self.on_interpretation_finished,
            self.update_measurement_display,
        )
        self.navigation_manager = NavigationManager(self.preview_widget.canvas)
        self.layer_factory = PreviewLayerFactory()

        self.preview_manager.set_interpretations_cleared_handler(
            self.interpretation_manager.clear_interpretations
        )
        self.interpretation_manager.set_preview_update_handler(
            self.preview_manager.update_from_checkboxes
        )

    def show_dialog(self, title: str, message: str, level: str = "info") -> Any:
        """Show a message box dialog.

        Args:
            title: Dialog title.
            message: Dialog content.
            level: Message level ("info", "warning", "critical", "question").

        """
        return show_user_message(self, title, message, level=level)

    def open_help(self) -> None:
        """Open the help file in the default browser based on user locale."""
        user_locale = QSettings().value("locale/userLocale", "en")
        if not isinstance(user_locale, str):
            user_locale = "en"

        plugin_dir = Path(__file__).parent.parent
        help_dir = plugin_dir / "help" / "html"
        help_file = help_dir / user_locale / "index.html"

        if not help_file.exists() and len(user_locale) > 2:  # noqa: PLR2004
            help_file = help_dir / user_locale[0:2] / "index.html"

        if not help_file.exists():
            help_file = help_dir / "en" / "index.html"

        if help_file.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(help_file)))
        else:
            self.push_message(
                self.tr("Error"),
                self.tr("Help file not found. Please run 'make docs' to generate it."),
                level=Qgis.MessageLevel.Warning,
            )

    def validate_inputs(self) -> bool:
        """Validate the inputs from the dialog via DialogInputManager."""
        is_valid, error_message = self.input_manager.validate_inputs()
        if not is_valid:
            show_user_message(self, self.tr("Validation Error"), error_message)
        return is_valid
