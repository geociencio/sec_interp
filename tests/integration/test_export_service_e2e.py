"""Integration tests for ExportService end-to-end workflows.

These tests exercise the full ExportService orchestration layer,
calling exporters through the service and verifying files on disk.
"""

from __future__ import annotations

import csv
import os
import shutil
import tempfile
from pathlib import Path

# Allow mocking by default unless overridden
import os

os.environ.setdefault("FORCE_MOCKS", "1")

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
    QgsVectorFileWriter,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QMetaType, QSize

from sec_interp.core.domain import GeologySegment, InterpretationPolygon
from sec_interp.core.domain.entities import StructureMeasurement
from sec_interp.core.services.export_service import ExportService
from tests.integration.base_integration import BaseIntegrationTest


def _make_line_layer(
    crs: QgsCoordinateReferenceSystem,
) -> QgsVectorLayer:
    """Create a minimal in-memory line layer with one east-pointing feature.

    Args:
        crs: Coordinate reference system for the layer.

    Returns:
        A valid QgsVectorLayer containing one horizontal line feature.

    """
    layer = QgsVectorLayer("LineString", "section_line", "memory")
    layer.setCrs(crs)
    provider = layer.dataProvider()

    feat = QgsFeature()
    feat.setGeometry(
        QgsGeometry.fromPolylineXY([QgsPointXY(1000, 2000), QgsPointXY(1100, 2000)])
    )
    provider.addFeature(feat)
    layer.updateExtents()
    return layer


