"""Unit tests for profile component cache-key builders."""

from __future__ import annotations

import unittest

from sec_interp.core.domain import PreviewParams
from sec_interp.core.services.profile.cache import (
    component_cache_key,
    drillholes_cache_key,
    geology_cache_key,
    structures_cache_key,
    topography_cache_key,
)


class FakeLayer:
    """Minimal layer stub exposing the stable ``id()`` used by cache keys."""

    def __init__(self, layer_id: str) -> None:
        self.layer_id = layer_id

    def id(self) -> str:
        return self.layer_id


def _params(**overrides):
    values = {
        "raster_layer": FakeLayer("raster-1"),
        "line_layer": FakeLayer("line-1"),
        "band_num": 1,
    }
    values.update(overrides)
    return PreviewParams(**values)


class TestComponentCacheKey(unittest.TestCase):
    def test_key_is_order_independent(self):
        self.assertEqual(
            component_cache_key(alpha=1, beta=2),
            component_cache_key(beta=2, alpha=1),
        )

    def test_key_uses_layer_id(self):
        self.assertEqual(
            component_cache_key(layer=FakeLayer("layer-1")),
            component_cache_key(layer=FakeLayer("layer-1")),
        )
        self.assertNotEqual(
            component_cache_key(layer=FakeLayer("layer-1")),
            component_cache_key(layer=FakeLayer("layer-2")),
        )


class TestComponentSpecificKeys(unittest.TestCase):
    def test_topography_key_tracks_raster_and_lod(self):
        base = _params()
        self.assertNotEqual(
            topography_cache_key(base),
            topography_cache_key(_params(raster_layer=FakeLayer("raster-2"))),
        )
        self.assertNotEqual(
            topography_cache_key(base),
            topography_cache_key(_params(max_points=2000)),
        )

    def test_geology_key_tracks_smoothing_and_field(self):
        base = _params(
            outcrop_layer=FakeLayer("outcrop-1"),
            outcrop_name_field="unit",
        )
        self.assertNotEqual(
            geology_cache_key(base),
            geology_cache_key(
                _params(
                    outcrop_layer=FakeLayer("outcrop-1"),
                    outcrop_name_field="unit",
                    smooth=True,
                    smooth_window=50,
                )
            ),
        )
        self.assertNotEqual(
            geology_cache_key(base),
            geology_cache_key(
                _params(
                    outcrop_layer=FakeLayer("outcrop-1"),
                    outcrop_name_field="formation",
                )
            ),
        )

    def test_structures_key_tracks_buffer_and_line(self):
        base = _params(struct_layer=FakeLayer("struct-1"), buffer_dist=50.0)
        self.assertNotEqual(
            structures_cache_key(base),
            structures_cache_key(
                _params(struct_layer=FakeLayer("struct-1"), buffer_dist=100.0)
            ),
        )
        self.assertNotEqual(
            structures_cache_key(base),
            structures_cache_key(
                _params(
                    line_layer=FakeLayer("line-2"),
                    struct_layer=FakeLayer("struct-1"),
                    buffer_dist=50.0,
                )
            ),
        )

    def test_drillhole_key_tracks_every_field_mapping(self):
        base = _params(
            collar_layer=FakeLayer("collar-1"),
            survey_layer=FakeLayer("survey-1"),
            interval_layer=FakeLayer("interval-1"),
            survey_id_field="hole_id",
            interval_lith_field="lith",
        )
        changed = _params(
            collar_layer=FakeLayer("collar-1"),
            survey_layer=FakeLayer("survey-1"),
            interval_layer=FakeLayer("interval-1"),
            survey_id_field="hole",
            interval_lith_field="lith",
        )
        self.assertNotEqual(drillholes_cache_key(base), drillholes_cache_key(changed))

    def test_keys_are_component_specific(self):
        params = _params()
        keys = {
            topography_cache_key(params),
            geology_cache_key(params),
            structures_cache_key(params),
            drillholes_cache_key(params),
        }
        self.assertEqual(len(keys), 4)


if __name__ == "__main__":
    unittest.main()
