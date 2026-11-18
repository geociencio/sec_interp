"""Tests for the complete QGIS 3D section handler."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from qgis.core import QgsCoordinateReferenceSystem, QgsGeometry, QgsPointXY

from sec_interp.core.domain import GeologySegment, StructureMeasurement
from sec_interp.core.services.export.handlers.section_3d import export_section_3d
from tests.base_test import BaseTestCase


class TestSection3DHandler(BaseTestCase):
    """The handler writes a multi-layer GeoPackage with the expected layers."""

    def setUp(self) -> None:
        super().setUp()
        self.crs = QgsCoordinateReferenceSystem("EPSG:32614")
        self.line_layer = MagicMock()
        self.line_layer.isValid.return_value = True
        feature = MagicMock()
        feature.geometry.return_value = QgsGeometry.fromPolylineXY(
            [QgsPointXY(1000, 2000), QgsPointXY(1100, 2000)]
        )
        self.line_layer.getFeatures.return_value = iter([feature])
        self.settings = MagicMock()
        self.settings.naming_pattern = None

    @patch("sec_interp.exporters.section_3d.scu_io.create_vector_writer")
    def test_geopackage_bundle(self, writer_factory: MagicMock) -> None:
        writer = MagicMock()
        writer_factory.return_value = writer
        msg: list[str] = []
        segment = GeologySegment(
            unit_name="Unit A",
            geometry_wkt=None,
            attributes={},
            points=[(0, 10), (50, 20), (100, 10)],
        )
        measurement = StructureMeasurement(
            distance=25.0,
            elevation=12.0,
            apparent_dip=45.0,
            original_dip=60.0,
            original_strike=120.0,
            attributes={},
        )

        export_section_3d(
            Path(self.output_dir),
            [(0, 10), (50, 20), (100, 15)],
            [segment],
            [measurement],
            self.line_layer,
            self.crs,
            msg,
            controller=None,
            settings=self.settings,
            ext=".gpkg",
        )

        self.assertEqual(writer_factory.call_count, 3)
        layer_names = [call.kwargs["layer_name"] for call in writer_factory.call_args_list]
        self.assertEqual(
            layer_names,
            ["topography_3d", "geology_3d", "structures_3d"],
        )
        paths = {call.args[0] for call in writer_factory.call_args_list}
        self.assertEqual(len(paths), 1)
        self.assertTrue(next(iter(paths)).endswith(".gpkg"))
        self.assertEqual(writer.addFeature.call_count, 3)
        self.assertEqual(len(msg), 1)
        self.assertIn("(3D)", msg[0])

    @patch("sec_interp.exporters.section_3d.scu_io.create_vector_writer")
    def test_shapefile_separate_layers(self, writer_factory: MagicMock) -> None:
        writer = MagicMock()
        writer_factory.return_value = writer
        msg: list[str] = []
        segment = GeologySegment(
            unit_name="Unit A",
            geometry_wkt=None,
            attributes={},
            points=[(0, 10), (50, 20), (100, 10)],
        )

        export_section_3d(
            Path(self.output_dir),
            [(0, 10), (50, 20), (100, 15)],
            [segment],
            None,
            self.line_layer,
            self.crs,
            msg,
            controller=None,
            settings=self.settings,
            ext=".shp",
        )

        self.assertEqual(writer_factory.call_count, 2)
        paths = {call.args[0] for call in writer_factory.call_args_list}
        self.assertEqual(len(paths), 2)
        self.assertEqual(len(msg), 2)
