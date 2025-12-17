"""
Controller for SecInterp profile data generation.
Handles orchestration of services and caching.
"""
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from sec_interp.core import utils as scu
from sec_interp.core.services import (
    GeologyService,
    ProfileService,
    StructureService,
    DrillholeService,
)
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
        self.drillhole_service = DrillholeService()
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

    def generate_profile_data(self, values: Dict[str, Any]) -> Tuple[List, Any, Any, Any, List[str]]:
        """Unified method to generate all profile data components.
        
        Args:
            values (dict): Validated input values.

        Returns:
            tuple: (profile_data, geol_data, struct_data, drillhole_data, messages)
        """
        profile_data = []
        geol_data = None
        struct_data = None
        drillhole_data = None
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

        # 4. Drillholes
        collar_layer = values.get("collar_layer_obj")
        if collar_layer:
            # Check requirements
            section_geom = values.get("section_geom")
            section_start = values.get("section_start")
            distance_area = values.get("distance_area")
            
            if section_geom and section_start and distance_area:
                # Project Collars
                collars = self.drillhole_service.project_collars(
                    collar_layer=collar_layer,
                    line_geom=section_geom,
                    line_start=section_start,
                    distance_area=distance_area,
                    buffer_width=buffer_dist,
                    collar_id_field=values.get("collar_id_field"),
                    use_geometry=values.get("collar_use_geometry", True),
                    collar_x_field=values.get("collar_x_field"),
                    collar_y_field=values.get("collar_y_field"),
                    collar_z_field=values.get("collar_z_field"),
                    collar_depth_field=values.get("collar_depth_field"),
                    dem_layer=raster_layer,
                )
                
                if collars:
                    messages.append(f"Drillholes: {len(collars)} collars projected")
                    
                    # Process Intervals if survey/interval layers exist
                    survey_layer = values.get("survey_layer_obj")
                    interval_layer = values.get("interval_layer_obj")
                    
                    if survey_layer and interval_layer:
                        section_azimuth = scu.calculate_line_azimuth(section_geom)
                        
                        dh_geol, dh_struct = self.drillhole_service.process_intervals(
                            collar_points=collars,
                            collar_layer=collar_layer,
                            survey_layer=survey_layer,
                            interval_layer=interval_layer,
                            collar_id_field=values.get("collar_id_field"),
                            use_geometry=values.get("collar_use_geometry", True),
                            collar_x_field=values.get("collar_x_field"),
                            collar_y_field=values.get("collar_y_field"),
                            line_geom=section_geom,
                            line_start=section_start,
                            distance_area=distance_area,
                            buffer_width=buffer_dist,
                            section_azimuth=section_azimuth,
                            survey_fields={
                                "id": values.get("survey_id_field"),
                                "depth": values.get("survey_depth_field"),
                                "azim": values.get("survey_azim_field"),
                                "incl": values.get("survey_incl_field"),
                            },
                            interval_fields={
                                "id": values.get("interval_id_field"),
                                "from": values.get("interval_from_field"),
                                "to": values.get("interval_to_field"),
                                "lith": values.get("interval_lith_field"),
                            }
                        )
                        drillhole_data = dh_struct # Should call it drillhole_traces or similar
                        # dh_geol contains flattened segments
                        # If we want to return both, we might need to adjust return signature again.
                        # For now, let's assume 'drillhole_data' contains the structured data (id, traces, segments)
                        # And potentially merge dh_geol into geol_data if needed? 
                        # Ideally UI separates them.
                        messages.append(f"Drillholes: {len(drillhole_data)} traces processed")

        return profile_data, geol_data, struct_data, drillhole_data, messages

