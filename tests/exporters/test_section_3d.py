"""Tests for the QGIS 3D section layer exporters."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from qgis.core import QgsCoordinateReferenceSystem, QgsWkbTypes

from sec_interp.core.domain import GeologySegment, SectionFrame, StructureMeasurement
from sec_interp.exporters.section_3d import (
    Geology3DExporter,
    Structure3DExporter,
    Topography3DExporter,
)
from tests.base_test import BaseTestCase


class TestSection3DExporters(BaseTestCase):
    """The section exporters preserve Z and the requested geometry type."""

    def setUp(self) -> None:
        super().setUp()
        self.frame = SectionFrame.from_endpoints(1000, 2000, 1100, 2000, "EPSG:32614")
        self.crs = QgsCoordinateReferenceSystem("EPSG:32614")
        self.output = Path(self.test_dir) / "layer.gpkg"

    @patch("sec_interp.exporters.section_3d.scu_io.create_vector_writer")
    def test_topography_line_z(self, writer_factory: MagicMock) -> None:
        writer = MagicMock()
        writer_factory.return_value = writer

        exporter = Topography3DExporter({})
        ok = exporter.export(
            self.output,
            {
                "profile_data": [(0, 10), (50, 20), (100, 15)],
                "frame": self.frame,
                "crs": self.crs,
                "section_id": "secc1",
            },
            layer_name="topography_3d",
        )

        self.assertTrue(ok)
        args = writer_factory.call_args.args
        self.assertEqual(args[3], QgsWkbTypes.Type.LineStringZ)
        feature = writer.addFeature.call_args.args[0]
        line = feature.geometry().constGet()
        self.assertEqual(line.pointN(0).z(), 10.0)
        self.assertEqual(line.pointN(1).x(), 1050.0)

    @patch("sec_interp.exporters.section_3d.scu_io.create_vector_writer")
    def test_geology_polygon_z(self, writer_factory: MagicMock) -> None:
        writer = MagicMock()
        writer_factory.return_value = writer
        segment = GeologySegment(
            unit_name="Unit A",
            geometry_wkt=None,
            attributes={"id": "u1", "color": "#00FF00"},
            points=[(0, 10), (50, 20), (100, 10)],
        )

        exporter = Geology3DExporter({})
        ok = exporter.export(
            self.output,
            {
                "geology_data": [segment],
                "frame": self.frame,
                "crs": self.crs,
                "section_id": "secc1",
            },
            layer_name="geology_3d",
        )

        self.assertTrue(ok)
        args = writer_factory.call_args.args
        self.assertEqual(args[3], QgsWkbTypes.Type.PolygonZ)
        feature = writer.addFeature.call_args.args[0]
        self.assertEqual(feature.attribute("unit"), "Unit A")
        self.assertEqual(feature.attribute("color"), "#00FF00")
        self.assertTrue(feature.geometry().is3D())

    @patch("sec_interp.exporters.section_3d.scu_io.create_vector_writer")
    def test_structure_point_z(self, writer_factory: MagicMock) -> None:
        writer = MagicMock()
        writer_factory.return_value = writer
        measurement = StructureMeasurement(
            distance=25.0,
            elevation=12.0,
            apparent_dip=45.0,
            original_dip=60.0,
            original_strike=120.0,
            attributes={"type": "fault"},
        )

        exporter = Structure3DExporter({})
        ok = exporter.export(
            self.output,
            {
                "structural_data": [measurement],
                "frame": self.frame,
                "crs": self.crs,
                "section_id": "secc1",
            },
            layer_name="structures_3d",
        )

        self.assertTrue(ok)
        args = writer_factory.call_args.args
        self.assertEqual(args[3], QgsWkbTypes.Type.PointZ)
        feature = writer.addFeature.call_args.args[0]
        self.assertEqual(feature.attribute("dip"), 60.0)
        self.assertEqual(feature.attribute("type"), "fault")

    def test_requires_frame(self) -> None:
        exporter = Topography3DExporter({})
        self.assertFalse(
            exporter.export(
                self.output,
                {"profile_data": [(0, 0), (10, 1)], "crs": self.crs},
            )
        )
