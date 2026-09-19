"""Tests for the preview orchestration service."""

from unittest.mock import MagicMock
from tests.base_test import BaseTestCase
from qgis.core import QgsVectorLayer, QgsRasterLayer, QgsGeometry, QgsPointXY, QgsField

from sec_interp.core.services.preview_service import PreviewService
from sec_interp.core.domain import PreviewParams, PreviewResult


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
        self.mock_line_lyr.setWkbType(1002)  # LineStringZ
        self.mock_line_lyr.featureCount = MagicMock(return_value=1)

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
        pts_manual = PreviewService.calculate_max_points(500, manual_max=50, auto_lod=False)
        self.assertEqual(pts_manual, 50)

    def test_generate_all_topo_only(self):
        """Test generating only topography."""
        # Mock line feature
        line_geom = QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(100, 0)])
        line_feat = MagicMock()
        line_feat.geometry.return_value = line_geom
        self.mock_line_lyr.getFeatures = MagicMock(side_effect=lambda: iter([line_feat]))

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
        self.mock_line_lyr.getFeatures = MagicMock(side_effect=lambda: iter([line_feat]))
        self.mock_controller.profile_service.generate_topographic_profile.return_value = []

        # Setup structure params
        self.params.struct_layer = QgsVectorLayer()
        self.params.struct_layer.isValid = MagicMock(return_value=True)
        self.params.struct_layer.setWkbType(1001)  # PointZ
        self.params.struct_layer.name = MagicMock(return_value="Structures")
        self.params.struct_layer.featureCount = MagicMock(return_value=10)
        self.params.struct_layer.fields().append(QgsField("dip", 6))
        self.params.struct_layer.fields().append(QgsField("strike", 6))
        self.params.dip_field = "dip"
        self.params.strike_field = "strike"

        # Mock structure service
        self.mock_controller.structure_service.project_structures.return_value = [{"id": 1}]

        # Mock structure extractor (Extract adapter)
        self.mock_controller.structure_extractor.extract_line.return_value = (
            [(0.0, 0.0), (100.0, 0.0)],
            (0.0, 0.0),
            90.0,
        )
        self.mock_controller.structure_extractor.detach_structures.return_value = []

        result = self.service.generate_all(self.params, MagicMock())

        self.assertIsNotNone(result.struct)
        self.assertEqual(len(result.struct), 1)
        self.mock_controller.structure_service.project_structures.assert_called_once()

    def test_generate_all_no_features(self):
        """Test error when no features in line layer."""
        self.mock_line_lyr.getFeatures = MagicMock(return_value=iter([]))
        self.mock_line_lyr.featureCount = MagicMock(return_value=0)

        from sec_interp.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            self.service.generate_all(self.params, MagicMock())
