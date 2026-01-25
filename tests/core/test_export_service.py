"""Tests for the export orchestration service."""

from unittest.mock import MagicMock, patch
from pathlib import Path
from tests.base_test import BaseTestCase
from qgis.core import (
    QgsVectorLayer,
    QgsRasterLayer,
    QgsRectangle,
    QgsCoordinateReferenceSystem,
    QgsGeometry,
)

from sec_interp.core.services.export_service import ExportService
from sec_interp.core.types import PreviewParams, GeologyData, StructureData


class TestExportService(BaseTestCase):
    """Tests for ExportService."""

    def setUp(self):
        super().setUp()
        self.service = ExportService()
        self.output_folder = Path("/tmp/export_test")

        # Setup common mock behavior
        self.mock_line_lyr = QgsVectorLayer()
        self.mock_line_lyr.isValid = MagicMock(return_value=True)
        self.mock_line_lyr.crs = MagicMock(
            return_value=QgsCoordinateReferenceSystem("EPSG:4326")
        )

        self.params = PreviewParams(
            raster_layer=QgsRasterLayer(), line_layer=self.mock_line_lyr, band_num=1
        )

    @patch("sec_interp.exporters.CSVExporter")
    @patch("sec_interp.exporters.ProfileLineShpExporter")
    @patch("sec_interp.exporters.AxesShpExporter")
    def test_export_data_minimal(self, mock_axes, mock_profile_shp, mock_csv):
        """Test minimal export (topography only)."""
        profile_data = [(0, 10), (100, 20)]

        result = self.service.export_data(
            self.output_folder,
            self.params,
            profile_data=profile_data,
            geol_data=None,
            struct_data=None,
        )

        self.assertIn("✓ Saving files...", result[0])
        mock_csv.return_value.export.assert_called()
        mock_profile_shp.return_value.export.assert_called()
        mock_axes.return_value.export.assert_called()

    @patch("sec_interp.exporters.CSVExporter")
    @patch("sec_interp.exporters.ProfileLineShpExporter")
    @patch("sec_interp.exporters.GeologyShpExporter")
    @patch("sec_interp.exporters.StructureShpExporter")
    @patch("sec_interp.exporters.DrillholeTraceShpExporter")
    @patch("sec_interp.exporters.DrillholeIntervalShpExporter")
    @patch("sec_interp.exporters.Interpretation2DExporter")
    @patch("sec_interp.exporters.Interpretation3DExporter")
    @patch("sec_interp.exporters.AxesShpExporter")
    def test_export_data_all_types(
        self,
        mock_axes,
        mock_interp3d,
        mock_interp2d,
        mock_dh_int,
        mock_dh_trace,
        mock_struct,
        mock_geol,
        mock_profile,
        mock_csv,
    ):
        """Test export with all data types."""
        from sec_interp.core.types import GeologySegment, StructureMeasurement

        profile_data = [(0, 10)]
        geol_data = [
            GeologySegment(
                unit_name="Unit A",
                geometry_wkt=None,
                attributes={},
                points=[(0, 10), (50, 10)],
            )
        ]
        struct_data = [
            StructureMeasurement(
                distance=10.0,
                elevation=100.0,
                apparent_dip=30.0,
                original_dip=45.0,
                original_strike=0.0,
                attributes={},
            )
        ]
        drillhole_data = [{"id": "BH1"}]
        interp_data = [{"id": 1}]

        result = self.service.export_data(
            self.output_folder,
            self.params,
            profile_data=profile_data,
            geol_data=geol_data,
            struct_data=struct_data,
            drillhole_data=drillhole_data,
            interp_data=interp_data,
        )

        # Verify all exporters were called
        mock_csv.return_value.export.assert_called()
        mock_geol.return_value.export.assert_called()
        mock_struct.return_value.export.assert_called()
        mock_dh_trace.return_value.export.assert_called()
        mock_dh_int.return_value.export.assert_called()
        mock_interp2d.return_value.export.assert_called()
        # Interpretation3DExporter depends on can_export_3d() settings

    @patch("sec_interp.exporters.CSVExporter")
    @patch("sec_interp.exporters.ProfileLineShpExporter")
    @patch("sec_interp.exporters.Interpretation2DExporter")
    @patch("sec_interp.exporters.Interpretation3DExporter")
    @patch("sec_interp.exporters.AxesShpExporter")
    def test_export_data_3d_restricted(
        self, mock_axes, mock_interp3d, mock_interp2d, mock_profile, mock_csv
    ):
        """Test 3D export restriction."""
        profile_data = [(0, 10)]
        interp_data = [{"id": 1}]

        # Case 1: Restricted
        with patch.object(
            self.service.access_control, "can_export_3d", return_value=False
        ):
            self.service.export_data(
                self.output_folder,
                self.params,
                profile_data=profile_data,
                geol_data=None,
                struct_data=None,
                interp_data=interp_data,
            )
            mock_interp3d.return_value.export.assert_not_called()
            mock_interp2d.return_value.export.assert_called()

        # Case 2: Allowed
        mock_interp2d.reset_mock()
        # Mock line feature for 3D export
        line_feat = MagicMock()
        self.mock_line_lyr.getFeatures.return_value = iter([line_feat])

        with patch.object(
            self.service.access_control, "can_export_3d", return_value=True
        ):
            self.service.export_data(
                self.output_folder,
                self.params,
                profile_data=profile_data,
                geol_data=None,
                struct_data=None,
                interp_data=interp_data,
            )
            mock_interp3d.return_value.export.assert_called()

    def test_export_data_missing_profile(self):
        """Test error when profile data is missing."""
        from sec_interp.core.exceptions import DataMissingError

        with self.assertRaises(DataMissingError):
            self.service.export_data(
                self.output_folder,
                self.params,
                profile_data=[],
                geol_data=None,
                struct_data=None,
            )

    @patch("sec_interp.exporters.CSVExporter")
    def test_export_data_no_line_layer(self, mock_csv):
        """Test error when line layer is missing (direct call)."""
        from sec_interp.core.exceptions import DataMissingError

        self.params.line_layer = None
        with self.assertRaises(DataMissingError):
            self.service.export_data(
                self.output_folder,
                self.params,
                profile_data=[(0, 10)],
                geol_data=None,
                struct_data=None,
            )

    @patch("sec_interp.exporters.GeologyShpExporter")
    def test_export_geology_error(self, mock_geol_shp):
        """Test error handling in geology export."""
        from sec_interp.core.types import GeologySegment
        from sec_interp.core.exceptions import ExportError

        mock_geol_shp.return_value.export.side_effect = Exception("error")
        geol_data = [GeologySegment("A", None, {}, [(0, 0)])]

        with self.assertRaises(ExportError):
            self.service._export_geology(
                self.output_folder, geol_data, MagicMock(), MagicMock(), []
            )

    @patch("sec_interp.exporters.StructureShpExporter")
    def test_export_structures_error(self, mock_struct_shp):
        """Test error handling in structure export."""
        from sec_interp.core.types import StructureMeasurement
        from sec_interp.core.exceptions import ExportError

        mock_struct_shp.return_value.export.side_effect = Exception("error")
        struct_data = [StructureMeasurement(0, 0, 0, 0, 0, {})]

        with self.assertRaises(ExportError):
            self.service._export_structures(
                self.output_folder,
                struct_data,
                self.params,
                MagicMock(),
                MagicMock(),
                [],
            )

    @patch("sec_interp.exporters.DrillholeTraceShpExporter")
    def test_export_drillholes_error(self, mock_dh):
        """Test error handling in drillhole export."""
        from sec_interp.core.exceptions import ExportError

        mock_dh.return_value.export.side_effect = Exception("error")

        with self.assertRaises(ExportError):
            self.service._export_drillholes(
                self.output_folder, [{"id": 1}], MagicMock(), []
            )

    @patch("sec_interp.exporters.AxesShpExporter")
    def test_export_axes_error(self, mock_axes):
        """Test error handling in axes export."""
        from sec_interp.core.exceptions import ExportError

        mock_axes.return_value.export.side_effect = Exception("error")

        with self.assertRaises(ExportError):
            self.service._export_axes(self.output_folder, [(0, 0)], MagicMock(), [])

    @patch("sec_interp.exporters.Interpretation2DExporter")
    @patch("sec_interp.exporters.Interpretation3DExporter")
    def test_export_interpretation_3d_invalid_line(self, mock_3d, mock_2d):
        """Test 3D export with invalid line layer."""
        interp_data = [{"id": 1}]
        self.mock_line_lyr.isValid.return_value = False

        with patch.object(
            self.service.access_control, "can_export_3d", return_value=True
        ):
            # Should skip 3D but NOT raise error if line is invalid
            self.service._export_interpretations(
                self.output_folder, interp_data, self.mock_line_lyr, MagicMock(), []
            )
            mock_3d.return_value.export.assert_not_called()

    @patch("sec_interp.exporters.Interpretation2DExporter")
    def test_export_interpretation_error(self, mock_2d):
        """Test error handling in interpretation export."""
        from sec_interp.core.exceptions import ExportError

        mock_2d.return_value.export.side_effect = Exception("error")

        with self.assertRaises(ExportError):
            self.service._export_interpretations(
                self.output_folder, [{"id": 1}], self.mock_line_lyr, MagicMock(), []
            )

    def test_get_map_settings(self):
        """Test QgsMapSettings configuration."""
        from qgis.core import QgsRectangle
        from qgis.PyQt.QtCore import QSize
        from qgis.PyQt.QtGui import QColor

        extent = QgsRectangle(0, 0, 100, 100)
        layers = [QgsVectorLayer()]
        size = QSize(800, 600)
        bg = QColor(255, 255, 255)

        settings = self.service.get_map_settings(layers, extent, size, bg)

        # In base_test, QgsMapSettings is a MagicMock instance
        self.assertIsNotNone(settings)
        # Verify settings were applied (through mocks)
        settings.setLayers.assert_called_with(layers)
        settings.setExtent.assert_called_with(extent)
        settings.setOutputSize.assert_called_with(size)
        settings.setBackgroundColor.assert_called_with(bg)

    @patch("sec_interp.exporters.ProfileLineShpExporter")
    def test_export_topography_error(self, mock_profile_shp):
        """Test error handling in topography export."""
        from sec_interp.core.exceptions import ExportError

        mock_profile_shp.return_value.export.side_effect = Exception("error")

        with self.assertRaises(ExportError):
            self.service._export_topography(
                self.output_folder, [(0, 0)], MagicMock(), MagicMock(), []
            )
