"""Pipeline for executing multiple validators."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from .base_validator import IValidator

if TYPE_CHECKING:
    from .project_validator import ValidationParams
    from .validation_helpers import ValidationContext


class ValidationPipeline:
    """Orchestrates the execution of multiple IValidator instances."""

    def __init__(self, validators: Iterable[IValidator] | None = None) -> None:
        """Initialize pipeline with optional list of validators."""
        self._validators: list[IValidator] = list(validators) if validators else []

    def add_validator(self, validator: IValidator) -> None:
        """Add a validator to the pipeline."""
        self._validators.append(validator)

    def execute(self, params: ValidationParams, context: ValidationContext) -> None:
        """Execute all validators in sequence."""
        for validator in self._validators:
            validator.validate(params, context)
