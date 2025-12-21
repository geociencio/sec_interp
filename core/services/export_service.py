"""Export service for SecInterp.

Orchestrates all export operations, including data (SHP, CSV) and 
preview (PNG, PDF, SVG) exports.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from qgis.core import QgsMapSettings, QgsRectangle, QgsProject

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
        values: Dict[str, Any],
        profile_data: List[Tuple],
        geol_data: Optional[List[Any]],
        struct_data: Optional[List[Any]],
        drillhole_data: Optional[List[Any]] = None,
    ) -> List[str]:
        """Export generated data to CSV and Shapefile formats.
        
        Args:
            output_folder: Destination folder.
            values: Input values containing layers and params.
            profile_data: Topographic profile data.
            geol_data: Geological data.
            struct_data: Structural data.
            drillhole_data: Drillhole data.
            
        Returns:
            List[str]: Log messages of saved files.
        """
        # Lazy import exporters to improve plugin load time
        from sec_interp.exporters import (
            AxesShpExporter,
            CSVExporter,
            GeologyShpExporter,
            ProfileLineShpExporter,
            StructureShpExporter,
            DrillholeTraceShpExporter,
            DrillholeIntervalShpExporter,
        )

        result_msg = ["✓ Saving files..."]
        csv_exporter = CSVExporter({})
        
        # Ensure we have data to work with
        if not profile_data:
             logger.warning("No profile data to export")
             return ["⚠ No profile data to export"]

        line_layer = values.get("line_layer_obj")
        if not line_layer:
            logger.error("Line layer not found in values")
            return ["⚠ Error: Line layer not found"]
            
        line_crs = line_layer.crs()

        # Export Topography
        logger.info("✓ Saving topographic profile...")
        csv_exporter.export(
            output_folder / "topo_profile.csv",
            {"headers": ["dist", "elev"], "rows": profile_data},
        )
        result_msg.append("  - topo_profile.csv")
        ProfileLineShpExporter({}).export(
            output_folder / "profile_line.shp",
            {"profile_data": profile_data, "crs": line_crs},
        )
        result_msg.append("  - profile_line.shp")

        # Export Geology
        if geol_data:
            logger.info("✓ Saving geological profile...")
            # Flatten segments for CSV
            geol_rows = []
            for s in geol_data:
                for p in s.points:
                    geol_rows.append((p[0], p[1], s.unit_name))
            
            csv_exporter.export(
                output_folder / "geol_profile.csv",
                {"headers": ["dist", "elev", "geology"], "rows": geol_rows},
            )
            result_msg.append("  - geol_profile.csv")
            
            GeologyShpExporter({}).export(
                output_folder / "geol_profile.shp",
                {
                    "geology_data": geol_data,
                    "crs": line_crs,
                },
            )
            result_msg.append("  - geol_profile.shp")

        # Export Structures
        if struct_data:
            logger.info("✓ Saving structural profile...")
            # CSV needs simple rows
            struct_rows = [(s.distance, s.apparent_dip) for s in struct_data]
            
            csv_exporter.export(
                output_folder / "structural_profile.csv",
                {"headers": ["dist", "apparent_dip"], "rows": struct_rows},
            )
            result_msg.append("  - structural_profile.csv")
            
            # Get raster resolution from values or layer
            raster_res = 1.0
            raster_layer = values.get("raster_layer_obj")
            if raster_layer:
                raster_res = raster_layer.rasterUnitsPerPixelX()
            
            StructureShpExporter({}).export(
                output_folder / "structural_profile.shp",
                {
                    "structural_data": struct_data,
                    "crs": line_crs,
                    "dip_scale_factor": values.get("dip_scale_factor", 1.0),
                    "raster_res": raster_res,
                },
            )
            result_msg.append("  - structural_profile.shp")

        # Export Drillholes
        if drillhole_data: 
            logger.info("✓ Saving drillhole data...")
            
            DrillholeTraceShpExporter({}).export(
                output_folder / "drillhole_traces.shp",
                {"drillhole_data": drillhole_data, "crs": line_crs}
            )
            result_msg.append("  - drillhole_traces.shp")
            
            DrillholeIntervalShpExporter({}).export(
                output_folder / "drillhole_intervals.shp",
                {"drillhole_data": drillhole_data, "crs": line_crs}
            )
            result_msg.append("  - drillhole_intervals.shp")

        # Export Axes
        logger.info("✓ Saving profile axes...")
        AxesShpExporter({}).export(
            output_folder / "profile_axes.shp",
            {"profile_data": profile_data, "crs": line_crs},
        )
        result_msg.append("  - profile_axes.shp")

        result_msg.append(f"\n✓ All files saved to:\n{output_folder}")
        return result_msg

    def get_map_settings(
        self, 
        layers: List[Any], 
        extent: QgsRectangle, 
        size: Optional[Any], 
        background_color: Any
    ) -> QgsMapSettings:
        """Create and configure QgsMapSettings for export.
        
        Args:
            layers: List of layers to include.
            extent: Map extent to export.
            size: Optional output size (QSize).
            background_color: Background color (QColor).
            
        Returns:
            Configured QgsMapSettings instance.
        """
        map_settings = QgsMapSettings()
        map_settings.setLayers(layers)
        map_settings.setExtent(extent)
        if size is not None:
            map_settings.setOutputSize(size)
        map_settings.setBackgroundColor(background_color)
        return map_settings
