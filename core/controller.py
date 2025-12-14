"""
Controller for SecInterp profile data generation.
Handles orchestration of services and caching.
"""
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from sec_interp.core import utils as scu
from sec_interp.core.services import GeologyService, ProfileService, StructureService
from sec_interp.core.data_cache import DataCache
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)

class ProfileController:
    """Orchestrates data generation services for SecInterp."""
    
    def __init__(self):
        """Initialize services and cache."""
        self.profile_service = ProfileService()
        self.geology_service = GeologyService()
        self.structure_service = StructureService()
        self.data_cache = DataCache()
        logger.debug("ProfileController initialized")

    def get_cached_data(self, inputs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Retrieve data from cache if available."""
        cache_key = self.data_cache.get_cache_key(inputs)
        return self.data_cache.get(cache_key)

    def cache_data(self, inputs: Dict[str, Any], data: Dict[str, Any]) -> None:
        """Cache the generated data."""
        cache_key = self.data_cache.get_cache_key(inputs)
        self.data_cache.set(cache_key, data)

    def generate_profile_data(self, values: Dict[str, Any]) -> Tuple[List, Any, Any, List[str]]:
        """Unified method to generate all profile data components.
        
        Args:
            values (dict): Validated input values.

        Returns:
            tuple: (profile_data, geol_data, struct_data, messages)
        """
        profile_data = []
        geol_data = None
        struct_data = None
        messages = []

        raster_layer = values["raster_layer_obj"]
        line_layer = values["line_layer_obj"]
        outcrop_layer = values.get("outcrop_layer_obj")
        structural_layer = values.get("structural_layer_obj")
        selected_band = values["selected_band"]
        buffer_dist = values["buffer_distance"]

        # 1. Topography
        profile_data = self.profile_service.generate_topographic_profile(
            line_layer, raster_layer, selected_band
        )

        if not profile_data:
            return None, None, None, ["Error: No profile data generated."]

        messages.append(f"✓ Data processed successfully!\n\nTopography: {len(profile_data)} points")

        # 2. Geology
        if outcrop_layer:
            outcrop_name_field = values.get("outcrop_name_field")
            if outcrop_name_field:
                geol_data = self.geology_service.generate_geological_profile(
                    line_layer,
                    raster_layer,
                    outcrop_layer,
                    outcrop_name_field,
                    selected_band,
                )
                if geol_data:
                    messages.append(f"Geology: {len(geol_data)} segments")
                else:
                    messages.append("Geology: No intersections")
            else:
                 messages.append("\n⚠ Outcrop layer selected but no geology field specified.")

        # 3. Structure
        if structural_layer:
            dip_field = values.get("dip_field")
            strike_field = values.get("strike_field")

            if dip_field and strike_field:
                line_feat = next(line_layer.getFeatures(), None)
                if line_feat:
                    line_geom = line_feat.geometry()
                    if line_geom and not line_geom.isNull():
                        line_azimuth = scu.calculate_line_azimuth(line_geom)
                        struct_data = self.structure_service.project_structures(
                            line_layer,
                            raster_layer,  # Added argument
                            structural_layer,
                            buffer_dist,
                            line_azimuth,
                            dip_field,
                            strike_field,
                            selected_band, # Added argument
                        )
                        
                        if struct_data:
                            messages.append(f"Structures: {len(struct_data)} points")
                        else:
                            messages.append(f"Structures: None in {buffer_dist}m buffer")
            else:
                 messages.append("\n⚠ Structural layer selected but dip/strike fields not specified.")

        return profile_data, geol_data, struct_data, messages

    def export_data(
        self, 
        output_folder: Path, 
        values: Dict[str, Any], 
        profile_data: List[Tuple],
        geol_data: Optional[List[Any]], 
        struct_data: Optional[List[Any]]
    ) -> List[str]:
        """Export generated data to CSV and Shapefile formats using lazy imports.
        
        Args:
            output_folder (Path): Destination folder.
            values (Dict): Input values containing layers and params.
            profile_data (List): Topographic profile data.
            geol_data (List): Geological data.
            struct_data (List): Structural data.
            
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
        )

        result_msg = ["✓ Saving files..."]
        csv_exporter = CSVExporter({})
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

        # Export Axes
        logger.info("✓ Saving profile axes...")
        AxesShpExporter({}).export(
            output_folder / "profile_axes.shp",
            {"profile_data": profile_data, "crs": line_crs},
        )
        result_msg.append("  - profile_axes.shp")

        result_msg.append(f"\n✓ All files saved to:\n{output_folder}")
        return result_msg
