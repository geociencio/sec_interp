"""Feature-id pass-through tests for profile component processors."""

from __future__ import annotations

from unittest.mock import MagicMock

from sec_interp.core.services.profile.drillholes import process_drillholes
from sec_interp.core.services.profile.geology import process_geology
from sec_interp.core.services.profile.structures import process_structures
from sec_interp.core.services.profile.topography import process_topography
from tests.base_test import BaseTestCase

FEATURE_ID = 42


def _params() -> MagicMock:
    params = MagicMock()
    params.section_feature_id = FEATURE_ID
    params.line_layer = MagicMock()
    params.raster_layer = MagicMock()
    params.band_num = 1
    params.buffer_dist = 100.0
    params.outcrop_layer = MagicMock()
    params.outcrop_name_field = "unit"
    params.smooth = False
    params.smooth_window = 0
    params.struct_layer = MagicMock()
    params.dip_field = "dip"
    params.strike_field = "strike"
    params.collar_layer = MagicMock()
    params.survey_layer = MagicMock()
    params.interval_layer = MagicMock()
    return params


def _cache() -> MagicMock:
    cache = MagicMock()
    cache.get.return_value = None
    return cache


class TestProfileFeatureIdPassThrough(BaseTestCase):
    """Each component processor forwards the selected section feature id."""

    def test_topography_forwards_feature_id(self) -> None:
        extractor = MagicMock()
        extractor.extract_profile.return_value = [(0.0, 1.0)]

        process_topography(_params(), extractor, _cache(), {})

        call = extractor.extract_profile.call_args
        self.assertEqual(call.kwargs["feature_id"], FEATURE_ID)

    def test_geology_forwards_feature_id(self) -> None:
        params = _params()
        extractor = MagicMock()
        extractor.extract_context.return_value = MagicMock()
        service = MagicMock()
        service.build_segments.return_value = []

        process_geology(params, extractor, service, _cache(), {})

        call = extractor.extract_context.call_args
        self.assertEqual(call.kwargs["feature_id"], FEATURE_ID)

    def test_structures_forwards_feature_id(self) -> None:
        params = _params()
        extractor = MagicMock()
        extractor.extract_section_and_structures.return_value = MagicMock()
        extractor.make_elevation_sampler.return_value = MagicMock()
        service = MagicMock()
        service.project_structures.return_value = []

        process_structures(params, extractor, service, _cache(), {})

        call = extractor.extract_section_and_structures.call_args
        self.assertEqual(call.kwargs["feature_id"], FEATURE_ID)

    def test_drillholes_forwards_feature_id(self) -> None:
        params = _params()
        extractor = MagicMock()
        extractor.extract_context.return_value = MagicMock()
        service = MagicMock()
        service.process_context.return_value = ([], [])

        process_drillholes(params, extractor, service, _cache(), {})

        call = extractor.extract_context.call_args
        self.assertEqual(call.kwargs["feature_id"], FEATURE_ID)
