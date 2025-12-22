"""Preview service for SecInterp.

This module provides a service to orchestrate the generation of all
preview components, decoupled from the GUI layer.
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple, Dict
from pathlib import Path

from qgis.core import QgsRasterLayer, QgsVectorLayer, QgsGeometry, QgsPointXY, QgsDistanceArea

from sec_interp.core.types import GeologyData, ProfileData, StructureData
from sec_interp.core import utils as scu
from sec_interp.core.performance_metrics import MetricsCollector, PerformanceTimer

@dataclass
class PreviewParams:
    """Parameters for preview generation."""
    raster_layer: QgsRasterLayer
    line_layer: QgsVectorLayer
    band_num: int
    buffer_dist: float = 100.0
    
    # Geology params
    outcrop_layer: Optional[QgsVectorLayer] = None
    outcrop_name_field: Optional[str] = None
    
    # Structure params
    struct_layer: Optional[QgsVectorLayer] = None
    dip_field: Optional[str] = None
    strike_field: Optional[str] = None
    dip_scale_factor: float = 1.0
    
    # Drillhole params
    collar_layer: Optional[QgsVectorLayer] = None
    collar_id_field: Optional[str] = None
    collar_use_geometry: bool = True
    collar_x_field: Optional[str] = None
    collar_y_field: Optional[str] = None
    collar_z_field: Optional[str] = None
    collar_depth_field: Optional[str] = None
    survey_layer: Optional[QgsVectorLayer] = None
    survey_id_field: Optional[str] = None
    survey_depth_field: Optional[str] = None
    survey_azim_field: Optional[str] = None
    survey_incl_field: Optional[str] = None
    interval_layer: Optional[QgsVectorLayer] = None
    interval_id_field: Optional[str] = None
    interval_from_field: Optional[str] = None
    interval_to_field: Optional[str] = None
    interval_lith_field: Optional[str] = None

@dataclass
class PreviewResult:
    """Consolidated results of preview generation."""
    topo: Optional[ProfileData] = None
    geol: Optional[GeologyData] = None
    struct: Optional[StructureData] = None
    drillhole: Optional[Any] = None
    metrics: MetricsCollector = field(default_factory=MetricsCollector)
    buffer_dist: float = 0.0

    def get_elevation_range(self) -> Tuple[float, float]:
        """Calculate the global elevation range across all data layers.

        Returns:
            Tuple[float, float]: (min_elevation, max_elevation)
        """
        elevations = []
        if self.topo:
            elevations.extend(p[1] for p in self.topo)
        if self.geol:
            for segment in self.geol:
                elevations.extend(p[1] for p in segment.points)
        if self.struct:
            elevations.extend(m.elevation for m in self.struct)
        if self.drillhole:
            for _, trace, segments in self.drillhole:
                if trace:
                    elevations.extend(p[1] for p in trace)
                if segments:
                    for seg in segments:
                        elevations.extend(p[1] for p in seg.points)

        if not elevations:
            return 0.0, 0.0
        return min(elevations), max(elevations)

    def get_distance_range(self) -> Tuple[float, float]:
        """Calculate the global distance range from topographic data.

        Returns:
            Tuple[float, float]: (min_distance, max_distance)
        """
        if not self.topo:
            return 0.0, 0.0
        return self.topo[0][0], self.topo[-1][0]

class PreviewService:
    """Orchestrates preview data generation."""
    
    def __init__(self, controller: Any):
        """Initialize with plugin controller to access other services.
        
        Args:
            controller: The SecInterpController instance
        """
        self.controller = controller

    def generate_all(self, params: PreviewParams, transform_context: Any) -> PreviewResult:
        """Generate all preview components.
        
        Args:
            params: Parameters for generation
            transform_context: QgsCoordinateTransformContext from map settings
            
        Returns:
            Consolidated preview results
        """
        result = PreviewResult(buffer_dist=params.buffer_dist)
        self.transform_context = transform_context
        
        # 1. Topography
        with PerformanceTimer("Topography Generation", result.metrics):
            result.topo = self.controller.profile_service.generate_topographic_profile(
                params.line_layer, params.raster_layer, params.band_num
            )
            if result.topo:
                result.metrics.record_count("Topography Points", len(result.topo))

        # 2. Structures
        if params.struct_layer and params.dip_field and params.strike_field:
            with PerformanceTimer("Structure Generation", result.metrics):
                line_feat = next(params.line_layer.getFeatures(), None)
                if line_feat:
                    line_geom = line_feat.geometry()
                    line_azimuth = scu.calculate_line_azimuth(line_geom)
                    
                    result.struct = self.controller.structure_service.project_structures(
                        line_lyr=params.line_layer,
                        raster_lyr=params.raster_layer,
                        struct_lyr=params.struct_layer,
                        buffer_m=params.buffer_dist,
                        line_az=line_azimuth,
                        dip_field=params.dip_field,
                        strike_field=params.strike_field,
                        band_number=params.band_num,
                    )
                    if result.struct:
                        result.metrics.record_count("Structure Points", len(result.struct))

        # 3. Drillholes
        if params.collar_layer:
            with PerformanceTimer("Drillhole Generation", result.metrics):
                result.drillhole = self._generate_drillholes(params)
                if result.drillhole:
                    result.metrics.record_count("Drillholes", len(result.drillhole))
        
        return result

    def _generate_drillholes(self, params: PreviewParams) -> Optional[Any]:
        """Internal helper for drillhole generation."""
        try:
            line_feat = next(params.line_layer.getFeatures(), None)
            if not line_feat:
                return None
                
            line_geom = line_feat.geometry()
            if line_geom.isMultipart():
                lines = line_geom.asMultiPolyline()
                points = lines[0] if lines else []
            else:
                points = line_geom.asPolyline()
                
            if not points:
                return None
                
            line_start = points[0]
            
            # Setup distance area
            distance_area = QgsDistanceArea()
            distance_area.setSourceCrs(params.line_layer.crs(), self.transform_context)
            
            projected_collars = self.controller.drillhole_service.project_collars(
                collar_layer=params.collar_layer,
                line_geom=line_geom,
                line_start=line_start,
                distance_area=distance_area,
                buffer_width=params.buffer_dist,
                collar_id_field=params.collar_id_field,
                use_geometry=params.collar_use_geometry,
                collar_x_field=params.collar_x_field,
                collar_y_field=params.collar_y_field,
                collar_z_field=params.collar_z_field,
                collar_depth_field=params.collar_depth_field,
                dem_layer=params.raster_layer
            )
            
            if not projected_collars:
                return None
                
            survey_fields = {
                "id": params.survey_id_field,
                "depth": params.survey_depth_field,
                "azim": params.survey_azim_field,
                "incl": params.survey_incl_field
            }
            
            interval_fields = {
                "id": params.interval_id_field,
                "from": params.interval_from_field,
                "to": params.interval_to_field,
                "lith": params.interval_lith_field
            }

            _, drillhole_data = self.controller.drillhole_service.process_intervals(
                collar_points=projected_collars,
                collar_layer=params.collar_layer,
                survey_layer=params.survey_layer,
                interval_layer=params.interval_layer,
                collar_id_field=params.collar_id_field,
                use_geometry=params.collar_use_geometry,
                collar_x_field=params.collar_x_field,
                collar_y_field=params.collar_y_field,
                line_geom=line_geom,
                line_start=line_start,
                distance_area=distance_area,
                buffer_width=params.buffer_dist,
                section_azimuth=scu.calculate_line_azimuth(line_geom),
                survey_fields=survey_fields,
                interval_fields=interval_fields
            )
            
            return drillhole_data
            
        except Exception:
            # logger.error(f"Error in PreviewService._generate_drillholes: {e}", exc_info=True)
            return None
