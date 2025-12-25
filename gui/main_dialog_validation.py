"""Validation module for SecInterp main dialog.

This module handles all validation logic for dialog inputs,
separating concerns and making the code more testable and maintainable.
"""

from typing import TYPE_CHECKING, Optional

from qgis.core import QgsRasterLayer, QgsVectorLayer, QgsWkbTypes
from qgis.PyQt.QtCore import QVariant

from sec_interp.core import validation as vu

from .main_dialog_config import ValidationMessages


if TYPE_CHECKING:
    from .main_dialog import SecInterpDialog


class DialogValidator:
    """Handles all validation logic for SecInterpDialog by collecting data
    and delegating to the core ProjectValidator.
    """

    def __init__(self, dialog: "sec_interp.gui.main_dialog.SecInterpDialog"):
        """Initialize validator with reference to parent dialog.

        Args:
            dialog: The :class:`sec_interp.gui.main_dialog.SecInterpDialog` instance to validate
        """
        self.dialog = dialog

    def _collect_params(self) -> vu.ValidationParams:
        """Collect all parameters from the UI widgets."""
        return vu.ValidationParams(
            raster_layer=self.dialog.page_dem.raster_combo.currentLayer(),
            band_number=self.dialog.page_dem.band_combo.currentBand(),
            line_layer=self.dialog.page_section.line_combo.currentLayer(),
            output_path=self.dialog.output_widget.filePath(),
            scale=self.dialog.page_dem.scale_spin.value(),
            vert_exag=self.dialog.page_dem.vertexag_spin.value(),
            buffer_dist=self.dialog.page_section.buffer_spin.value(),
            outcrop_layer=self.dialog.page_geology.layer_combo.currentLayer(),
            outcrop_field=self.dialog.page_geology.field_combo.currentData(),
            struct_layer=self.dialog.page_struct.layer_combo.currentLayer(),
            struct_dip_field=self.dialog.page_struct.dip_combo.currentData(),
            struct_strike_field=self.dialog.page_struct.strike_combo.currentData(),
            dip_scale_factor=self.dialog.page_struct.scale_spin.value(),
        )

    def validate_inputs(self) -> tuple[bool, str]:
        """Validate all dialog inputs by delegating to core."""
        params = self._collect_params()
        return vu.ProjectValidator.validate_all(params)

    def validate_preview_requirements(self) -> tuple[bool, str]:
        """Validate minimum requirements for preview by delegating to core."""
        params = self._collect_params()
        return vu.ProjectValidator.validate_preview_requirements(params)
