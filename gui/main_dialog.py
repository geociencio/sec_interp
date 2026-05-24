"""Main Dialog Module.

Contains the SecInterpDialog class which is the primary UI for the plugin.
"""

from __future__ import annotations

import contextlib
import traceback
from pathlib import Path
from typing import Any

from qgis.core import Qgis, QgsProject
from qgis.PyQt.QtCore import QSettings, QUrl
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtWidgets import QDialogButtonBox, QPushButton

from sec_interp.core.domain import InterpretationPolygon
from sec_interp.core.exceptions import SecInterpError
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
from .main_dialog_utils import DialogEntityManager
from .preview_layer_factory import PreviewLayerFactory
from .ui.main_window import SecInterpMainWindow

logger = get_logger(__name__)


class _NoOpMessageBar:
    """Safe no-op messagebar when iface is not available."""

    def pushMessage(self, *_args, **_kwargs) -> None:
        """No-op implementation of pushMessage."""
        return None


class SecInterpDialog(SecInterpMainWindow):
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
        # Initialize the base class which sets up the programmatic UI
        super().__init__(iface, parent)

        self.iface = iface
        self.plugin_instance = plugin_instance
        self.project = QgsProject.instance()

        # Provide a safe, no-op messagebar when iface is not available (tests)
        if self.iface is None:
            self.messagebar = _NoOpMessageBar()
        else:
            self.messagebar = self.iface.messageBar()

        # Initialize manager instances
        self._init_managers()

        # Create legend widget
        self.legend_widget = LegendWidget(self.preview_widget.canvas)

        # Store current preview data
        self.current_topo_data = None
        self.current_geol_data = None
        self.current_struct_data = None
        self.current_canvas = None
        self.current_layers = []
        # Interpretations list is now managed by interpretation_manager
        # Note: interpretation_manager is initialized later in _init_managers

        # Add cache and reset buttons
        self.clear_cache_btn = QPushButton(self.tr("Clear Cache"))
        self.clear_cache_btn.setToolTip(
            self.tr("Clear cached data to force re-processing.")
        )
        self.button_box.addButton(self.clear_cache_btn, QDialogButtonBox.ActionRole)

        self.reset_defaults_btn = QPushButton(self.tr("Reset Defaults"))
        self.reset_defaults_btn.setToolTip(
            self.tr("Reset all inputs to their default values.")
        )
        self.button_box.addButton(self.reset_defaults_btn, QDialogButtonBox.ActionRole)

        # Initialize map tools via tool_manager
        self.tool_manager.initialize_tools()

        # Connect all signals
        self.signal_manager = SignalManager(self)
        self.signal_manager.connect_all()

        # Initial state update
        self.state_manager.update_all()
        self.state_manager.load_settings()

        # Flag to control saving settings on close
        self._save_on_close = True

    def _init_managers(self) -> None:
        """Initialize all manager instances."""
        from sec_interp.core.services.preview_service import PreviewService

        self.input_manager = InputManager(self)
        self.state_manager = StateManager(self)
        self.preview_manager = PreviewManager(
            self, PreviewService(self.plugin_instance.controller)
        )
        self.export_manager = ExportManager(self)
        self.state_manager.setup_indicators()
        self.interpretation_manager = InterpretationManager(self)
        self.interpretation_manager.load_interpretations()
        self.tool_manager = ToolManager(self)
        self.navigation_manager = NavigationManager(self)
        self.layer_factory = PreviewLayerFactory()

    def push_message(
        self,
        title: str,
        message: str,
        level: int = Qgis.Info,
        duration: int = 5,
        show_in_plugin: bool = True,
    ) -> None:
        """Push a message to the QGIS message bar and optionally to plugin results.

        Args:
            title: Message title.
            message: Message content.
            level: Qgis message level (Info, Warning, Critical, Success).
            duration: Visibility duration in seconds.
            show_in_plugin: If True, also show message in plugin results area.

        """
        # Show in QGIS message bar
        if self.messagebar:
            self.messagebar.pushMessage(title, message, level=level, duration=duration)

        # Also show in plugin results area if requested
        if show_in_plugin and hasattr(self, "preview_widget"):
            # Determine icon and color based on level
            if level == Qgis.Success:
                icon = "✓"
                color = "#28a745"  # Green
            elif level == Qgis.Warning:
                icon = "⚠"
                color = "#ffc107"  # Yellow
            elif level == Qgis.Critical:
                icon = "✗"
                color = "#dc3545"  # Red
            else:  # Info
                icon = "ℹ"
                color = "#17a2b8"  # Blue

            # Format message with HTML
            formatted_msg = f'<span style="color: {color}; font-weight: bold;">{icon} {title}:</span> {message}'
            self.preview_widget.results_text.append(formatted_msg)

    def show_dialog(self, title: str, message: str, level: str = "info") -> Any:
        """Show a message box dialog.

        Args:
            title: Dialog title.
            message: Dialog content.
            level: Message level ("info", "warning", "critical", "question").

        """
        return show_user_message(self, title, message, level=level)

    def handle_error(self, error: Exception, title: str = "Error") -> None:
        """Centralized error handling for the dialog.

        Args:
            error: The exception to handle.
            title: Title for the error message box.

        """
        if isinstance(error, SecInterpError):
            msg = str(error)
            logger.warning(
                f"{title}: {msg} - Details: {getattr(error, 'details', 'N/A')}"
            )
            self.show_dialog(title, msg, level="warning")
        else:
            msg = self.tr("An unexpected error occurred: {}").format(error)
            details = traceback.format_exc()
            logger.error(f"{title}: {msg}\n{details}")
            self.show_dialog(
                title,
                self.tr("{}\n\nPlease check the logs for details.").format(msg),
                level="critical",
            )

    def wheelEvent(self, event: Any) -> None:
        """Handle mouse wheel for zooming in preview via navigation_manager."""
        if self.navigation_manager.handle_wheel_event(event):
            return
        super().wheelEvent(event)

    def closeEvent(self, event: Any) -> None:
        """Handle dialog close event to clean up all resources."""
        if self._save_on_close:
            self.state_manager.save_settings()

        self._cleanup_resources()

        with contextlib.suppress(AttributeError, RuntimeError, TypeError):
            super().closeEvent(event)

    def _cleanup_resources(self) -> None:
        """Clean up map tools, managers, signals, and components."""
        logger.info("Closing dialog, cleaning up resources...")
        self._cleanup_map_tools()
        self._cleanup_managers()
        self._cleanup_signals_and_components()

    def _cleanup_map_tools(self) -> None:
        """Clean up active map tools and reset their states."""
        if hasattr(self, "tool_manager") and self.tool_manager:
            with contextlib.suppress(Exception):
                if self.tool_manager.measure_tool:
                    self.tool_manager.measure_tool.cleanup_finalized()
                if self.tool_manager.interpretation_tool:
                    self.tool_manager.interpretation_tool.reset()
            logger.debug("Map tools cleaned up")

    def _cleanup_managers(self) -> None:
        """Clean up all manager instances and save their data."""
        with contextlib.suppress(Exception):
            self.interpretation_manager.save_interpretations()
            self.preview_manager.cleanup()
        logger.debug("Managers cleaned up")

    def _cleanup_signals_and_components(self) -> None:
        """Disconnect all signals and clean up UI components."""
        if hasattr(self, "signal_manager"):
            self.signal_manager.disconnect_all()
        logger.debug("Signals disconnected")

        if hasattr(self, "legend_widget") and self.legend_widget:
            with contextlib.suppress(Exception):
                self.legend_widget.cleanup()

    def open_help(self) -> None:
        """Open the help file in the default browser based on user locale."""
        # Get QGIS locale (e.g., 'es', 'pt_BR', 'pl')
        user_locale = QSettings().value("locale/userLocale", "en")
        if not isinstance(user_locale, str):
            user_locale = "en"

        # 1. Try exact locale folder first (e.g., help/html/pt_BR/)
        plugin_dir = Path(__file__).parent.parent
        help_dir = plugin_dir / "help" / "html"
        help_file = help_dir / user_locale / "index.html"

        # 2. Try language-only fallback (e.g., pt)
        if not help_file.exists() and len(user_locale) > 2:  # noqa: PLR2004
            help_file = help_dir / user_locale[0:2] / "index.html"

        # 3. Final fallback to English
        if not help_file.exists():
            help_file = help_dir / "en" / "index.html"

        if help_file.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(help_file)))
        else:
            self.push_message(
                self.tr("Error"),
                self.tr("Help file not found. Please run 'make docs' to generate it."),
                level=Qgis.Warning,
            )

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
            "show_interpretations": bool(
                self.preview_widget.chk_interpretations.isChecked()
            ),
            "show_legend": bool(self.preview_widget.chk_legend.isChecked()),
            "max_points": self.preview_widget.spin_max_points.value(),
            "auto_lod": self.preview_widget.chk_auto_lod.isChecked(),
            "use_adaptive_sampling": bool(
                self.preview_widget.chk_adaptive_sampling.isChecked()
            ),
        }

    def update_preview_from_checkboxes(self) -> None:
        """Update preview when checkboxes change.

        This method delegates to PreviewManager for preview updates.
        """
        self.preview_manager.update_from_checkboxes()

    def preview_profile_handler(self) -> None:
        """Generate a quick preview with topographic, geological, and structural data.

        This method delegates to PreviewManager for preview generation.
        """
        success, message = self.preview_manager.generate_preview()
        if success:
            # Auto-save settings on successful preview
            self.state_manager.save_settings()

        if not success and message:
            self.push_message(self.tr("Preview Error"), message, level=Qgis.Warning)

    def export_preview(self) -> None:
        """Export the current preview to a file using ExportManager."""
        self.export_manager.export_preview()

    def accept_handler(self) -> None:
        """Handle the accept button click event."""
        # Proactively save settings as UI state, even if validation fails
        self.state_manager.save_settings()

        # When running without a QGIS iface (tests), skip strict validation
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

    def validate_inputs(self) -> bool:
        """Validate the inputs from the dialog.

        This method delegates to DialogInputManager for input validation.
        """
        is_valid, error_message = self.input_manager.validate_inputs()
        if not is_valid:
            show_user_message(self, self.tr("Validation Error"), error_message)
        return is_valid

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

    def _populate_field_combobox(
        self, source_combobox: Any, target_combobox: Any
    ) -> None:
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
