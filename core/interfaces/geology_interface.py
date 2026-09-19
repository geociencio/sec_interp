"""Interface for Geology services."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from sec_interp.core.domain.task_inputs import GeologyContext


class IGeologyService(ABC):
    """Abstract interface for the Geological Profiling Service."""

    @abstractmethod
    def build_segments(self, context: GeologyContext, feedback: Any | None = None) -> Any:
        """Build geological segments from a detached context.

        Args:
            context: Fully-detached geology data (Extract output).
            feedback: Optional feedback object for progress/cancellation.

        Returns:
            GeologyData: List of GeologySegment objects.

        """
        pass
