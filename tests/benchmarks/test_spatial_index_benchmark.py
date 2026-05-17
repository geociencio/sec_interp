"""Benchmarks for InterpretationManager spatial lookups."""

import unittest
from unittest.mock import MagicMock
from qgis.core import QgsPointXY

from tests.integration.base_integration import BaseIntegrationTest
from tests.benchmarks.benchmark_utils import benchmark, BenchmarkMixin
from sec_interp.gui.dialog_interpretation_manager import InterpretationManager


class MockDialog:
    """Mock main dialog for testing."""
    def __init__(self):
        self.preview_manager = MagicMock()
        self.layer_factory = MagicMock()
        self.page_interpretation = MagicMock()
        self.project = MagicMock()


class MockSegment:
    """Mock geological segment."""
    def __init__(self, unit_name, points):
        self.unit_name = unit_name
        self.points = points
        self.attributes = {"test": 1}


class MockInterval:
    """Mock drillhole interval."""
    def __init__(self, rock_unit, points):
        self.rock_unit = rock_unit
        self.points = points
        self.attributes = {"test": 1}


class TestSpatialIndexBenchmarks(BaseIntegrationTest, BenchmarkMixin):
    """Benchmark tests for spatial index integration in InterpretationManager."""

    def setUp(self):
        super().setUp()
        self.dialog = MockDialog()
        self.manager = InterpretationManager(self.dialog)

        # Generate large dataset for baseline benchmark
        self.geol_data = []
        for i in range(5000):
            # Segments with 10 points each
            points = [(float(i + j), float(j)) for j in range(10)]
            self.geol_data.append(MockSegment(f"Unit_{i}", points))

        self.dh_data = []
        for i in range(5000):
            points = [(float(i - j), float(j)) for j in range(5)]
            # Mocking dh tuple structure
            interval_list = [MockInterval(f"Rock_{i}", points)]
            self.dh_data.append((0, 0, interval_list))

        self.dialog.preview_manager.cached_data = {
            "geol": self.geol_data,
            "drillhole": self.dh_data
        }

        self.dialog.page_interpretation.get_data.return_value = {
            "inherit_geology": True,
            "inherit_drillholes": True
        }

    @benchmark
    def test_baseline_attribute_inheritance(self):
        """Benchmark applying attribute inheritance using the baseline O(N*M) search."""
        # Create a mock interpretation polygon
        interp = MagicMock()
        interp.vertices_2d = [(2500.0, 5.0), (2510.0, 5.0), (2510.0, -5.0), (2500.0, -5.0)]
        interp.attributes = {}

        config = self.dialog.page_interpretation.get_data()

        def run_inheritance():
            self.manager.apply_attribute_inheritance(interp, config)

        # Baseline might take ~0.05-0.1s for 5000 segments with current pure Python loops
        # This assert limits execution time so we can see the time output from @benchmark
        self.assertExecutionTime(run_inheritance, 1.0)


if __name__ == "__main__":
    unittest.main()
