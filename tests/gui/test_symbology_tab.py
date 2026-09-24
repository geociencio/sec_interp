"""Tests for the Settings Symbology tab."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

from qgis.PyQt.QtWidgets import QApplication

from sec_interp.gui.ui.pages.settings.symbology_tab import SymbologyTab
from tests.base_test import BaseTestCase

_KEYS = {
    "color_mode",
    "ramp_name",
    "single_color_hex",
    "topo_line_width",
    "struct_color",
    "struct_width",
    "drill_trace_color",
    "drill_trace_width",
    "drill_labels",
    "interp_color",
    "show_legend",
    "legend_pos",
    "legend_font_size",
    "legend_max_items",
}


class TestSymbologyTab(BaseTestCase):
    """Per-layer symbology controls and their data contract."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure a QApplication exists for widget construction."""
        super().setUpClass()
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self) -> None:
        super().setUp()
        self.tab = SymbologyTab()
        self.tab.radio_single.isChecked.return_value = False
        self.tab.ramp_button.colorRampName.return_value = "Spectral"
        self.tab.topo_color_button.color.return_value.name.return_value = "#1f77b4"

    def test_get_data_contract(self) -> None:
        """get_data exposes the per-layer style keys."""
        data = self.tab.get_data()
        self.assertTrue(_KEYS.issubset(data))
        self.assertEqual(data["color_mode"], "gradient")
        self.assertEqual(data["ramp_name"], "Spectral")

    def test_load_applies_values(self) -> None:
        """load() applies persisted symbology."""
        self.tab.load(
            {
                "color_mode": "single",
                "ramp_name": "RdYlGn",
                "struct_color": "#00ff00",
                "drill_labels": False,
            }
        )
        self.tab.radio_single.setChecked.assert_called_with(True)
        self.tab.ramp_button.setColorRampFromName.assert_called_with("RdYlGn")
        self.tab.struct_color_button.setColor.assert_called()
        self.assertFalse(self.tab.chk_drill_labels.isChecked())

    def test_changed_emitted_on_control_change(self) -> None:
        """A control change emits the tab's changed signal."""
        self.tab.connect_signals()
        handler = MagicMock()
        self.tab.changed.connect(handler)

        self.tab.chk_drill_labels.setChecked(False)

        handler.assert_called()

    def test_reset_sets_gradient(self) -> None:
        """reset() returns to the gradient mode."""
        self.tab.reset()
        self.tab.radio_gradient.setChecked.assert_called_with(True)

    def test_mode_toggle_visibility(self) -> None:
        """Single mode hides the ramp and shows the color button."""
        self.tab.radio_single.isChecked.return_value = True

        with (
            patch.object(self.tab.ramp_button, "setVisible") as ramp_visible,
            patch.object(self.tab.topo_color_button, "setVisible") as color_visible,
        ):
            self.tab._on_topo_mode_changed()

        ramp_visible.assert_called_with(False)
        color_visible.assert_called_with(True)

    def test_connect_disconnect(self) -> None:
        """Signal wiring is symmetric."""
        self.tab.connect_signals()
        self.tab.disconnect_signals()

    def test_units_refresh_and_actions(self) -> None:
        """The per-unit editor reflects and mutates the ColorManager."""
        from sec_interp.gui.renderers.color_manager import ColorManager

        manager = ColorManager()
        manager.register_units({"A", "B"})

        self.tab.set_unit_manager(manager)

        self.assertEqual([row.unit_name for row in self.tab._unit_rows], ["A", "B"])

        self.tab._on_unit_visibility("A", False)
        self.assertTrue(manager.is_hidden("A"))

        self.tab._on_unit_label("A", "Alias")
        self.assertEqual(manager.label("A"), "Alias")

        self.tab._on_unit_move("B", -1)
        self.assertEqual(manager.ordered_units(), ["B", "A"])

    def test_reset_units_clears_customization(self) -> None:
        """Reset clears hidden flags, labels and order."""
        from sec_interp.gui.renderers.color_manager import ColorManager

        manager = ColorManager()
        manager.register_units({"A", "B"})
        manager.set_hidden("A", True)
        manager.set_label("A", "Alias")
        self.tab.set_unit_manager(manager)

        self.tab.reset_units()

        self.assertFalse(manager.is_hidden("A"))
        self.assertEqual(manager.label("A"), "A")
        self.assertEqual(manager.ordered_units(), ["A", "B"])
