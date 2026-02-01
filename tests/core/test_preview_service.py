"""Tests for the preview orchestration service."""

from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from qgis.core import QgsVectorLayer, QgsRasterLayer, QgsGeometry, QgsPointXY

from sec_interp.core.services.preview_service import PreviewService
from sec_interp.core.domain import PreviewParams, PreviewResult
from sec_interp.core.exceptions import (
    SecInterpError,
    GeometryError,
    ProcessingError,
    DataMissingError,
)


class TestPreviewService(BaseTestCase):
    """Tests for PreviewService."""

    def setUp(self):
        super().setUp()
        self.mock_controller = MagicMock()
        self.service = PreviewService(self.mock_controller)

        # Setup common mock behavior
        self.mock_line_lyr = QgsVectorLayer()
        self.mock_line_lyr.isValid = MagicMock(return_value=True)
        self.mock_line_lyr.name = MagicMock(return_value="Section Line")

        self.mock_raster_lyr = QgsRasterLayer()
        self.mock_raster_lyr.isValid = MagicMock(return_value=True)

        self.params = PreviewParams(
            raster_layer=self.mock_raster_lyr,
            line_layer=self.mock_line_lyr,
            band_num=1,
            canvas_width=800,
            auto_lod=True,
        )

    def test_calculate_max_points(self):
        """Test LOV point calculation."""
        # Base case
        pts = PreviewService.calculate_max_points(500, auto_lod=True)
        self.assertEqual(pts, 1000)  # 500 * 2

        # Zoomed in (ratio > 1.1)
        pts_zoomed = PreviewService.calculate_max_points(500, ratio=10.0, auto_lod=True)
        self.assertGreater(pts_zoomed, 1000)

        # Manual max
        pts_manual = PreviewService.calculate_max_points(
            500, manual_max=50, auto_lod=False
        )
        self.assertEqual(pts_manual, 50)

    def test_generate_all_topo_only(self):
        """Test generating only topography."""
        # Mock line feature
        line_geom = QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(100, 0)])
        line_feat = MagicMock()
        line_feat.geometry.return_value = line_geom
        self.mock_line_lyr.getFeatures = MagicMock(
            side_effect=lambda: iter([line_feat])
        )

        # Mock profile service
        self.mock_controller.profile_service.generate_topographic_profile.return_value = [
            (0.0, 10.0),
            (100.0, 15.0),
        ]

        result = self.service.generate_all(self.params, MagicMock())

        self.assertIsInstance(result, PreviewResult)
        self.assertEqual(len(result.topo), 2)
        self.mock_controller.profile_service.generate_topographic_profile.assert_called_once()

    def test_generate_all_with_structures(self):
        """Test generating topo and structures."""
        # Setup topo mocks
        line_geom = QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(100, 0)])
        line_feat = MagicMock()
        line_feat.geometry.return_value = line_geom
        self.mock_line_lyr.getFeatures = MagicMock(
            side_effect=lambda: iter([line_feat])
        )
        self.mock_controller.profile_service.generate_topographic_profile.return_value = (
            []
        )

        # Setup structure params
        self.params.struct_layer = QgsVectorLayer()
        self.params.dip_field = "dip"
        self.params.strike_field = "strike"

        # Mock structure service
        self.mock_controller.structure_service.project_structures.return_value = [
            {"id": 1}
        ]

        result = self.service.generate_all(self.params, MagicMock())

        self.assertIsNotNone(result.struct)
        self.assertEqual(len(result.struct), 1)
        self.mock_controller.structure_service.project_structures.assert_called_once()

    def test_generate_all_with_drillholes(self):
        """Test generating topo and drillholes."""
        # Setup topo mocks
        line_geom = QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(100, 0)])
        line_feat = MagicMock()
        line_feat.geometry.return_value = line_geom
        self.mock_line_lyr.getFeatures = MagicMock(
            side_effect=lambda: iter([line_feat])
        )
        self.mock_controller.profile_service.generate_topographic_profile.return_value = (
            []
        )

        # Setup drillhole params
        self.params.collar_layer = QgsVectorLayer()
        self.params.collar_id_field = "HOLEID"
        self.params.survey_layer = QgsVectorLayer()
        self.params.survey_id_field = "HOLEID"
        self.params.survey_depth_field = "DEPTH"
        self.params.survey_azim_field = "AZIMUTH"
        self.params.survey_incl_field = "DIP"
        self.params.interval_layer = QgsVectorLayer()
        self.params.interval_id_field = "HOLEID"
        self.params.interval_from_field = "FROM"
        self.params.interval_to_field = "TO"
        self.params.interval_lith_field = "LITH"

        # Mock drillhole service
        ds = self.mock_controller.drillhole_service
        ds.collar_processor.detach_features.return_value = (
            {"BH1"},
            [{"id": "BH1"}],
            {},
        )
        ds.project_collars.return_value = [("BH1", 0.0, 100.0, 0.0, 50.0)]
        ds._fetch_bulk_data.return_value = {"BH1": []}
        ds.process_intervals.return_value = (None, [{"id": "BH1", "trace": []}])

        result = self.service.generate_all(self.params, MagicMock())

        self.assertEqual(len(result.drillhole), 1)
        ds.collar_processor.detach_features.assert_called_once()
        ds.project_collars.assert_called_once()

    def test_generate_all_no_features(self):
        """Test error when no features in line layer."""
        self.mock_line_lyr.getFeatures = MagicMock(return_value=iter([]))

        with self.assertRaises(GeometryError):
            self.service.generate_all(self.params, MagicMock())

    def test_generate_drillholes_multipart(self):
        """Test drillhole generation with multipart line."""
        pts = [QgsPointXY(0, 0), QgsPointXY(100, 0)]
        line_geom = MagicMock()
        line_geom.isMultipart.return_value = True
        line_geom.asMultiPolyline.return_value = [pts]
        line_geom.vertices.return_value = pts
        line_geom.length.return_value = 100.0
        line_geom.isNull.return_value = False
        line_geom.type.return_value = 1  # QgsWkbTypes.LineGeometry

        line_feat = MagicMock()
        line_feat.geometry.return_value = line_geom
        self.mock_line_lyr.getFeatures = MagicMock(
            side_effect=lambda: iter([line_feat])
        )

        self.params.collar_layer = QgsVectorLayer()
        self.params.collar_id_field = "HOLEID"
        self.params.survey_layer = QgsVectorLayer()
        self.params.survey_id_field = "HOLEID"
        self.params.survey_depth_field = "DEPTH"
        self.params.survey_azim_field = "AZIMUTH"
        self.params.survey_incl_field = "DIP"
        self.params.interval_layer = QgsVectorLayer()
        self.params.interval_id_field = "HOLEID"
        self.params.interval_from_field = "FROM"
        self.params.interval_to_field = "TO"
        self.params.interval_lith_field = "LITH"

        ds = self.mock_controller.drillhole_service
        ds.collar_processor.detach_features.return_value = (
            {"BH1"},
            [{"id": "BH1"}],
            {},
        )
        ds.project_collars.return_value = [("BH1", 0.0, 100.0, 0.0, 50.0)]
        ds._fetch_bulk_data.return_value = {"BH1": []}
        ds.process_intervals.return_value = (None, [{"id": "BH1", "trace": []}])

        result = self.service.generate_all(self.params, MagicMock())
        self.assertIsNotNone(result.drillhole)

    def test_generate_drillholes_no_id_field(self):
        """Test skipping drillholes when ID field is missing (direct call)."""
        line_geom = QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(100, 0)])
        line_feat = MagicMock()
        line_feat.geometry.return_value = line_geom
        self.mock_line_lyr.getFeatures = MagicMock(
            side_effect=lambda: iter([line_feat])
        )
        self.service.transform_context = MagicMock()

        self.params.collar_id_field = None
        # Call internal method directly to bypass general validation in generate_all
        result = self.service._generate_drillholes(self.params)
        self.assertIsNone(result)

    def test_generate_drillholes_no_vertices(self):
        """Test error when section line has no vertices."""
        # Use real MockQgsGeometry (QgsGeometry in this env)
        line_geom = QgsGeometry()
        # Ensure it has NO points
        line_geom._polyline = []
        if hasattr(line_geom, "isNull"):
            # If it's a mock or has the method
            line_geom.isNull = MagicMock(return_value=False)

        line_feat = MagicMock()
        line_feat.geometry.return_value = line_geom
        self.mock_line_lyr.getFeatures = MagicMock(
            side_effect=lambda: iter([line_feat])
        )
        self.service.transform_context = MagicMock()

        # MUST set this or it returns None early
        self.params.collar_id_field = "HOLEID"

        from sec_interp.core.exceptions import GeometryError

        with self.assertRaises(GeometryError) as cm:
            self.service._generate_drillholes(self.params)
        self.assertIn("no vertices", str(cm.exception))

    def test_generate_drillholes_interval_failure(self):
        """Test interval processing failure handling."""
        line_geom = QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(100, 0)])
        line_feat = MagicMock()
        line_feat.geometry.return_value = line_geom
        self.mock_line_lyr.getFeatures = MagicMock(
            side_effect=lambda: iter([line_feat])
        )
        self.service.transform_context = MagicMock()

        self.params.collar_layer = QgsVectorLayer()
        self.params.collar_id_field = "HOLEID"
        self.params.survey_layer = QgsVectorLayer()
        self.params.survey_id_field = "HOLEID"
        self.params.survey_depth_field = "DEPTH"
        self.params.survey_azim_field = "AZIMUTH"
        self.params.survey_incl_field = "DIP"
        self.params.interval_layer = QgsVectorLayer()
        self.params.interval_id_field = "HOLEID"
        self.params.interval_from_field = "FROM"
        self.params.interval_to_field = "TO"
        self.params.interval_lith_field = "LITH"

        ds = self.mock_controller.drillhole_service
        ds.collar_processor.detach_features.return_value = (
            {"BH1"},
            [{"id": "BH1"}],
            {},
        )
        ds.project_collars.return_value = [("BH1", 0.0, 100.0, 0.0, 50.0)]
        ds._fetch_bulk_data.return_value = {"BH1": []}
        ds.process_intervals.side_effect = SecInterpError("Interval failure")

        from sec_interp.core.exceptions import ProcessingError

        with self.assertRaises(ProcessingError):
            self.service._generate_drillholes(self.params)

    def test_generate_drillholes_none_collars(self):
        """Test returning None when no collars are projected."""
        line_geom = QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(100, 0)])
        line_feat = MagicMock()
        line_feat.geometry.return_value = line_geom
        self.mock_line_lyr.getFeatures = MagicMock(
            side_effect=lambda: iter([line_feat])
        )
        self.service.transform_context = MagicMock()

        self.params.collar_id_field = "HOLEID"
        ds = self.mock_controller.drillhole_service
        ds.collar_processor.detach_features.return_value = (
            {"BH1"},
            [{"id": "BH1"}],
            {},
        )
        ds.project_collars.return_value = []

        result = self.service._generate_drillholes(self.params)
        self.assertIsNone(result)

    def test_generate_drillholes_no_features_direct(self):
        """Test error when no features in line layer (direct call)."""
        # Use MagicMock for the layer to ensure side_effect works as expected
        mock_lyr = MagicMock()
        mock_lyr.getFeatures = MagicMock(side_effect=lambda: iter([]))
        mock_lyr.name.return_value = "Mock Line"

        self.params.line_layer = mock_lyr
        self.params.collar_id_field = "hole_id"  # Ensure it doesn't return early

        with self.assertRaises(GeometryError):
            self.service._generate_drillholes(self.params)

    def test_generate_drillholes_processing_error_direct(self):
        """Test projection failure handling (direct call)."""
        line_geom = QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(100, 0)])
        line_feat = MagicMock()
        line_feat.geometry.return_value = line_geom
        self.mock_line_lyr.getFeatures = MagicMock(
            side_effect=lambda: iter([line_feat])
        )
        self.service.transform_context = MagicMock()

        self.params.collar_id_field = "HOLEID"
        ds = self.mock_controller.drillhole_service
        ds.collar_processor.detach_features.return_value = (
            {"BH1"},
            [{"id": "BH1"}],
            {},
        )
        ds.project_collars.side_effect = SecInterpError("Test failure")

        from sec_interp.core.exceptions import ProcessingError

        with self.assertRaises(ProcessingError):
            self.service._generate_drillholes(self.params)
