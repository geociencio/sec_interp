"""Signal management module for SecInterp main dialog.

This module handles all signal connections for the dialog,
separating signal setup from the main dialog class.
"""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

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
        """Connect all signals in organized groups."""
        self._connect_button_signals()
        self._connect_preview_signals()
        self._connect_page_signals()
        self._connect_tool_signals()

    def disconnect_all(self) -> None:
        """Disconnect all signals to prevent memory leaks."""
        self._disconnect_button_signals()
        self._disconnect_preview_signals()
        self._disconnect_page_signals()
        self._disconnect_tool_signals()

    def _disconnect_button_signals(self) -> None:
        """Disconnect main dialog button signals."""
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

        if hasattr(self.dialog, "clear_cache_btn") and self.dialog.clear_cache_btn:
            with contextlib.suppress(TypeError, RuntimeError):
                self.dialog.clear_cache_btn.clicked.disconnect()

        if hasattr(self.dialog, "reset_defaults_btn") and self.dialog.reset_defaults_btn:
            with contextlib.suppress(TypeError, RuntimeError):
                self.dialog.reset_defaults_btn.clicked.disconnect()

    def _disconnect_preview_signals(self) -> None:
        """Disconnect preview-related signals."""
        with contextlib.suppress(AttributeError, TypeError, RuntimeError):
            self.dialog.preview_widget.btn_preview.clicked.disconnect(
                self.dialog.preview_profile_handler
            )
        with contextlib.suppress(AttributeError, TypeError, RuntimeError):
            self.dialog.preview_widget.btn_export.clicked.disconnect(self.dialog.export_preview)
        with contextlib.suppress(AttributeError, TypeError, RuntimeError):
            self.dialog.preview_widget.btn_measure.toggled.disconnect(
                self.dialog.toggle_measure_tool
            )
        with contextlib.suppress(AttributeError, TypeError, RuntimeError):
            self.dialog.preview_widget.btn_interpret.toggled.disconnect(
                self.dialog.toggle_interpretation_tool
            )
        with contextlib.suppress(AttributeError, TypeError, RuntimeError):
            self.dialog.preview_widget.btn_finalize.clicked.disconnect(
                self.dialog.tool_manager.measure_tool.finalize_measurement
            )

        with contextlib.suppress(AttributeError, TypeError, RuntimeError):
            self.dialog.preview_widget.chk_topo.stateChanged.disconnect(
                self.dialog.update_preview_from_checkboxes
            )
        with contextlib.suppress(AttributeError, TypeError, RuntimeError):
            self.dialog.preview_widget.chk_geol.stateChanged.disconnect(
                self.dialog.update_preview_from_checkboxes
            )
        with contextlib.suppress(AttributeError, TypeError, RuntimeError):
            self.dialog.preview_widget.chk_struct.stateChanged.disconnect(
                self.dialog.update_preview_from_checkboxes
            )
        with contextlib.suppress(AttributeError, TypeError, RuntimeError):
            self.dialog.preview_widget.chk_drillholes.stateChanged.disconnect(
                self.dialog.update_preview_from_checkboxes
            )
        with contextlib.suppress(AttributeError, TypeError, RuntimeError):
            self.dialog.preview_widget.chk_interpretations.stateChanged.disconnect(
                self.dialog.update_preview_from_checkboxes
            )
        with contextlib.suppress(AttributeError, TypeError, RuntimeError):
            self.dialog.preview_widget.chk_legend.stateChanged.disconnect(
                self.dialog.update_preview_from_checkboxes
            )

        with contextlib.suppress(AttributeError, TypeError, RuntimeError):
            self.dialog.preview_widget.spin_max_points.valueChanged.disconnect(
                self.dialog.update_preview_from_checkboxes
            )
        with contextlib.suppress(AttributeError, TypeError, RuntimeError):
            self.dialog.preview_widget.chk_auto_lod.toggled.disconnect(
                self.dialog.update_preview_from_checkboxes
            )
        with contextlib.suppress(AttributeError, TypeError, RuntimeError):
            self.dialog.preview_widget.chk_adaptive_sampling.toggled.disconnect(
                self.dialog.update_preview_from_checkboxes
            )

    def _disconnect_page_signals(self) -> None:
        """Disconnect page-specific signals."""
        with contextlib.suppress(TypeError, RuntimeError):
            self.dialog.output_widget.fileChanged.disconnect(self.dialog.update_button_state)

        with contextlib.suppress(TypeError, RuntimeError):
            self.dialog.page_dem.raster_combo.layerChanged.disconnect(
                self.dialog.update_button_state
            )
            self.dialog.page_dem.raster_combo.layerChanged.disconnect(
                self.dialog.update_preview_checkbox_states
            )

        with contextlib.suppress(TypeError, RuntimeError):
            self.dialog.page_section.line_combo.layerChanged.disconnect(
                self.dialog.update_button_state
            )
            self.dialog.page_section.line_combo.layerChanged.disconnect(
                self.dialog.update_preview_checkbox_states
            )

        with contextlib.suppress(TypeError, RuntimeError):
            self.dialog.page_geology.dataChanged.disconnect(
                self.dialog.update_preview_checkbox_states
            )
            self.dialog.page_struct.dataChanged.disconnect(
                self.dialog.update_preview_checkbox_states
            )
            self.dialog.page_drillhole.dataChanged.disconnect(
                self.dialog.update_preview_checkbox_states
            )

        # Recursively disconnect all pages
        pages = [
            self.dialog.page_dem,
            self.dialog.page_section,
            self.dialog.page_geology,
            self.dialog.page_struct,
            self.dialog.page_drillhole,
            self.dialog.page_interpretation,
            self.dialog.preview_widget,
            self.dialog.page_settings,
        ]
        for page in pages:
            if hasattr(page, "disconnect_signals"):
                with contextlib.suppress(Exception):
                    page.disconnect_signals()

    def _disconnect_tool_signals(self) -> None:
        """Disconnect map tool signals and window signals."""
        with contextlib.suppress(AttributeError, TypeError, RuntimeError):
            self.dialog.tool_manager.disconnect_signals()

        with contextlib.suppress(AttributeError, TypeError, RuntimeError):
            self.dialog.disconnect_signals()

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
        self.dialog.reset_defaults_btn.clicked.connect(self.dialog.reset_defaults_handler)

    def _connect_preview_signals(self) -> None:
        """Connect preview-related signals."""
        self.dialog.preview_widget.btn_preview.clicked.connect(self.dialog.preview_profile_handler)
        self.dialog.preview_widget.btn_export.clicked.connect(self.dialog.export_preview)

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
        self.dialog.page_dem.raster_combo.layerChanged.connect(self.dialog.update_button_state)
        self.dialog.page_dem.raster_combo.layerChanged.connect(
            self.dialog.update_preview_checkbox_states
        )

        # Section page
        self.dialog.page_section.line_combo.layerChanged.connect(self.dialog.update_button_state)
        self.dialog.page_section.line_combo.layerChanged.connect(
            self.dialog.update_preview_checkbox_states
        )

        # Data pages
        self.dialog.page_geology.dataChanged.connect(self.dialog.update_preview_checkbox_states)
        self.dialog.page_struct.dataChanged.connect(self.dialog.update_preview_checkbox_states)
        self.dialog.page_drillhole.dataChanged.connect(self.dialog.update_preview_checkbox_states)

    def _connect_tool_signals(self) -> None:
        """Connect map tool signals."""
        self.dialog.preview_widget.btn_measure.toggled.connect(self.dialog.toggle_measure_tool)
        self.dialog.preview_widget.btn_interpret.toggled.connect(
            self.dialog.toggle_interpretation_tool
        )
        self.dialog.preview_widget.btn_finalize.clicked.connect(
            self.dialog.tool_manager.measure_tool.finalize_measurement
        )
