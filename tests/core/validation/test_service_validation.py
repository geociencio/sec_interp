"""Unit tests for Service Layer Domain Validation (Level 3)."""

from unittest.mock import MagicMock
from tests.base_test import BaseTestCase
from qgis.core import (
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsFields,
    QgsField,
    QgsCoordinateReferenceSystem,
    QMetaType,
)

from sec_interp.core.services.geology_service import GeologyService
from sec_interp.core.services.drillhole_service import DrillholeService
from sec_interp.core.services.drillhole.drillhole_orchestrator import (
    DrillholeTaskOrchestrator,
)
from sec_interp.core.exceptions import ValidationError, DataMissingError


class TestServiceValidation(BaseTestCase):
    """Test domain validation rules in services."""

    def setUp(self):
        super().setUp()
        self.geology_service = GeologyService()
        self.drillhole_service = DrillholeService()
        self.orchestrator = DrillholeTaskOrchestrator(self.drillhole_service)

        # Common Mocks
        self.mock_line_lyr = MagicMock()
        self.mock_line_lyr.isValid.return_value = True
        self.mock_line_lyr.name.return_value = "Line Layer"
        self.mock_line_lyr.crs.return_value = QgsCoordinateReferenceSystem("EPSG:32718")

        # Mock Geometry for Line (required for some checks)
        line_feat = QgsFeature()
        line_feat.setGeometry(
            QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(100, 0)])
        )
        self.mock_line_lyr.getFeatures.return_value = iter([line_feat])

        self.mock_raster_lyr = MagicMock()
        self.mock_raster_lyr.isValid.return_value = True
        self.mock_raster_lyr.bandCount.return_value = 1

        self.mock_outcrop_lyr = MagicMock()
        self.mock_outcrop_lyr.isValid.return_value = True

        # Mock Fields for Outcrop
        fields = QgsFields()
        fields.append(QgsField("unit", QMetaType.Type.String))
        self.mock_outcrop_lyr.fields.return_value = fields

    def test_geology_service_validates_band_number(self):
        """GeologyService should reject invalid band numbers."""
        # Case 0: Band <= 0
        with self.assertRaises(ValidationError) as cm:
            self.geology_service.generate_geological_profile(
                self.mock_line_lyr,
                self.mock_raster_lyr,
                self.mock_outcrop_lyr,
                "unit",
                band_number=0,
            )
        self.assertIn("positive", str(cm.exception))

        # Case 2: Band > bandCount
        self.mock_raster_lyr.bandCount.return_value = 1
        with self.assertRaises(ValidationError) as cm:
            self.geology_service.generate_geological_profile(
                self.mock_line_lyr,
                self.mock_raster_lyr,
                self.mock_outcrop_lyr,
                "unit",
                band_number=99,
            )
        self.assertIn("exceeds raster band count", str(cm.exception))

    def test_geology_service_validates_outcrop_field(self):
        """GeologyService should reject non-existent outcrop field."""
        # Field 'not_exist' is not in fields list
        with self.assertRaises(ValidationError) as cm:
            self.geology_service.generate_geological_profile(
                self.mock_line_lyr,
                self.mock_raster_lyr,
                self.mock_outcrop_lyr,
                "not_exist",
                band_number=1,
            )
        self.assertIn("Field 'not_exist' not found", str(cm.exception))

    def test_geology_service_validates_layer_validity(self):
        """GeologyService should check if layers are valid."""
        invalid_layer = MagicMock()
        invalid_layer.isValid.return_value = False
        invalid_layer.name.return_value = "Invalid Layer"

        with self.assertRaises(DataMissingError) as cm:
            self.geology_service.generate_geological_profile(
                invalid_layer, self.mock_raster_lyr, self.mock_outcrop_lyr, "unit"
            )
        self.assertIn("Invalid layer", str(cm.exception))

    def test_drillhole_service_validates_buffer_width(self):
        """DrillholeService should reject non-positive buffer width."""
        line_geom = QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(100, 0)])
        line_start = QgsPointXY(0, 0)
        da = MagicMock()

        with self.assertRaises(ValidationError) as cm:
            self.drillhole_service.project_collars(
                collar_data=[{"id": "test"}],
                line_data=line_geom,
                distance_area=da,
                buffer_width=-5.0,  # Invalid
                collar_id_field="id",
                use_geometry=True,
                collar_x_field="",
                collar_y_field="",
                collar_z_field="",
                collar_depth_field="",
            )
        self.assertIn("must be positive", str(cm.exception))

    def test_drillhole_orchestrator_validates_line_layer(self):
        """DrillholeTaskOrchestrator should reject line layer with no features."""
        empty_line_lyr = MagicMock()
        empty_line_lyr.isValid.return_value = True
        empty_line_lyr.getFeatures.return_value = iter([])

        mock_collar_lyr = MagicMock()
        fields = QgsFields()
        fields.append(QgsField("id"))
        fields.append(QgsField("z"))
        fields.append(QgsField("depth"))
        mock_collar_lyr.fields.return_value = fields

        with self.assertRaises(DataMissingError) as cm:
            self.orchestrator.prepare_task_input(
                line_layer=empty_line_lyr,
                buffer_width=10.0,
                collar_layer=mock_collar_lyr,
                collar_id_field="id",
                use_geometry=True,
                collar_x_field="",
                collar_y_field="",
                collar_z_field="z",
                collar_depth_field="depth",
                survey_layer=MagicMock(),
                survey_fields={},
                interval_layer=MagicMock(),
                interval_fields={},
            )
        self.assertIn("Line layer has no features", str(cm.exception))

    def test_drillhole_service_validates_collar_fields(self):
        """DrillholeService should validate existence of ID field."""
        mock_layer = MagicMock()
        mock_layer.isValid.return_value = True
        mock_layer.fields.return_value = QgsFields()  # Empty fields

        line_geom = QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(100, 0)])

        with self.assertRaises(ValidationError) as cm:
            self.orchestrator.prepare_task_input(
                line_layer=self.mock_line_lyr,
                buffer_width=10.0,
                collar_layer=mock_layer,
                collar_id_field="id_does_not_exist",
                use_geometry=True,
                collar_x_field="",
                collar_y_field="",
                collar_z_field="z",
                collar_depth_field="depth",
                survey_layer=MagicMock(),
                survey_fields={},
                interval_layer=MagicMock(),
                interval_fields={},
            )
        self.assertIn(
            "Collar ID field 'id_does_not_exist' not found", str(cm.exception)
        )
