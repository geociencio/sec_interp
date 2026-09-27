"""Tests for the preview controls (topography smoothing options)."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

from qgis.PyQt.QtWidgets import QApplication

from sec_interp.gui.dialog_facade_mixin import DialogFacadeMixin
from sec_interp.gui.ui.pages.preview_page import PreviewWidget
from tests.base_test import BaseTestCase


class _Facade(DialogFacadeMixin):
    """Minimal host exposing only what ``get_preview_options`` reads."""

    def __init__(self, widget: PreviewWidget) -> None:
        self.preview_widget = widget
        self.page_settings = MagicMock()
        self.page_settings.symbology_tab.get_data.return_value = {"show_legend": True}


class TestPreviewSmoothingControls(BaseTestCase):
    """Smooth checkbox + window plumbing in the Controls group."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure a QApplication exists for widget construction."""
        super().setUpClass()
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self) -> None:
        super().setUp()
        self.widget = PreviewWidget()

    def test_dump_includes_smooth_keys(self) -> None:
        """dump() carries the smoothing keys."""
        self.widget.chk_smooth.setChecked(False)
        self.widget.spin_smooth_window.value.return_value = 30

        data = self.widget.dump()

        self.assertFalse(data["smooth"])
        self.assertEqual(data["smooth_window"], 30)

    def test_toggle_enables_window(self) -> None:
        """Enabling Smooth enables the window spinbox."""
        self.widget._toggle_smooth_spin(True)

        self.widget.spin_smooth_window.setEnabled.assert_called_with(True)

    def test_load_restores_smooth(self) -> None:
        """load() applies the persisted smoothing state."""
        self.widget.load({"smooth": True, "smooth_window": 120})

        self.assertTrue(self.widget.chk_smooth.isChecked())
        self.widget.spin_smooth_window.setValue.assert_called_with(120)

    def test_reset_disables_smooth(self) -> None:
        """reset() turns smoothing off and restores the default window."""
        self.widget.chk_smooth.setChecked(True)

        self.widget.reset()

        self.assertFalse(self.widget.chk_smooth.isChecked())
        self.widget.spin_smooth_window.setValue.assert_called_with(30)

    def test_get_preview_options_exposes_smooth(self) -> None:
        """get_preview_options() reports the smoothing selection."""
        self.widget.chk_smooth.setChecked(True)
        self.widget.spin_smooth_window.value.return_value = 45
        facade = _Facade(self.widget)

        options = facade.get_preview_options()

        self.assertTrue(options["smooth"])
        self.assertEqual(options["smooth_window"], 45)
