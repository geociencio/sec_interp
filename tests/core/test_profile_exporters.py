"""Tests for profile exporters."""

from pathlib import Path
from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from qgis.core import (
    QgsPointXY,
    QgsFields,
    QgsField,
    QgsFeature,
    QgsGeometry,
    QgsCoordinateReferenceSystem,
    QgsVectorFileWriter,
)
from qgis.PyQt.QtCore import QMetaType

from sec_interp.exporters.profile_exporters import (
    ProfileLineShpExporter,
    GeologyShpExporter,
    StructureShpExporter,
    AxesShpExporter,
)


class TestProfileExporters(BaseTestCase):
    """Tests for ProfileLineShpExporter, GeologyShpExporter, StructureShpExporter, and AxesShpExporter."""

    def setUp(self):
        super().setUp()
        self.output_path = Path("/tmp/test_export.shp")
        self.crs = QgsCoordinateReferenceSystem("EPSG:4326")
        self.settings = {"dpi": 300}

    @patch("sec_interp.exporters.profile_exporters.scu_io.create_vector_writer")
    def test_profile_line_exporter_success(self, mock_writer_factory):
        """Test successful export of profile line."""
        mock_writer = MagicMock()
        mock_writer.hasError.return_value = QgsVectorFileWriter.NoError
        mock_writer_factory.return_value = mock_writer
        exporter = ProfileLineShpExporter(self.settings)

        data = {"profile_data": [(0, 100), (100, 200)], "crs": self.crs}

        result = exporter.export(self.output_path, data)
        self.assertTrue(result)
        mock_writer.addFeature.assert_called_once()

    def test_profile_line_exporter_missing_data(self):
        """Test profile line exporter with missing data."""
        exporter = ProfileLineShpExporter(self.settings)
        self.assertFalse(exporter.export(self.output_path, {}))

    @patch("sec_interp.exporters.profile_exporters.scu_io.create_vector_writer")
    def test_geology_exporter_success(self, mock_writer_factory):
        """Test successful export of geology profile."""
        mock_writer = MagicMock()
        mock_writer.hasError.return_value = QgsVectorFileWriter.NoError
        mock_writer_factory.return_value = mock_writer
        exporter = GeologyShpExporter(self.settings)

        segment = MagicMock()
        segment.points = [(0, 100), (100, 200)]
        segment.attributes = {"unit": "lith1"}

        data = {"geology_data": [segment], "crs": self.crs}

        result = exporter.export(self.output_path, data)
        self.assertTrue(result)
        mock_writer.addFeature.assert_called_once()

    def test_geology_exporter_short_segment(self):
        """Test geology exporter with segment having less than 2 points."""
        exporter = GeologyShpExporter(self.settings)
        segment = MagicMock()
        segment.points = [(0, 100)]
        segment.attributes = {}

        fields = QgsFields()
        feat = exporter._create_geology_feature(segment, fields)
        self.assertIsNone(feat)

    @patch("sec_interp.exporters.profile_exporters.scu_io.create_vector_writer")
    def test_structure_exporter_success(self, mock_writer_factory):
        """Test successful export of structural profile."""
        mock_writer = MagicMock()
        mock_writer.hasError.return_value = QgsVectorFileWriter.NoError
        mock_writer_factory.return_value = mock_writer
        exporter = StructureShpExporter(self.settings)

        m = MagicMock()
        m.distance = 50.0
        m.elevation = 150.0
        m.apparent_dip = 45.0
        m.attributes = {"type": "foliation"}

        data = {
            "structural_data": [m],
            "crs": self.crs,
            "dip_scale_factor": 4,
            "raster_res": 1.0,
        }

        result = exporter.export(self.output_path, data)
        self.assertTrue(result)
        mock_writer.addFeature.assert_called_once()

        # Test negative dip for dx branch
        m.apparent_dip = -45.0
        feat = exporter._create_structure_feature(m, QgsFields(), 4.0)
        self.assertIsNotNone(feat)

    @patch("sec_interp.exporters.profile_exporters.scu_io.create_vector_writer")
    def test_axes_exporter_success(self, mock_writer_factory):
        """Test successful export of profile axes."""
        mock_writer = MagicMock()
        mock_writer.hasError.return_value = QgsVectorFileWriter.NoError
        mock_writer_factory.return_value = mock_writer
        exporter = AxesShpExporter(self.settings)

        data = {"profile_data": [(0, 100), (100, 200)], "crs": self.crs}

        result = exporter.export(self.output_path, data)
        self.assertTrue(result)
        # Should add 3 features: Left, Right, Bottom axes
        self.assertEqual(mock_writer.addFeature.call_count, 3)

    @patch("sec_interp.exporters.profile_exporters.scu_io.create_vector_writer")
    def test_axes_exporter_single_point(self, mock_writer_factory):
        """Test axes exporter with single point or constant data."""
        mock_writer = MagicMock()
        mock_writer.hasError.return_value = QgsVectorFileWriter.NoError
        mock_writer_factory.return_value = mock_writer
        exporter = AxesShpExporter(self.settings)
        data = {"profile_data": [(100, 100), (100, 100)], "crs": self.crs}
        result = exporter.export(self.output_path, data)
        self.assertTrue(result)

    def test_exporter_errors(self):
        """Test error handling in exporters."""
        with patch(
            "sec_interp.exporters.profile_exporters.scu_io.create_vector_writer",
            side_effect=Exception("mock fail"),
        ):
            data = {"profile_data": [(0, 0)], "crs": self.crs}
            self.assertFalse(
                ProfileLineShpExporter(self.settings).export(self.output_path, data)
            )

            data = {"geology_data": [MagicMock()], "crs": self.crs}
            self.assertFalse(
                GeologyShpExporter(self.settings).export(self.output_path, data)
            )

            data = {"structural_data": [MagicMock()], "crs": self.crs}
            self.assertFalse(
                StructureShpExporter(self.settings).export(self.output_path, data)
            )

            data = {"profile_data": [(0, 0)], "crs": self.crs}
            self.assertFalse(
                AxesShpExporter(self.settings).export(self.output_path, data)
            )

    def test_geology_fields_empty(self):
        """Test _create_geology_fields with empty data."""
        exporter = GeologyShpExporter(self.settings)
        fields = exporter._create_geology_fields([])
        self.assertEqual(len(fields.names()), 0)

    def test_supported_extensions(self):
        """Test supported extensions for all exporters."""
        exporters = [
            ProfileLineShpExporter(self.settings),
            GeologyShpExporter(self.settings),
            StructureShpExporter(self.settings),
            AxesShpExporter(self.settings),
        ]
        for exporter in exporters:
            self.assertEqual(
                exporter.get_supported_extensions(), [".shp", ".gpkg", ".dxf"]
            )

    @patch("sec_interp.exporters.profile_exporters.scu_io.create_vector_writer")
    def test_profile_line_exporter_null_geom(self, mock_writer_func):
        """Test profile line exporter with null geometry."""
        exporter = ProfileLineShpExporter(self.settings)
        # Patch QgsGeometry via the module where it is imported/used
        with patch(
            "sec_interp.exporters.profile_exporters.QgsGeometry"
        ) as mock_geom_cls:
            mock_geom = MagicMock()
            mock_geom.isNull.return_value = True
            mock_geom_cls.fromPolylineXY.return_value = mock_geom

            data = {"profile_data": [(0, 0)], "crs": self.crs}
            self.assertFalse(exporter.export(self.output_path, data))

    def test_geology_exporter_missing_data(self):
        """Test geology exporter with missing data."""
        exporter = GeologyShpExporter(self.settings)
        self.assertFalse(exporter.export(self.output_path, {}))

    def test_structure_exporter_missing_data(self):
        """Test structure exporter with missing data."""
        exporter = StructureShpExporter(self.settings)
        self.assertFalse(exporter.export(self.output_path, {}))

    def test_axes_exporter_missing_data(self):
        """Test axes exporter with missing data."""
        exporter = AxesShpExporter(self.settings)
        self.assertFalse(exporter.export(self.output_path, {}))
