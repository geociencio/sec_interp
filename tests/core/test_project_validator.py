"""Tests for project validation orchestrator."""

from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from qgis.core import QgsVectorLayer, QgsRasterLayer, QgsWkbTypes

from sec_interp.core.validation.project_validator import (
    ValidationParams,
    ProjectValidator,
)
from sec_interp.core.validation.validation_helpers import validate_reasonable_ranges
from sec_interp.core.exceptions import ValidationError


class TestProjectValidator(BaseTestCase):
    """Tests for project_validator.py"""

    def test_validate_reasonable_ranges(self):
        """Test detection of extreme/erroneous values."""
        # Normal values
        warnings = validate_reasonable_ranges({"vert_exag": 2.0, "buffer": 100})
        self.assertEqual(len(warnings), 0)

        # High vertical exaggeration
        warnings = validate_reasonable_ranges({"vert_exag": 15.0})
        self.assertEqual(len(warnings), 1)
        self.assertIn("very high", warnings[0])

        # Negative buffer
        warnings = validate_reasonable_ranges({"buffer": -10})
        self.assertEqual(len(warnings), 1)
        self.assertIn("cannot be negative", warnings[0])

    def test_validate_preview_requirements(self):
        """Test minimal requirements for preview."""
        params = ValidationParams()

        # Missing everything
        with self.assertRaises(ValidationError):
            ProjectValidator.validate_preview_requirements(params)

        # Valid
        params.raster_layer = QgsRasterLayer()
        params.line_layer = QgsVectorLayer()
        self.assertTrue(ProjectValidator.validate_preview_requirements(params))

    @patch("sec_interp.core.validation.project_validator.validate_output_path")
    @patch("sec_interp.core.validation.project_validator.validate_layer_has_features")
    @patch("sec_interp.core.validation.project_validator.validate_layer_geometry")
    def test_validate_all_success(self, mock_geom, mock_feat, mock_output):
        """Test full validation success path."""
        mock_geom.return_value = (True, "")
        mock_feat.return_value = (True, "")
        mock_output.return_value = (True, "", None)

        params = ValidationParams(
            raster_layer=QgsRasterLayer(),
            line_layer=QgsVectorLayer(),
            output_path="/tmp/test",
            scale=1000,
            vert_exag=1.0,
        )

        self.assertTrue(ProjectValidator.validate_all(params))

    def test_validate_all_numeric_failures(self):
        """Test numeric range failures in validate_all."""
        params = ValidationParams(
            raster_layer=QgsRasterLayer(),
            line_layer=QgsVectorLayer(),
            output_path="/tmp/test",
            scale=0.5,  # < 1
            vert_exag=0.05,  # < 0.1
        )

        # Mock other validators to not fail
        with (
            patch(
                "sec_interp.core.validation.project_validator.validate_layer_geometry",
                return_value=(True, ""),
            ),
            patch(
                "sec_interp.core.validation.project_validator.validate_layer_has_features",
                return_value=(True, ""),
            ),
            patch(
                "sec_interp.core.validation.project_validator.validate_output_path",
                return_value=(True, "", None),
            ),
        ):

            with self.assertRaises(ValidationError) as cm:
                ProjectValidator.validate_all(params)

            self.assertIn("Scale must be >= 1", str(cm.exception))
            self.assertIn("Vertical exaggeration must be >= 0.1", str(cm.exception))

    def test_is_drillhole_complete(self):
        """Test drillhole completion check."""
        params = ValidationParams()
        self.assertFalse(ProjectValidator.is_drillhole_complete(params))

        # Collar ok
        params.collar_layer = MagicMock()
        params.collar_id = "HOLEID"
        params.collar_use_geom = True
        self.assertTrue(ProjectValidator.is_drillhole_complete(params))

        # Survey layer provided but fields missing
        params.survey_layer = MagicMock()
        self.assertFalse(ProjectValidator.is_drillhole_complete(params))

        # Survey layer fields ok
        params.survey_id = "ID"
        params.survey_depth = "DEPTH"
        params.survey_azim = "AZIM"
        params.survey_incl = "INCL"
        self.assertTrue(ProjectValidator.is_drillhole_complete(params))

    @patch("sec_interp.core.validation.project_validator.validate_field_exists")
    @patch("sec_interp.core.validation.project_validator.validate_layer_has_features")
    @patch("sec_interp.core.validation.project_validator.validate_layer_geometry")
    def test_is_geology_complete(self, mock_geom, mock_feat, mock_field):
        """Test geology completion check."""
        mock_geom.return_value = (True, "")
        mock_feat.return_value = (True, "")
        mock_field.return_value = (True, "")

        params = ValidationParams()
        self.assertFalse(ProjectValidator.is_geology_complete(params))

        params.outcrop_layer = MagicMock()
        params.outcrop_field = "UNIT"
        self.assertTrue(ProjectValidator.is_geology_complete(params))

    @patch(
        "sec_interp.core.validation.project_validator.validate_structural_requirements"
    )
    def test_is_structure_complete(self, mock_struct):
        """Test structure completion check."""
        mock_struct.return_value = (True, "")

        params = ValidationParams()
        self.assertFalse(ProjectValidator.is_structure_complete(params))

        params.struct_layer = MagicMock()
        params.struct_dip_field = "DIP"
        params.struct_strike_field = "STRIKE"
        self.assertTrue(ProjectValidator.is_structure_complete(params))
