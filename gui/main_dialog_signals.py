"""Signal management module for SecInterp main dialog.

This module handles all signal connections for the dialog,
separating signal setup from the main dialog class.
"""

from typing import TYPE_CHECKING

from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


if TYPE_CHECKING:
    from .main_dialog import SecInterpDialog


class DialogSignalManager:
    """Manages all signal connections for SecInterpDialog.

    This class organizes signal connections into logical groups,
    making the dialog initialization cleaner and more maintainable.
    """

    def __init__(self, dialog: "sec_interp.gui.main_dialog.SecInterpDialog"):
        """Initialize signal manager.

        Args:
            dialog: The :class:`sec_interp.gui.main_dialog.SecInterpDialog` instance
        """
        self.dialog = dialog

    def connect_all(self):
        """Connect all signals in organized groups."""
        self._connect_button_signals()
        self._connect_preview_signals()
        self._connect_page_signals()
        self._connect_tool_signals()

    def _connect_button_signals(self):
        """Connect dialog button signals."""
        # Main dialog buttons
        self.dialog.button_box.accepted.connect(self.dialog.accept_handler)
        self.dialog.button_box.rejected.connect(self.dialog.reject_handler)
        self.dialog.button_box.helpRequested.connect(self.dialog.open_help)

        # Clear cache button
        self.dialog.clear_cache_btn.clicked.connect(self.dialog.clear_cache_handler)

    def _connect_preview_signals(self):
        """Connect preview-related signals."""
        # Preview action buttons
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

    def _connect_page_signals(self):
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

    def _connect_tool_signals(self):
        """Connect map tool signals."""
        # Measure tool
        self.dialog.preview_widget.btn_measure.toggled.connect(
            self.dialog.toggle_measure_tool
        )

        # Finalize button with debug wrapper
        def finalize_with_log():
            logger.info("Finalize button clicked!")
            self.dialog.measure_tool.finalize_measurement()

        self.dialog.preview_widget.btn_finalize.clicked.connect(finalize_with_log)

        self.dialog.measure_tool.measurementChanged.connect(
            self.dialog.update_measurement_display
        )
        self.dialog.measure_tool.measurementCleared.connect(
            lambda: self.dialog.preview_widget.results_text.clear()
        )
