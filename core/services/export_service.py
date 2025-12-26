from __future__ import annotations


"""Export service for SecInterp.

This module provides a service to orchestrate all export operations,
including data (Shapefile, CSV) and preview (PNG, PDF, SVG) exports.
"""

from pathlib import Path
from typing import Any, Optional

from qgis.core import QgsMapSettings, QgsProject, QgsRectangle

from sec_interp.core.exceptions import DataMissingError, ExportError
from sec_interp.core.types import PreviewParams
from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


class ExportService:
    """Service to orchestrate all export operations."""

    def __init__(self, controller: Optional[Any] = None):
        """Initialize the export service.

        Args:
            controller: Optional reference to ProfileController for data access.
        """
        self.controller = controller

    def export_data(
        self,
        output_folder: Path,
        params: PreviewParams,
        profile_data: list[tuple],
        geol_data: Optional[list[Any]],
        struct_data: Optional[list[Any]],
        drillhole_data: Optional[list[Any]] = None,
        interpretations: Optional[list[Any]] = None,
    ) -> list[str]:
        """Export generated data to CSV and Shapefile formats.

        Args:
            output_folder: Destination directory for all exported files.
            params: Correctly validated parameters for the export run.
            profile_data: Topographic profile points (dist, elevation).
            geol_data: List of GeologySegment objects.
            struct_data: List of StructureMeasurement objects.
            drillhole_data: Optional list of drillhole trace and interval data.

        Returns:
            A list of user-friendly log messages describing the exported files.

        Raises:
            DataMissingError: If critical topographic data is missing.
            ExportError: If any sub-exporter fails during execution.
        """
        # Lazy import exporters to improve plugin load time
        from sec_interp.exporters import (
            AxesShpExporter,
            CSVExporter,
            DrillholeIntervalShpExporter,
            DrillholeTraceShpExporter,
            GeologyShpExporter,
            Interpretation25DExporter,
            ProfileLineShpExporter,
            StructureShpExporter,
        )

        result_msg = ["✓ Saving files..."]
        csv_exporter = CSVExporter({})

        # Ensure we have data to work with
        if not profile_data:
            raise DataMissingError("No profile data available for export")

        line_layer = params.line_layer
        if not line_layer:
            raise DataMissingError("Section line layer not found in parameters")

        line_crs = line_layer.crs()

        # Export Topography
        logger.info("✓ Saving topographic profile...")
        try:
            csv_exporter.export(
                output_folder / "topo_profile.csv",
                {"headers": ["dist", "elev"], "rows": profile_data},
            )
            ProfileLineShpExporter({}).export(
                output_folder / "profile_line.shp",
                {"profile_data": profile_data, "crs": line_crs},
            )
        except Exception as e:
            raise ExportError(f"Topography export failed: {e!s}") from e

        result_msg.extend(["  - topo_profile.csv", "  - profile_line.shp"])

        # Export Geology
        if geol_data:
            logger.info("✓ Saving geological profile...")
            try:
                # Flatten segments for CSV
                geol_rows = []
                for s in geol_data:
                    for p in s.points:
                        geol_rows.append((p[0], p[1], s.unit_name))

                csv_exporter.export(
                    output_folder / "geol_profile.csv",
                    {"headers": ["dist", "elev", "geology"], "rows": geol_rows},
                )
                GeologyShpExporter({}).export(
                    output_folder / "geol_profile.shp",
                    {
                        "geology_data": geol_data,
                        "crs": line_crs,
                    },
                )
            except Exception as e:
                raise ExportError(f"Geology export failed: {e!s}") from e

            result_msg.extend(["  - geol_profile.csv", "  - geol_profile.shp"])

        # Export Structures
        if struct_data:
            logger.info("✓ Saving structural profile...")
            try:
                # CSV needs simple rows
                struct_rows = [(s.distance, s.apparent_dip) for s in struct_data]

                csv_exporter.export(
                    output_folder / "structural_profile.csv",
                    {"headers": ["dist", "apparent_dip"], "rows": struct_rows},
                )

                # Get raster resolution from values or layer
                raster_res = 1.0
                raster_layer = params.raster_layer
                if raster_layer:
                    raster_res = raster_layer.rasterUnitsPerPixelX()

                StructureShpExporter({}).export(
                    output_folder / "structural_profile.shp",
                    {
                        "structural_data": struct_data,
                        "crs": line_crs,
                        "dip_scale_factor": params.dip_scale_factor,
                        "raster_res": raster_res,
                    },
                )
            except Exception as e:
                raise ExportError(f"Structure export failed: {e!s}") from e

            result_msg.extend(
                ["  - structural_profile.csv", "  - structural_profile.shp"]
            )

        # Export Drillholes
        if drillhole_data:
            logger.info("✓ Saving drillhole data...")
            try:
                DrillholeTraceShpExporter({}).export(
                    output_folder / "drillhole_traces.shp",
                    {"drillhole_data": drillhole_data, "crs": line_crs},
                )
                DrillholeIntervalShpExporter({}).export(
                    output_folder / "drillhole_intervals.shp",
                    {"drillhole_data": drillhole_data, "crs": line_crs},
                )
            except Exception as e:
                raise ExportError(f"Drillhole export failed: {e!s}") from e

            result_msg.extend(
                ["  - drillhole_traces.shp", "  - drillhole_intervals.shp"]
            )

        # Export Interpretations
        if interpretations and self.controller:
            logger.info("✓ Saving 2.5D interpretations...")
            try:
                # 1. Project 2D interpretations to 2.5D using controller
                # We use the first feature of line_layer as the section line
                section_line = None
                features = list(line_layer.getFeatures())
                if features:
                    section_line = features[0].geometry()

                if section_line:
                    projected = self.controller.project_interpretations(
                        interpretations,
                        section_line,
                        line_crs,
                        params.vertical_exag,
                    )

                    # 2. Export projected data
                    Interpretation25DExporter({}).export_interpretations(
                        output_folder / "interpretations_25d.shp",
                        projected,
                        line_crs,
                    )
                    result_msg.append("  - interpretations_25d.shp")
                else:
                    logger.warning(
                        "Could not get geometry for interpretation projection."
                    )
            except Exception as e:
                logger.error(f"Interpretation export failed: {e}")
                result_msg.append(f"  ⚠ Interpretation export failed: {e}")

        # Export Axes
        logger.info("✓ Saving profile axes...")
        try:
            AxesShpExporter({}).export(
                output_folder / "profile_axes.shp",
                {"profile_data": profile_data, "crs": line_crs},
            )
        except Exception as e:
            raise ExportError(f"Profile axes export failed: {e!s}") from e

        result_msg.append(f"\n✓ All files saved to:\n{output_folder}")
        return result_msg

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
