from __future__ import annotations


"""Controller for SecInterp profile data generation.

This module handles the orchestration of various data generation services
(topography, geology, structures, drillholes) and manages result caching.
"""

import math
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Tuple

from sec_interp.core import utils as scu
from sec_interp.core.config import ConfigService
from sec_interp.core.data_cache import DataCache
from sec_interp.core.exceptions import DataMissingError, ProcessingError
from sec_interp.core.services import (
    DrillholeService,
    GeologyService,
    ProfileService,
    StructureService,
)
from sec_interp.core.types import PreviewParams
from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


class ProfileController:
    """Orchestrates data generation services for SecInterp profile creation."""

    def __init__(self):
        """Initialize services and the data cache."""
        self.config_service = ConfigService()
        self.data_cache = DataCache()
        self.profile_service = ProfileService()
        self.geology_service = GeologyService()
        self.structure_service = StructureService()
        self.drillhole_service = DrillholeService()
        logger.debug("ProfileController initialized")

    def connect_layer_notifications(self, layers: list[Any]) -> None:
        """Connect to layer signals for automatic cache invalidation on data changes.

        Args:
            layers: List of QgsMapLayer objects to monitor.
        """
        for layer in layers:
            if not layer:
                continue
            # When layer data changes, clear cache for its bucket or altogether
            layer.dataChanged.connect(self.data_cache.clear)
            logger.debug(f"Connected cache invalidation to layer: {layer.name()}")

    def get_cached_data(self, inputs: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Retrieve data from cache if available for the given inputs.

        Args:
            inputs: Dictionary of input parameters to generate cache key.

        Returns:
            Cached data dictionary if found, else None.
        """
        cache_key = self.data_cache.get_cache_key(inputs)
        return self.data_cache.get(cache_key)

    def cache_data(self, inputs: dict[str, Any], data: dict[str, Any]) -> None:
        """Cache the generated data resulting from the given inputs.

        Args:
            inputs: Dictionary of input parameters to generate cache key.
            data: Data dictionary to cache.
        """
        cache_key = self.data_cache.get_cache_key(inputs)
        self.data_cache.set(cache_key, data)

    def generate_profile_data(
        self, params: PreviewParams
    ) -> tuple[list, Any, Any, Any, list[str]]:
        """Unified method to generate all profile data components with granular caching.

        Orchestrates topography sampling, geology intersection, structural projection,
        and drillhole desurveying.

        Args:
            params: Validated input parameters for preview generation.

        Returns:
            tuple: A five-element tuple containing:
                - profile_data: List of topographic points (x, z).
                - geol_data: List of GeologySegment objects.
                - struct_data: List of StructureMeasurement objects.
                - drillhole_data: Drillhole projection result object.
                - messages: List of status or warning messages for the user.

        Raises:
            ProcessingError: If critical data (like topography) cannot be generated.
        """
        # Phase 5: Native validation
        params.validate()

        messages = []

        # Metadata for cache (LOD / max_points info)
        cache_meta = {
            "max_points": params.max_points,
            "canvas_width": params.canvas_width,
            "timestamp": time.time(),
        }

        # Cache key helpers updated to use params attributes
        def get_sub_key(param_values: list[Any]) -> str:
            # Simple hash for a subset of parameters
            import hashlib
            hasher = hashlib.md5()
            for val in param_values:
                from qgis.core import QgsMapLayer
                if isinstance(val, QgsMapLayer):
                    hasher.update(val.id().encode("utf-8"))
                else:
                    hasher.update(str(val).encode("utf-8"))
            return hasher.hexdigest()

        raster_layer = params.raster_layer
        line_layer = params.line_layer
        outcrop_layer = params.outcrop_layer
        structural_layer = params.struct_layer
        selected_band = params.band_num
        buffer_dist = params.buffer_dist

        # 1. Topography
        topo_key = get_sub_key(["selected_band", "max_points"])
        profile_data = self.data_cache.get("topo", topo_key)
        if profile_data:
            logger.debug("Cache hit: Topography")
        else:
            profile_data = self.profile_service.generate_topographic_profile(
                line_layer, raster_layer, selected_band
            )
            if not profile_data:
                raise ProcessingError("No topographic profile data was generated.")
            self.data_cache.set("topo", topo_key, profile_data, cache_meta)

        messages.append(
            f"✓ Data processed successfully!\n\nTopography: {len(profile_data)} points"
        )

        # 2. Geology
        geol_data = None
        if outcrop_layer:
            geol_key = get_sub_key([params.outcrop_layer, params.outcrop_name_field, params.band_num])
            geol_data = self.data_cache.get("geol", geol_key)
            if geol_data:
                logger.debug("Cache hit: Geology")
            else:
                outcrop_name_field = params.outcrop_name_field
                if outcrop_name_field:
                    geol_data = self.geology_service.generate_geological_profile(
                        line_layer,
                        raster_layer,
                        outcrop_layer,
                        outcrop_name_field,
                        selected_band,
                    )
                    if geol_data:
                        self.data_cache.set("geol", geol_key, geol_data, cache_meta)
                        messages.append(f"Geology: {len(geol_data)} segments")
                    else:
                        messages.append("Geology: No intersections")
                else:
                    messages.append("\n⚠ Outcrop layer selected but no geology field specified.")

        # 3. Structure
        struct_data = None
        if structural_layer:
            struct_key = get_sub_key([
                params.struct_layer, params.buffer_dist, params.dip_field,
                params.strike_field, params.band_num
            ])
            struct_data = self.data_cache.get("struct", struct_key)
            if struct_data:
                logger.debug("Cache hit: Structure")
            else:
                dip_field = params.dip_field
                strike_field = params.strike_field

                if dip_field and strike_field:
                    line_feat = next(line_layer.getFeatures(), None)
                    if line_feat:
                        line_geom = line_feat.geometry()
                        if line_geom and not line_geom.isNull():
                            line_azimuth = scu.calculate_line_azimuth(line_geom)
                            struct_data = self.structure_service.project_structures(
                                line_layer,
                                raster_layer,
                                structural_layer,
                                buffer_dist,
                                line_azimuth,
                                dip_field,
                                strike_field,
                                selected_band,
                            )

                            if struct_data:
                                self.data_cache.set("struct", struct_key, struct_data, cache_meta)
                                messages.append(f"Structures: {len(struct_data)} points")
                            else:
                                messages.append(f"Structures: None in {buffer_dist}m buffer")
                    else:
                        messages.append("\n⚠ Structural layer selected but dip/strike fields not specified.")

        # 4. Drillholes
        drillhole_data = None
        collar_layer = params.collar_layer
        if collar_layer:
            drill_key = get_sub_key([
                params.collar_layer, params.survey_layer, params.interval_layer,
                params.buffer_dist, params.collar_id_field, params.survey_id_field, params.interval_id_field
            ])
            drillhole_data = self.data_cache.get("drill", drill_key)
            if drillhole_data:
                logger.debug("Cache hit: Drillholes")
            else:
                # Derive required components
                line_feat = next(line_layer.getFeatures(), None)
                if line_feat:
                    section_geom = line_feat.geometry()
                    section_start = scu.get_line_vertices(section_geom)[0]
                    distance_area = scu.create_distance_area(line_layer.crs())

                    # Project Collars
                    collars = self.drillhole_service.project_collars(
                        collar_layer=collar_layer,
                        line_geom=section_geom,
                        line_start=section_start,
                        distance_area=distance_area,
                        buffer_width=buffer_dist,
                        collar_id_field=params.collar_id_field,
                        use_geometry=params.collar_use_geometry,
                        collar_x_field=params.collar_x_field,
                        collar_y_field=params.collar_y_field,
                        collar_z_field=params.collar_z_field,
                        collar_depth_field=params.collar_depth_field,
                        dem_layer=raster_layer,
                        line_crs=line_layer.crs(),
                    )

                    if collars:
                        # Process Intervals if survey/interval layers exist
                        survey_layer = params.survey_layer
                        interval_layer = params.interval_layer

                        if survey_layer and interval_layer:
                            section_azimuth = scu.calculate_line_azimuth(section_geom)
                            _, drillhole_data = self.drillhole_service.process_intervals(
                                collar_points=collars,
                                collar_layer=collar_layer,
                                survey_layer=survey_layer,
                                interval_layer=interval_layer,
                                collar_id_field=params.collar_id_field,
                                use_geometry=params.collar_use_geometry,
                                collar_x_field=params.collar_x_field,
                                collar_y_field=params.collar_y_field,
                                line_geom=section_geom,
                                line_start=section_start,
                                distance_area=distance_area,
                                buffer_width=buffer_dist,
                                section_azimuth=section_azimuth,
                                survey_fields={
                                    "id": params.survey_id_field,
                                    "depth": params.survey_depth_field,
                                    "azim": params.survey_azim_field,
                                    "incl": params.survey_incl_field,
                                },
                                interval_fields={
                                    "id": params.interval_id_field,
                                    "from": params.interval_from_field,
                                    "to": params.interval_to_field,
                                    "lith": params.interval_lith_field,
                                },
                            )
        return profile_data, geol_data, struct_data, drillhole_data, messages
