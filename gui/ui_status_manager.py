"""UI Status and indication manager for SecInterp main dialog."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qgis.PyQt.QtCore import Qt
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
        self.update_page_states()
        self.update_preview_checkbox_states()
        self.update_raster_status()
        self.update_section_status()

    def update_page_states(self) -> None:
        """Enable dependent pages only when DEM and Section are valid.

        Geology/Structural/Drillholes stay disabled until the two mandatory
        inputs are filled; if the visible page becomes disabled, fall back
        to the DEM page.
        """
        im = self.dialog.input_manager
        ready = bool(im.is_section_valid("dem") and im.is_section_valid("section"))
        for attr in ("nav_geology", "nav_struct", "nav_drillhole"):
            item = getattr(self.dialog, attr, None)
            if item is None:
                continue
            self._set_item_enabled(item, ready)
        if not ready:
            sidebar = getattr(self.dialog, "sidebar", None)
            if sidebar is not None and sidebar.currentRow() in (2, 3, 4):
                sidebar.setCurrentRow(0)

    @staticmethod
    def _set_item_enabled(item: Any, enabled: bool) -> None:
        """Enable or disable a ``QListWidgetItem`` through its flags.

        ``QListWidgetItem`` has no ``setDisabled`` (that is a ``QWidget``
        method); item interactivity is controlled by the
        ``Qt.ItemFlag.ItemIsEnabled`` flag.
        """
        flags = item.flags()
        if enabled:
            flags |= Qt.ItemFlag.ItemIsEnabled
        else:
            flags &= ~Qt.ItemFlag.ItemIsEnabled
        item.setFlags(flags)

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
        """Enable or disable buttons (S0/S1/S2 gating).

        S0 (DEM/Section incomplete): everything disabled. S1 (inputs valid,
        no current preview): only Preview and OK. S2 (preview generated for
        the current inputs): Export/Measure/Interpret join in.
        """
        im = self.dialog.input_manager
        can_preview = im.can_preview()
        preview_current = bool(can_preview) and self._is_preview_current()

        pw = self.dialog.preview_widget
        pw.btn_preview.setEnabled(can_preview)
        self.dialog.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(can_preview)
        pw.btn_export.setEnabled(preview_current)
        pw.btn_measure.setEnabled(preview_current)
        pw.btn_interpret.setEnabled(preview_current)

        if hasattr(self.dialog, "btn_save"):
            self.dialog.btn_save.setEnabled(im.can_export())

    def _is_preview_current(self) -> bool:
        """Check whether a preview was generated for the current inputs.

        Fail-closed: without a preview manager (or on any error) the
        dependent buttons stay disabled.
        """
        pm = getattr(self.dialog, "preview_manager", None)
        is_current = getattr(pm, "is_preview_current", None)
        if not callable(is_current):
            return False
        try:
            return bool(is_current())
        except Exception:
            return False

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
