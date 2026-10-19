"""Regression tests for component cache keys in ProfileController.

The export path calls ``ProfileController.generate_profile_data``; a cache key
that omits an input (layer, field mapping, smoothing) returns stale data. Each
test changes one input and asserts the extractor is called again.
"""

import unittest
from unittest.mock import MagicMock

from sec_interp.core.controller import ProfileController
from sec_interp.core.domain import PreviewParams


class FakeLayer:
    """Minimal layer stub exposing the stable ``id()`` used by cache keys."""

    def __init__(self, layer_id: str) -> None:
        self.layer_id = layer_id

    def id(self) -> str:
        return self.layer_id


class TestControllerCacheKeys(unittest.TestCase):
    """Every component cache key must include all inputs that affect its data."""

    def setUp(self):
        self.controller = ProfileController()
        self.controller.profile_extractor = MagicMock()
        self.controller.profile_extractor.extract_profile.return_value = [(0.0, 10.0)]
        self.controller.geology_extractor = MagicMock()
        self.controller.geology_extractor.extract_context.return_value = MagicMock()
        self.controller.geology_service = MagicMock()
        self.controller.geology_service.build_segments.return_value = [MagicMock()]
        self.controller.structure_extractor = MagicMock()
        self.controller.structure_extractor.extract_section_and_structures.return_value = (
            MagicMock()
        )
        self.controller.structure_extractor.make_elevation_sampler.return_value = MagicMock()
        self.controller.structure_service = MagicMock()
        self.controller.structure_service.project_structures.return_value = [MagicMock()]
        self.controller.drillhole_extractor = MagicMock()
        self.controller.drillhole_extractor.extract_context.return_value = MagicMock()
        self.controller.drillhole_service = MagicMock()
        self.controller.drillhole_service.process_context.return_value = ([], [MagicMock()])

    def _params(self, **overrides):
        values = {
            "raster_layer": FakeLayer("raster-1"),
            "line_layer": FakeLayer("line-1"),
            "band_num": 1,
        }
        values.update(overrides)
        return PreviewParams(**values)

    def test_topography_cache_varies_with_raster_layer(self):
        self.controller._process_topography(self._params(), {}, [])
        self.controller._process_topography(
            self._params(raster_layer=FakeLayer("raster-2")), {}, []
        )

        self.assertEqual(self.controller.profile_extractor.extract_profile.call_count, 2)

    def test_geology_cache_varies_with_smoothing(self):
        params = self._params(
            outcrop_layer=FakeLayer("outcrop-1"),
            outcrop_name_field="unit",
        )
        self.controller._process_geology(params, {}, [])

        smoothed = self._params(
            outcrop_layer=FakeLayer("outcrop-1"),
            outcrop_name_field="unit",
            smooth=True,
            smooth_window=50,
        )
        self.controller._process_geology(smoothed, {}, [])

        self.assertEqual(self.controller.geology_extractor.extract_context.call_count, 2)

    def test_structure_cache_varies_with_line_layer(self):
        params = self._params(
            struct_layer=FakeLayer("struct-1"),
            dip_field="dip",
            strike_field="strike",
        )
        self.controller._process_structures(params, {}, [])

        moved_line = self._params(
            line_layer=FakeLayer("line-2"),
            struct_layer=FakeLayer("struct-1"),
            dip_field="dip",
            strike_field="strike",
        )
        self.controller._process_structures(moved_line, {}, [])

        extracted = self.controller.structure_extractor.extract_section_and_structures
        self.assertEqual(extracted.call_count, 2)

    def test_drillhole_cache_varies_with_field_mapping(self):
        params = self._params(
            collar_layer=FakeLayer("collar-1"),
            survey_layer=FakeLayer("survey-1"),
            interval_layer=FakeLayer("interval-1"),
            collar_id_field="hole_id",
            survey_id_field="hole_id",
            survey_depth_field="depth",
            survey_azim_field="azimuth",
            survey_incl_field="inclination",
            interval_id_field="hole_id",
            interval_from_field="from",
            interval_to_field="to",
            interval_lith_field="lith",
        )
        self.controller._process_drillholes(params, {}, [])

        remapped = self._params(
            collar_layer=FakeLayer("collar-1"),
            survey_layer=FakeLayer("survey-1"),
            interval_layer=FakeLayer("interval-1"),
            collar_id_field="hole_id",
            survey_id_field="hole",
            survey_depth_field="depth",
            survey_azim_field="azimuth",
            survey_incl_field="inclination",
            interval_id_field="hole_id",
            interval_from_field="from",
            interval_to_field="to",
            interval_lith_field="lith",
        )
        self.controller._process_drillholes(remapped, {}, [])

        self.assertEqual(self.controller.drillhole_extractor.extract_context.call_count, 2)


if __name__ == "__main__":
    unittest.main()
