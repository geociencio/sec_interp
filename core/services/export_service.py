"""Export service for SecInterp.

This module provides a service to orchestrate all export operations,
including data (Shapefile, CSV) and preview (PNG, PDF, SVG) exports.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qgis.core import QgsMapSettings, QgsRectangle

from sec_interp.core.exceptions import DataMissingError, ExportError
from sec_interp.core.services.access_control_service import AccessControlService
from sec_interp.core.types import PreviewParams
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class ExportService:
    """Service to orchestrate all export operations."""

    def __init__(self, controller: Any | None = None):
        """Initialize the export service.

        Args:
            controller: Optional reference to ProfileController for data access.

        """
        self.controller = controller
        self.access_control = AccessControlService()

    def export_data(
        self,
        output_folder: Path,
        params: PreviewParams,
        profile_data: list[tuple],
        geol_data: list[Any] | None,
        struct_data: list[Any] | None,
        drillhole_data: list[Any] | None = None,
        interp_data: list[Any] | None = None,
    ) -> list[str]:
        """Export generated data to CSV and Shapefile formats.

        Args:
            output_folder: Destination directory for all exported files.
            params: Correctly validated parameters for the export run.
            profile_data: Topographic profile points (dist, elevation).
            geol_data: List of GeologySegment objects.
            struct_data: List of StructureMeasurement objects.
            drillhole_data: Optional list of drillhole data.
            interp_data: Optional list of InterpretationPolygon objects.

        Returns:
            A list of user-friendly log messages.

        """
        # Ensure we have data to work with
        if not profile_data:
            raise DataMissingError("No profile data available for export")

        line_layer = params.line_layer
        if not line_layer:
            raise DataMissingError("Section line layer not found in parameters")

        line_crs = line_layer.crs()
        result_msg = ["✓ Saving files..."]

        from sec_interp.exporters import CSVExporter

        csv_exporter = CSVExporter({})

        # Orchestrate sub-exports
        self._export_topography(output_folder, profile_data, line_crs, csv_exporter, result_msg)
        self._export_geology(output_folder, geol_data, line_crs, csv_exporter, result_msg)
        self._export_structures(
            output_folder, struct_data, params, line_crs, csv_exporter, result_msg
        )
        self._export_drillholes(output_folder, drillhole_data, line_crs, result_msg)
        self._export_interpretations(output_folder, interp_data, line_layer, line_crs, result_msg)
        self._export_axes(output_folder, profile_data, line_crs, result_msg)

        result_msg.append(f"\n✓ All files saved to:\n{output_folder}")
        return result_msg

    def _export_topography(
        self, folder: Path, data: list[tuple], crs: Any, csv_exporter: Any, msg: list[str]
    ) -> None:
        """Export topographic data."""
        from sec_interp.exporters import ProfileLineShpExporter

        logger.info("✓ Saving topographic profile...")
        try:
            csv_exporter.export(
                folder / "topo_profile.csv", {"headers": ["dist", "elev"], "rows": data}
            )
            ProfileLineShpExporter({}).export(
                folder / "profile_line.shp", {"profile_data": data, "crs": crs}
            )
            msg.extend(["  - topo_profile.csv", "  - profile_line.shp"])
        except Exception as e:
            raise ExportError(f"Topography export failed: {e!s}") from e

    def _export_geology(
        self, folder: Path, data: list[Any] | None, crs: Any, csv_exporter: Any, msg: list[str]
    ) -> None:
        """Export geological data."""
        if not data:
            return
        from sec_interp.exporters import GeologyShpExporter

        logger.info("✓ Saving geological profile...")
        try:
            rows = [(p[0], p[1], s.unit_name) for s in data for p in s.points]
            csv_exporter.export(
                folder / "geol_profile.csv",
                {"headers": ["dist", "elev", "geology"], "rows": rows},
            )
            GeologyShpExporter({}).export(
                folder / "geol_profile.shp", {"geology_data": data, "crs": crs}
            )
            msg.extend(["  - geol_profile.csv", "  - geol_profile.shp"])
        except Exception as e:
            raise ExportError(f"Geology export failed: {e!s}") from e

    def _export_structures(
        self,
        folder: Path,
        data: list[Any] | None,
        params: PreviewParams,
        crs: Any,
        csv_exporter: Any,
        msg: list[str],
    ) -> None:
        """Export structural data."""
        if not data:
            return
        from sec_interp.exporters import StructureShpExporter

        logger.info("✓ Saving structural profile...")
        try:
            rows = [(s.distance, s.apparent_dip) for s in data]
            csv_exporter.export(
                folder / "structural_profile.csv",
                {"headers": ["dist", "apparent_dip"], "rows": rows},
            )

            raster_res = 1.0
            if params.raster_layer:
                raster_res = params.raster_layer.rasterUnitsPerPixelX()

            StructureShpExporter({}).export(
                folder / "structural_profile.shp",
                {
                    "structural_data": data,
                    "crs": crs,
                    "dip_scale_factor": params.dip_scale_factor,
                    "raster_res": raster_res,
                },
            )
            msg.extend(["  - structural_profile.csv", "  - structural_profile.shp"])
        except Exception as e:
            raise ExportError(f"Structure export failed: {e!s}") from e

    def _export_drillholes(
        self, folder: Path, data: list[Any] | None, crs: Any, msg: list[str]
    ) -> None:
        """Export drillhole data."""
        if not data:
            return
        from sec_interp.exporters import (
            DrillholeIntervalShpExporter,
            DrillholeTraceShpExporter,
        )

        logger.info("✓ Saving drillhole data...")
        try:
            DrillholeTraceShpExporter({}).export(
                folder / "drillhole_traces.shp", {"drillhole_data": data, "crs": crs}
            )
            DrillholeIntervalShpExporter({}).export(
                folder / "drillhole_intervals.shp", {"drillhole_data": data, "crs": crs}
            )
            msg.extend(["  - drillhole_traces.shp", "  - drillhole_intervals.shp"])
        except Exception as e:
            raise ExportError(f"Drillhole export failed: {e!s}") from e

    def _export_interpretations(
        self,
        folder: Path,
        data: list[Any] | None,
        line_layer: Any,
        crs: Any,
        msg: list[str],
    ) -> None:
        """Export interpretation data."""
        if not data:
            logger.info("No interpretations provided for export.")
            return
        from sec_interp.exporters import Interpretation2DExporter

        logger.info("✓ Saving interpretation data...")
        try:
            # 2D Export (Standard)
            Interpretation2DExporter({}).export(
                folder / "interpretations.shp", {"interpretations": data}
            )
            msg.append("  - interpretations.shp")

            # 3D Export (Restricted Feature)
            if self.access_control.can_export_3d():
                from sec_interp.exporters import Interpretation3DExporter

                logger.info("✓ Saving 3D interpretation data...")
                # Get section line geometry
                if line_layer and line_layer.isValid():
                    line_geom = next(line_layer.getFeatures()).geometry()

                    Interpretation3DExporter({}).export(
                        folder / "interpretations_3d.shp",
                        {
                            "interpretations": data,
                            "section_line": line_geom,
                            "crs": crs,
                        },
                    )
                    msg.append("  - interpretations_3d.shp (3D)")
                else:
                    logger.warning("Invalid section line layer, skipping 3D export.")
            else:
                logger.info("3D Export features are restricted for this user.")

        except Exception as e:
            raise ExportError(f"Interpretation export failed: {e!s}") from e

    def _export_axes(self, folder: Path, data: list[tuple], crs: Any, msg: list[str]) -> None:
        """Export profile axes."""
        from sec_interp.exporters import AxesShpExporter

        logger.info("✓ Saving profile axes...")
        try:
            AxesShpExporter({}).export(
                folder / "profile_axes.shp", {"profile_data": data, "crs": crs}
            )
        except Exception as e:
            raise ExportError(f"Profile axes export failed: {e!s}") from e

    def get_map_settings(
        self,
        layers: list[Any],
        extent: QgsRectangle,
        size: Any | None,
        background_color: Any,
    ) -> QgsMapSettings:
        """Create and configure QgsMapSettings for canvas or image export.

        Args:
            layers: List of map layers to be rendered.
            extent: The spatial extent (bounding box) of the view.
            size: Optional output size in pixels (QSize).
            background_color: The background color for the render (QColor).

        Returns:
            A configured QgsMapSettings instance ready for rendering.

        """
        map_settings = QgsMapSettings()
        map_settings.setLayers(layers)
        map_settings.setExtent(extent)
        if size is not None:
            map_settings.setOutputSize(size)
        map_settings.setBackgroundColor(background_color)
        return map_settings
