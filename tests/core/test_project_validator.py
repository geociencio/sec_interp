"""Tests for project validation orchestrator."""

from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase

from sec_interp.core.validation.project_validator import (
    ValidationParams,
    ProjectValidator,
)
from sec_interp.core.validation.validation_helpers import validate_reasonable_ranges
from sec_interp.core.validation.layer_metadata import (
    GEOMETRY_LINE,
    KIND_RASTER,
    KIND_VECTOR,
    LayerMetadata,
)
from sec_interp.core.validation.project_validators import (
    SECTION_GEOGRAPHIC_CRS_ERROR,
    SECTION_TWO_POINT_ERROR,
    SECTION_ZERO_LENGTH_ERROR,
)
from sec_interp.core.exceptions import ValidationError


def _raster_metadata():
    return LayerMetadata(name="DEM", is_valid=True, kind=KIND_RASTER, band_count=1)


def _vector_metadata():
    return LayerMetadata(name="Line", is_valid=True, kind=KIND_VECTOR)


def _line_metadata(crs_is_geographic=False):
    return LayerMetadata(
        name="Line",
        is_valid=True,
        kind=KIND_VECTOR,
        geometry_type=GEOMETRY_LINE,
        feature_count=1,
        crs_is_geographic=crs_is_geographic,
    )


