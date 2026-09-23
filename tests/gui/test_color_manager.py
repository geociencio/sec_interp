"""Tests for per-unit color overrides and visibility (ColorManager)."""

from __future__ import annotations

from unittest.mock import patch

from qgis.PyQt.QtGui import QColor

from sec_interp.gui.renderers.base_renderer import build_categorized_line_style
from sec_interp.gui.renderers.color_manager import ColorManager
from tests.base_test import BaseTestCase


class TestColorManager(BaseTestCase):
    """Overrides, hidden units and unit registry."""

    def setUp(self) -> None:
        super().setUp()
        self.manager = ColorManager()

    def test_register_units_sorted(self) -> None:
        self.manager.register_units({"B", "A", ""})

        self.assertEqual(self.manager.known_units(), ["A", "B"])

    def test_override_wins(self) -> None:
        custom = QColor("#ff0000")
        self.manager.set_color("A", custom)

        self.assertEqual(self.manager.get_color("A"), custom)

    def test_override_survives_active_units_reset(self) -> None:
        custom = QColor("#00ff00")
        self.manager.set_color("A", custom)
        self.manager._active_units = {}  # simulate PreviewRenderer cleanup

        self.assertEqual(self.manager.get_color("A"), custom)

    def test_hidden_flag(self) -> None:
        self.manager.set_hidden("A", True)
        self.assertIn("A", self.manager.hidden_units())
        self.assertTrue(self.manager.is_hidden("A"))
        self.manager.set_hidden("A", False)
        self.assertFalse(self.manager.is_hidden("A"))

    def test_dump_load_roundtrip(self) -> None:
        self.manager.set_hidden("A", True)
        self.manager.set_color("B", QColor("#0000ff"))
        data = self.manager.dump()

        self.assertIn("B", data["overrides"])
        self.assertEqual(data["hidden"], ["A"])

        restored = ColorManager()
        restored.load(data)
        self.assertTrue(restored.is_hidden("A"))
        self.assertIn("B", restored.overrides())


class TestCategorizedHiddenUnits(BaseTestCase):
    """Hidden units are excluded from the categorized renderer."""

    def test_hidden_units_are_skipped(self) -> None:
        manager = ColorManager()
        with patch("sec_interp.gui.renderers.base_renderer.QgsRendererCategory") as category:
            build_categorized_line_style(manager, {"A", "B"}, hidden={"B"})

        self.assertEqual(category.call_count, 1)
