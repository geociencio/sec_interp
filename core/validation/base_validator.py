"""Base interface for project validators."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .project_validator import ValidationParams
    from .validation_helpers import ValidationContext


class IValidator(ABC):
    """Interface for specialized validators."""

    @abstractmethod
    def validate(self, params: ValidationParams, context: ValidationContext) -> None:
        """Execute validation logic.

        Args:
            params: Parameters to validate.
            context: Context to accumulate errors.

        """
        pass
