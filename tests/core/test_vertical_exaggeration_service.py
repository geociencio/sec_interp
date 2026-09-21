"""Tests for the adaptive VerticalExaggerationService."""

from __future__ import annotations

import ast
from pathlib import Path

from sec_interp.core.domain import GeologySegment, StructureMeasurement
from sec_interp.core.domain.dtos import PreviewResult
from sec_interp.core.domain.entities import DrillholeProjection
from sec_interp.core.services.vertical_exaggeration_service import (
    VerticalExaggerationService,
)
from tests.base_test import BaseTestCase


def _make_struct(distance: float, elevation: float) -> StructureMeasurement:
    """Build a minimal projected structural measurement."""
    return StructureMeasurement(
        distance=distance,
        elevation=elevation,
        apparent_dip=45.0,
        original_dip=45.0,
        original_strike=90.0,
        attributes={},
    )


class TestVerticalExaggerationService(BaseTestCase):
    """Tests for VerticalExaggerationService adaptive algorithm."""

    def setUp(self):
        """Initialize the service under test."""
        super().setUp()
        self.service = VerticalExaggerationService()

    def test_calculate_flat_profile(self):
        """Flat profile (5000m / 20m relief) requires strong exaggeration."""
        topo = [(float(d), 100.0) for d in range(0, 5001, 500)]
        topo[-1] = (5000.0, 120.0)  # elev_range = 20 -> ratio 0.004 -> base 10.0

        ve = self.service.calculate(topo, None)

        self.assertGreater(ve, 5.0)
        self.assertEqual(ve, 10.0)

    def test_calculate_steep_profile(self):
        """Steep profile (ratio > 0.5) is already expressive, VE stays ~1.0."""
        # 200m distance, 150m relief -> ratio 0.75 -> base 1.0
        topo = [(0.0, 100.0), (100.0, 200.0), (200.0, 250.0)]

        ve = self.service.calculate(topo, None)

        self.assertAlmostEqual(ve, 1.0)

    def test_dense_structures_reduce_ve(self):
        """Structural density > 0.1 (1 per 10m) damps VE by 0.7."""
        # 1000m distance, 50m relief -> ratio 0.05 -> base 5.0
        topo = [(0.0, 100.0), (500.0, 120.0), (1000.0, 150.0)]
        # 101 measurements over 1000m -> density 0.101 -> mult 0.7
        struct = [_make_struct(float(i * 10), 120.0) for i in range(101)]

        ve = self.service.calculate(topo, struct)

        self.assertEqual(ve, 3.5)  # 5.0 * 0.7

    def test_sparse_structures_increase_ve(self):
        """Structural density <= 0.01 boosts VE by 1.3."""
        # 1000m distance, 50m relief -> ratio 0.05 -> base 5.0
        topo = [(0.0, 100.0), (500.0, 120.0), (1000.0, 150.0)]
        # 5 measurements over 1000m -> density 0.005 -> mult 1.3
        struct = [_make_struct(float(i * 200), 120.0) for i in range(5)]

        ve = self.service.calculate(topo, struct)

        self.assertEqual(ve, 6.5)  # 5.0 * 1.3

    def test_empty_struct_data(self):
        """None or empty structural data applies a neutral multiplier."""
        topo = [(0.0, 100.0), (500.0, 120.0), (1000.0, 150.0)]

        ve_none = self.service.calculate(topo, None)
        ve_empty = self.service.calculate(topo, [])

        self.assertEqual(ve_none, 5.0)
        self.assertEqual(ve_empty, ve_none)

    def test_empty_topo_data(self):
        """Empty or missing topography returns the default VE."""
        self.assertEqual(self.service.calculate([], None), 1.0)
        self.assertEqual(self.service.calculate(None, None), 1.0)
        self.assertEqual(self.service.calculate(None, [_make_struct(0.0, 100.0)]), 1.0)

    def test_clamp_bounds(self):
        """Results always stay within [MIN, MAX] across the input space."""
        service = self.service
        for dist in (10.0, 100.0, 1000.0, 10000.0):
            for relief in (0.0, 1.0, 10.0, 100.0, 1000.0, 5000.0):
                topo = [(0.0, 0.0), (dist, relief)]
                for count in (0, 1, 10, 500):
                    struct = [_make_struct(0.0, 0.0)] * count or None
                    ve = service.calculate(topo, struct)
                    self.assertGreaterEqual(ve, service.MIN_VERT_EXAG)
                    self.assertLessEqual(ve, service.MAX_VERT_EXAG)

        # Defensive clamp contract on extreme raw values
        self.assertEqual(service._clamp(0.0), service.MIN_VERT_EXAG)
        self.assertEqual(service._clamp(1000.0), service.MAX_VERT_EXAG)

    def test_calculate_from_result(self):
        """PreviewResult path uses topo+struct only, ignoring async layers."""
        # topo: 1000m / 10m relief -> base 10.0 if only topo is considered
        topo = [(0.0, 100.0), (1000.0, 110.0)]
        # geol/drillhole carry a huge elevation (5000m); if they were
        # included, the ratio would be ~5.0 and the VE would drop to 1.0.
        geol = [GeologySegment("Unit A", None, {}, [(0.0, 100.0), (1000.0, 5000.0)])]
        drillhole = [
            DrillholeProjection(
                hole_id="DH-1",
                distance=500.0,
                elevation=5000.0,
                offset=0.0,
                total_depth=100.0,
                segments=[GeologySegment("Unit A", None, {}, [(0.0, 5000.0)])],
            )
        ]
        result = PreviewResult(topo=topo, geol=geol, struct=None, drillhole=drillhole)

        ve = self.service.calculate_from_result(result)

        self.assertEqual(ve, self.service.calculate(topo, None))
        self.assertEqual(ve, 10.0)

    def test_no_qgis_import(self):
        """The service must remain QGIS-agnostic (architecture boundary)."""
        service_file = (
            Path(__file__).resolve().parents[2]
            / "core"
            / "services"
            / "vertical_exaggeration_service.py"
        )
        tree = ast.parse(service_file.read_text(encoding="utf-8"))

        imported_roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".")[0])

        self.assertNotIn("qgis", imported_roots)
        self.assertNotIn("PyQt5", imported_roots)
        self.assertNotIn("PyQt6", imported_roots)
