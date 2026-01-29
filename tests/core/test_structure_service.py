"""Tests for Structure Service."""

from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from qgis.core import (
    QgsPointXY,
    QgsGeometry,
    QgsFeature,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsCoordinateReferenceSystem,
)

from sec_interp.core.services.structure_service import StructureService
from sec_interp.core.exceptions import DataMissingError, ProcessingError


class TestStructureService(BaseTestCase):
    """Tests for StructureService."""

    def setUp(self):
        super().setUp()
        self.service = StructureService()

        # Setup mock layers
        self.mock_line_lyr = MagicMock()
        self.mock_raster_lyr = MagicMock()
        self.mock_struct_lyr = MagicMock()

        # Setup line geometry
        self.line_geom = QgsGeometry.fromPolylineXY(
            [QgsPointXY(0, 0), QgsPointXY(100, 0)]
        )
        self.line_feat = QgsFeature()
        self.line_feat.setGeometry(self.line_geom)

        self.mock_line_lyr.getFeatures.return_value = iter([self.line_feat])
        self.mock_line_lyr.crs.return_value = QgsCoordinateReferenceSystem("EPSG:32633")
        self.mock_line_lyr.name.return_value = "Line Layer"

        self.mock_struct_lyr.crs.return_value = QgsCoordinateReferenceSystem(
            "EPSG:32633"
        )
        self.mock_struct_lyr.name.return_value = "Structure Layer"

    def test_project_structures_success(self):
        """Test full structure projection."""
        # Setup mock features
        feat = QgsFeature()
        feat["dip"] = 45.0
        feat["strike"] = 90.0
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(50, 5)))

        # Define fields mock
        fields = MagicMock()
        fields.names.return_value = ["dip", "strike"]
        feat.fields = MagicMock(return_value=fields)
        feat.attributes = MagicMock(return_value=[45.0, 90.0])
        feat.geometry = MagicMock(return_value=QgsGeometry.fromPointXY(QgsPointXY(50, 5)))

        # Patch dependencies
        with patch(
            "sec_interp.core.services.structure_service.scu.filter_features_by_buffer"
        ) as mock_filter, patch(
            "sec_interp.core.services.structure_service.scu.create_distance_area"
        ) as mock_da_cls, patch(
            "sec_interp.core.services.structure_service.scu.sample_point_elevation"
        ) as mock_sample:
            mock_filter.return_value = [feat]

            da = MagicMock()
            da.measureLine.return_value = 50.0
            mock_da_cls.return_value = da
            mock_sample.return_value = 150.0

            # Mock raster sampling
            provider = MagicMock()
            ident_res = MagicMock()
            ident_res.results.return_value = {1: 150.0}
            provider.identify.return_value = ident_res
            self.mock_raster_lyr.dataProvider.return_value = provider

            results = self.service.project_structures(
                line_geom=self.line_geom,
                line_start=QgsPointXY(0, 0),
                da=da,
                raster_lyr=self.mock_raster_lyr,
                struct_data=[
                    {
                        "wkt": feat.geometry().asWkt(),
                        "attributes": {"dip": 45.0, "strike": 90.0},
                    }
                ],
                buffer_m=10,
                line_az=0.0,
                dip_field="dip",
                strike_field="strike",
            )

            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].distance, 50.0)
            self.assertEqual(results[0].elevation, 150.0)
            self.assertEqual(results[0].original_dip, 45.0)

        attributes = {"dip": "45", "strike": "090"}
        data = self.service._parse_structural_data(attributes, "strike", "dip", 0.0)
        self.assertIsNotNone(data)
        strike, dip, app_dip = data
        self.assertEqual(strike, 90.0)
        self.assertEqual(dip, 45.0)

    def test_create_buffer_zone_error(self):
        """Test error handling in buffer creation."""
        with patch(
            "sec_interp.core.services.structure_service.scu.create_buffer_geometry"
        ) as mock_buf:
            mock_buf.side_effect = ValueError("Test Error")
            with self.assertRaises(ProcessingError):
                self.service._create_buffer_zone(
                    self.line_geom, QgsCoordinateReferenceSystem(), 10.0
                )

        # Provider mock setup is done in test_project_structures_success,
        # but let's re-do it or use scu.sample_point_elevation mock
        with patch("sec_interp.core.services.structure_service.scu.sample_point_elevation") as mock_sample:
            mock_sample.return_value = 250.0
            val = self.service._process_single_structure(
                {"wkt": "POINT(0 0)", "attributes": {"dip": 45, "strike": 0}},
                self.line_geom,
                QgsPointXY(0, 0),
                MagicMock(),
                self.mock_raster_lyr,
                1,
                0.0,
                "dip",
                "strike"
            )
            self.assertEqual(val.elevation, 250.0)
