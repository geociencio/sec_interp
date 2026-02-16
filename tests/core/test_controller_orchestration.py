"""Tests for ProfileController orchestration and usage of injected services."""

import unittest
from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from sec_interp.core.controller import ProfileController


class TestControllerOrchestration(BaseTestCase):
    """Test that ProfileController orchestrates its injected services correctly."""

    def setUp(self):
        super().setUp()
        self.controller = ProfileController()
        # Mock the actual service objects already in the controller
        self.controller.drillhole_service = MagicMock()
        self.controller.drillhole_orchestrator = MagicMock()
        self.controller.geology_service = MagicMock()
        self.controller.structure_service = MagicMock()
        self.controller.profile_service = MagicMock()

    def test_process_topography_delegation(self):
        """Verify that _process_topography calls the profile service."""
        params = MagicMock()
        messages = []

        self.controller._process_topography(params, {}, messages)

        self.controller.profile_service.generate_topographic_profile.assert_called_once()

    def test_process_geology_delegation(self):
        """Verify that _process_geology calls the geology service."""
        params = MagicMock()
        params.outcrop_layer = MagicMock()
        messages = []

        self.controller._process_geology(params, {}, messages)

        self.controller.geology_service.generate_geological_profile.assert_called_once()

    def test_process_drillholes_delegation(self):
        """Verify that _process_drillholes calls the drillhole orchestrator."""
        params = MagicMock()
        params.collar_layer = MagicMock()
        messages = []

        self.controller._process_drillholes(params, {}, messages)

        self.controller.drillhole_orchestrator.run_preview.assert_called_once_with(
            params
        )


if __name__ == "__main__":
    unittest.main()
