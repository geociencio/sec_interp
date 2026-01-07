"""Benchmarks for export operations."""

import unittest
import shutil
import tempfile
from pathlib import Path
from qgis.core import (
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsFields,
    QgsField,
    QgsVectorFileWriter,
    QgsProject,
    QgsCoordinateReferenceSystem,
    QgsWkbTypes
)
from qgis.PyQt.QtCore import QMetaType

from tests.integration.base_integration import BaseIntegrationTest
from tests.benchmarks.benchmark_utils import benchmark, BenchmarkMixin

class TestExportBenchmarks(BaseIntegrationTest, BenchmarkMixin):
    """Benchmark tests for export operations."""

    def setUp(self):
        super().setUp()
        self.test_dir = Path(tempfile.mkdtemp())
        self.crs = QgsCoordinateReferenceSystem("EPSG:4326")

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        super().tearDown()

    def _create_dummy_features(self, count: int) -> list[QgsFeature]:
        features = []
        fields = QgsFields()
        fields.append(QgsField("id", QMetaType.Int))
        fields.append(QgsField("name", QMetaType.QString))

        for i in range(count):
            feat = QgsFeature(fields)
            feat.setAttribute("id", i)
            feat.setAttribute("name", f"Feature {i}")
            feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(i, i)))
            features.append(feat)
        return features

    @benchmark
    def test_shapefile_write_performance_1k(self):
        """Benchmark writing 1000 features to a shapefile."""
        features = self._create_dummy_features(1000)
        output_path = str(self.test_dir / "bench_1k.shp")

        def write_shp():
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = "ESRI Shapefile"

            writer = QgsVectorFileWriter.create(
                output_path,
                features[0].fields(),
                QgsWkbTypes.Point,
                self.crs,
                QgsProject.instance().transformContext(),
                options
            )

            if writer.hasError() != QgsVectorFileWriter.NoError:
                raise Exception(writer.errorMessage())

            for feat in features:
                writer.addFeature(feat)

            del writer

        self.assertExecutionTime(write_shp, 1.0) # Should be well under 1s

    @benchmark
    def test_shapefile_write_performance_10k(self):
        """Benchmark writing 10,000 features to a shapefile."""
        features = self._create_dummy_features(10000)
        output_path = str(self.test_dir / "bench_10k.shp")

        def write_shp():
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = "ESRI Shapefile"

            writer = QgsVectorFileWriter.create(
                output_path,
                features[0].fields(),
                QgsWkbTypes.Point,
                self.crs,
                QgsProject.instance().transformContext(),
                options
            )

            for feat in features:
                writer.addFeature(feat)

            del writer

        self.assertExecutionTime(write_shp, 5.0)

if __name__ == '__main__':
    unittest.main()
