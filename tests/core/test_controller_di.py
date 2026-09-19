"""Verification tests for Dependency Injection in ProfileController."""

import unittest
from unittest.mock import MagicMock
from sec_interp.core.controller import ProfileController
from sec_interp.core.services.drillhole_service import DrillholeService
from sec_interp.core.services.geology_service import GeologyService


class TestControllerDI(unittest.TestCase):
    """Test that ProfileController correctly injects dependencies."""

    def test_controller_initialization_injects_dependencies(self):
        """Verify that services in Controller have the expected dependencies."""
        mock_data_fetcher = MagicMock()
        mock_structure_extractor = MagicMock()
        mock_geology_extractor = MagicMock()
        controller = ProfileController(
            data_fetcher=mock_data_fetcher,
            structure_extractor=mock_structure_extractor,
            geology_extractor=mock_geology_extractor,
        )

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
        self.assertIs(controller.data_fetcher, mock_data_fetcher)
        self.assertIs(
            controller.drillhole_service.trajectory_engine, controller.trajectory_engine
        )

        # Verify Extract adapter injection
        self.assertIs(controller.structure_extractor, mock_structure_extractor)
        self.assertIs(controller.geology_extractor, mock_geology_extractor)

    def test_manual_injection_into_services(self):
        """Verify that we can manually inject mocks into services."""
        mock_collar = MagicMock()

        dh_service = DrillholeService(collar_processor=mock_collar)
        geol_service = GeologyService()

        self.assertIs(dh_service.collar_processor, mock_collar)
        self.assertIsNotNone(geol_service)

        # Default processors should still be instantiated
        self.assertIsNotNone(dh_service.survey_processor)


if __name__ == "__main__":
    unittest.main()
