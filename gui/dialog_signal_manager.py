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
                ok_btn.clicked.disconnect(self.dialog.accept_handler)

        cancel_btn = self.dialog.button_box.button(QDialogButtonBox.Cancel)
        if cancel_btn:
            with contextlib.suppress(TypeError, RuntimeError):
                cancel_btn.clicked.disconnect(self.dialog.reject_handler)

        save_btn = self.dialog.button_box.button(QDialogButtonBox.Save)
        if save_btn:
            with contextlib.suppress(TypeError, RuntimeError):
                save_btn.clicked.disconnect(self.dialog.export_manager.export_data)

        with contextlib.suppress(TypeError, RuntimeError):
            self.dialog.button_box.helpRequested.disconnect(self.dialog.open_help)

        with contextlib.suppress(TypeError, RuntimeError):
            self.dialog.clear_cache_btn.clicked.disconnect(self.dialog.clear_cache_handler)

    def _disconnect_preview_signals(self) -> None:
        """Disconnect preview-related signals."""
        preview_btns = [
            (
                self.dialog.preview_widget.btn_preview,
                self.dialog.preview_profile_handler,
            ),
            (self.dialog.preview_widget.btn_export, self.dialog.export_preview),
            (self.dialog.preview_widget.btn_measure, self.dialog.toggle_measure_tool),
            (
                self.dialog.preview_widget.btn_interpret,
                self.dialog.toggle_interpretation_tool,
            ),
        ]
        for btn, slot in preview_btns:
            with contextlib.suppress(AttributeError, TypeError, RuntimeError):
                btn.clicked.disconnect(slot)
            with contextlib.suppress(AttributeError, TypeError, RuntimeError):
                btn.toggled.disconnect(slot)

        preview_chks = [
            self.dialog.preview_widget.chk_topo,
            self.dialog.preview_widget.chk_geol,
            self.dialog.preview_widget.chk_struct,
            self.dialog.preview_widget.chk_drillholes,
            self.dialog.preview_widget.chk_interpretations,
            self.dialog.preview_widget.chk_legend,
        ]
        for chk in preview_chks:
            with contextlib.suppress(AttributeError, TypeError, RuntimeError):
                chk.stateChanged.disconnect(self.dialog.update_preview_from_checkboxes)

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
        sm = self.dialog.state_manager

        ok_btn = self.dialog.button_box.button(QDialogButtonBox.Ok)
        if ok_btn:
            sm._connect_checked(ok_btn, ok_btn.clicked, self.dialog.accept_handler)

        cancel_btn = self.dialog.button_box.button(QDialogButtonBox.Cancel)
        if cancel_btn:
            sm._connect_checked(cancel_btn, cancel_btn.clicked, self.dialog.reject_handler)

        save_btn = self.dialog.button_box.button(QDialogButtonBox.Save)
        if save_btn:
            sm._connect_checked(save_btn, save_btn.clicked, self.dialog.export_manager.export_data)

        sm._connect_checked(
            self.dialog.button_box, self.dialog.button_box.helpRequested, self.dialog.open_help
        )
        sm._connect_checked(
            self.dialog.clear_cache_btn,
            self.dialog.clear_cache_btn.clicked,
            self.dialog.clear_cache_handler,
        )

    def _connect_preview_signals(self) -> None:
        """Connect preview-related signals."""
        sm = self.dialog.state_manager
        pw = self.dialog.preview_widget

        sm._connect_checked(
            pw.btn_preview, pw.btn_preview.clicked, self.dialog.preview_profile_handler
        )
        sm._connect_checked(pw.btn_export, pw.btn_export.clicked, self.dialog.export_preview)

        # Preview layer checkboxes
        for chk in [
            pw.chk_topo,
            pw.chk_geol,
            pw.chk_struct,
            pw.chk_drillholes,
            pw.chk_interpretations,
            pw.chk_legend,
        ]:
            sm._connect_checked(chk, chk.stateChanged, self.dialog.update_preview_from_checkboxes)

        # Preview settings
        sm._connect_checked(
            pw.spin_max_points,
            pw.spin_max_points.valueChanged,
            self.dialog.update_preview_from_checkboxes,
        )
        sm._connect_checked(
            pw.chk_auto_lod, pw.chk_auto_lod.toggled, self.dialog.update_preview_from_checkboxes
        )
        sm._connect_checked(
            pw.chk_adaptive_sampling,
            pw.chk_adaptive_sampling.toggled,
            self.dialog.update_preview_from_checkboxes,
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
        sm = self.dialog.state_manager
        pw = self.dialog.preview_widget
        mt = self.dialog.tool_manager.measure_tool

        sm._connect_checked(pw.btn_measure, pw.btn_measure.toggled, self.dialog.toggle_measure_tool)
        sm._connect_checked(
            pw.btn_interpret, pw.btn_interpret.toggled, self.dialog.toggle_interpretation_tool
        )
        sm._connect_checked(pw.btn_finalize, pw.btn_finalize.clicked, mt.finalize_measurement)

        sm._connect_checked(mt, mt.measurementChanged, self.dialog.update_measurement_display)
        sm._connect_checked(mt, mt.measurementFinished, lambda: pw.btn_measure.setChecked(False))
        sm._connect_checked(mt, mt.measurementCleared, lambda: pw.results_text.clear())
