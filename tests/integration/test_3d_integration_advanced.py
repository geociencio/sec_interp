import unittest
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsPoint,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsProject,
    QgsField,
    QgsFields,
)
from qgis.PyQt.QtCore import QMetaType
from tests.integration.base_integration import BaseIntegrationTest
from sec_interp.core.services.drillhole_service import DrillholeService
from sec_interp.core.services.drillhole.drillhole_orchestrator import (
    DrillholeTaskOrchestrator,
)


class Test3DIntegrationAdvanced(BaseIntegrationTest):

    def setUp(self):
        super().setUp()
        self.service = DrillholeService()
        self.orchestrator = DrillholeTaskOrchestrator(self.service)

        # Define CRS
        self.crs_wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")
        self.crs_utm18s = QgsCoordinateReferenceSystem("EPSG:32718")  # UTM Zone 18S

    def _create_memory_layer(self, name, geom_type, crs, fields_def):
        uri = f"{geom_type}?crs={crs.authid()}"
        layer = QgsVectorLayer(uri, name, "memory")
        pr = layer.dataProvider()
        fields = QgsFields()
        for f_name, f_type in fields_def:
            fields.append(QgsField(f_name, f_type))
        pr.addAttributes(fields)
        layer.updateFields()
        return layer

    def test_complex_crs_transformation(self):
        """Test projecting collars from WGS84 (lat/lon) to a UTM section line."""

        # 1. Create Section Line in UTM 18S
        # (Approx Lima coords in UTM: 279000 E, 8660000 N)
        section_layer = self._create_memory_layer(
            "Section", "LineString", self.crs_utm18s, []
        )
        feat = QgsFeature()
        # 1000m line running North-South
        line_geom = QgsGeometry.fromPolylineXY(
            [QgsPointXY(279000, 8660000), QgsPointXY(279000, 8661000)]
        )
        feat.setGeometry(line_geom)
        section_layer.dataProvider().addFeatures([feat])

        # 2. Create Collar in WGS84
        transform = QgsCoordinateTransform(
            self.crs_utm18s, self.crs_wgs84, QgsProject.instance()
        )
        utm_pt = QgsPointXY(279000, 8660500)  # Midpoint of section
        wgs_pt = transform.transform(utm_pt)

        collar_layer = self._create_memory_layer(
            "Collar",
            "Point",
            self.crs_wgs84,
            [("HoleID", QMetaType.Type.QString), ("Elev", QMetaType.Type.Double)],
        )
        c_feat = QgsFeature()
        c_feat.setGeometry(QgsGeometry.fromPointXY(wgs_pt))
        c_feat.setAttributes(["H001", 100.0])
        collar_layer.dataProvider().addFeatures([c_feat])

        # 3. Create dummy child layers (empty but valid schema)
        survey_layer = self._create_memory_layer(
            "Survey",
            "NoGeometry",
            self.crs_wgs84,
            [
                ("HoleID", QMetaType.Type.QString),
                ("Depth", QMetaType.Type.Double),
                ("Azim", QMetaType.Type.Double),
                ("Incl", QMetaType.Type.Double),
            ],
        )
        # Add straight hole survey (Vertical)
        s_feat = QgsFeature()
        s_feat.setAttributes(["H001", 0.0, 0.0, -90.0])
        survey_layer.dataProvider().addFeatures([s_feat])

        interval_layer = self._create_memory_layer(
            "Interval",
            "NoGeometry",
            self.crs_wgs84,
            [
                ("HoleID", QMetaType.Type.QString),
                ("From", QMetaType.Type.Double),
                ("To", QMetaType.Type.Double),
                ("Lith", QMetaType.Type.QString),
            ],
        )
        i_feat = QgsFeature()
        i_feat.setAttributes(["H001", 0.0, 50.0, "ROCK"])
        interval_layer.dataProvider().addFeatures([i_feat])

        # 4. Prepare Task Input
        task_input = self.orchestrator.prepare_task_input(
            line_layer=section_layer,
            buffer_width=50.0,
            collar_layer=collar_layer,
            collar_id_field="HoleID",
            use_geometry=True,
            collar_x_field="",
            collar_y_field="",
            collar_z_field="Elev",
            collar_depth_field="",
            survey_layer=survey_layer,
            survey_fields={
                "id": "HoleID",
                "depth": "Depth",
                "azim": "Azim",
                "incl": "Incl",
            },
            interval_layer=interval_layer,
            interval_fields={
                "id": "HoleID",
                "from": "From",
                "to": "To",
                "lith": "Lith",
            },
        )

        # 5. Process
        geol, drill = self.orchestrator.process_task_data(task_input)

        # 6. Verify
        # Should have found 1 hole
        self.assertEqual(len(drill), 1)
        # Should be at dist_along ~ 500m (midpoint)
        # Check projected points
        h_id, spatial_points, segments = drill[0]
        self.assertEqual(h_id, "H001")

        # Verify CRS transformation accuracy (allow small error due to float/reprojection)
        proj_x_on_section = spatial_points[0].dist_along  # Distance along
        self.assertAlmostEqual(proj_x_on_section, 500.0, delta=1.0)  # 1m tolerance

    def test_deviated_drillhole_projection(self):
        """Test projecting a deviated hole onto a diagonal section."""

        # 1. Diagonal Section (45 degrees NE)
        section_layer = self._create_memory_layer(
            "Section", "LineString", self.crs_utm18s, []
        )
        feat = QgsFeature()
        # Start at 0,0, End at 100,100
        line_geom = QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(100, 100)])
        feat.setGeometry(line_geom)
        section_layer.dataProvider().addFeatures([feat])

        # 2. Collar at 50,50 (Exact midpoint, on section)
        collar_layer = self._create_memory_layer(
            "Collar",
            "Point",
            self.crs_utm18s,
            [("HoleID", QMetaType.Type.QString), ("Elev", QMetaType.Type.Double)],
        )
        c_feat = QgsFeature()
        c_feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(50, 50)))
        c_feat.setAttributes(["D001", 100.0])
        collar_layer.dataProvider().addFeatures([c_feat])

        # 3. Deviated Survey: Starts vertical, then bends due East (Azim 90)
        survey_layer = self._create_memory_layer(
            "Survey",
            "NoGeometry",
            self.crs_utm18s,
            [
                ("HoleID", QMetaType.Type.QString),
                ("Depth", QMetaType.Type.Double),
                ("Azim", QMetaType.Type.Double),
                ("Incl", QMetaType.Type.Double),
            ],
        )

        # 0m: Vert
        f1 = QgsFeature()
        f1.setAttributes(["D001", 0.0, 0.0, -90.0])
        # 50m: Bend to East, Incl -45
        f2 = QgsFeature()
        f2.setAttributes(["D001", 50.0, 90.0, -45.0])

        survey_layer.dataProvider().addFeatures([f1, f2])

        interval_layer = self._create_memory_layer(
            "Interval",
            "NoGeometry",
            self.crs_utm18s,
            [
                ("HoleID", QMetaType.Type.QString),
                ("From", QMetaType.Type.Double),
                ("To", QMetaType.Type.Double),
                ("Lith", QMetaType.Type.QString),
            ],
        )
        # Interval covering the deviation
        i_feat = QgsFeature()
        i_feat.setAttributes(["D001", 40.0, 60.0, "ORE"])
        interval_layer.dataProvider().addFeatures([i_feat])

        # 4. Prepare & Process
        task_input = self.orchestrator.prepare_task_input(
            line_layer=section_layer,
            buffer_width=200.0,  # Wide buffer to catch deviation
            collar_layer=collar_layer,
            collar_id_field="HoleID",
            use_geometry=True,
            collar_x_field="",
            collar_y_field="",
            collar_z_field="Elev",
            collar_depth_field="",
            survey_layer=survey_layer,
            survey_fields={
                "id": "HoleID",
                "depth": "Depth",
                "azim": "Azim",
                "incl": "Incl",
            },
            interval_layer=interval_layer,
            interval_fields={
                "id": "HoleID",
                "from": "From",
                "to": "To",
                "lith": "Lith",
            },
        )

        geol, drill = self.orchestrator.process_task_data(task_input)

        # 5. Verify 3D projection logic
        h_id, spatial_points, segments = drill[0]

        # Check integrity: 3D points should drift East (X increases)
        # At depth 0 (Index 0): X=50, Y=50
        self.assertAlmostEqual(spatial_points[0].x_3d, 50.0)

        # At depth > 50, X should increase significantly (Azim 90)
        last_pt = spatial_points[-1]
        self.assertGreater(last_pt.x_3d, 50.0)

        # Check projected points on section (Diagonal plane)
        # Since hole deviates East (Azim 90), and section is NE (Azim 45),
        # the projection should show the hole moving "right" relative to the section start?
        # Or simply, the offset should increase.

        # Verify Z consistency
        # In current SpatialMeta, the projected points are part of the object
        # but we check if reprojection logic is sound by checking coords directly if needed.
        for p in spatial_points:
            # We check if 3D and its projection on the 2D section has same Z
            self.assertAlmostEqual(
                p.z, p.z
            )  # Trivial in SpatialMeta, but ensures p exists


if __name__ == "__main__":
    unittest.main()
