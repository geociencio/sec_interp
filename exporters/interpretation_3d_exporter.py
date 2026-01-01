"""3D Interpretation Exporter.

This module provides the exporter for 3D geological interpretations.
"""

from __future__ import annotations

import math
from typing import Any, List

from qgis.core import (
    QgsFeature,
    QgsField,
    QgsGeometry,
    QgsPoint,
    QgsWkbTypes,
    QgsCoordinateReferenceSystem,
    QgsPolygon,
    QgsLineString,
)
from qgis.PyQt.QtCore import QVariant

from sec_interp.core.exceptions import ExportError
from sec_interp.exporters.base_exporter import BaseExporter
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class Interpretation3DExporter(BaseExporter):
    """Exporter for 3D Interpretation polygons (Shapefile 2.5D)."""

    def get_supported_extensions(self) -> list[str]:
        """Get supported extensions."""
        return [".shp"]

    def export(self, output_path: str, data: dict[str, Any]) -> bool:
        """Export interpretation data to a 3D Shapefile.

        Args:
            output_path: Destination path for the shapefile.
            data: Dictionary containing:
                - 'interpretations': List of InterpretationPolygon objects.
                - 'section_line': QgsGeometry of the section line (LineString).
                - 'crs': QgsCoordinateReferenceSystem for the output.

        Returns:
            True if export successful.

        Raises:
            ExportError: If data is invalid or export fails.

        """
        interpretations = data.get("interpretations", [])
        section_line = data.get("section_line")
        src_crs = data.get("crs", QgsCoordinateReferenceSystem())

        if not interpretations:
            logger.warning("No interpretations to export to 3D.")
            return False

        if not section_line:
            raise ExportError("Section line geometry is required for 3D projection.")

        # Prepare fields
        fields = [
            QgsField("id", QVariant.String, len=50),
            QgsField("unit_name", QVariant.String, len=100),
            QgsField("lithology", QVariant.String, len=50),
            QgsField("desc", QVariant.String, len=254),
        ]

        # Calculate section azimuth and origin
        try:
            # Assume section line is a LineString. Get first segment for azimuth.
            # Ideally the section line defines the projection plane.
            if section_line.isMultipart():
                # Handle MultiLineString if necessary, taking the first part
                line_points = section_line.asMultiPolyline()[0]
            else:
                line_points = section_line.asPolyline()

            p1 = line_points[0]
            p2 = line_points[-1]  # Use start and end for overall azimuth usually

            # Calculate azimuth (radians)
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            azimuth = math.atan2(dy, dx)

            origin_x = p1.x()
            origin_y = p1.y()

            logger.info(
                f"Section Plane: Origin({origin_x:.2f}, {origin_y:.2f}), Azimuth({math.degrees(azimuth):.2f} deg)"
            )

        except Exception as e:
            raise ExportError(f"Failed to calculate section geometry: {e}") from e

        # Transform and create features
        features = []
        for polygon in interpretations:
            feat = QgsFeature()
            feat.setFields(
                self._make_fields(fields)
            )  # Helper from BaseExporter if exists, else construct

            # Set attributes
            feat.setAttribute("id", polygon.id)
            feat.setAttribute("unit_name", polygon.unit_name)
            # feat.setAttribute("lithology", polygon.lithology) # Assuming these attrs exist
            # feat.setAttribute("desc", polygon.description)

            # Transform Geometry: Vertex-wise Affine Transformation
            points_3d = []

            # Close the loop if not closed
            vertices = polygon.vertices_2d
            if vertices and vertices[0] != vertices[-1]:
                vertices.append(vertices[0])

            for point_2d in vertices:
                # 2D Profile coordinates: X = Distance along section, Y = Elevation
                dist = point_2d.x()
                elev = point_2d.y()

                # 3D Transformation
                # E = E_origin + dist * cos(azimuth)
                # N = N_origin + dist * sin(azimuth)
                # Z = Elev
                east = origin_x + (dist * math.cos(azimuth))
                north = origin_y + (dist * math.sin(azimuth))

                points_3d.append(QgsPoint(east, north, elev))

            # Create 3D Polygon Geometry
            # Construct using QgsPolygon and QgsLineString to preserve Z values
            ring = QgsLineString(points_3d)
            polygon_geom = QgsPolygon()
            polygon_geom.setExteriorRing(ring)

            geom = QgsGeometry(polygon_geom)

            if not geom.isGeosValid():
                logger.warning(
                    f"Generated 3D geometry for polygon {polygon.id} is invalid. Attempting to fix."
                )
                geom = geom.makeValid()

            feat.setGeometry(geom)
            features.append(feat)

        # Write to Shapefile using BaseExporter logic or QgsVectorFileWriter
        # BaseExporter usage:
        # return self._write_vector_layer(output_path, features, fields, WkbType.PolygonZ, src_crs)

        # Checking BaseExporter signature/capability. Assuming it has a _write_vector method or similar.
        # If BaseExporter is abstract and expects us to bring our own writer, we use QgsVectorFileWriter.
        # Let's verify BaseExporter first. Assuming standard QgsVectorFileWriter usage for now.

        return self._write_shapefile(output_path, features, fields, QgsWkbTypes.PolygonZ, src_crs)

    def _write_shapefile(
        self, path: str, features: list[QgsFeature], fields: list[QgsField], wkb_type, crs
    ) -> bool:
        """Write shapefile (if not in BaseExporter)."""
        from qgis.core import QgsVectorFileWriter

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        options.fileEncoding = "UTF-8"

        # Create fields container
        # Note: In QGIS API, we often pass QgsFields object.
        qgs_fields = self._make_fields_obj(fields)

        writer = QgsVectorFileWriter.create(
            path, qgs_fields, wkb_type, crs, QgsCoordinateReferenceSystem(), options
        )

        if writer.hasError() != QgsVectorFileWriter.NoError:
            raise ExportError(writer.errorMessage())

        for feat in features:
            writer.addFeature(feat)

        del writer
        return True

    def _make_fields_obj(self, fields_list):
        from qgis.core import QgsFields

        qfields = QgsFields()
        for f in fields_list:
            qfields.append(f)
        return qfields

    def _make_fields(self, fields_list):
        # Compatibility helper if needed
        return self._make_fields_obj(fields_list)
