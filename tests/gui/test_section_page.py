"""Tests for the SectionPage 2-point line invariant."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

from qgis.PyQt.QtWidgets import QApplication

from sec_interp.gui.ui.pages.section_page import SectionPage
from tests.base_test import BaseTestCase

_METRICS_PATH = "sec_interp.gui.ui.pages.section_page.extract_section_line_metrics"


def _layer(*, valid: bool = True, geographic: bool = False) -> MagicMock:
    """Build a fake line layer for validation."""
    layer = MagicMock()
    layer.isValid.return_value = valid
    crs = MagicMock()
    crs.isValid.return_value = True
    crs.isGeographic.return_value = geographic
    layer.crs.return_value = crs
    return layer


class TestSectionPageValidation(BaseTestCase):
    """Validate that SectionPage enforces exactly 2 line vertices."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure a QApplication exists for widget construction."""
        super().setUpClass()
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self) -> None:
        super().setUp()
        self.page = SectionPage()
        self.page.line_combo.currentLayer = MagicMock(return_value=None)

    def test_requires_layer(self) -> None:
        """No layer selected fails with the required message."""
        ok, msg = self.page.validate()
        self.assertFalse(ok)
        self.assertEqual(msg, "Section line layer is required")

    def test_rejects_invalid_layer(self) -> None:
        """An invalid layer fails fast."""
        self.page.line_combo.currentLayer = MagicMock(
            return_value=_layer(valid=False)
        )
        ok, msg = self.page.validate()
        self.assertFalse(ok)
        self.assertEqual(msg, "Section line layer is not valid")

    def test_rejects_geographic_crs(self) -> None:
        """A geographic (degrees) CRS is rejected."""
        self.page.line_combo.currentLayer = MagicMock(
            return_value=_layer(geographic=True)
        )
        ok, msg = self.page.validate()
        self.assertFalse(ok)
        self.assertEqual(msg, "Section line must use a projected CRS (metric units)")

    def test_accepts_two_point_line(self) -> None:
        """A 2-vertex line passes."""
        self.page.line_combo.currentLayer = MagicMock(return_value=_layer())
        with patch(_METRICS_PATH, return_value=(2, 100.0)):
            self.assertTrue(self.page.validate()[0])

    def test_rejects_three_vertex_line(self) -> None:
        """A 3-vertex polyline is rejected with a clear message."""
        self.page.line_combo.currentLayer = MagicMock(return_value=_layer())
        with patch(_METRICS_PATH, return_value=(3, 100.0)):
            ok, msg = self.page.validate()
        self.assertFalse(ok)
        self.assertEqual(msg, "Section line must have exactly 2 vertices (start and end)")

    def test_rejects_zero_length(self) -> None:
        """A zero-length line is rejected."""
        self.page.line_combo.currentLayer = MagicMock(return_value=_layer())
        with patch(_METRICS_PATH, return_value=(2, 0.0)):
            ok, msg = self.page.validate()
        self.assertFalse(ok)
        self.assertEqual(msg, "Section line has zero length")

    def test_rejects_unreadable_geometry(self) -> None:
        """An unreadable geometry fails with a clear message."""
        self.page.line_combo.currentLayer = MagicMock(return_value=_layer())
        with patch(_METRICS_PATH, return_value=(None, None)):
            ok, msg = self.page.validate()
        self.assertFalse(ok)
        self.assertEqual(msg, "Section line layer has no readable line geometry")

    def test_is_complete_delegates_to_validate(self) -> None:
        """is_complete reflects validate()."""
        self.page.line_combo.currentLayer = MagicMock(return_value=None)
        self.assertFalse(self.page.is_complete())

        self.page.line_combo.currentLayer = MagicMock(return_value=_layer())
        with patch(_METRICS_PATH, return_value=(2, 100.0)):
            self.assertTrue(self.page.is_complete())


if __name__ == "__main__":
    import unittest

    unittest.main()
