"""UI status management module for SecInterp main dialog.

This module handles updating button states, preview checkboxes, and 
required field indicators.
"""

from typing import TYPE_CHECKING
from qgis.core import Qgis
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import QDialogButtonBox

if TYPE_CHECKING:
    from .main_dialog import SecInterpDialog

class DialogStatusManager:
    """Manages UI state and status indicators."""

    def __init__(self, dialog: "SecInterpDialog"):
        """Initialize status manager with reference to parent dialog."""
        self.dialog = dialog

    def update_all(self) -> None:
        """Update all UI status components."""
        self.update_button_state()
        self.update_preview_checkbox_states()
        self.update_raster_status()
        self.update_section_status()

    def update_preview_checkbox_states(self) -> None:
        """Enable or disable preview checkboxes based on input validity."""
        has_section = bool(self.dialog.page_section.line_combo.currentLayer())
        has_dem = bool(self.dialog.page_dem.raster_combo.currentLayer())
        
        # Topography requires DEM + Section Line
        self.dialog.preview_widget.chk_topo.setEnabled(has_dem and has_section)
        
        # Geology requires Geology Data + Section Line
        has_geol = self.dialog.page_geology.is_complete()
        self.dialog.preview_widget.chk_geol.setEnabled(has_geol and has_section)
        
        # Structure requires Structure Data + Section Line
        has_struct = self.dialog.page_struct.is_complete()
        self.dialog.preview_widget.chk_struct.setEnabled(has_struct and has_section)
        
        # Drillhole requires Drillhole Data + Section Line
        has_drill = self.dialog.page_drillhole.is_complete()
        self.dialog.preview_widget.chk_drillholes.setEnabled(has_drill and has_section)

    def update_button_state(self) -> None:
        """Enable or disable buttons based on input validity."""
        has_section = bool(self.dialog.page_section.line_combo.currentLayer())
        has_dem = bool(self.dialog.page_dem.raster_combo.currentLayer())
        has_output = bool(self.dialog.output_widget.filePath())

        # Preview requires: DEM + Cross-section line
        can_preview = has_dem and has_section
        self.dialog.preview_widget.btn_preview.setEnabled(can_preview)

        # OK button requires basic validation
        self.dialog.button_box.button(QDialogButtonBox.Ok).setEnabled(can_preview)

        # Export (Save) button requires: DEM + Cross-section line + Output path
        # Note: Save button might be part of buttonBox or separate. 
        # In this plugin it usually uses the standard Ok button or a "Process" button.
        # If there's an explicit Save button in some versions:
        if hasattr(self.dialog, 'btn_save'):
            self.dialog.btn_save.setEnabled(can_preview and has_output)

    def setup_indicators(self) -> None:
        """Setup required field indicators with warning icons."""
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
        layer = self.dialog.page_dem.raster_combo.currentLayer()
        label = self.dialog.page_dem.lbl_raster_status
        if layer:
            label.setPixmap(self._success_icon.pixmap(16, 16))
            label.setToolTip("Raster layer selected")
        else:
            label.setPixmap(self._warning_icon.pixmap(16, 16))
            label.setToolTip("Raster layer is required")

    def update_section_status(self) -> None:
        """Update section line status icon based on selection."""
        layer = self.dialog.page_section.line_combo.currentLayer()
        label = self.dialog.page_section.lbl_section_status
        if layer:
            label.setPixmap(self._success_icon.pixmap(16, 16))
            label.setToolTip("Section line selected")
        else:
            label.setPixmap(self._warning_icon.pixmap(16, 16))
            label.setToolTip("Section line is required")
