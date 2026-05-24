"""Signal management module for SecInterp main dialog.

This module handles all signal connections for the dialog,
separating signal setup from the main dialog class.
"""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

from qgis.PyQt.QtWidgets import QDialogButtonBox

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


if TYPE_CHECKING:
    from .main_dialog import SecInterpDialog


class SignalManager:
    """Manages all signal connections for SecInterpDialog.

    This class organizes signal connections into logical groups,
    making the dialog initialization cleaner and more maintainable.
    """

    def __init__(self, dialog: SecInterpDialog) -> None:
        """Initialize signal manager.

        Args:
            dialog: The :class:`sec_interp.gui.main_dialog.SecInterpDialog` instance

        """
        self.dialog = dialog

    def connect_all(self) -> None:
        """Connect all signals in organized groups.

        This method is idempotent: it disconnects first to avoid double connections.
        """
        self.disconnect_all()

        self._connect_button_signals()
        self._connect_preview_signals()
        self._connect_page_signals()
        self._connect_tool_signals()

    def disconnect_all(self) -> None:
        """Disconnect all signals to prevent memory leaks."""
        logger.debug("Starting exhaustive signal disconnection")
        self._disconnect_button_signals()
        self._disconnect_preview_signals()
        self._disconnect_page_signals()
        self._disconnect_tool_signals()
        logger.debug("Signal disconnection complete")

    def _disconnect_button_signals(self) -> None:
        """Disconnect main dialog button signals."""
        self._disconnect_dialog_buttons()
        self._disconnect_custom_buttons()

    def _disconnect_dialog_buttons(self) -> None:
        """Disconnect standard dialog buttons."""
        ok_btn = self.dialog.button_box.button(QDialogButtonBox.Ok)
        if ok_btn:
            with contextlib.suppress(TypeError, RuntimeError):
                ok_btn.clicked.disconnect()

        cancel_btn = self.dialog.button_box.button(QDialogButtonBox.Cancel)
        if cancel_btn:
            with contextlib.suppress(TypeError, RuntimeError):
                cancel_btn.clicked.disconnect()

        save_btn = self.dialog.button_box.button(QDialogButtonBox.Save)
        if save_btn:
            with contextlib.suppress(TypeError, RuntimeError):
                save_btn.clicked.disconnect()

        with contextlib.suppress(TypeError, RuntimeError):
            self.dialog.button_box.helpRequested.disconnect()

    def _disconnect_custom_buttons(self) -> None:
        """Disconnect custom buttons like clear cache and reset defaults."""
        if hasattr(self.dialog, "clear_cache_btn") and self.dialog.clear_cache_btn:
            with contextlib.suppress(TypeError, RuntimeError):
                self.dialog.clear_cache_btn.clicked.disconnect()

        if (
            hasattr(self.dialog, "reset_defaults_btn")
            and self.dialog.reset_defaults_btn
        ):
            with contextlib.suppress(TypeError, RuntimeError):
                self.dialog.reset_defaults_btn.clicked.disconnect()

    def _disconnect_preview_signals(self) -> None:
        """Disconnect preview-related signals explicitly for analyzer compliance."""
        self._disconnect_preview_action_buttons()
        self._disconnect_preview_options()

    def _disconnect_preview_action_buttons(self) -> None:
        """Disconnect preview action buttons."""
        with contextlib.suppress(Exception):
            self.dialog.preview_widget.btn_preview.clicked.disconnect()
        with contextlib.suppress(Exception):
            self.dialog.preview_widget.btn_export.clicked.disconnect()
        with contextlib.suppress(Exception):
            self.dialog.preview_widget.btn_measure.toggled.disconnect()
        with contextlib.suppress(Exception):
            self.dialog.preview_widget.btn_interpret.toggled.disconnect()
        with contextlib.suppress(Exception):
            self.dialog.preview_widget.btn_finalize.clicked.disconnect()

    def _disconnect_preview_options(self) -> None:
        """Disconnect preview options."""
        self._disconnect_preview_checkboxes()
        self._disconnect_preview_misc_options()

    def _disconnect_preview_checkboxes(self) -> None:
        """Disconnect layer visibility checkboxes."""
        with contextlib.suppress(Exception):
            self.dialog.preview_widget.chk_topo.stateChanged.disconnect()
        with contextlib.suppress(Exception):
            self.dialog.preview_widget.chk_geol.stateChanged.disconnect()
        with contextlib.suppress(Exception):
            self.dialog.preview_widget.chk_struct.stateChanged.disconnect()
        with contextlib.suppress(Exception):
            self.dialog.preview_widget.chk_drillholes.stateChanged.disconnect()
        with contextlib.suppress(Exception):
            self.dialog.preview_widget.chk_interpretations.stateChanged.disconnect()

    def _disconnect_preview_misc_options(self) -> None:
        """Disconnect legend, spinboxes, and adaptive sampling."""
        with contextlib.suppress(Exception):
            self.dialog.preview_widget.chk_legend.stateChanged.disconnect()
        with contextlib.suppress(Exception):
            self.dialog.preview_widget.spin_max_points.valueChanged.disconnect()
        with contextlib.suppress(Exception):
            self.dialog.preview_widget.chk_auto_lod.toggled.disconnect()
        with contextlib.suppress(Exception):
            self.dialog.preview_widget.chk_adaptive_sampling.toggled.disconnect()

    def _disconnect_page_signals(self) -> None:
        """Disconnect page-specific signals with full tracking."""
        self._disconnect_explicit_page_signals()
        self._disconnect_sequential_pages()

    def _disconnect_explicit_page_signals(self) -> None:
        """Explicitly disconnect the signals reported as leaking by analyzer."""
        with contextlib.suppress(Exception):
            self.dialog.page_dem.raster_combo.layerChanged.disconnect()
        with contextlib.suppress(Exception):
            self.dialog.page_section.line_combo.layerChanged.disconnect()
        with contextlib.suppress(Exception):
            self.dialog.page_geology.dataChanged.disconnect()
        with contextlib.suppress(Exception):
            self.dialog.page_struct.dataChanged.disconnect()
        with contextlib.suppress(Exception):
            self.dialog.page_drillhole.dataChanged.disconnect()
        with contextlib.suppress(Exception):
            self.dialog.output_widget.fileChanged.disconnect()

    def _disconnect_sequential_pages(self) -> None:
        """Sequential cleanup for all managed components."""
        pages = [
            self.dialog.page_dem,
            self.dialog.page_section,
            self.dialog.page_geology,
            self.dialog.page_struct,
            self.dialog.page_drillhole,
            self.dialog.page_interpretation,
            self.dialog.preview_widget,
            self.dialog.preview_manager,
            self.dialog.page_settings,
        ]

        for page in pages:
            if not page:
                continue

            # Method 1: Call disconnect_signals if it exists
            if hasattr(page, "disconnect_signals"):
                with contextlib.suppress(Exception):
                    page.disconnect_signals()

            # Method 2: Disconnect known signals explicitly (legacy/fallback)
            self._disconnect_known_page_signals(page)

    def _disconnect_known_page_signals(self, page: Any) -> None:
        """Disconnect known signals for pages that might not have disconnect_signals."""
        self._disconnect_layer_combo_signals(page)
        self._disconnect_data_changed_signals(page)

    def _disconnect_layer_combo_signals(self, page: Any) -> None:
        """Disconnect layer combo signals."""
        if hasattr(page, "raster_combo") and page.raster_combo:
            with contextlib.suppress(Exception):
                page.raster_combo.layerChanged.disconnect()

        if hasattr(page, "line_combo") and page.line_combo:
            with contextlib.suppress(Exception):
                page.line_combo.layerChanged.disconnect()

    def _disconnect_data_changed_signals(self, page: Any) -> None:
        """Disconnect data changed signals."""
        if hasattr(page, "dataChanged"):
            with contextlib.suppress(Exception):
                page.dataChanged.disconnect()

        if hasattr(page, "fileChanged"):
            with contextlib.suppress(Exception):
                page.fileChanged.disconnect()

    def _disconnect_tool_signals(self) -> None:
        """Disconnect map tool signals and window signals."""
        if hasattr(self.dialog, "tool_manager") and self.dialog.tool_manager:
            with contextlib.suppress(AttributeError, TypeError, RuntimeError):
                self.dialog.tool_manager.disconnect_signals()

    def _connect_button_signals(self) -> None:
        """Connect dialog button signals."""
        ok_btn = self.dialog.button_box.button(QDialogButtonBox.Ok)
        if ok_btn:
            ok_btn.clicked.connect(self.dialog.accept_handler)

        cancel_btn = self.dialog.button_box.button(QDialogButtonBox.Cancel)
        if cancel_btn:
            cancel_btn.clicked.connect(self.dialog.reject_handler)

        save_btn = self.dialog.button_box.button(QDialogButtonBox.Save)
        if save_btn:
            save_btn.clicked.connect(self.dialog.export_manager.export_data)

        self.dialog.button_box.helpRequested.connect(self.dialog.open_help)
        self.dialog.clear_cache_btn.clicked.connect(self.dialog.clear_cache_handler)
        self.dialog.reset_defaults_btn.clicked.connect(
            self.dialog.reset_defaults_handler
        )

    def _connect_preview_signals(self) -> None:
        """Connect preview-related signals."""
        self.dialog.preview_widget.btn_preview.clicked.connect(
            self.dialog.preview_profile_handler
        )
        self.dialog.preview_widget.btn_export.clicked.connect(
            self.dialog.export_preview
        )

        # Preview layer checkboxes
        self.dialog.preview_widget.chk_topo.stateChanged.connect(
            self.dialog.update_preview_from_checkboxes
        )
        self.dialog.preview_widget.chk_geol.stateChanged.connect(
            self.dialog.update_preview_from_checkboxes
        )
        self.dialog.preview_widget.chk_struct.stateChanged.connect(
            self.dialog.update_preview_from_checkboxes
        )
        self.dialog.preview_widget.chk_drillholes.stateChanged.connect(
            self.dialog.update_preview_from_checkboxes
        )
        self.dialog.preview_widget.chk_interpretations.stateChanged.connect(
            self.dialog.update_preview_from_checkboxes
        )
        self.dialog.preview_widget.chk_legend.stateChanged.connect(
            self.dialog.update_preview_from_checkboxes
        )

        # Preview settings
        self.dialog.preview_widget.spin_max_points.valueChanged.connect(
            self.dialog.update_preview_from_checkboxes
        )
        self.dialog.preview_widget.chk_auto_lod.toggled.connect(
            self.dialog.update_preview_from_checkboxes
        )
        self.dialog.preview_widget.chk_adaptive_sampling.toggled.connect(
            self.dialog.update_preview_from_checkboxes
        )

    def _connect_page_signals(self) -> None:
        """Connect page-specific signals for state updates."""
        # Output path changes
        self.dialog.output_widget.fileChanged.connect(self.dialog.update_button_state)

        # DEM page
        self.dialog.page_dem.raster_combo.layerChanged.connect(
            self.dialog.update_button_state
        )
        self.dialog.page_dem.raster_combo.layerChanged.connect(
            self.dialog.update_preview_checkbox_states
        )

        # Section page
        self.dialog.page_section.line_combo.layerChanged.connect(
            self.dialog.update_button_state
        )
        self.dialog.page_section.line_combo.layerChanged.connect(
            self.dialog.update_preview_checkbox_states
        )

        # Data pages
        self.dialog.page_geology.dataChanged.connect(
            self.dialog.update_preview_checkbox_states
        )
        self.dialog.page_struct.dataChanged.connect(
            self.dialog.update_preview_checkbox_states
        )
        self.dialog.page_drillhole.dataChanged.connect(
            self.dialog.update_preview_checkbox_states
        )

        # Reconnect internal signals for all pages
        pages = [
            self.dialog.page_dem,
            self.dialog.page_section,
            self.dialog.page_geology,
            self.dialog.page_struct,
            self.dialog.page_drillhole,
            self.dialog.page_interpretation,
            self.dialog.preview_widget,
            self.dialog.preview_manager,
            self.dialog.page_settings,
        ]
        for page in pages:
            if hasattr(page, "connect_signals"):
                with contextlib.suppress(Exception):
                    page.connect_signals()

    def _connect_tool_signals(self) -> None:
        """Connect map tool signals."""
        self.dialog.preview_widget.btn_measure.toggled.connect(
            self.dialog.toggle_measure_tool
        )
        self.dialog.preview_widget.btn_interpret.toggled.connect(
            self.dialog.toggle_interpretation_tool
        )
        self.dialog.preview_widget.btn_finalize.clicked.connect(
            self.dialog.tool_manager.measure_tool.finalize_measurement
        )

        # IMPORTANT: Restore tool-internal signal connections (measurementChanged, polygonFinished, etc)
        if hasattr(self.dialog, "tool_manager") and self.dialog.tool_manager:
            self.dialog.tool_manager.connect_signals()
