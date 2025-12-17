"""
Data export orchestrator for SecInterp.
Handles coordination of various exporters to save profile data.
"""
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)

class DataExportOrchestrator:
    """Orchestrates data export to various formats."""

    def __init__(self):
        """Initialize the orchestrator."""
        pass

    def export_data(
        self, 
        output_folder: Path, 
        values: Dict[str, Any], 
        profile_data: List[Tuple],
        geol_data: Optional[List[Any]], 
        struct_data: Optional[List[Any]],
        drillhole_data: Optional[List[Any]] = None
    ) -> List[str]:
        """Export generated data to CSV and Shapefile formats using lazy imports.
        
        Args:
            output_folder (Path): Destination folder.
            values (Dict): Input values containing layers and params.
            profile_data (List): Topographic profile data.
            geol_data (List): Geological data.
            struct_data (List): Structural data.
            drillhole_data (List): Drillhole data.
            
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

        line_crs = values["line_layer_obj"].crs()

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
            
            StructureShpExporter({}).export(
                output_folder / "structural_profile.shp",
                {
                    "structural_data": struct_data,
                    "crs": line_crs,
                    "dip_scale_factor": values.get("dip_scale_factor", 1.0),
                    "raster_res": values["raster_layer_obj"].rasterUnitsPerPixelX(),
                },
            )
            result_msg.append("  - structural_profile.shp")

        # Export Drillholes
        if values.get("collar_layer_obj") and drillhole_data: # Check if drillholes were processed
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