class TestProjectValidator(BaseTestCase):
    """Tests for project_validator.py"""

    def test_validate_reasonable_ranges(self):
        """Test detection of extreme/erroneous values."""
        warnings = validate_reasonable_ranges({"vert_exag": 2.0, "buffer": 100})
        self.assertEqual(len(warnings), 0)

        warnings = validate_reasonable_ranges({"vert_exag": 15.0})
        self.assertEqual(len(warnings), 1)
        self.assertIn("very high", warnings[0])

        warnings = validate_reasonable_ranges({"buffer": -10})
        self.assertEqual(len(warnings), 1)
        self.assertIn("cannot be negative", warnings[0])

    def test_crs_compatibility_warning(self):
        """Mismatched CRSs warn; matching CRSs stay silent."""
        same = ValidationParams(
            raster_layer=LayerMetadata(
                name="DEM", is_valid=True, kind=KIND_RASTER, crs_authid="EPSG:3857"
            ),
            line_layer=LayerMetadata(
                name="Line", is_valid=True, kind=KIND_VECTOR, crs_authid="EPSG:3857"
            ),
        )
        self.assertEqual(ProjectValidator.crs_compatibility_warning(same), "")

        mismatch = ValidationParams(
            raster_layer=LayerMetadata(
                name="DEM", is_valid=True, kind=KIND_RASTER, crs_authid="EPSG:4326"
            ),
            line_layer=LayerMetadata(
                name="Line", is_valid=True, kind=KIND_VECTOR, crs_authid="EPSG:3857"
            ),
        )
        warning = ProjectValidator.crs_compatibility_warning(mismatch)
        self.assertIn("CRS mismatch", warning)
        self.assertIn("EPSG:3857", warning)

    def test_crs_plausibility_error_blocks_mislabelled_layer(self):
        """A degree-like extent declared as projected is reported as an error."""
        params = ValidationParams(
            raster_layer=LayerMetadata(
                name="DEM",
                is_valid=True,
                kind=KIND_RASTER,
                crs_is_geographic=False,
                extent_xmin=-99.0,
                extent_ymin=22.7,
                extent_xmax=-98.99,
                extent_ymax=23.0,
            ),
        )

        error = ProjectValidator.crs_plausibility_error(params)

        self.assertIn("DEM", error)

    def test_crs_plausibility_error_silent_for_plausible_layer(self):
        """Correctly labelled layers produce no error."""
        params = ValidationParams(
            raster_layer=LayerMetadata(
                name="DEM",
                is_valid=True,
                kind=KIND_RASTER,
                crs_is_geographic=True,
                extent_xmin=-99.0,
                extent_ymin=22.7,
                extent_xmax=-98.99,
                extent_ymax=23.0,
            ),
        )

        self.assertEqual(ProjectValidator.crs_plausibility_error(params), "")

    @patch("qgis.core.QgsProject.instance")
    def test_validate_preview_requirements(self, mock_project):
        """Test minimal requirements for preview."""
        params = ValidationParams()
        with (
            patch(
                "sec_interp.core.validation.project_validators.validate_layer_geometry",
                return_value=(True, ""),
            ),
            patch(
                "sec_interp.core.validation.project_validators.validate_layer_has_features",
                return_value=(True, ""),
            ),
        ):
            # Missing everything
            with self.assertRaises(ValidationError):
                ProjectValidator.validate_preview_requirements(params)

            # Valid setup
            params.raster_layer = _raster_metadata()
            params.line_layer = _vector_metadata()
            self.assertTrue(ProjectValidator.validate_preview_requirements(params))

    @patch("sec_interp.core.validation.path_validator.validate_output_path")
    @patch("qgis.core.QgsProject.instance")
    def test_validate_all_success(self, mock_project, mock_output):
        """Test full validation success path."""
        mock_output.return_value = (True, "", None)

        params = ValidationParams(
            raster_layer=_raster_metadata(),
            line_layer=_vector_metadata(),
            output_path="/tmp/test",
            scale=1000,
            vert_exag=1.0,
        )

        with (
            patch(
                "sec_interp.core.validation.project_validators.validate_layer_geometry",
                return_value=(True, ""),
            ),
            patch(
                "sec_interp.core.validation.project_validators.validate_layer_has_features",
                return_value=(True, ""),
            ),
        ):
            self.assertTrue(ProjectValidator.validate_all(params))

    def test_validate_all_numeric_failures(self):
        """Test numeric range failures in validate_all."""
        params = ValidationParams(
            raster_layer=_raster_metadata(),
            line_layer=_vector_metadata(),
            output_path="/tmp/test",
            scale=0.5,  # < 1
            vert_exag=0.05,  # < 0.1
        )

        with (
            patch(
                "sec_interp.core.validation.project_validators.validate_layer_geometry",
                return_value=(True, ""),
            ),
            patch(
                "sec_interp.core.validation.project_validators.validate_layer_has_features",
                return_value=(True, ""),
            ),
            patch(
                "sec_interp.core.validation.path_validator.validate_output_path",
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

        params.collar_layer = LayerMetadata(is_valid=True)
        params.collar_id = "HOLEID"
        params.collar_use_geom = True
        self.assertTrue(ProjectValidator.is_drillhole_complete(params))

        params.survey_layer = LayerMetadata(is_valid=True)
        self.assertFalse(ProjectValidator.is_drillhole_complete(params))

        params.survey_id = "ID"
        params.survey_depth = "DEPTH"
        params.survey_azim = "AZIM"
        params.survey_incl = "INCL"
        self.assertTrue(ProjectValidator.is_drillhole_complete(params))

    @patch("sec_interp.core.validation.layer_validator.validate_field_exists")
    @patch("sec_interp.core.validation.layer_validator.validate_layer_has_features")
    @patch("sec_interp.core.validation.layer_validator.validate_layer_geometry")
    def test_is_geology_complete(self, mock_geom, mock_feat, mock_field):
        """Test geology completion check."""
        mock_geom.return_value = (True, "")
        mock_feat.return_value = (True, "")
        mock_field.return_value = (True, "")

        params = ValidationParams()
        self.assertFalse(ProjectValidator.is_geology_complete(params))

        params.outcrop_layer = LayerMetadata(is_valid=True)
        params.outcrop_field = "UNIT"

        self.assertTrue(ProjectValidator.is_geology_complete(params))

    @patch(
        "sec_interp.core.validation.project_validators.validate_structural_requirements"
    )
    def test_is_structure_complete(self, mock_struct):
        """Test structure completion check."""
        mock_struct.return_value = (True, "")

        params = ValidationParams()
        self.assertFalse(ProjectValidator.is_structure_complete(params))

        params.struct_layer = LayerMetadata(is_valid=True)
        params.struct_dip_field = "DIP"
        params.struct_strike_field = "STRIKE"

        self.assertTrue(ProjectValidator.is_structure_complete(params))


class TestSectionLineGeometryRule(BaseTestCase):
    """The mandatory 2-point section-line invariant."""

    def _params(self, **overrides):
        base = {
            "line_layer": _line_metadata(),
            "line_vertex_count": 2,
            "line_length": 100.0,
        }
        base.update(overrides)
        return ValidationParams(**base)

    def test_valid_two_point_line(self):
        """A 2-vertex, non-zero, projected line has no geometry error."""
        self.assertEqual(ProjectValidator.section_geometry_error(self._params()), "")

    def test_missing_layer_yields_no_error(self):
        """Without a line layer the rule abstains (presence handled elsewhere)."""
        self.assertEqual(ProjectValidator.section_geometry_error(ValidationParams()), "")

    def test_three_vertices_rejected(self):
        """A polyline with more than two vertices violates the invariant."""
        self.assertEqual(
            ProjectValidator.section_geometry_error(self._params(line_vertex_count=3)),
            SECTION_TWO_POINT_ERROR,
        )

    def test_zero_length_rejected(self):
        """A zero-length section line is rejected."""
        self.assertEqual(
            ProjectValidator.section_geometry_error(self._params(line_length=0.0)),
            SECTION_ZERO_LENGTH_ERROR,
        )

    def test_geographic_crs_rejected(self):
        """A geographic CRS (degrees) is rejected."""
        self.assertEqual(
            ProjectValidator.section_geometry_error(
                self._params(line_layer=_line_metadata(crs_is_geographic=True))
            ),
            SECTION_GEOGRAPHIC_CRS_ERROR,
        )

    def test_unknown_primitives_skip_checks(self):
        """Unknown vertex count / length (None) skip their checks."""
        params = ValidationParams(line_layer=_line_metadata())
        self.assertEqual(ProjectValidator.section_geometry_error(params), "")

    def test_preview_pipeline_surfaces_two_point_error(self):
        """validate_preview_requirements reports the 2-point message."""
        params = self._params(line_vertex_count=3)
        with (
            patch(
                "sec_interp.core.validation.project_validators.validate_layer_geometry",
                return_value=(True, ""),
            ),
            patch(
                "sec_interp.core.validation.project_validators.validate_layer_has_features",
                return_value=(True, ""),
            ),
        ):
            with self.assertRaises(ValidationError) as cm:
                ProjectValidator.validate_preview_requirements(params)
        self.assertIn(SECTION_TWO_POINT_ERROR, str(cm.exception))
