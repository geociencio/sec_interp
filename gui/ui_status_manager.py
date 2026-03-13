"""UI Status and indication manager for SecInterp main dialog."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qgis.PyQt.QtWidgets import QDialogButtonBox

if TYPE_CHECKING:
    from sec_interp.gui.main_dialog import SecInterpDialog  # type: ignore


class UIStatusManager:
    """Manages visual status (indicators, icons, button enablement) of the dialog."""

    def __init__(self, dialog: SecInterpDialog) -> None:
        """Initialize UI status manager."""
        self.dialog = dialog
        self._warning_icon = None
        self._success_icon = None

    def setup_indicators(self) -> None:
        """Set up required field indicators with warning icons."""
        self._warning_icon = self.dialog.getThemeIcon("mMessageLogCritical.svg")
        self._success_icon = self.dialog.getThemeIcon("mIconSuccess.svg")

        # Initial update
        self.update_raster_status()
        self.update_section_status()

    def update_all(self) -> None:
        """Update all visual status components."""
        self.update_button_state()
        self.update_preview_checkbox_states()
        self.update_raster_status()
        self.update_section_status()

    def update_preview_checkbox_states(self) -> None:
        """Enable or disable preview checkboxes based on input validity."""
        im = self.dialog.input_manager
        has_section = im.is_section_valid("section")
        has_dem = im.is_section_valid("dem")

        pw = self.dialog.preview_widget
        pw.chk_topo.setEnabled(has_dem and has_section)
        pw.chk_geol.setEnabled(im.is_section_valid("geology") and has_section)
        pw.chk_struct.setEnabled(im.is_section_valid("structure") and has_section)
        pw.chk_drillholes.setEnabled(im.is_section_valid("drillhole") and has_section)

    def update_button_state(self) -> None:
        """Enable or disable buttons based on input validity."""
        im = self.dialog.input_manager
        can_preview = im.can_preview()

        self.dialog.preview_widget.btn_preview.setEnabled(can_preview)
        self.dialog.button_box.button(QDialogButtonBox.Ok).setEnabled(can_preview)

        if hasattr(self.dialog, "btn_save"):
            self.dialog.btn_save.setEnabled(im.can_export())

    def update_raster_status(self) -> None:
        """Update raster layer status icon."""
        if not self._warning_icon:
            return
        im = self.dialog.input_manager
        label = self.dialog.page_dem.lbl_raster_status
        if im.is_section_valid("dem"):
            label.setPixmap(self._success_icon.pixmap(16, 16))
            label.setToolTip(self.dialog.tr("Raster layer selected"))
        else:
            label.setPixmap(self._warning_icon.pixmap(16, 16))
            label.setToolTip(im.get_section_error("dem"))

    def update_section_status(self) -> None:
        """Update section line status icon."""
        if not self._warning_icon:
            return
        im = self.dialog.input_manager
        label = self.dialog.page_section.lbl_section_status
        if im.is_section_valid("section"):
            label.setPixmap(self._success_icon.pixmap(16, 16))
            label.setToolTip(self.dialog.tr("Section line selected"))
        else:
            label.setPixmap(self._warning_icon.pixmap(16, 16))
            label.setToolTip(im.get_section_error("section"))
