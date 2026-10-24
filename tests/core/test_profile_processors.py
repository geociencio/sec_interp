"""Direct tests for the extracted profile component processors."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from sec_interp.core.domain import PreviewParams
from sec_interp.core.services.profile.cache import topography_cache_key
from sec_interp.core.services.profile.drillholes import process_drillholes
from sec_interp.core.services.profile.errors import (
    ProfileDataError,
    ProfileInputError,
    ProfileServiceError,
)
from sec_interp.core.services.profile.geology import process_geology
from sec_interp.core.services.profile.pipeline import build_profile_data
from sec_interp.core.services.profile.structures import process_structures
from sec_interp.core.services.profile.topography import process_topography


class FakeLayer:
    """Minimal layer stub with the stable ``id()`` used by cache keys."""

    def __init__(self, layer_id: str) -> None:
        """Store the fake layer identifier."""
        self.layer_id = layer_id

    def id(self) -> str:
        return self.layer_id


class FakeCache:
    """In-memory cache with the DataCache subset used by the processors."""

    def __init__(self) -> None:
        """Initialize an empty cache."""
        self.entries: dict[tuple[str, str], object] = {}

    def get(self, bucket: str, key: str):
        return self.entries.get((bucket, key))

    def set(self, bucket: str, key: str, data, metadata=None) -> None:
        self.entries[(bucket, key)] = data


def _params(**overrides):
    values = {
        "raster_layer": FakeLayer("raster-1"),
        "line_layer": FakeLayer("line-1"),
        "band_num": 1,
    }
    values.update(overrides)
    return PreviewParams(**values)


class TestTopographyProcessor(unittest.TestCase):
    def test_cache_hit_skips_extractor(self):
        params = _params()
        cache = FakeCache()
        cache.set("topo", topography_cache_key(params), [(0.0, 10.0)])
        extractor = MagicMock()

        result = process_topography(params, extractor, cache, {})

        self.assertEqual(result, [(0.0, 10.0)])
        extractor.extract_profile.assert_not_called()

    def test_typed_errors(self):
        cache = FakeCache()
        with self.assertRaises(ProfileInputError):
            process_topography(_params(raster_layer=None), MagicMock(), cache, {})

        with self.assertRaises(ProfileServiceError):
            process_topography(_params(), None, cache, {})

        empty = MagicMock()
        empty.extract_profile.return_value = []
        with self.assertRaises(ProfileDataError):
            process_topography(_params(), empty, cache, {})


class TestGeologyProcessor(unittest.TestCase):
    def test_missing_layers_raise_input_error(self):
        params = _params(
            outcrop_layer=FakeLayer("outcrop-1"),
            line_layer=None,
        )
        with self.assertRaises(ProfileInputError):
            process_geology(params, MagicMock(), MagicMock(), FakeCache(), {})

    def test_missing_service_raises_service_error(self):
        params = _params(outcrop_layer=FakeLayer("outcrop-1"))
        with self.assertRaises(ProfileServiceError):
            process_geology(params, MagicMock(), None, FakeCache(), {})

    def test_empty_segments_return_empty_list(self):
        params = _params(outcrop_layer=FakeLayer("outcrop-1"))
        extractor = MagicMock()
        service = MagicMock()
        service.build_segments.return_value = []

        self.assertEqual(process_geology(params, extractor, service, FakeCache(), {}), [])


class TestStructureAndDrillholeErrors(unittest.TestCase):
    def test_structure_service_error(self):
        params = _params(struct_layer=FakeLayer("struct-1"))
        with self.assertRaises(ProfileServiceError):
            process_structures(params, MagicMock(), None, FakeCache(), {})

    def test_structure_missing_context_returns_none(self):
        params = _params(struct_layer=FakeLayer("struct-1"))
        extractor = MagicMock()
        extractor.extract_section_and_structures.return_value = None

        self.assertIsNone(process_structures(params, extractor, MagicMock(), FakeCache(), {}))

    def test_drillhole_service_error(self):
        params = _params(collar_layer=FakeLayer("collar-1"))
        with self.assertRaises(ProfileServiceError):
            process_drillholes(params, MagicMock(), None, FakeCache(), {})

    def test_drillhole_missing_context_returns_none(self):
        params = _params(collar_layer=FakeLayer("collar-1"))
        extractor = MagicMock()
        extractor.extract_context.return_value = None

        self.assertIsNone(process_drillholes(params, extractor, MagicMock(), FakeCache(), {}))


class TestProfilePipeline(unittest.TestCase):
    def test_calls_components_in_fixed_order(self):
        calls: list[str] = []
        params = _params()

        def component(name: str):
            def run(params, cache_meta, messages):
                calls.append(name)
                messages.append(name)
                return name

            return run

        result = build_profile_data(
            params,
            component("topo"),
            component("geol"),
            component("struct"),
            component("drill"),
        )

        self.assertEqual(calls, ["topo", "geol", "struct", "drill"])
        self.assertEqual(result, ("topo", "geol", "struct", "drill", calls))


if __name__ == "__main__":
    unittest.main()
