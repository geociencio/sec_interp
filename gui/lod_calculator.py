"""LOD Calculation for SecInterp preview."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qgis.gui import QgsMapCanvas


class LODCalculator:
    """Calculates Level of Detail (LOD) based on canvas zoom levels."""

    def __init__(self, canvas: QgsMapCanvas) -> None:
        """Initialize the LOD calculator.

        Args:
            canvas: The map canvas to calculate LOD for.

        """
        self.canvas = canvas

    def calculate_max_points(self) -> int:
        """Determine ideal point density based on current zoom.

        Returns:
            int: The maximum number of points to render.

        """
        # Simple heuristic based on diagonal length in map units vs section length
        if not self.canvas:
            return 1000

        extent = self.canvas.extent()
        diag = extent.width() + extent.height()

        LOW_RES_THRESHOLD = 5000
        HIGH_RES_THRESHOLD = 500
        LOW_RES_POINTS = 500
        HIGH_RES_POINTS = 2000
        DEFAULT_POINTS = 1000

        # Low density for wide views, high density for closeups
        if diag > LOW_RES_THRESHOLD:
            return LOW_RES_POINTS
        if diag < HIGH_RES_THRESHOLD:
            return HIGH_RES_POINTS
        return DEFAULT_POINTS
