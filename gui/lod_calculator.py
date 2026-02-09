from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qgis.gui import QgsMapCanvas


class LODCalculator:
    """Calculates Level of Detail (LOD) based on canvas zoom levels."""

    def __init__(self, canvas: QgsMapCanvas):
        self.canvas = canvas

    def calculate_max_points(self) -> int:
        """Determine ideal point density based on current zoom."""
        # Simple heuristic based on diagonal length in map units vs section length
        if not self.canvas:
            return 1000

        extent = self.canvas.extent()
        diag = extent.width() + extent.height()

        # Low density for wide views, high density for closeups
        if diag > 5000:
            return 500
        if diag < 500:
            return 2000
        return 1000
