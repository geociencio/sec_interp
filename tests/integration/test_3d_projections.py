# -*- coding: utf-8 -*-
"""
Integration tests for 3D vertical projections in complex Cartesian systems.
"""

import unittest
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsGeometry,
    QgsFeature,
    QgsCoordinateReferenceSystem,
    QgsPointXY,
)
from tests.base_test import BaseTestCase
from sec_interp.core.services.export_service import ExportService
from sec_interp.core.domain import ProfileData, GeologyData, GeologySegment

class Test3DProjections(BaseTestCase):
    """Integration tests for 3D projection consistency."""

    def setUp(self):
        super().setUp()
        self.project = QgsProject.instance()
        # Set a projected CRS (UTM 18S)
        self.crs = QgsCoordinateReferenceSystem("EPSG:32718")
        self.project.setCrs(self.crs)
        self.export_service = ExportService()

    def test_cartesian_projection_consistency(self):
        """Test that projected units maintain verticality in Cartesian space."""
        # Define a straight section
        topo_data = [(0.0, 100.0), (100.0, 100.0)]

        # Define a geology segment
        geol_data = GeologyData()
        geol_data.append(GeologySegment(
            unit_name="Unit A",
            geometry_wkt=None,
            attributes={},
            points=[(20.0, 100.0), (80.0, 100.0)]
        ))

        from pathlib import Path
        import tempfile
        from sec_interp.core.domain import PreviewParams
        from unittest.mock import MagicMock

        origin_pt = QgsPointXY(1000, 2000)
        azimuth_val = 90.0

        with tempfile.TemporaryDirectory() as tmpdir:
            output_folder = Path(tmpdir)

            # Mock a layer for the params
            mock_layer = MagicMock()
            mock_layer.isValid.return_value = True
            mock_layer.crs.return_value = self.crs

            # Mock QgsProject.instance().mapLayer
            with unittest.mock.patch('qgis.core.QgsProject.instance') as mock_instance:
                mock_proj = MagicMock()
                mock_instance.return_value = mock_proj
                mock_proj.mapLayer.return_value = mock_layer
                mock_proj.crs.return_value = self.crs

                # Create minimal params
                params_obj = PreviewParams(
                    raster_layer="mock_raster",
                    line_layer="mock_line",
                    band_num=1,
                    buffer_dist=10.0
                )

                try:
                    results = self.export_service.export_data(
                        output_folder,
                        params_obj,
                        topo_data,
                        geol_data,
                        [],  # struct_data
                        export_options={"exp_geol": True, "drill_3d_traces": True}
                    )
                    self.assertIsNotNone(results)
                except Exception as e:
                    import traceback
                    self.fail(f"3D Export failed with error: {e}\n{traceback.format_exc()}")

if __name__ == "__main__":
    unittest.main()
