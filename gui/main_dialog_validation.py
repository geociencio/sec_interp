# -*- coding: utf-8 -*-
"""
Validation module for SecInterp main dialog.

This module handles all validation logic for dialog inputs,
separating concerns and making the code more testable and maintainable.
"""

from typing import Tuple, List, Optional, TYPE_CHECKING
from qgis.core import QgsVectorLayer, QgsRasterLayer, QgsWkbTypes
from qgis.PyQt.QtCore import QVariant

from ..core import validation as vu
from .main_dialog_config import ValidationMessages

if TYPE_CHECKING:
    from .main_dialog import SecInterpDialog


class DialogValidator:
    """Handles all validation logic for SecInterpDialog.
    
    This class encapsulates validation logic that was previously
    embedded in the main dialog class, improving separation of concerns
    and testability.
    """
    
    def __init__(self, dialog: 'SecInterpDialog'):
        """Initialize validator with reference to parent dialog.
        
        Args:
            dialog: The SecInterpDialog instance to validate
        """
        self.dialog = dialog
    
    def validate_inputs(self) -> Tuple[bool, str]:
        """Validate all dialog inputs.
        
        This is the main validation orchestrator that checks all required
        and optional inputs for correctness.
        
        Returns:
            Tuple of (is_valid, error_message). If valid, error_message is empty.
        """
        errors: List[str] = []
        
        # Run all validation checks
        validators = [
            self._validate_raster_layer,
            self._validate_section_line,
            self._validate_output_path,
            self._validate_numeric_inputs,
            self._validate_geology_inputs,
            self._validate_structure_inputs,
        ]
        
        for validator in validators:
            error = validator()
            if error:
                errors.append(error)
        
        if errors:
            return False, "\\n".join(errors)
        
        return True, ""
    
    def validate_preview_requirements(self) -> Tuple[bool, str]:
        """Validate minimum requirements for preview generation.
        
        Preview requires at minimum:
        - DEM raster layer
        - Cross-section line
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        errors: List[str] = []
        
        # Check raster layer
        raster_layer = self.dialog.rasterdem.currentLayer()
        if not raster_layer:
            errors.append(ValidationMessages.MISSING_RASTER)
        
        # Check section line
        line_layer = self.dialog.crossline.currentLayer()
        if not line_layer:
            errors.append(ValidationMessages.MISSING_SECTION_LINE)
        
        if errors:
            return False, "\\n".join(errors)
        
        return True, ""
    
    def _validate_raster_layer(self) -> Optional[str]:
        """Validate raster DEM layer selection.
        
        Returns:
            Error message if invalid, None if valid
        """
        raster_layer = self.dialog.rasterdem.currentLayer()
        if not raster_layer:
            return ValidationMessages.MISSING_RASTER
        
        # Validate band number
        band_num = self.dialog.band.currentBand()
        if not band_num:
            return "No band selected"
        
        is_valid, error = vu.validate_raster_band(raster_layer, band_num)
        if not is_valid:
            return error
        
        return None
    
    def _validate_section_line(self) -> Optional[str]:
        """Validate cross-section line layer selection.
        
        Returns:
            Error message if invalid, None if valid
        """
        line_layer = self.dialog.crossline.currentLayer()
        if not line_layer:
            return ValidationMessages.MISSING_SECTION_LINE
        
        # Validate geometry type
        is_valid, error = vu.validate_layer_geometry(
            line_layer, QgsWkbTypes.LineGeometry
        )
        if not is_valid:
            return error
        
        # Validate has features
        is_valid, error = vu.validate_layer_has_features(line_layer)
        if not is_valid:
            return error
        
        return None
    
    def _validate_output_path(self) -> Optional[str]:
        """Validate output directory path.
        
        Returns:
            Error message if invalid, None if valid
        """
        output_path = self.dialog.dest_fold.filePath()
        if not output_path:
            return ValidationMessages.MISSING_OUTPUT_PATH
        
        is_valid, error, _ = vu.validate_output_path(output_path)
        if not is_valid:
            return error
        
        return None
    
    def _validate_numeric_inputs(self) -> Optional[str]:
        """Validate all numeric input fields.
        
        Returns:
            Error message if any invalid, None if all valid
        """
        errors: List[str] = []
        
        # Scale
        is_valid, error, _ = vu.validate_numeric_input(
            self.dialog.scale.text(), min_val=1, field_name="Scale"
        )
        if not is_valid:
            errors.append(error)
        
        # Vertical exaggeration
        is_valid, error, _ = vu.validate_numeric_input(
            self.dialog.vertexag.text(), min_val=0.1, field_name="Vertical exaggeration"
        )
        if not is_valid:
            errors.append(error)
        
        # Buffer distance
        is_valid, error, _ = vu.validate_numeric_input(
            self.dialog.buffer_distance.text(), min_val=0, field_name="Buffer distance"
        )
        if not is_valid:
            errors.append(error)
        
        # Dip scale factor
        is_valid, error, _ = vu.validate_numeric_input(
            self.dialog.dip_scale_factor.text(), min_val=0.1, field_name="Dip scale factor"
        )
        if not is_valid:
            errors.append(error)
        
        if errors:
            return "\\n".join(errors)
        
        return None
    
    def _validate_geology_inputs(self) -> Optional[str]:
        """Validate geological layer inputs if selected.
        
        Returns:
            Error message if invalid, None if valid or not selected
        """
        outcrop_layer = self.dialog.outcrop.currentLayer()
        if not outcrop_layer:
            return None  # Optional layer, skip if not selected
        
        errors: List[str] = []
        
        # Validate geometry type
        is_valid, error = vu.validate_layer_geometry(
            outcrop_layer, QgsWkbTypes.PolygonGeometry
        )
        if not is_valid:
            errors.append(error)
            return "\\n".join(errors)  # Don't continue if geometry is wrong
        
        # Validate has features
        is_valid, error = vu.validate_layer_has_features(outcrop_layer)
        if not is_valid:
            errors.append(error)
        
        # Validate outcrop name field
        if not self.dialog.ocropname.currentText():
            errors.append(ValidationMessages.MISSING_OUTCROP_FIELD)
        else:
            field_name = self.dialog.ocropname.currentData()
            is_valid, error = vu.validate_field_exists(outcrop_layer, field_name)
            if not is_valid:
                errors.append(error)
        
        if errors:
            return "\\n".join(errors)
        
        return None
    
    def _validate_structure_inputs(self) -> Optional[str]:
        """Validate structural layer inputs if selected.
        
        Returns:
            Error message if invalid, None if valid or not selected
        """
        struct_layer = self.dialog.structural.currentLayer()
        if not struct_layer:
            return None  # Optional layer, skip if not selected
        
        errors: List[str] = []
        
        # Validate geometry type
        is_valid, error = vu.validate_layer_geometry(
            struct_layer, QgsWkbTypes.PointGeometry
        )
        if not is_valid:
            errors.append(error)
            return "\\n".join(errors)  # Don't continue if geometry is wrong
        
        # Validate has features
        is_valid, error = vu.validate_layer_has_features(struct_layer)
        if not is_valid:
            errors.append(error)
        
        # Validate dip field
        if not self.dialog.dip.currentText():
            errors.append(ValidationMessages.MISSING_DIP_FIELD)
        else:
            dip_field = self.dialog.dip.currentData()
            is_valid, error = vu.validate_field_exists(struct_layer, dip_field)
            if not is_valid:
                errors.append(error)
            else:
                # Validate field type (should be numeric)
                is_valid, error = vu.validate_field_type(
                    struct_layer, dip_field, [QVariant.Int, QVariant.Double]
                )
                if not is_valid:
                    errors.append(error)
        
        # Validate strike field
        if not self.dialog.strike.currentText():
            errors.append(ValidationMessages.MISSING_STRIKE_FIELD)
        else:
            strike_field = self.dialog.strike.currentData()
            is_valid, error = vu.validate_field_exists(struct_layer, strike_field)
            if not is_valid:
                errors.append(error)
            else:
                # Validate field type (should be numeric)
                is_valid, error = vu.validate_field_type(
                    struct_layer, strike_field, [QVariant.Int, QVariant.Double]
                )
                if not is_valid:
                    errors.append(error)
        
        if errors:
            return "\\n".join(errors)
        
        return None
