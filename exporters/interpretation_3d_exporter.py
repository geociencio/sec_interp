"""3D Interpretation Exporter.

This module provides the exporter for 3D geological interpretations.
"""

from __future__ import annotations

import math
from typing import Any, List
from pathlib import Path

from qgis.core import (
    QgsFeature,
    QgsField,
    QgsGeometry,
    QgsPoint,
    QgsPointXY,
    QgsWkbTypes,
    QgsCoordinateReferenceSystem,
    QgsPolygon,
    QgsLineString,
)
from qgis.PyQt.QtCore import QMetaType, QVariant
from qgis.PyQt.QtGui import QColor

from sec_interp.core.exceptions import ExportError
from sec_interp.core.types import InterpretationPolygon
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
        all_attr_keys = set()
        for interp in interpretations:
            if interp.attributes:
                all_attr_keys.update(interp.attributes.keys())
        sorted_keys = sorted(all_attr_keys)

        fields = [
            QgsField("id", QMetaType.Type.QString, len=50),
            QgsField("name", QMetaType.Type.QString, len=100),
            QgsField("type", QMetaType.Type.QString, len=50),
            QgsField("color", QMetaType.Type.QString, len=10),
            QgsField("created_at", QMetaType.Type.QString, len=30),
        ]

        # Add custom fields
        for key in sorted_keys:
            fields.append(QgsField(key, QMetaType.Type.QString, len=255))

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
            p2 = line_points[-1]

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
            feat.setAttribute("name", polygon.name)
            feat.setAttribute("type", polygon.type)
            feat.setAttribute("color", polygon.color)
            feat.setAttribute("created_at", polygon.created_at)

            # 1. Deduplicate vertices and ensure 2D validity
            raw_vertices_2d = list(polygon.vertices_2d)
            if not raw_vertices_2d:
                continue

            # Remove consecutive duplicates
            dedup_vertices = []
            for v in raw_vertices_2d:
                if not dedup_vertices or v != dedup_vertices[-1]:
                    dedup_vertices.append(v)

            # Close loop if needed
            if len(dedup_vertices) > 2 and dedup_vertices[0] != dedup_vertices[-1]:
                dedup_vertices.append(dedup_vertices[0])

            if len(dedup_vertices) < 4:  # At least 3 points + 1 closure
                logger.warning(f"Polygon {polygon.id} has insufficient unique vertices. Skipping.")
                continue

            # Create 2D geometry first to validate/fix
            qgs_points_2d = [QgsPointXY(x, y) for x, y in dedup_vertices]
            geom_2d = QgsGeometry.fromPolygonXY([qgs_points_2d])

            if not geom_2d.isGeosValid():
                logger.info(
                    f"Correcting 2D geometry for polygon {polygon.id} (e.g. self-intersections)"
                )
                geom_2d = geom_2d.makeValid()

            # 2. Project validated 2D vertices to 3D
            # Note: makeValid might have changed topology (MultiPolygon),
            # so we iterate over all rings of the validated (potentially multi) geometry.

            # Using asGeometryCollection to be safe across geometry types (Polygon/MultiPolygon)
            features.extend(
                self._project_to_3d_features(
                    geom_2d,
                    polygon,
                    fields,
                    origin_x,
                    origin_y,
                    azimuth,
                    sorted_keys,
                    vert_exag=1.0,
                )
            )
            # vert_exag 1.0 because 2D coordinates are already exag in tool? No, tool uses raw canvas coords.
            # Actually, the tool saves (dist, elev). Elev is NOT exag in the InterpretationPolygon.
            # It's only exag during rendering.
            # So vert_exag here should be 1.0 (true geometry).

        # Write to Shapefile using BaseExporter logic or QgsVectorFileWriter
        # BaseExporter usage:
        # return self._write_vector_layer(output_path, features, fields, WkbType.PolygonZ, src_crs)

        # Checking BaseExporter signature/capability. Assuming it has a _write_vector method or similar.
        # If BaseExporter is abstract and expects us to bring our own writer, we use QgsVectorFileWriter.
        # Let's verify BaseExporter first. Assuming standard QgsVectorFileWriter usage for now.

        success = self._write_shapefile(
            output_path, features, fields, QgsWkbTypes.PolygonZ, src_crs
        )

        if success:
            try:
                self._generate_qml_style(output_path, interpretations, fields, src_crs)
            except Exception as e:
                logger.warning(f"Failed to generate QML style: {e}")
                # Don't fail the whole export if only QML fails

        return success

    def _generate_qml_style(
        self,
        shp_path: Path | str,
        interpretations: list[InterpretationPolygon],
        fields: list[QgsField],
        crs: QgsCoordinateReferenceSystem,
    ) -> None:
        """Generate a QML style file for the exported shapefile."""
        from qgis.core import (
            QgsVectorLayer,
            QgsCategorizedSymbolRenderer,
            QgsRendererCategory,
            QgsFillSymbol,
        )

        # Import 3D components if available
        try:
            from qgis._3d import QgsPolygon3DSymbol, QgsVectorLayer3DRenderer

            HAS_3D = True
        except ImportError:
            HAS_3D = False

        shp_path = Path(shp_path)
        qml_path = shp_path.with_suffix(".qml")

        # Create a temporary layer to build the style
        # We use a memory layer with the same schema
        layer = QgsVectorLayer(f"PolygonZ?crs={crs.authid()}", "temp_style", "memory")
        layer.dataProvider().addAttributes(fields)
        layer.updateFields()

        # 1. 2D Categorized Symbology
        categories = []
        unique_units = {}  # name -> color
        for p in interpretations:
            if p.name not in unique_units:
                unique_units[p.name] = p.color

        for name, color_hex in unique_units.items():
            color = QColor(color_hex)
            if not color.isValid():
                color = QColor("#FF0000")

            # 2D Symbol
            symbol = QgsFillSymbol.createSimple(
                {
                    "color": f"{color.red()},{color.green()},{color.blue()},180",
                    "outline_color": f"{color.darker(150).red()},{color.darker(150).green()},{color.darker(150).blue()}",
                    "outline_width": "0.3",
                }
            )

            category = QgsRendererCategory(name, symbol, name)
            categories.append(category)

        renderer = QgsCategorizedSymbolRenderer("name", categories)
        layer.setRenderer(renderer)

        # 2. 3D Symbology (Native QGIS 3D)
        if HAS_3D:
            symbol_3d = QgsPolygon3DSymbol()
            # In QGIS 3D, we can set the material to follow the color attribute
            # or set it based on the data. For simplicity in QML, we can set a
            # single symbol that uses data defined properties for the material color.

            # Setup data-defined color for 3D material
            from qgis.core import QgsProperty

            # Diffuse color is the main color of the 3D object
            symbol_3d.dataDefinedProperties().setProperty(
                QgsPolygon3DSymbol.Property.Diffuse, QgsProperty.fromField("color")
            )
            # Ambient color (usually same as diffuse but darker or same)
            symbol_3d.dataDefinedProperties().setProperty(
                QgsPolygon3DSymbol.Property.Ambient, QgsProperty.fromField("color")
            )

            # Altitude binding to absolute (our Z is absolute interpretation)
            # symbol_3d.setAltitudeBinding(QgsPolygon3DSymbol.AltBindAbsolute)
            # symbol_3d.setAltitudeClamping(QgsPolygon3DSymbol.AltClampAbsolute)

            renderer_3d = QgsVectorLayer3DRenderer(symbol_3d)
            layer.setRenderer3D(renderer_3d)
            logger.debug("Configured native 3D renderer in QML")

        # Save style to disk
        msg, ok = layer.saveNamedStyle(str(qml_path))
        if ok:
            logger.info(f"Generated QML style: {qml_path}")
        else:
            logger.warning(f"Failed to save QML style: {msg}")

    def _project_to_3d_features(
        self,
        geom_2d: QgsGeometry,
        polygon: InterpretationPolygon,
        fields: list[QgsField],
        origin_x: float,
        origin_y: float,
        azimuth: float,
        custom_keys: list[str],
        vert_exag: float = 1.0,
    ) -> list[QgsFeature]:
        """Project a 2D geometry (potentially MultiPolygon) to 3D features."""
        projected_features = []

        # Handle MultiPolygon by treating it as multiple polygons
        polygons_2d = geom_2d.asMultiPolygon() if geom_2d.isMultipart() else [geom_2d.asPolygon()]

        for poly_2d in polygons_2d:
            # poly_2d is a list of rings (list of QgsPointXY)
            rings_3d = []
            for ring_2d in poly_2d:
                points_3d = []
                for p_2d in ring_2d:
                    # Apply Affine Transformation
                    east = origin_x + (p_2d.x() * math.cos(azimuth))
                    north = origin_y + (p_2d.x() * math.sin(azimuth))
                    elev = p_2d.y() / vert_exag

                    points_3d.append(QgsPoint(east, north, elev))

                rings_3d.append(QgsLineString(points_3d))

            if not rings_3d:
                continue

            # Construct 3D Polygon
            polygon_3d = QgsPolygon()
            polygon_3d.setExteriorRing(rings_3d[0])
            for i in range(1, len(rings_3d)):
                polygon_3d.addInteriorRing(rings_3d[i])

            geom_3d = QgsGeometry(polygon_3d)

            # Create feature
            feat = QgsFeature()
            feat.setFields(self._make_fields(fields))
            feat.setAttribute("id", polygon.id)
            feat.setAttribute("name", polygon.name)
            feat.setAttribute("type", polygon.type)
            feat.setAttribute("color", polygon.color)
            feat.setAttribute("created_at", polygon.created_at)

            # Set custom attributes
            for key in custom_keys:
                val = polygon.attributes.get(key, "")
                feat.setAttribute(key, str(val))

            feat.setGeometry(geom_3d)

            projected_features.append(feat)

        return projected_features

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

        from qgis.core import QgsProject

        writer = QgsVectorFileWriter.create(
            str(path), qgs_fields, wkb_type, crs, QgsProject.instance().transformContext(), options
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
