"""Interpretation 3D export utilities.

This module provides the exporter for 3D geological interpretations.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsLineString,
    QgsPoint,
    QgsPointXY,
    QgsPolygon,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QCoreApplication, QMetaType
from qgis.PyQt.QtGui import QColor

import sec_interp.core.utils.io as scu_io
from sec_interp.core.domain import InterpretationPolygon
from sec_interp.core.exceptions import ExportError
from sec_interp.exporters.base_exporter import BaseExporter
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)

# Constants for 3D geometry validation
MIN_VALID_POLYGON_VERTICES = 4
MIN_REQUIRED_FOR_CLOSURE = 2


class Interpretation3DExporter(BaseExporter):
    """Exporter for 3D Interpretation polygons (Shapefile 2.5D)."""

    def get_supported_extensions(self) -> list[str]:
        """Get supported extensions."""
        return [".shp", ".gpkg", ".dxf"]

    def export(self, output_path: str, data: dict[str, Any], layer_name: str | None = None) -> bool:
        """Export interpretation data to a 3D Shapefile."""
        interpretations = data.get("interpretations", [])
        section_line = data.get("section_line")
        src_crs = data.get("crs", QgsCoordinateReferenceSystem())

        if not self._validate_export_input(interpretations, section_line):
            return False

        # Prepare fields
        fields, sorted_keys = self._prepare_fields(interpretations)

        # Calculate section azimuth and origin
        try:
            origin_x, origin_y, azimuth = self._calculate_section_geometry(section_line)
        except Exception as e:
            raise ExportError(f"Failed to calculate section geometry: {e}") from e

        # Transform and create features
        features = self._collect_projected_features(
            interpretations, fields, sorted_keys, origin_x, origin_y, azimuth
        )

        success = self._write_shapefile(
            output_path,
            features,
            fields,
            QgsWkbTypes.PolygonZ,
            src_crs,
            layer_name=layer_name,
        )

        if success:
            self._handle_post_export_styles(output_path, interpretations, fields, src_crs)

        return success

    def _validate_export_input(self, interpretations: list, section_line: Any) -> bool:
        """Validate input for 3D export."""
        if not interpretations:
            logger.warning("No interpretations to export to 3D.")
            return False

        if not section_line:
            raise ExportError(
                QCoreApplication.translate(
                    "Interpretation3DExporter",
                    "Section line geometry is required for 3D projection.",
                )
            )
        return True

    def _handle_post_export_styles(
        self, output_path: str, interpretations: list, fields: list, crs: Any
    ) -> None:
        """Handle style generation after successful export."""
        try:
            self._generate_qml_style(output_path, interpretations, fields, crs)
        except Exception as e:
            logger.warning(f"Failed to generate QML style: {e}")

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
        )

        # Import 3D components if available
        try:
            import qgis._3d  # noqa: F401

            HAS_3D = True
        except ImportError:
            HAS_3D = False

        shp_path = Path(shp_path)
        qml_path = shp_path.with_suffix(".qml")

        # Create a temporary layer to build the style (with Z support)
        layer = QgsVectorLayer(f"Polygon?crs={crs.authid()}&z=yes", "temp_style", "memory")
        layer.dataProvider().addAttributes(fields)
        layer.updateFields()

        # 1. 2D Categorized Symbology
        self._setup_2d_renderer(layer, interpretations)

        # 2. 3D Symbology (Native QGIS 3D - Rule Based)
        if HAS_3D:
            try:
                self._configure_3d_renderer(layer, interpretations)
            except Exception as e:
                logger.warning(f"Failed to configure 3D renderer: {e}")

        # Save style to disk
        msg, ok = layer.saveNamedStyle(str(qml_path))
        if ok:
            logger.info(f"Generated QML style: {qml_path}")
        else:
            logger.warning(f"Failed to save QML style: {msg}")

    def _setup_2d_renderer(
        self, layer: QgsVectorLayer, interpretations: list[InterpretationPolygon]
    ) -> None:
        """Set up 2D categorized renderer for the layer."""
        from qgis.core import (
            QgsCategorizedSymbolRenderer,
            QgsFillSymbol,
            QgsRendererCategory,
        )

        categories = []
        unique_units = {p.name: p.color for p in interpretations}

        for name, color_hex in unique_units.items():
            color = QColor(color_hex)
            if not color.isValid():
                color = QColor("#FF0000")

            symbol = QgsFillSymbol.createSimple(
                {
                    "color": f"{color.red()},{color.green()},{color.blue()},180",
                    "outline_color": f"{color.darker(150).red()},{color.darker(150).green()},{color.darker(150).blue()}",
                    "outline_width": "0.3",
                }
            )

            categories.append(QgsRendererCategory(name, symbol, name))

        renderer = QgsCategorizedSymbolRenderer("name", categories)
        layer.setRenderer(renderer)

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
            rings_3d = self._create_3d_rings(poly_2d, origin_x, origin_y, azimuth, vert_exag)

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

    def _create_3d_rings(
        self,
        poly_2d: list[list[QgsPointXY]],
        origin_x: float,
        origin_y: float,
        azimuth: float,
        vert_exag: float,
    ) -> list[QgsLineString]:
        """Transform 2D rings to 3D LineStrings.

        Args:
            poly_2d: List of rings, each a list of points.
            origin_x: X coordinate of the section origin.
            origin_y: Y coordinate of the section origin.
            azimuth: Section azimuth.
            vert_exag: Vertical exaggeration.

        Returns:
            List of 3D LineStrings.

        """
        rings_3d = []
        cos_a = math.cos(azimuth)
        sin_a = math.sin(azimuth)

        for ring_2d in poly_2d:
            points_3d = []
            for p_2d in ring_2d:
                east = origin_x + (p_2d.x() * cos_a)
                north = origin_y + (p_2d.x() * sin_a)
                elev = p_2d.y() / vert_exag
                points_3d.append(QgsPoint(east, north, elev))

            rings_3d.append(QgsLineString(points_3d))
        return rings_3d

    def _write_shapefile(
        self,
        path: str,
        features: list[QgsFeature],
        fields: list[QgsField],
        wkb_type,
        crs,
        layer_name: str | None = None,
    ) -> bool:
        """Write shapefile (if not in BaseExporter)."""
        from qgis.core import QgsVectorFileWriter

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        options.fileEncoding = "UTF-8"
        # Create fields container
        # Note: In QGIS API, we often pass QgsFields object.
        qgs_fields = self._make_fields_obj(fields)

        writer = scu_io.create_vector_writer(
            str(path), crs, qgs_fields, wkb_type, layer_name=layer_name
        )

        if writer.hasError() != QgsVectorFileWriter.NoError:
            raise ExportError(writer.errorMessage())

        for feat in features:
            writer.addFeature(feat)

        del writer
        return True

    def _make_fields_obj(self, fields_list: list[QgsField]) -> QgsFields:
        from qgis.core import QgsFields

        qfields = QgsFields()
        for f in fields_list:
            qfields.append(f)
        return qfields

    def _make_fields(self, fields_list: list[QgsField]) -> QgsFields:
        # Compatibility helper if needed
        return self._make_fields_obj(fields_list)

    def _prepare_fields(self, interpretations: list[Any]) -> tuple[list[QgsField], list[str]]:
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

        for key in sorted_keys:
            fields.append(QgsField(key, QMetaType.Type.QString, len=255))
        return fields, sorted_keys

    def _calculate_section_geometry(self, section_line: QgsGeometry) -> tuple[float, float, float]:
        """Calculate origin and azimuth from section line."""
        if section_line.isMultipart():
            line_points = section_line.asMultiPolyline()[0]
        else:
            line_points = section_line.asPolyline()

        p1 = line_points[0]
        p2 = line_points[-1]

        # Calculate azimuth (radians)
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        azimuth = math.atan2(dy, dx)

        logger.info(
            f"Section Plane: Origin({p1.x():.2f}, {p1.y():.2f}), Azimuth({math.degrees(azimuth):.2f} deg)"
        )
        return p1.x(), p1.y(), azimuth

    def _collect_projected_features(
        self,
        interpretations: list[Any],
        fields: list[QgsField],
        sorted_keys: list[str],
        origin_x: float,
        origin_y: float,
        azimuth: float,
    ) -> list[QgsFeature]:
        features = []
        for polygon in interpretations:
            geom_2d = self._prepare_2d_geometry(polygon)
            if not geom_2d:
                continue

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
        return features

    def _prepare_2d_geometry(self, polygon: Any) -> QgsGeometry | None:
        """Prepare and validate 2D geometry from polygon vertices."""
        vertices = self._get_unique_vertices(polygon.vertices_2d)
        if not vertices:
            return None

        vertices = self._ensure_closed_polygon(vertices)

        if len(vertices) < MIN_VALID_POLYGON_VERTICES:
            logger.warning(f"Polygon {polygon.id} has insufficient unique vertices. Skipping.")
            return None

        qgs_points_3d = [QgsPoint(x, y, 0.0) for x, y in vertices]
        polygon_2d = QgsPolygon()
        polygon_2d.setExteriorRing(QgsLineString(qgs_points_3d))
        geom_2d = QgsGeometry(polygon_2d)

        if not geom_2d.isGeosValid():
            logger.info(f"Correcting 2D geometry for polygon {polygon.id}")
            geom_2d = geom_2d.makeValid()

        return geom_2d

    def _get_unique_vertices(self, vertices_2d: Any) -> list:
        """Deduplicate consecutive vertices."""
        raw_list = list(vertices_2d)
        if not raw_list:
            return []

        dedup = []
        for v in raw_list:
            if not dedup or v != dedup[-1]:
                dedup.append(v)
        return dedup

    def _ensure_closed_polygon(self, vertices: list) -> list:
        """Ensure the polygon vertices are closed."""
        if len(vertices) > MIN_REQUIRED_FOR_CLOSURE and vertices[0] != vertices[-1]:
            return [*vertices, vertices[0]]
        return vertices

    def _configure_3d_renderer(
        self, layer: QgsVectorLayer, interpretations: list[InterpretationPolygon]
    ) -> None:
        """Set up rule-based 3D renderer for the layer."""
        from qgis._3d import (
            QgsPhongMaterialSettings,
            QgsPolygon3DSymbol,
            QgsRuleBased3DRenderer,
        )

        # Create root rule
        root_rule = QgsRuleBased3DRenderer.Rule(None)

        unique_units = {p.name: p.color for p in interpretations}

        for name, color_hex in unique_units.items():
            # 1. Create specific material for this unit
            color = QColor(color_hex)
            if not color.isValid():
                color = QColor("#FF0000")

            material = QgsPhongMaterialSettings()
            material.setDiffuse(color)
            material.setAmbient(color.lighter(120))  # Slight ambient boost

            # 2. Create symbol with this material
            symbol_3d = QgsPolygon3DSymbol()
            symbol_3d.setMaterialSettings(material)

            # 3. Create rule with filter
            # Signature: QgsRuleBased3DRenderer.Rule(symbol, filterExp='', description='', elseRule=False)
            filter_expr = f"\"name\" = '{name}'"
            rule = QgsRuleBased3DRenderer.Rule(symbol_3d, filter_expr, name)
            root_rule.appendChild(rule)

        # Apply renderer to layer
        renderer_3d = QgsRuleBased3DRenderer(root_rule)
        layer.setRenderer3D(renderer_3d)
        logger.debug(
            f"Configured Rule-Based 3D renderer in QML with {len(unique_units)} categories"
        )
