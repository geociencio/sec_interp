from __future__ import annotations

"""Validation manager for SecInterp main dialog.

This module provides a declarative way to define and execute validation rules
for the main dialog UI, separating UI logic from core business rules.
"""

from typing import TYPE_CHECKING

from sec_interp.core.exceptions import ValidationError
from sec_interp.core.validation.project_validator import ProjectValidator

if TYPE_CHECKING:
    from sec_interp.gui.main_dialog import SecInterpDialog


class DialogValidationManager:
    """Manages UI-level validation rules and state."""

    def __init__(self, dialog: SecInterpDialog) -> None:
        """Initialize validation manager.

        Args:
            dialog: The main dialog instance.

        """
        self.dialog = dialog
        self._setup_rules()

    def _setup_rules(self) -> None:
        """Define validation rules declaratively."""
        # Rules return (is_valid, error_message, field_id)
        self.rules = {
            "dem": {
                "check": lambda p: bool(p.raster_layer),
                "message": self.dialog.tr("Raster DEM layer is required"),
                "field": "raster_layer",
            },
            "section": {
                "check": lambda p: bool(p.line_layer),
                "message": self.dialog.tr("Cross-section line layer is required"),
                "field": "line_layer",
            },
            "output": {
                "check": lambda p: bool(p.output_path),
                "message": self.dialog.tr("Output directory path is required"),
                "field": "output_path",
            },
            "geology": {
                "check": lambda p: (
                    ProjectValidator.is_geology_complete(p) if p.outcrop_layer else True
                ),
                "message": self.dialog.tr("Geology configuration is incomplete"),
                "field": "outcrop_layer",
            },
            "structure": {
                "check": lambda p: (
                    ProjectValidator.is_structure_complete(p) if p.struct_layer else True
                ),
                "message": self.dialog.tr("Structure configuration is incomplete"),
                "field": "struct_layer",
            },
            "drillhole": {
                "check": lambda p: (
                    ProjectValidator.is_drillhole_complete(p) if p.collar_layer else True
                ),
                "message": self.dialog.tr("Drillhole configuration is incomplete"),
                "field": "collar_layer",
            },
        }

    def validate_inputs(self) -> tuple[bool, str]:
        """Validate all dialog inputs by delegating to core.

        Returns:
            A tuple containing (is_valid, error_message).

        """
        params = self.dialog.data_aggregator.get_validation_params()
        try:
            ProjectValidator.validate_all(params)
            return True, ""
        except ValidationError as e:
            return False, str(e)

    def validate_preview_requirements(self) -> tuple[bool, str]:
        """Validate minimum requirements for preview.

        Returns:
            A tuple containing (is_valid, error_message).

        """
        params = self.dialog.data_aggregator.get_validation_params()
        try:
            ProjectValidator.validate_preview_requirements(params)
            return True, ""
        except ValidationError as e:
            return False, str(e)

    def is_section_valid(self, section: str) -> bool:
        """Check if a specific section is valid based on declarative rules.

        Args:
            section: The section key (e.g., 'dem', 'section').

        Returns:
            True if valid.

        """
        if section not in self.rules:
            return True

        params = self.dialog.data_aggregator.get_validation_params()
        return self.rules[section]["check"](params)

    def get_section_error(self, section: str) -> str:
        """Get error message for a section if invalid.

        Args:
            section: The section key.

        Returns:
            Error message or empty string.

        """
        if self.is_section_valid(section):
            return ""
        return self.rules[section]["message"]

    def can_preview(self) -> bool:
        """Check if basic requirements for preview are met.

        Returns:
            True if preview is possible.

        """
        # Shortcut for common check: DEM + Section
        return self.is_section_valid("dem") and self.is_section_valid("section")

    def can_export(self) -> bool:
        """Check if requirements for export/save are met.

        Returns:
            True if export is possible.

        """
        return self.can_preview() and self.is_section_valid("output")
