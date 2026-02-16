"""Interface for 3D Rendering Engines."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from sec_interp.core.domain.dtos import PreviewResult


class IRenderer3D(ABC):
    """Interface for engines that can render profile data in 3D space."""

    @abstractmethod
    def render_3d(self, data: PreviewResult, **kwargs: Any) -> bool:
        """Render the provided data in a 3D context.

        Args:
            data: The processed profile data containing SpatialMeta.
            **kwargs: Implementation specific rendering options.

        Returns:
            True if rendering was successful.

        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear the 3D scene."""
        pass
