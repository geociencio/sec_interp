from __future__ import annotations

"""Interface for Preview services."""

from abc import ABC, abstractmethod
from typing import Any


class IPreviewService(ABC):
    """Abstract interface for the Preview Orchestration Service."""

    @abstractmethod
    def generate_all(self, params: Any, transform_context: Any, **kwargs: Any) -> Any:
        """Generate all preview components in a consolidated result.

        Args:
            params: Validated parameters for preview generation.
            transform_context: QgsCoordinateTransformContext from map settings.
            **kwargs: Additional generation options (e.g., skip filters).

        Returns:
            PreviewResult: Consolidated preview results object.

        """
        pass
