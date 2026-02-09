from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from qgis.core import QgsPointXY, QgsApplication
from sec_interp.gui.main_dialog_interpretation import DialogInterpretationManager
from sec_interp.core.domain import InterpretationPolygon, GeologySegment


class TestAttributeInheritance(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.qgs = QgsApplication([], False)
        cls.qgs.initQgis()

    @classmethod
    def tearDownClass(cls):
        cls.qgs.exitQgis()
        cls.qgs = None
        super().tearDownClass()

    def test_inheritance_midpoint_bias(self):
        """
        Test that inheritance picks the *geometrically* closest feature,
        even if its midpoint is further away.
        """
        # 1. Setup DialogInterpretationManager with minimal mocks
        mock_dialog = MagicMock()
        mock_dialog.layer_factory = MagicMock()
        mock_dialog.layer_factory.get_color_for_unit.return_value = MagicMock(
            name=lambda: "#FF0000"
        )
        mock_dialog.preview_manager = MagicMock()

        # Mock cached data
        # geology segment: long line from x=10 to x=100. Midpoint x=55.
        # polygon: at x=12. Distance to geol start=2. Distance to geol mid=43.
        # drillhole: at x=30. Distance to poly=18.

        geol_points = [(x, 0) for x in range(10, 101, 10)]  # 10, 20, ... 100
        geol_seg = GeologySegment(
            unit_name="GeologyUnit",
            geometry_wkt=None,
            attributes={},
            points=geol_points,
        )

        dh_points_tuple = [(30, 0), (31, 0)]
        dh_points_obj = [(40, 0), (41, 0)]

        # 1. Tuple mocks: (id_str, trace, intervals_list)
        dh_int_tuple = MagicMock()
        dh_int_tuple.rock_unit = "DrillholeTuple"
        dh_int_tuple.points = dh_points_tuple
        dh_int_tuple.attributes = {}
        dh_tuple = ("DH1", [], [dh_int_tuple])

        # 2. Object mocks: obj.intervals = [interval]
        dh_int_obj = MagicMock()
        dh_int_obj.rock_unit = "DrillholeObj"
        dh_int_obj.points = dh_points_obj
        dh_int_obj.attributes = {}

        dh_obj = MagicMock()
        dh_obj.intervals = [dh_int_obj]

        mock_dialog.preview_manager.cached_data = {
            "geol": [geol_seg],
            "drillhole": [dh_tuple, dh_obj],
        }

        # Create InterpretationManager
        interp_manager = DialogInterpretationManager(mock_dialog)

        # 2. Setup Polygon at x=12, y=0
        poly = InterpretationPolygon(
            id="poly1",
            name="NewPoly",
            type="lithology",
            vertices_2d=[(11, -1), (13, -1), (12, 1)],  # Centroid ~ (12, 0)
            attributes={},
        )

        # 3. Configure to inherit from both
        config = {
            "inherit_geology": True,
            "inherit_drillholes": True,
            "custom_fields": [],
        }

        # 4. Run Inheritance
        interp_manager.apply_attribute_inheritance(poly, config)

        # 5. Assertions
        # We EXPECT GeologyUnit to win because the polygon is at x=12 and Geol starts at x=10 (dist=2).
        # But if the bug exists, DrillholeUnit (at x=30) will win because Geol Midpoint(55) is far.

        print(f"Inherited Name: {poly.name}")
        self.assertEqual(
            poly.name,
            "GeologyUnit",
            "Should inherit from closest geometry (Geology), not closest midpoint (Drillhole)",
        )


if __name__ == "__main__":
    import unittest

    unittest.main()
