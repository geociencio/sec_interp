"""Tests for the SectionPage 2-point line invariant and profile style."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

from qgis.PyQt.QtWidgets import QApplication

from sec_interp.core.domain import PreviewParams
from sec_interp.gui.adapters.geometry import ProfileRasterStats
from sec_interp.gui.preview_param_hasher import PreviewParamHasher
from sec_interp.gui.ui.pages.section_page import SectionPage
from tests.base_test import BaseTestCase

_SECTION_PAGE = "sec_interp.gui.ui.pages.section_page"

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
        self.page.line_combo.currentLayer = MagicMock(return_value=_layer(valid=False))
        ok, msg = self.page.validate()
        self.assertFalse(ok)
        self.assertEqual(msg, "Section line layer is not valid")

    def test_rejects_geographic_crs(self) -> None:
        """A geographic (degrees) CRS is rejected."""
        self.page.line_combo.currentLayer = MagicMock(return_value=_layer(geographic=True))
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


class TestTopoStyleHash(BaseTestCase):
    """The preview hash must change when the profile style changes."""

    def test_style_changes_hash(self) -> None:
        base = PreviewParams(raster_layer="r", line_layer="l", band_num=1)
        gradient = PreviewParams(
            raster_layer="r",
            line_layer="l",
            band_num=1,
            color_mode="gradient",
            ramp_name="Spectral",
        )
        single = PreviewParams(
            raster_layer="r",
            line_layer="l",
            band_num=1,
            color_mode="single",
            single_color_hex="#ff0000",
        )

        h_base = PreviewParamHasher.calculate_hash(base)
        h_gradient = PreviewParamHasher.calculate_hash(gradient)
        h_single = PreviewParamHasher.calculate_hash(single)

        self.assertNotEqual(h_base, h_gradient)
        self.assertNotEqual(h_gradient, h_single)

    def test_smoothing_changes_hash(self) -> None:
        base = PreviewParams(raster_layer="r", line_layer="l", band_num=1)
        smoothed = PreviewParams(
            raster_layer="r",
            line_layer="l",
            band_num=1,
            smooth=True,
            smooth_window=50,
        )

        self.assertNotEqual(
            PreviewParamHasher.calculate_hash(base),
            PreviewParamHasher.calculate_hash(smoothed),
        )


class TestSectionPageDemStats(BaseTestCase):
    """Read-only perfil-vs-DEM statistics via the injected DEM provider."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure a QApplication exists for widget construction."""
        super().setUpClass()
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self) -> None:
        super().setUp()
        self.page = SectionPage()

    def _with_line(self):
        return (
            patch.object(self.page.line_combo, "currentLayer", return_value=MagicMock()),
            patch(f"{_SECTION_PAGE}.resolve_section_geometry", return_value=MagicMock()),
            patch(f"{_SECTION_PAGE}.create_distance_area", return_value=MagicMock()),
        )

    def test_update_dem_stats_display(self) -> None:
        """Stats are formatted into the fields."""
        raster = MagicMock()
        raster.isValid.return_value = True
        self.page.set_dem_provider(lambda: (raster, 1))
        stats = ProfileRasterStats(
            count=430,
            minimum=221.0,
            maximum=593.0,
            mean=433.4,
            resolution=14.24,
            length=6109.0,
        )

        line_patch, geom_patch, da_patch = self._with_line()
        with (
            line_patch,
            geom_patch,
            da_patch,
            patch(f"{_SECTION_PAGE}.profile_raster_statistics", return_value=stats),
        ):
            self.page.update_dem_stats()

        self.assertEqual(self.page.min_edit.text(), "221.00")
        self.assertEqual(self.page.max_edit.text(), "593.00")
        self.assertEqual(self.page.mean_edit.text(), "433.40")
        self.assertEqual(self.page.samples_edit.text(), "430 @ 14.24")

    def test_update_dem_stats_blanks_without_raster(self) -> None:
        """No DEM selection blanks the fields."""
        self.page.set_dem_provider(lambda: (None, 1))
        self.page.min_edit.setText("stale")

        self.page.update_dem_stats()

        self.assertEqual(self.page.min_edit.text(), "")

    def test_update_dem_stats_blanks_when_no_stats(self) -> None:
        """Unusable sampling blanks the fields without raising."""
        raster = MagicMock()
        raster.isValid.return_value = True
        self.page.set_dem_provider(lambda: (raster, 1))
        self.page.mean_edit.setText("stale")

        line_patch, geom_patch, da_patch = self._with_line()
        with (
            line_patch,
            geom_patch,
            da_patch,
            patch(f"{_SECTION_PAGE}.profile_raster_statistics", return_value=None),
        ):
            self.page.update_dem_stats()

        self.assertEqual(self.page.mean_edit.text(), "")


if __name__ == "__main__":
    import unittest

    unittest.main()
