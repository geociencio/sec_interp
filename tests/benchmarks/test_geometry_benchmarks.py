"""Benchmarks for geometric operations."""

import unittest
import math
from qgis.core import (
    QgsGeometry,
    QgsPointXY,
    QgsPoint,
    QgsLineString,
    QgsPolygon,
    QgsWkbTypes
)

from tests.integration.base_integration import BaseIntegrationTest
from tests.benchmarks.benchmark_utils import benchmark, BenchmarkMixin

class TestGeometryBenchmarks(BaseIntegrationTest, BenchmarkMixin):
    """Benchmark tests for geometry operations."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Pre-generate large datasets for benchmarking
        cls.large_polygon_points = [
            QgsPointXY(x, 0) for x in range(1000)
        ] + [
            QgsPointXY(x, 100) for x in range(999, -1, -1)
        ]

    @benchmark
    def test_polygon_creation_performance(self):
        """Benchmark creating complex polygons."""
        def create_polygon():
            return QgsGeometry.fromPolygonXY([self.large_polygon_points])

        # Should be very fast (< 0.01s) even for 2000 points
        self.assertExecutionTime(create_polygon, 0.05)

    @benchmark
    def test_geometry_validation_performance(self):
        """Benchmark geometry validation check."""
        poly = QgsGeometry.fromPolygonXY([self.large_polygon_points])

        def validate():
            return poly.isGeosValid()

        self.assertExecutionTime(validate, 0.1)

    @benchmark
    def test_projection_math_performance(self):
        """Benchmark mathematical projection calculations."""
        # Test pure math performance for 3D projection logic
        points = [(i, i * 0.5, 100) for i in range(10000)]
        origin_x, origin_y = 1000, 1000
        azimuth = math.radians(45)
        cos_az = math.cos(azimuth)
        sin_az = math.sin(azimuth)

        def project_points():
            results = []
            for x, y, z in points:
                east = origin_x + (x * cos_az)
                north = origin_y + (x * sin_az)
                results.append((east, north, z))
            return results

        # 10k points should process instantly
        self.assertExecutionTime(project_points, 0.05)

    @benchmark
    def test_qgis_3d_geometry_construction(self):
        """Benchmark constructing QgsPolygon with Z dimension."""
        def construct_3d():
            points_3d = []
            for i in range(1000):
                points_3d.append(QgsPoint(i, i, 100))

            line = QgsLineString(points_3d)
            poly = QgsPolygon()
            poly.setExteriorRing(line)
            geom = QgsGeometry(poly)
            return geom

        self.assertExecutionTime(construct_3d, 0.1)

if __name__ == '__main__':
    unittest.main()
