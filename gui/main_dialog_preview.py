# -*- coding: utf-8 -*-
"""
Preview management module for SecInterp main dialog.

This module handles preview generation, rendering, and updates,
separating preview logic from the main dialog class.
"""

from typing import Optional, Tuple, Dict, Any, TYPE_CHECKING
from pathlib import Path
import tempfile

from qgis.core import QgsVectorLayer, QgsRasterLayer
from ..core.types import ProfileData, GeologyData, StructureData
from ..core import utils as scu
from ..core import validation as vu
from ..logger_config import get_logger

if TYPE_CHECKING:
    from .main_dialog import SecInterpDialog

logger = get_logger(__name__)


class PreviewManager:
    """Manages preview generation and rendering for the dialog.
    
    This class encapsulates all preview-related logic, including data
    generation, rendering, and updates based on user interactions.
    """
    
    def __init__(self, dialog: 'SecInterpDialog'):
        """Initialize preview manager with reference to parent dialog.
        
        Args:
            dialog: The SecInterpDialog instance
        """
        self.dialog = dialog
        self.cached_data: Dict[str, Any] = {
            'topo': None,
            'geol': None,
            'struct': None
        }
    
    def generate_preview(self) -> Tuple[bool, str]:
        """Generate complete preview with all available data layers.
        
        This is the main preview generation method that orchestrates
        data generation and rendering.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # 1. Validation
            raster_layer, line_layer, band_num = self._validate_requirements()
            
            self.dialog.results.setPlainText("Generating preview...")
            
            # 2. Data Generation
            with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
                tmp_path = Path(tmp.name)
            
            try:
                # Generate topography
                profile_data = self.generate_topography(line_layer, raster_layer, band_num)
                
                if not profile_data or len(profile_data) < 2:
                    return False, "No profile data generated. Check that the line intersects the raster."
                
                # Generate geology (optional)
                geol_data = self.generate_geology(line_layer, raster_layer, band_num)
                
                # Generate structures (optional)
                buffer_dist = self._get_buffer_distance()
                struct_data = self.generate_structures(line_layer, buffer_dist)
                
                # Cache the data
                self.cached_data['topo'] = profile_data
                self.cached_data['geol'] = geol_data
                self.cached_data['struct'] = struct_data
                
            finally:
                if tmp_path.exists():
                    tmp_path.unlink()
            
            # 3. Visualization
            self.dialog.plugin_instance.draw_preview(profile_data, geol_data, struct_data)
            
            # 4. Results Reporting
            result_msg = self._format_results_message(profile_data, geol_data, struct_data, buffer_dist)
            self.dialog.results.setPlainText(result_msg)
            
            return True, "Preview generated successfully"
            
        except ValueError as e:
            error_msg = f"⚠ {str(e)}"
            self.dialog.results.setPlainText(error_msg)
            return False, str(e)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            error_msg = f"⚠ Error generating preview: {str(e)}\\n\\nDetails:\\n{error_details}"
            self.dialog.results.setPlainText(error_msg)
            logger.error(f"Preview generation failed: {e}", exc_info=True)
            return False, str(e)
    
    def update_from_checkboxes(self) -> None:
        """Update preview when checkboxes change.
        
        This method re-renders the preview using cached data and
        current checkbox states without regenerating data.
        """
        if not self.cached_data['topo']:
            return  # No data to display
        
        # Get checkbox states
        show_topo = self.dialog.show_topography.isChecked()
        show_geol = self.dialog.show_geology.isChecked()
        show_struct = self.dialog.show_structures.isChecked()
        
        # Prepare data based on checkboxes
        topo_data = self.cached_data['topo'] if show_topo else None
        geol_data = self.cached_data['geol'] if show_geol else None
        struct_data = self.cached_data['struct'] if show_struct else None
        
        # Re-render
        self.dialog.plugin_instance.draw_preview(topo_data, geol_data, struct_data)
    
    def generate_topography(
        self,
        line_layer: QgsVectorLayer,
        raster_layer: QgsRasterLayer,
        band_num: int
    ) -> Optional[ProfileData]:
        """Generate topographic profile data.
        
        Args:
            line_layer: Cross-section line layer
            raster_layer: DEM raster layer
            band_num: Raster band number
        
        Returns:
            List of (distance, elevation) tuples or None if failed
        """
        try:
            return self.dialog.plugin_instance.profile_service.generate_topographic_profile(
                line_layer, raster_layer, band_num
            )
        except Exception as e:
            logger.error(f"Error generating topography: {e}", exc_info=True)
            return None
    
    def generate_geology(
        self,
        line_layer: QgsVectorLayer,
        raster_layer: QgsRasterLayer,
        band_num: int
    ) -> Optional[GeologyData]:
        """Generate geological profile data if outcrop layer is selected.
        
        Args:
            line_layer: Cross-section line layer
            raster_layer: DEM raster layer
            band_num: Raster band number
        
        Returns:
            List of (distance, elevation, geology_name) tuples or None
        """
        outcrop_layer = self.dialog.outcrop.currentLayer()
        if not outcrop_layer:
            logger.debug("No outcrop layer selected")
            return None
        
        outcrop_name_field = self.dialog.ocropname.currentField()
        if not outcrop_name_field:
            logger.debug("No outcrop name field selected")
            return None
        
        try:
            logger.info(f"Generating geological profile with field: {outcrop_name_field}")
            result = self.dialog.plugin_instance.geology_service.generate_geological_profile(
                line_layer,
                raster_layer,
                outcrop_layer,
                outcrop_name_field,
                band_num,
            )
            logger.info(f"Geological profile result: {len(result) if result else 0} points")
            return result
        except Exception as e:
            logger.error(f"Error generating geological profile: {e}", exc_info=True)
            return None
    
    def generate_structures(
        self,
        line_layer: QgsVectorLayer,
        buffer_dist: float
    ) -> Optional[StructureData]:
        """Generate structural data if structural layer is selected.
        
        Args:
            line_layer: Cross-section line layer
            buffer_dist: Buffer distance in meters
        
        Returns:
            List of (distance, apparent_dip) tuples or None
        """
        structural_layer = self.dialog.structural.currentLayer()
        if not structural_layer:
            return None
        
        dip_field = self.dialog.dip.currentField()
        strike_field = self.dialog.strike.currentField()
        
        if not dip_field or not strike_field:
            return None
        
        try:
            # Get line azimuth
            line_feat = next(line_layer.getFeatures(), None)
            if not line_feat:
                return None
            
            line_geom = line_feat.geometry()
            line_azimuth = scu.calculate_line_azimuth(line_geom)
            
            return self.dialog.plugin_instance.structure_service.project_structures(
                line_layer,
                structural_layer,
                buffer_dist,
                line_azimuth,
                dip_field,
                strike_field,
            )
        except Exception as e:
            logger.error(f"Error generating structures: {e}", exc_info=True)
            return None
    
    def _validate_requirements(self) -> Tuple[QgsRasterLayer, QgsVectorLayer, int]:
        """Validate minimum requirements for preview generation.
        
        Returns:
            Tuple of (raster_layer, line_layer, band_num)
        
        Raises:
            ValueError: If validation fails
        """
        raster_layer = self.dialog.rasterdem.currentLayer()
        if not raster_layer:
            raise ValueError("No raster layer selected")
        
        line_layer = self.dialog.crossline.currentLayer()
        if not line_layer:
            raise ValueError("No crossline layer selected")
        
        band_num = self.dialog.band.currentBand()
        if not band_num:
            raise ValueError("No band selected")
        
        return raster_layer, line_layer, band_num
    
    def _get_buffer_distance(self) -> float:
        """Get buffer distance from dialog, with fallback to default.
        
        Returns:
            Buffer distance in meters
        """
        _, _, buffer_dist = vu.validate_numeric_input(
            self.dialog.buffer_distance.text(),
            field_name="Buffer distance",
            allow_empty=True,
        )
        return buffer_dist if buffer_dist is not None else 100.0
    
    def _format_results_message(
        self,
        profile_data: ProfileData,
        geol_data: Optional[GeologyData],
        struct_data: Optional[StructureData],
        buffer_dist: float
    ) -> str:
        """Format results message for display.
        
        Args:
            profile_data: Topographic profile data
            geol_data: Geological profile data (optional)
            struct_data: Structural data (optional)
            buffer_dist: Buffer distance used
        
        Returns:
            Formatted message string
        """
        lines = [
            "✓ Preview generated!",
            "",
            f"Topography: {len(profile_data)} points",
        ]
        
        if geol_data:
            lines.append(f"Geology: {len(geol_data)} points")
        else:
            lines.append("Geology: No intersections or layer not selected")
        
        if struct_data:
            lines.append(f"Structures: {len(struct_data)} points")
        else:
            lines.append(f"Structures: None in {buffer_dist}m buffer or layer not selected")
        
        lines.extend([
            "",
            f"Distance: {profile_data[0][0]:.1f} - {profile_data[-1][0]:.1f} m",
            f"Elevation: {min(p[1] for p in profile_data):.1f} - {max(p[1] for p in profile_data):.1f} m",
            "",
            "Adjust 'Vert. Exag.' and click Preview to update."
        ])
        
        return "\n".join(lines)
