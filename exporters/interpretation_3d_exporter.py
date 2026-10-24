"""Interpretation 3D export utilities.

This module provides the exporter for 3D geological interpretations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsField,
    QgsGeometry,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QCoreApplication

from sec_interp.core.domain import InterpretationPolygon
from sec_interp.core.exceptions import ExportError
from sec_interp.exporters.base_exporter import BaseExporter
from sec_interp.exporters.interpretation_3d.fields import (
    prepare_fields,
    write_shapefile,
)
from sec_interp.exporters.interpretation_3d.geometry import (
    calculate_section_geometry,
    collect_projected_features,
)
from sec_interp.exporters.interpretation_3d.style import generate_qml_style
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class Interpretation3DExporter(BaseExporter):
    """Exporter for 3D Interpretation polygons (Shapefile 2.5D)."""

    def get_supported_extensions(self) -> list[str]:
        """Get supported extensions."""
        return [".shp", ".gpkg", ".dxf"]

    def export(
        self,
        output_path: str | Path,
        data: dict[str, Any],
        layer_name: str | None = None,
    ) -> bool:
        """Export interpretation data to a 3D Shapefile."""
        interpretations = data.get("interpretations", [])
        section_line = data.get("section_line")
        src_crs = data.get("crs", QgsCoordinateReferenceSystem())

        if not self._validate_export_input(interpretations, section_line):
            return False

        fields, sorted_keys = self._prepare_fields(interpretations)
        try:
            origin_x, origin_y, azimuth = self._calculate_section_geometry(
                cast(QgsGeometry, section_line)
            )
        except Exception as exc:
            raise ExportError(f"Failed to calculate section geometry: {exc}") from exc  # no-i18n

        features = self._collect_projected_features(
            interpretations, fields, sorted_keys, origin_x, origin_y, azimuth
        )
        success = self._write_shapefile(
            output_path,
            features,
            fields,
            QgsWkbTypes.Type.PolygonZ,
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
        self,
        output_path: str | Path,
        interpretations: list,
        fields: list[QgsField],
        crs: Any,
    ) -> None:
        """Handle style generation after successful export."""
        try:
            self._generate_qml_style(output_path, interpretations, fields, crs)
        except Exception as exc:
            logger.warning(f"Failed to generate QML style: {exc}")

    def _generate_qml_style(
        self,
        shp_path: Path | str,
        interpretations: list[InterpretationPolygon],
        fields: list[QgsField],
        crs: QgsCoordinateReferenceSystem,
    ) -> None:
        """Generate a QML style file for the exported shapefile."""
        generate_qml_style(shp_path, interpretations, fields, crs)

    def _prepare_fields(self, interpretations: list[Any]) -> tuple[list[QgsField], list[str]]:
        """Prepare fixed and custom attribute fields."""
        return prepare_fields(interpretations)

    def _calculate_section_geometry(self, section_line: QgsGeometry) -> tuple[float, float, float]:
        """Calculate origin and azimuth from the section line."""
        return calculate_section_geometry(section_line)

    def _collect_projected_features(
        self,
        interpretations: list[Any],
        fields: list[QgsField],
        sorted_keys: list[str],
        origin_x: float,
        origin_y: float,
        azimuth: float,
    ) -> list[Any]:
        """Project every valid interpretation polygon to 3D features."""
        return collect_projected_features(
            interpretations,
            fields,
            sorted_keys,
            origin_x,
            origin_y,
            azimuth,
        )

    def _write_shapefile(
        self,
        path: str | Path,
        features: list[Any],
        fields: list[QgsField],
        wkb_type: Any,
        crs: Any,
        layer_name: str | None = None,
    ) -> bool:
        """Write the projected features to a vector file."""
        return write_shapefile(path, features, fields, wkb_type, crs, layer_name=layer_name)
