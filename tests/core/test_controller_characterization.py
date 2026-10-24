"""Characterization tests for ProfileController behavior.

These tests are the safety net for the module-size refactor: they pin the
current messages, cache behavior, ``None`` returns and orchestration order of
``core/controller.py`` before its component logic moves to
``core/services/profile/``.

They intentionally assert observable behavior, not private helper structure.
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from sec_interp.core.controller import ProfileController
from sec_interp.core.domain import PreviewParams
from sec_interp.core.exceptions import ProcessingError
from tests.base_test import BaseTestCase


class FakeLayer:
    """Minimal layer stub exposing the stable ``id()`` used by cache keys."""

    def __init__(self, layer_id: str) -> None:
        self.layer_id = layer_id

    def id(self) -> str:
        return self.layer_id


class TestControllerCharacterization(BaseTestCase):
    """Freeze ProfileController behavior while its implementation is extracted."""

    def setUp(self) -> None:
        super().setUp()
        self.controller = ProfileController()
        self.controller.tr = lambda message: message  # type: ignore[method-assign]
        self.controller.profile_extractor = MagicMock()
        self.controller.geology_extractor = MagicMock()
        self.controller.geology_service = MagicMock()
        self.controller.structure_extractor = MagicMock()
        self.controller.structure_service = MagicMock()
        self.controller.drillhole_extractor = MagicMock()
        self.controller.drillhole_service = MagicMock()
        self.messages: list[str] = []
        self.params = self._params()

    def _params(self, **overrides):
        values = {
            "raster_layer": FakeLayer("raster-1"),
            "line_layer": FakeLayer("line-1"),
            "band_num": 1,
        }
        values.update(overrides)
        return PreviewParams(**values)

    # -- Topography -----------------------------------------------------

    def test_topography_success_message_and_cache_hit(self):
        self.controller.profile_extractor.extract_profile.return_value = [
            (0.0, 10.0),
            (10.0, 20.0),
        ]

        first = self.controller._process_topography(self.params, {}, self.messages)
        second = self.controller._process_topography(self.params, {}, self.messages)

        self.assertEqual(first, [(0.0, 10.0), (10.0, 20.0)])
        self.assertEqual(second, first)
        self.assertEqual(
            self.messages,
            [
                "✓ Data processed successfully!\n\nTopography: 2 points",
                "✓ Data processed successfully!\n\nTopography: 2 points",
            ],
        )
        self.controller.profile_extractor.extract_profile.assert_called_once()

    def test_topography_errors_keep_current_messages(self):
        cases = [
            (
                "missing layers",
                lambda c: self._params(raster_layer=None),
                "Required layers for topography are missing.",
            ),
            (
                "missing extractor",
                lambda c: self._params(),
                "Topography service failed to load.",
            ),
            (
                "empty profile",
                lambda c: self._params(),
                "No topographic profile data was generated.",
            ),
        ]
        for name, params_factory, expected in cases:
            with self.subTest(name=name):
                controller = ProfileController()
                controller.tr = lambda message: message  # type: ignore[method-assign]
                controller.profile_extractor = MagicMock()
                params = params_factory(controller)
                if name == "missing extractor":
                    controller.profile_extractor = None
                elif name == "empty profile":
                    controller.profile_extractor.extract_profile.return_value = []

                with self.assertRaises(ProcessingError) as ctx:
                    controller._process_topography(params, {}, [])

                self.assertEqual(str(ctx.exception), expected)

    # -- Geology --------------------------------------------------------

    def test_geology_success_message_and_cache_hit(self):
        params = self._params(
            outcrop_layer=FakeLayer("outcrop-1"),
            outcrop_name_field="unit",
        )
        self.controller.geology_extractor.extract_context.return_value = MagicMock()
        self.controller.geology_service.build_segments.return_value = [MagicMock()] * 2

        first = self.controller._process_geology(params, {}, self.messages)
        second = self.controller._process_geology(params, {}, self.messages)

        self.assertEqual(len(first), 2)
        self.assertEqual(first, second)
        self.assertEqual(
            self.messages,
            ["Geology: 2 segments", "Geology: 2 segments"],
        )
        self.controller.geology_service.build_segments.assert_called_once()

    def test_geology_no_data_and_service_missing_messages(self):
        params = self._params(
            outcrop_layer=FakeLayer("outcrop-2"),
            outcrop_name_field="unit",
        )
        self.controller.geology_extractor.extract_context.return_value = MagicMock()
        self.controller.geology_service.build_segments.return_value = []

        self.assertEqual(
            self.controller._process_geology(params, {}, self.messages), []
        )
        self.assertEqual(self.messages, ["Geology: No intersections"])

        missing_service = ProfileController()
        missing_service.tr = lambda message: message  # type: ignore[method-assign]
        missing_service.geology_extractor = MagicMock()
        missing_service.geology_service = None
        missing_params = self._params(
            outcrop_layer=FakeLayer("outcrop-3"),
            outcrop_name_field="unit",
        )
        messages: list[str] = []

        self.assertIsNone(
            missing_service._process_geology(missing_params, {}, messages)
        )
        self.assertEqual(messages, ["Geology: Service failed to load"])

    def test_geology_without_outcrop_returns_none_without_message(self):
        self.assertIsNone(self.controller._process_geology(self.params, {}, self.messages))
        self.assertEqual(self.messages, [])

    # -- Structures -----------------------------------------------------

    def test_structures_success_message_and_cache_hit(self):
        params = self._params(
            struct_layer=FakeLayer("struct-1"),
            dip_field="dip",
            strike_field="strike",
        )
        ctx = MagicMock()
        self.controller.structure_extractor.extract_section_and_structures.return_value = ctx
        self.controller.structure_service.project_structures.return_value = [MagicMock()] * 3

        first = self.controller._process_structures(params, {}, self.messages)
        second = self.controller._process_structures(params, {}, self.messages)

        self.assertEqual(len(first), 3)
        self.assertEqual(first, second)
        self.assertEqual(
            self.messages,
            ["Structures: 3 points", "Structures: 3 points"],
        )
        self.controller.structure_service.project_structures.assert_called_once()

    def test_structures_empty_and_service_missing_messages(self):
        params = self._params(
            struct_layer=FakeLayer("struct-2"),
            buffer_dist=50.0,
        )
        self.controller.structure_extractor.extract_section_and_structures.return_value = (
            MagicMock()
        )
        self.controller.structure_service.project_structures.return_value = []

        self.assertEqual(
            self.controller._process_structures(params, {}, self.messages), []
        )
        self.assertEqual(self.messages, ["Structures: None in 50.0m buffer"])

        missing_service = ProfileController()
        missing_service.tr = lambda message: message  # type: ignore[method-assign]
        missing_service.structure_extractor = MagicMock()
        missing_service.structure_service = None
        messages: list[str] = []
        missing_params = self._params(struct_layer=FakeLayer("struct-3"))

        self.assertIsNone(
            missing_service._process_structures(missing_params, {}, messages)
        )
        self.assertEqual(messages, ["Structures: Service failed to load"])

    # -- Drillholes -----------------------------------------------------

    def test_drillholes_have_no_success_message_and_cache_hit(self):
        params = self._params(collar_layer=FakeLayer("collar-1"))
        self.controller.drillhole_extractor.extract_context.return_value = MagicMock()
        self.controller.drillhole_service.process_context.return_value = (
            [],
            [MagicMock()],
        )

        first = self.controller._process_drillholes(params, {}, self.messages)
        second = self.controller._process_drillholes(params, {}, self.messages)

        self.assertEqual(len(first), 1)
        self.assertEqual(first, second)
        self.assertEqual(self.messages, [])
        self.controller.drillhole_service.process_context.assert_called_once()

    def test_drillholes_service_missing_message(self):
        self.controller.drillhole_service = None
        params = self._params(collar_layer=FakeLayer("collar-2"))

        self.assertIsNone(self.controller._process_drillholes(params, {}, self.messages))
        self.assertEqual(self.messages, ["Drillholes: Service failed to load"])

    def test_drillholes_without_collar_returns_none_without_message(self):
        self.assertIsNone(self.controller._process_drillholes(self.params, {}, self.messages))
        self.assertEqual(self.messages, [])

    # -- Orchestration --------------------------------------------------

    def test_generate_profile_data_message_order_and_result(self):
        params = self._params(
            outcrop_layer=FakeLayer("outcrop-4"),
            outcrop_name_field="unit",
            struct_layer=FakeLayer("struct-4"),
            dip_field="dip",
            strike_field="strike",
            collar_layer=FakeLayer("collar-4"),
        )
        self.controller.profile_extractor.extract_profile.return_value = [(0.0, 1.0)]
        self.controller.geology_extractor.extract_context.return_value = MagicMock()
        self.controller.geology_service.build_segments.return_value = [MagicMock()]
        self.controller.structure_extractor.extract_section_and_structures.return_value = (
            MagicMock()
        )
        self.controller.structure_service.project_structures.return_value = [
            MagicMock()
        ]
        self.controller.drillhole_extractor.extract_context.return_value = MagicMock()
        self.controller.drillhole_service.process_context.return_value = (
            [],
            [MagicMock()],
        )

        result = self.controller.generate_profile_data(params)

        topo, geol, struct, drill, messages = result
        self.assertEqual(topo, [(0.0, 1.0)])
        self.assertEqual(len(geol), 1)
        self.assertEqual(len(struct), 1)
        self.assertEqual(len(drill), 1)
        self.assertEqual(
            messages,
            [
                "✓ Data processed successfully!\n\nTopography: 1 points",
                "Geology: 1 segments",
                "Structures: 1 points",
            ],
        )

    def test_generate_profile_data_stops_on_validation_error(self):
        params = self._params(band_num=0)

        with self.assertRaises(ValueError):
            self.controller.generate_profile_data(params)

        self.controller.profile_extractor.extract_profile.assert_not_called()


if __name__ == "__main__":
    unittest.main()
