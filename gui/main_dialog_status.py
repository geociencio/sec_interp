"""UI status management module for SecInterp main dialog.

This module handles updating button states, preview checkboxes, and
required field indicators.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from qgis.PyQt.QtWidgets import QDialogButtonBox

if TYPE_CHECKING:
    pass


class DialogStatusManager:
    """Manage the status bar and indicators for the main dialog."""

    def __init__(self, dialog: SecInterpDialog) -> None:
        """Initialize status manager with reference to parent dialog.

        Args:
            dialog: The :class:`sec_interp.gui.main_dialog.SecInterpDialog` instance

        """
        self.dialog = dialog

    def update_all(self) -> None:
        """Update all UI status components."""
        self.update_button_state()
        self.update_preview_checkbox_states()
        self.update_raster_status()
        self.update_section_status()

    def update_preview_checkbox_states(self) -> None:
        """Enable or disable preview checkboxes based on input validity."""
        vm = self.dialog.validation_manager
        has_section = vm.is_section_valid("section")
        has_dem = vm.is_section_valid("dem")

        # Topography requires DEM + Section Line
        self.dialog.preview_widget.chk_topo.setEnabled(has_dem and has_section)

        # Geology requires Geology Data + Section Line
        self.dialog.preview_widget.chk_geol.setEnabled(
            vm.is_section_valid("geology") and has_section
        )

        # Structure requires Structure Data + Section Line
        self.dialog.preview_widget.chk_struct.setEnabled(
            vm.is_section_valid("structure") and has_section
        )

        # Drillhole requires Drillhole Data + Section Line
        self.dialog.preview_widget.chk_drillholes.setEnabled(
            vm.is_section_valid("drillhole") and has_section
        )

    def update_button_state(self) -> None:
        """Enable or disable buttons based on input validity."""
        vm = self.dialog.validation_manager
        can_preview = vm.can_preview()

        # Preview requires: DEM + Cross-section line
        self.dialog.preview_widget.btn_preview.setEnabled(can_preview)

        # OK button requires basic validation
        self.dialog.button_box.button(QDialogButtonBox.Ok).setEnabled(can_preview)

        # Export (Save) button requires: DEM + Cross-section line + Output path
        if hasattr(self.dialog, "btn_save"):
            self.dialog.btn_save.setEnabled(vm.can_export())

    def setup_indicators(self) -> None:
        """Set up required field indicators with warning icons."""
        warning_icon = self.dialog.getThemeIcon("mMessageLogCritical.svg")
        success_icon = self.dialog.getThemeIcon("mIconSuccess.svg")

        # Store icons for later use
        self._warning_icon = warning_icon
        self._success_icon = success_icon

        # Initial update
        self.update_raster_status()
        self.update_section_status()

    def update_raster_status(self) -> None:
        """Update raster layer status icon based on selection."""
        vm = self.dialog.validation_manager
        label = self.dialog.page_dem.lbl_raster_status
        if vm.is_section_valid("dem"):
            label.setPixmap(self._success_icon.pixmap(16, 16))
            label.setToolTip(self.dialog.tr("Raster layer selected"))
        else:
            label.setPixmap(self._warning_icon.pixmap(16, 16))
            label.setToolTip(vm.get_section_error("dem"))

    def update_section_status(self) -> None:
        """Update section line status icon based on selection."""
        vm = self.dialog.validation_manager
        label = self.dialog.page_section.lbl_section_status
        if vm.is_section_valid("section"):
            label.setPixmap(self._success_icon.pixmap(16, 16))
            label.setToolTip(self.dialog.tr("Section line selected"))
        else:
            label.setPixmap(self._warning_icon.pixmap(16, 16))
            label.setToolTip(vm.get_section_error("section"))
