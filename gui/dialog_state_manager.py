"""State management module for SecInterp main dialog.

Handles both visual status (indicators, button enablement) and
persistence (saving/loading settings) by delegating to specialized managers.
"""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

from sec_interp.logger_config import get_logger

from .dialog_settings_persistence import DialogSettingsPersistence
from .ui_status_manager import UIStatusManager

if TYPE_CHECKING:
    from sec_interp.gui.main_dialog import SecInterpDialog

logger = get_logger(__name__)


class StateManager:
    """Manages the state of the dialog via delegation.

    This class acts as a central orchestrator connecting specialized managers
    for persistence and visual status.
    """

    def __init__(self, dialog: SecInterpDialog) -> None:
        """Initialize state manager and its components."""
        self.dialog = dialog
        self._connected_widgets: list[Any] = []

        # Specialized Managers
        self.persistence = DialogSettingsPersistence(dialog)
        self.status_manager = UIStatusManager(dialog)

    # --- Orchestration ---

    def setup_indicators(self) -> None:
        """Set up required field indicators with warning icons."""
        self.status_manager.setup_indicators()

    def update_all(self) -> None:
        """Update all UI status components."""
        self.status_manager.update_all()

    def update_preview_checkbox_states(self) -> None:
        """Enable or disable preview checkboxes."""
        self.status_manager.update_preview_checkbox_states()

    def update_button_state(self) -> None:
        """Enable or disable buttons based on input validity."""
        self.status_manager.update_button_state()

    def update_raster_status(self) -> None:
        """Update raster layer status icon."""
        self.status_manager.update_raster_status()

    def update_section_status(self) -> None:
        """Update section line status icon."""
        self.status_manager.update_section_status()

    # --- Signal Management ---

    def disconnect_signals(self) -> None:
        """Disconnect all UI signals to prevent memory leaks."""
        logger.debug(f"Disconnecting {len(self._connected_widgets)} UI signals")
        for _widget, signal, slot in self._connected_widgets:
            with contextlib.suppress(TypeError, RuntimeError):
                signal.disconnect(slot)
        self._connected_widgets.clear()

    def connect_checked(self, widget: Any, signal: Any, slot: Any) -> None:
        """Connect a signal and track it for later disconnection."""
        signal.connect(slot)
        self._connected_widgets.append((widget, signal, slot))

    # --- Persistence Delegation ---

    def load_settings(self) -> None:
        """Load user settings from previous session."""
        self.persistence.load_settings()
        # Update all status indicators after bulk restoration
        self.update_all()
        logger.info("Settings loaded and UI updated")

    def save_settings(self) -> None:
        """Save user settings for next session."""
        self.persistence.save_settings()

    def reset_to_defaults(self) -> None:
        """Reset all dialog inputs to their default values."""
        self.persistence.reset_pages()
        self.persistence.reset_preview()
        self._reset_tools()

        self.dialog.preview_widget.results_text.append(
            self.dialog.tr("✓ Form reset to default values")
        )
        self.update_all()
        logger.info("Dialog reset to defaults by user")

    def _reset_tools(self) -> None:
        """Reset internal tools and interpretations."""
        if hasattr(self.dialog, "tool_manager"):
            self.dialog.tool_manager.measure_tool.reset()

        # Handle interpretations via manager or direct property (backward compat)
        if (
            hasattr(self.dialog, "interpretation_manager")
            and self.dialog.interpretation_manager
        ):
            self.dialog.interpretation_manager.interpretations = []
            self.dialog.interpretation_manager.save_interpretations()
        elif hasattr(self.dialog, "interpretations"):
            self.dialog.interpretations = []
            if hasattr(self.dialog, "_save_interpretations"):
                self.dialog._save_interpretations()
