from abc import ABC, abstractmethod
from typing import Any, Optional

from qgis.core import QgsRasterLayer, QgsVectorLayer


class IPreviewService(ABC):
    """Abstract interface for the Preview Orchestration Service."""

    @abstractmethod
    def generate_all(self, params: Any, transform_context: Any) -> Any:
        """Generate all preview components in a consolidated result.

        Args:
            params: Validated parameters for preview generation.
            transform_context: QgsCoordinateTransformContext from map settings.

        Returns:
            PreviewResult: Consolidated preview results object.
        """
        pass