class TestExportServiceTopographyE2E(BaseIntegrationTest):
    """E2E tests for ExportService topography export pipeline."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up QGIS and shared test fixtures."""
        super().setUpClass()
        cls.crs = QgsCoordinateReferenceSystem("EPSG:32719")
        cls.test_dir = Path(tempfile.mkdtemp(prefix="secinterp_export_test_"))

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up temporary directory."""
        super().tearDownClass()
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir)

    def setUp(self) -> None:
        """Prepare per-test isolated output folder and line layer."""
        super().setUp()
        self.output_dir = self.test_dir / self._testMethodName
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Register a real line layer in the QGIS project
        self.line_layer = _make_line_layer(self.crs)
        QgsProject.instance().addMapLayer(self.line_layer)

        # Minimal profile points: [(dist, elev), ...]
        self.profile_data = [(0.0, 500.0), (50.0, 510.0), (100.0, 505.0)]

        # Build a minimal PreviewParams-like object with the real layer
        # ExportService._orchestrate_exports resolves line_layer from the project
        # when it is a string (layer ID), or uses the object directly.
        self.service = ExportService(controller=None)

    def tearDown(self) -> None:
        """Remove registered layer from the project."""
        QgsProject.instance().removeMapLayer(self.line_layer.id())
        super().tearDown()

    def _make_params(self) -> object:
        """Build a minimal params object with line_layer set to the real layer.

        Returns:
            A simple namespace object mimicking a PreviewParams instance.

        """
        import types

        params = types.SimpleNamespace()
        # Pass the layer object directly so ExportService can skip project lookup
        params.line_layer = self.line_layer
        params.raster_layer = None
        return params

    # ------------------------------------------------------------------
    # Topography export (CSV + profile_line.shp + profile_axes.shp)
    # ------------------------------------------------------------------

    def test_export_topography_creates_csv(self) -> None:
        """ExportService should produce topo_profile.csv with correct content."""
        params = self._make_params()
        msgs = self.service.export_data(
            output_folder=self.output_dir,
            params=params,
            profile_data=self.profile_data,
            geol_data=None,
            struct_data=None,
            export_options={
                "exp_topo": True,
                "exp_geol": False,
                "exp_struct": False,
                "exp_drill": False,
                "exp_interp": False,
            },
        )

        csv_path = self.output_dir / "profile" / "topo_profile.csv"
        self.assertTrue(csv_path.exists(), f"Expected {csv_path} to exist")

        with csv_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertEqual(len(rows), 3)
        self.assertAlmostEqual(float(rows[0]["dist"]), 0.0)
        self.assertAlmostEqual(float(rows[0]["elev"]), 500.0)
        self.assertAlmostEqual(float(rows[2]["dist"]), 100.0)

        # Return messages should signal success with relative paths
        self.assertTrue(
            any("profile/topo_profile.csv" in m for m in msgs),
            f"Expected relative path in: {msgs}",
        )

    def test_export_topography_creates_shp(self) -> None:
        """ExportService should produce a valid profile_line.shp."""
        params = self._make_params()
        self.service.export_data(
            output_folder=self.output_dir,
            params=params,
            profile_data=self.profile_data,
            geol_data=None,
            struct_data=None,
            export_options={
                "exp_topo": True,
                "exp_geol": False,
                "exp_struct": False,
                "exp_drill": False,
                "exp_interp": False,
            },
        )

        shp_path = self.output_dir / "profile" / "profile_line.shp"
        self.assertTrue(shp_path.exists(), f"Expected {shp_path} to exist")

        layer = QgsVectorLayer(str(shp_path), "profile", "ogr")
        self.assertTrue(layer.isValid(), "profile_line.shp is not a valid QGIS layer")
        features = list(layer.getFeatures())
        self.assertEqual(len(features), 1, "Expected exactly one profile line feature")

    def test_export_nothing_when_all_options_disabled(self) -> None:
        """ExportService should return a warning when all options are disabled."""
        params = self._make_params()
        msgs = self.service.export_data(
            output_folder=self.output_dir,
            params=params,
            profile_data=self.profile_data,
            geol_data=None,
            struct_data=None,
            export_options={
                "exp_topo": False,
                "exp_geol": False,
                "exp_struct": False,
                "exp_drill": False,
                "exp_interp": False,
            },
        )
        self.assertTrue(
            any("No export options" in m for m in msgs),
            f"Expected warning message, got: {msgs}",
        )
        # No output files should have been created
        exported_files = list(self.output_dir.glob("*"))
        self.assertEqual(len(exported_files), 0)

    def test_export_raises_when_no_profile_data(self) -> None:
        """ExportService.export_data should raise DataMissingError if profile_data is empty."""
        from sec_interp.core.exceptions import DataMissingError

        params = self._make_params()
        with self.assertRaises(DataMissingError):
            self.service.export_data(
                output_folder=self.output_dir,
                params=params,
                profile_data=[],
                geol_data=None,
                struct_data=None,
            )


class TestExportServiceGeologyE2E(BaseIntegrationTest):
    """E2E tests for ExportService geology export pipeline."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up QGIS and shared test fixtures."""
        super().setUpClass()
        cls.crs = QgsCoordinateReferenceSystem("EPSG:32719")
        cls.test_dir = Path(tempfile.mkdtemp(prefix="secinterp_geol_test_"))

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up temporary directory."""
        super().tearDownClass()
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir)

    def setUp(self) -> None:
        """Set up per-test state."""
        super().setUp()
        self.output_dir = self.test_dir / self._testMethodName
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.line_layer = _make_line_layer(self.crs)
        QgsProject.instance().addMapLayer(self.line_layer)

        self.profile_data = [(0.0, 500.0), (50.0, 510.0), (100.0, 505.0)]
        self.geol_data = [
            GeologySegment(
                unit_name="Andesite",
                geometry_wkt=None,
                attributes={"unit": "Andesite", "code": "AND"},
                points=[(0.0, 500.0), (50.0, 510.0)],
            ),
            GeologySegment(
                unit_name="Granite",
                geometry_wkt=None,
                attributes={"unit": "Granite", "code": "GRA"},
                points=[(50.0, 510.0), (100.0, 505.0)],
            ),
        ]
        self.service = ExportService(controller=None)

    def tearDown(self) -> None:
        """Remove registered layer."""
        QgsProject.instance().removeMapLayer(self.line_layer.id())
        super().tearDown()

    def _make_params(self) -> object:
        """Build minimal params object.

        Returns:
            Namespace with line_layer and raster_layer attributes.

        """
        import types

        params = types.SimpleNamespace()
        params.line_layer = self.line_layer
        params.raster_layer = None
        return params

    def test_export_geology_creates_csv_and_shp(self) -> None:
        """ExportService should produce geol_profile.csv and geol_profile.shp."""
        params = self._make_params()
        msgs = self.service.export_data(
            output_folder=self.output_dir,
            params=params,
            profile_data=self.profile_data,
            geol_data=self.geol_data,
            struct_data=None,
            export_options={
                "exp_topo": False,
                "exp_geol": True,
                "exp_struct": False,
                "exp_drill": False,
                "exp_interp": False,
            },
        )

        # CSV check
        csv_path = self.output_dir / "profile" / "geol_profile.csv"
        self.assertTrue(csv_path.exists(), f"Expected {csv_path}")
        with csv_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        self.assertGreater(len(rows), 0)
        self.assertIn("geology", rows[0])
        self.assertEqual(rows[0]["geology"], "Andesite")

        # SHP check
        shp_path = self.output_dir / "profile" / "geol_profile.shp"
        self.assertTrue(shp_path.exists(), f"Expected {shp_path}")
        layer = QgsVectorLayer(str(shp_path), "geol", "ogr")
        self.assertTrue(layer.isValid())
        features = list(layer.getFeatures())
        self.assertEqual(len(features), 2, "Expected one feature per geology segment")

        # Message check
        self.assertTrue(any("geol_profile.csv" in m for m in msgs))
        self.assertTrue(any("geol_profile.shp" in m for m in msgs))

    def test_export_geology_skips_when_no_data(self) -> None:
        """ExportService should skip geology export gracefully when geol_data is None."""
        params = self._make_params()
        # Should not raise, and no geology files should be created
        self.service.export_data(
            output_folder=self.output_dir,
            params=params,
            profile_data=self.profile_data,
            geol_data=None,
            struct_data=None,
            export_options={
                "exp_topo": False,
                "exp_geol": True,
                "exp_struct": False,
                "exp_drill": False,
                "exp_interp": False,
            },
        )
        self.assertFalse((self.output_dir / "profile" / "geol_profile.csv").exists())
        self.assertFalse((self.output_dir / "profile" / "geol_profile.shp").exists())


class TestExportServiceInterpretationE2E(BaseIntegrationTest):
    """E2E tests for ExportService interpretation export pipeline (2D path)."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up QGIS and temporary directory."""
        super().setUpClass()
        cls.crs = QgsCoordinateReferenceSystem("EPSG:32719")
        cls.test_dir = Path(tempfile.mkdtemp(prefix="secinterp_interp_test_"))

    @classmethod
    def tearDownClass(cls) -> None:
        """Remove temporary directory."""
        super().tearDownClass()
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir)

    def setUp(self) -> None:
        """Set up per-test state."""
        super().setUp()
        self.output_dir = self.test_dir / self._testMethodName
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.line_layer = _make_line_layer(self.crs)
        QgsProject.instance().addMapLayer(self.line_layer)

        self.profile_data = [(0.0, 500.0), (100.0, 500.0)]
        self.interp_data = [
            InterpretationPolygon(
                id="i1",
                name="Alteration Zone",
                type="Alteration",
                vertices_2d=[
                    (10.0, 490.0),
                    (40.0, 490.0),
                    (40.0, 510.0),
                    (10.0, 510.0),
                ],
            )
        ]
        self.service = ExportService(controller=None)

    def tearDown(self) -> None:
        """Remove registered layer."""
        QgsProject.instance().removeMapLayer(self.line_layer.id())
        super().tearDown()

    def _make_params(self) -> object:
        """Build minimal params object.

        Returns:
            Namespace with line_layer and raster_layer attributes.

        """
        import types

        params = types.SimpleNamespace()
        params.line_layer = self.line_layer
        params.raster_layer = None
        return params

    def test_export_interpretations_creates_2d_shp(self) -> None:
        """ExportService should produce interpretations.shp for 2D interpretation data.

        Note: Interpretation2DExporter uses writeAsVectorFormatV3 with an in-memory
        layer. The resulting .shp file may be written with a slightly different name if
        QGIS appends a suffix. We therefore look for any .shp in the output dir as
        a fallback before asserting the canonical name.
        """
        params = self._make_params()
        msgs = self.service.export_data(
            output_folder=self.output_dir,
            params=params,
            profile_data=self.profile_data,
            geol_data=None,
            struct_data=None,
            interp_data=self.interp_data,
            export_options={
                "exp_topo": False,
                "exp_geol": False,
                "exp_struct": False,
                "exp_drill": False,
                "exp_interp": True,
            },
        )

        # The exporter logs the path it wrote to; accept any .shp in the output dir
        shp_files = list(self.output_dir.rglob("*.shp"))
        self.assertGreater(
            len(shp_files),
            0,
            f"No .shp files found in {self.output_dir} or subdirectories. Contents: {list(self.output_dir.iterdir())}",
        )

        # Use the first (and expected only) shapefile found
        shp_path = shp_files[0]
        layer = QgsVectorLayer(str(shp_path), "interp", "ogr")
        self.assertTrue(layer.isValid(), f"{shp_path.name} is not a valid QGIS layer")

        features = list(layer.getFeatures())
        self.assertEqual(len(features), 1)
        self.assertEqual(features[0]["name"], "Alteration Zone")

        # Service message should confirm interpretations were saved
        self.assertTrue(any("interpretations.shp" in m for m in msgs))

    def test_export_interpretations_skips_when_empty(self) -> None:
        """ExportService should skip interpretation export gracefully when list is empty."""
        params = self._make_params()
        # Should not raise
        self.service.export_data(
            output_folder=self.output_dir,
            params=params,
            profile_data=self.profile_data,
            geol_data=None,
            struct_data=None,
            interp_data=[],
            export_options={
                "exp_topo": False,
                "exp_geol": False,
                "exp_struct": False,
                "exp_drill": False,
                "exp_interp": True,
            },
        )
        self.assertFalse((self.output_dir / "profile" / "interpretations.shp").exists())


