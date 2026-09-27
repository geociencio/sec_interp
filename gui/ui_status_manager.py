"""UI Status and indication manager for SecInterp main dialog."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qgis.core import Qgis
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QDialogButtonBox

if TYPE_CHECKING:
    from sec_interp.gui.main_dialog import SecInterpDialog  # type: ignore

# Generic traffic-light styles: no dependency on theme icon names or Qt style.
_STATUS_OK_STYLE = "background-color: #2e7d32; border-radius: 8px;"
_STATUS_ERROR_STYLE = "background-color: #c62828; border-radius: 8px;"
_STATUS_WARNING_STYLE = "background-color: #f9a825; border-radius: 8px;"


class UIStatusManager:
    """Manages visual status (indicators, icons, button enablement) of the dialog."""

    def __init__(self, dialog: SecInterpDialog) -> None:
        """Initialize UI status manager."""
        self.dialog = dialog

    def setup_indicators(self) -> None:
        """Paint the initial required-field indicators."""
        self.update_raster_status()
        self.update_section_status()

    def _apply_status(
        self,
        label: Any,
        ok: bool,
        ok_tooltip: str,
        error_tooltip: str,
        warning_tooltip: str = "",
    ) -> None:
        """Paint a status indicator as a colored dot.

        Uses a stylesheet dot (``background-color`` + ``border-radius``) so the
        state is always visible regardless of the active QGIS theme or Qt style.
        A non-empty ``warning_tooltip`` paints amber (valid but degraded).
        """
        label.clear()
        if not ok:
            label.setStyleSheet(_STATUS_ERROR_STYLE)
            label.setToolTip(error_tooltip)
        elif warning_tooltip:
            label.setStyleSheet(_STATUS_WARNING_STYLE)
            label.setToolTip(warning_tooltip)
        else:
            label.setStyleSheet(_STATUS_OK_STYLE)
            label.setToolTip(ok_tooltip)

    def update_all(self) -> None:
        """Update all visual status components."""
        self.update_button_state()
        self.update_page_states()
        self.update_preview_checkbox_states()
        self.update_raster_status()
        self.update_section_status()
        self._announce_crs_warnings()

    def _announce_crs_warnings(self) -> None:
        """Announce once per distinct CRS message.

        ``update_all`` runs on many signals, so a message is only pushed when
        the text actually changes (including clearing it). A mislabelled CRS is
        blocking (critical); a plain CRS mismatch is a warning.
        """
        im = self.dialog.input_manager
        plausibility = im.get_crs_plausibility_error()
        mismatch = im.get_crs_warning()
        signature = (plausibility, mismatch)
        if signature == getattr(self, "_last_crs_signature", None):
            return
        self._last_crs_signature = signature
        if plausibility:
            self.dialog.push_message(
                self.dialog.tr("Possible CRS mislabel"),
                plausibility,
                level=Qgis.MessageLevel.Critical,
                duration=10,
            )
        elif mismatch:
            self.dialog.push_message(
                self.dialog.tr("CRS mismatch"),
                mismatch,
                level=Qgis.MessageLevel.Warning,
                duration=10,
            )

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
        pw.btn_preview.setToolTip(
            self.dialog.tr("Generate preview") if can_preview else self._preview_blocked_reason()
        )
        self.dialog.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(can_preview)
        pw.btn_export.setEnabled(preview_current)
        pw.btn_measure.setEnabled(preview_current)
        pw.btn_interpret.setEnabled(preview_current)

        if hasattr(self.dialog, "btn_save"):
            self.dialog.btn_save.setEnabled(im.can_export())

    def _preview_blocked_reason(self) -> str:
        """Return the human-readable reason why Preview is disabled."""
        im = self.dialog.input_manager
        return (
            im.get_section_error("section")
            or im.get_section_error("dem")
            or im.get_crs_plausibility_error()
            or self.dialog.tr("Complete the required inputs")
        )

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
        """Update raster layer status icon (red on mislabel, amber on mismatch)."""
        im = self.dialog.input_manager
        ok = im.is_section_valid("dem")
        plausibility = im.get_crs_plausibility_error()
        if plausibility:
            self._apply_status(
                self.dialog.page_dem.lbl_raster_status,
                False,
                self.dialog.tr("Raster layer selected"),
                plausibility,
            )
            return
        warning = im.get_crs_warning() if ok else ""
        self._apply_status(
            self.dialog.page_dem.lbl_raster_status,
            ok,
            self.dialog.tr("Raster layer selected"),
            im.get_section_error("dem"),
            warning_tooltip=warning,
        )

    def update_section_status(self) -> None:
        """Update section line status icon."""
        im = self.dialog.input_manager
        ok = im.is_section_valid("section")
        self._apply_status(
            self.dialog.page_section.lbl_section_status,
            ok,
            self.dialog.tr("Section line selected"),
            im.get_section_error("section"),
        )
