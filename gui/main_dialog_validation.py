"""Validation module for SecInterp main dialog.

This module handles all validation logic for dialog inputs,
separating concerns and making the code more testable and maintainable.
"""

from typing import TYPE_CHECKING

from sec_interp.core.exceptions import ValidationError
from sec_interp.core.validation.project_validator import ProjectValidator

if TYPE_CHECKING:
    from sec_interp.gui.main_dialog import SecInterpDialog


class DialogValidator:
    """Handles all validation logic for SecInterpDialog by collecting data
    and delegating to the core ProjectValidator.
    """

    def __init__(self, dialog: "SecInterpDialog") -> None:
        """Initialize validator with reference to parent dialog.

        Args:
            dialog: The main dialog instance.

        """
        self.dialog = dialog

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
        """Validate minimum requirements for preview by delegating to core.

        Returns:
            A tuple containing (is_valid, error_message).

        """
        params = self.dialog.data_aggregator.get_validation_params()
        try:
            ProjectValidator.validate_preview_requirements(params)
            return True, ""
        except ValidationError as e:
            return False, str(e)
