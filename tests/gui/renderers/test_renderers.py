"""Tests for GUI Renderers."""

import unittest
from unittest.mock import MagicMock, patch

from sec_interp.tests.base_test import BaseTestCase
from sec_interp.gui.renderers import topo_renderer
from sec_interp.gui.renderers.drillhole_renderer import DrillholeRenderer
from sec_interp.gui.renderers.topo_renderer import TopoRenderer
from sec_interp.gui.renderers.color_manager import ColorManager


class TestDrillholeRenderer(BaseTestCase):
    """Test suite for DrillholeRenderer."""

    def setUp(self):
        super().setUp()
        self.mock_color_manager = MagicMock(spec=ColorManager)
        self.renderer = DrillholeRenderer(self.mock_color_manager)
        self.mock_layer = MagicMock()

    def test_apply_trace_style(self):
        """Test applying style for drillhole traces."""
        self.renderer.apply_style(self.mock_layer, role="trace")

        # Verify renderer was set
        self.mock_layer.setRenderer.assert_called_once()
        # Verify labeling was set
        self.mock_layer.setLabeling.assert_called_once()
        self.mock_layer.setLabelsEnabled.assert_called_with(True)

    def test_apply_interval_style(self):
        """Test applying style for lithological intervals."""
        self.mock_color_manager.get_color.return_value = MagicMock()
        unique_units = {"LithA", "LithB"}

        self.renderer.apply_style(
            self.mock_layer, role="interval", unique_units=unique_units
        )

        # Verify renderer was set
        self.mock_layer.setRenderer.assert_called_once()
        # Should have called get_color for each unit
        self.assertEqual(self.mock_color_manager.get_color.call_count, 2)


class TestTopoRenderer(BaseTestCase):
    """Test suite for TopoRenderer."""

    def setUp(self):
        super().setUp()
        self.renderer = TopoRenderer()
        self.mock_layer = MagicMock()

    def test_apply_style(self):
        """Test applying style for topography."""
        self.renderer.apply_style(self.mock_layer)

        # Verify renderer was set
        self.mock_layer.setRenderer.assert_called_once()

    def test_gradient_mode_uses_graduated_renderer(self):
        """Gradient mode builds a graduated (ramp) renderer."""
        with (
            patch.object(topo_renderer, "QgsGraduatedSymbolRenderer") as graduated,
            patch.object(topo_renderer, "QgsSingleSymbolRenderer") as single,
        ):
            self.renderer.apply_style(
                self.mock_layer, color_mode="gradient", ramp_name="Spectral"
            )

        graduated.assert_called_once()
        single.assert_not_called()

    def test_single_mode_uses_single_symbol_renderer(self):
        """Single mode builds a single-symbol renderer."""
        with (
            patch.object(topo_renderer, "QgsSingleSymbolRenderer") as single,
            patch.object(topo_renderer, "QgsGraduatedSymbolRenderer") as graduated,
        ):
            self.renderer.apply_style(
                self.mock_layer, color_mode="single", single_color="#ff0000"
            )

        single.assert_called_once()
        graduated.assert_not_called()

    def test_unknown_ramp_does_not_crash(self):
        """An unknown ramp name falls back without raising."""
        self.renderer.apply_style(
            self.mock_layer, color_mode="gradient", ramp_name="NotARealRamp"
        )

        self.mock_layer.setRenderer.assert_called_once()


if __name__ == "__main__":
    unittest.main()
