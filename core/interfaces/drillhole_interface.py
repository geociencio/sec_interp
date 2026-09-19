"""Interface for Drillhole services."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from sec_interp.core.domain.task_inputs import DrillholeContext


class IDrillholeService(ABC):
    """Abstract interface for the Drillhole Processing Service."""

    @abstractmethod
    def process_context(self, context: DrillholeContext, feedback: Any | None = None) -> Any:
        """Process drillholes from a detached context.

        Args:
            context: Fully-detached drillhole data (Extract output).
            feedback: Optional feedback object for progress/cancellation.

        Returns:
            A tuple ``(geol_data, drillhole_data)``.

        """
        pass
