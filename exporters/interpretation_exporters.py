"""Interpretation exporters for SecInterp.

This module provides exporters for 2D and 2.5D interpretation data,
leveraging the base Shapefile and CSV exporters.
"""

from pathlib import Path
from typing import Any

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsWkbTypes,
)

from sec_interp.logger_config import get_logger
from .shp_exporter import ShapefileExporter


logger = get_logger(__name__)


class Interpretation25DExporter(ShapefileExporter):
    """Exporter for 2.5D interpretations (with M coordinates)."""

    def export_interpretations(
        self,
        output_path: Path,
        interpretations: list[Any],
        crs: QgsCoordinateReferenceSystem,
    ) -> bool:
        """Export a list of InterpretationPolygon25D objects to vector format.

        Args:
            output_path: Path to the output file (.shp or .gpkg)
            interpretations: List of InterpretationPolygon25D objects
            crs: The project's coordinate reference system

        Returns:
            bool: True if export was successful, False otherwise
        """
        if not interpretations:
            logger.warning("No interpretations to export.")
            return False

        features_data = []
        for interp in interpretations:
            # Flatten interpretation object for the base exporter
            features_data.append(
                {
                    "geometry": interp.geometry,
                    "attributes": {
                        "id": interp.id,
                        "name": interp.name,
                        "type": interp.type,
                        **interp.attributes,
                    },
                }
            )

        # Configure base exporter settings
        self.settings["geometry_type"] = QgsWkbTypes.PolygonM
        self.settings["crs"] = crs

        logger.info(
            f"Exporting {len(interpretations)} interpretations to {output_path}"
        )
        return self.export(output_path, features_data)