class TestExportServiceStructuralE2E(BaseIntegrationTest):
    """E2E tests for ExportService structural measurements export."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.crs = QgsCoordinateReferenceSystem("EPSG:32719")
        cls.test_dir = Path(tempfile.mkdtemp(prefix="secinterp_struct_test_"))

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir)

    def setUp(self) -> None:
        super().setUp()
        self.output_dir = self.test_dir / self._testMethodName
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.line_layer = _make_line_layer(self.crs)
        QgsProject.instance().addMapLayer(self.line_layer)
        self.service = ExportService(controller=None)

    def _make_params(self) -> object:
        import types

        params = types.SimpleNamespace()
        params.line_layer = self.line_layer
        params.raster_layer = None
        return params

    def test_export_structures_with_string_fields(self) -> None:
        """Verify export succeeds when structural fields are Strings (v3.4.1 fix)."""
        struct_data = [
            StructureMeasurement(
                distance=50.0,
                elevation=500.0,
                apparent_dip=15.0,
                original_dip=19.0,
                original_strike=344.0,
                attributes={"label": "S1", "strike_txt": "N 16ø W, 19ø SW"},
            )
        ]

        params = self._make_params()
        msgs = self.service.export_data(
            output_folder=self.output_dir,
            params=params,
            profile_data=[(0.0, 500.0), (100.0, 500.0)],
            geol_data=None,
            struct_data=struct_data,
            export_options={
                "exp_topo": False,
                "exp_geol": False,
                "exp_struct": True,
                "exp_drill": False,
                "exp_interp": False,
            },
        )

        # Check SHP file in subfolder
        shp_path = self.output_dir / "profile" / "structural_measurements.shp"
        self.assertTrue(shp_path.exists())

        # Verify relative path in result message
        self.assertTrue(
            any("profile/structural_measurements.shp" in m for m in msgs),
            f"Expected relative path 'profile/...' but got: {msgs}",
        )
