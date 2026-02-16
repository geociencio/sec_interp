"""Verification tests for Dependency Injection in ProfileController."""

import unittest
from unittest.mock import MagicMock
from sec_interp.core.controller import ProfileController
from sec_interp.core.services.drillhole_service import DrillholeService
from sec_interp.core.services.geology_service import GeologyService


class TestControllerDI(unittest.TestCase):
    """Test that ProfileController correctly injects dependencies."""

    def test_controller_initialization_injects_dependencies(self):
        """Verify that services in Controller have the expected processors."""
        controller = ProfileController()

        # Verify DrillholeService injection
        self.assertIs(
            controller.drillhole_service.collar_processor, controller.collar_processor
        )
        self.assertIs(
            controller.drillhole_service.survey_processor, controller.survey_processor
        )
        self.assertIs(
            controller.drillhole_service.interval_processor,
            controller.interval_processor,
        )
        self.assertIs(
            controller.drillhole_service.data_fetcher, controller.data_fetcher
        )
        self.assertIs(
            controller.drillhole_service.trajectory_engine, controller.trajectory_engine
        )

        # Verify GeologyService injection
        self.assertIs(
            controller.geology_service.profile_sampler, controller.profile_sampler
        )
        self.assertIs(
            controller.geology_service.outcrop_processor, controller.outcrop_processor
        )

    def test_manual_injection_into_services(self):
        """Verify that we can manually inject mocks into services."""
        mock_collar = MagicMock()
        mock_sampler = MagicMock()

        dh_service = DrillholeService(collar_processor=mock_collar)
        geol_service = GeologyService(profile_sampler=mock_sampler)

        self.assertIs(dh_service.collar_processor, mock_collar)
        self.assertIs(geol_service.profile_sampler, mock_sampler)

        # Default others should still be instantiated
        self.assertIsNotNone(dh_service.survey_processor)
        self.assertIsNotNone(geol_service.outcrop_processor)


if __name__ == "__main__":
    unittest.main()
