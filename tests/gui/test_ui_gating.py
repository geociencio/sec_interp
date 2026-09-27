"""Tests for S0/S1/S2 button gating, page states and Mandatory labels."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from sec_interp.core.domain import PreviewParams
from sec_interp.gui.dialog_preview_manager import PreviewManager
from sec_interp.gui.dialog_state_manager import StateManager
from sec_interp.gui.preview_param_hasher import (
    PreviewParamHasher,
    assemble_preview_params,
)
from sec_interp.gui.ui_status_manager import UIStatusManager
from tests.base_test import BaseTestCase
from tests.mocks.qt_mocks import MockQListWidgetItem


def _mock_dialog() -> MagicMock:
    """Build a MagicMock dialog with the widgets gating touches."""
    dialog = MagicMock()
    dialog.tr.side_effect = lambda text: text
    dialog.preview_widget = MagicMock()
    dialog.button_box = MagicMock()
    dialog.sidebar = MagicMock()
    dialog.nav_geology = MockQListWidgetItem()
    dialog.nav_struct = MockQListWidgetItem()
    dialog.nav_drillhole = MockQListWidgetItem()
    dialog.input_manager = MagicMock()
    dialog.input_manager.get_crs_warning.return_value = ""
    dialog.input_manager.get_crs_plausibility_error.return_value = ""
    dialog.input_manager.get_section_error.return_value = ""
    dialog.preview_manager = MagicMock()
    return dialog


class TestButtonGating(BaseTestCase):
    """S0/S1/S2 button enablement through UIStatusManager."""

    def setUp(self) -> None:
        super().setUp()
        self.dialog = _mock_dialog()
        self.manager = UIStatusManager(self.dialog)

    def _states(self) -> tuple[MagicMock, MagicMock, MagicMock, MagicMock]:
        pw = self.dialog.preview_widget
        return pw.btn_preview, pw.btn_export, pw.btn_measure, pw.btn_interpret

    def test_s0_everything_disabled(self) -> None:
        """S0: incomplete inputs disable Preview and the dependent trio."""
        self.dialog.input_manager.can_preview.return_value = False
        self.dialog.input_manager.can_export.return_value = False
        self.dialog.preview_manager.is_preview_current.return_value = False

        self.manager.update_button_state()

        preview, export, measure, interpret = self._states()
        preview.setEnabled.assert_called_with(False)
        export.setEnabled.assert_called_with(False)
        measure.setEnabled.assert_called_with(False)
        interpret.setEnabled.assert_called_with(False)

    def test_s1_only_preview_enabled(self) -> None:
        """S1: valid inputs without a current preview enable Preview only."""
        self.dialog.input_manager.can_preview.return_value = True
        self.dialog.preview_manager.is_preview_current.return_value = False

        self.manager.update_button_state()

        preview, export, measure, interpret = self._states()
        preview.setEnabled.assert_called_with(True)
        export.setEnabled.assert_called_with(False)
        measure.setEnabled.assert_called_with(False)
        interpret.setEnabled.assert_called_with(False)

    def test_s2_trio_enabled(self) -> None:
        """S2: a preview for the current inputs enables the dependent trio."""
        self.dialog.input_manager.can_preview.return_value = True
        self.dialog.preview_manager.is_preview_current.return_value = True

        self.manager.update_button_state()

        preview, export, measure, interpret = self._states()
        preview.setEnabled.assert_called_with(True)
        export.setEnabled.assert_called_with(True)
        measure.setEnabled.assert_called_with(True)
        interpret.setEnabled.assert_called_with(True)

    def test_trio_requires_valid_inputs(self) -> None:
        """The trio stays disabled when inputs are invalid, even if current."""
        self.dialog.input_manager.can_preview.return_value = False
        self.dialog.preview_manager.is_preview_current.return_value = True

        self.manager.update_button_state()

        _, export, measure, interpret = self._states()
        export.setEnabled.assert_called_with(False)
        measure.setEnabled.assert_called_with(False)
        interpret.setEnabled.assert_called_with(False)

    def test_missing_preview_manager_fails_closed(self) -> None:
        """Without a preview manager the trio stays disabled (fail-closed)."""
        self.dialog.input_manager.can_preview.return_value = True
        del self.dialog.preview_manager

        self.manager.update_button_state()

        _, export, measure, interpret = self._states()
        export.setEnabled.assert_called_with(False)
        measure.setEnabled.assert_called_with(False)
        interpret.setEnabled.assert_called_with(False)

    def test_preview_tooltip_shows_blocked_reason(self) -> None:
        """A disabled Preview button explains why via its tooltip."""
        self.dialog.input_manager.can_preview.return_value = False
        self.dialog.input_manager.get_section_error.side_effect = lambda s: (
            "Section line must have exactly 2 vertices (start and end)"
            if s == "section"
            else ""
        )

        self.manager.update_button_state()

        self.dialog.preview_widget.btn_preview.setToolTip.assert_called_with(
            "Section line must have exactly 2 vertices (start and end)"
        )

    def test_preview_tooltip_restored_when_enabled(self) -> None:
        """An enabled Preview button shows the normal tooltip."""
        self.dialog.input_manager.can_preview.return_value = True
        self.dialog.preview_manager.is_preview_current.return_value = False

        self.manager.update_button_state()

        self.dialog.preview_widget.btn_preview.setToolTip.assert_called_with(
            "Generate preview"
        )


class TestPageStates(BaseTestCase):
    """Geology/Structural/Drillholes pages blocked until DEM + Section."""

    def setUp(self) -> None:
        super().setUp()
        self.dialog = _mock_dialog()
        self.manager = UIStatusManager(self.dialog)

    def test_pages_disabled_until_mandatory_inputs(self) -> None:
        """Invalid DEM/Section disables the three dependent pages."""
        self.dialog.input_manager.is_section_valid.side_effect = lambda s: s != "dem"
        self.dialog.sidebar.currentRow.return_value = 0

        self.manager.update_page_states()

        self.assertFalse(self.dialog.nav_geology.isEnabled())
        self.assertFalse(self.dialog.nav_struct.isEnabled())
        self.assertFalse(self.dialog.nav_drillhole.isEnabled())

    def test_pages_enabled_when_ready(self) -> None:
        """Valid DEM + Section enables the three dependent pages."""
        self.dialog.input_manager.is_section_valid.return_value = True
        self.dialog.sidebar.currentRow.return_value = 0

        self.manager.update_page_states()

        self.assertTrue(self.dialog.nav_geology.isEnabled())
        self.assertTrue(self.dialog.nav_struct.isEnabled())
        self.assertTrue(self.dialog.nav_drillhole.isEnabled())
        self.dialog.sidebar.setCurrentRow.assert_not_called()

    def test_falls_back_to_dem_page(self) -> None:
        """Sitting on a page that becomes disabled returns to row 0."""
        self.dialog.input_manager.is_section_valid.return_value = False
        self.dialog.sidebar.currentRow.return_value = 3

        self.manager.update_page_states()

        self.dialog.sidebar.setCurrentRow.assert_called_once_with(0)


class TestMandatoryLabels(BaseTestCase):
    """DEM / Section pages are explicitly tagged Mandatory."""

    def test_dem_page_title_marks_mandatory(self) -> None:
        """DemPage group title carries the Mandatory tag."""
        from sec_interp.gui.ui.pages.dem_page import DemPage

        page = DemPage()
        self.assertIn("Digital Elevation Model", page.title)
        self.assertIn("Mandatory", page.title)

    def test_section_page_title_marks_mandatory(self) -> None:
        """SectionPage group title carries the Mandatory tag."""
        from sec_interp.gui.ui.pages.section_page import SectionPage

        page = SectionPage()
        self.assertIn("Cross Section Line", page.title)
        self.assertIn("Mandatory", page.title)

    def test_sidebar_tags_first_two_items(self) -> None:
        """The DEM and Section sidebar entries carry the Mandatory tag."""
        from sec_interp.gui.ui.main_window import SecInterpMainWindow

        with patch("sec_interp.gui.ui.sidebar.QListWidgetItem") as mock_item:
            SecInterpMainWindow(None)

        texts = [call.args[0] for call in mock_item.call_args_list]
        self.assertGreaterEqual(len(texts), 2)
        self.assertIn("Mandatory", texts[0])
        self.assertIn("Mandatory", texts[1])


class TestStatusIndicatorFallback(BaseTestCase):
    """Status indicators use a generic stylesheet dot (no theme icons)."""

    def test_error_status_uses_error_dot(self) -> None:
        """An invalid section paints a red dot with the error tooltip."""
        dialog = _mock_dialog()
        dialog.input_manager.is_section_valid.return_value = False
        dialog.input_manager.get_section_error.return_value = "Section line error"
        manager = UIStatusManager(dialog)

        manager.update_section_status()

        label = dialog.page_section.lbl_section_status
        label.setStyleSheet.assert_called_with(
            "background-color: #c62828; border-radius: 8px;"
        )
        label.setToolTip.assert_called_with("Section line error")

    def test_ok_status_uses_ok_dot(self) -> None:
        """A valid section paints a green dot."""
        dialog = _mock_dialog()
        dialog.input_manager.is_section_valid.return_value = True
        manager = UIStatusManager(dialog)

        manager.update_section_status()

        label = dialog.page_section.lbl_section_status
        label.setStyleSheet.assert_called_with(
            "background-color: #2e7d32; border-radius: 8px;"
        )


class TestCrsMismatchWarning(BaseTestCase):
    """CRS mismatch paints an amber DEM dot and warns only once."""

    def test_raster_status_is_amber_on_crs_mismatch(self) -> None:
        dialog = _mock_dialog()
        dialog.input_manager.is_section_valid.return_value = True
        dialog.input_manager.get_crs_warning.return_value = "⚠ CRS mismatch detected!"
        manager = UIStatusManager(dialog)

        manager.update_raster_status()

        label = dialog.page_dem.lbl_raster_status
        label.setStyleSheet.assert_called_with(
            "background-color: #f9a825; border-radius: 8px;"
        )
        label.setToolTip.assert_called_with("⚠ CRS mismatch detected!")

    def test_announce_crs_mismatch_only_once(self) -> None:
        dialog = _mock_dialog()
        dialog.input_manager.get_crs_warning.return_value = "⚠ CRS mismatch detected!"
        manager = UIStatusManager(dialog)

        manager._announce_crs_warnings()
        manager._announce_crs_warnings()

        dialog.push_message.assert_called_once()
        self.assertEqual(dialog.push_message.call_args.args[0], "CRS mismatch")

    def test_reannounce_when_warning_changes(self) -> None:
        dialog = _mock_dialog()
        manager = UIStatusManager(dialog)

        dialog.input_manager.get_crs_warning.return_value = "A"
        manager._announce_crs_warnings()
        dialog.input_manager.get_crs_warning.return_value = ""
        manager._announce_crs_warnings()
        dialog.input_manager.get_crs_warning.return_value = "B"
        manager._announce_crs_warnings()

        self.assertEqual(dialog.push_message.call_count, 2)


class TestCrsPlausibilityBlocking(BaseTestCase):
    """A mislabelled CRS paints a red DEM dot and blocks once."""

    def test_raster_status_is_red_on_plausibility_error(self) -> None:
        dialog = _mock_dialog()
        dialog.input_manager.is_section_valid.return_value = True
        dialog.input_manager.get_crs_plausibility_error.return_value = "looks like degrees"
        manager = UIStatusManager(dialog)

        manager.update_raster_status()

        label = dialog.page_dem.lbl_raster_status
        label.setStyleSheet.assert_called_with(
            "background-color: #c62828; border-radius: 8px;"
        )
        label.setToolTip.assert_called_with("looks like degrees")

    def test_announce_plausibility_is_critical_and_once(self) -> None:
        dialog = _mock_dialog()
        dialog.input_manager.get_crs_plausibility_error.return_value = "looks like degrees"
        manager = UIStatusManager(dialog)

        manager._announce_crs_warnings()
        manager._announce_crs_warnings()

        dialog.push_message.assert_called_once()
        self.assertEqual(dialog.push_message.call_args.args[0], "Possible CRS mislabel")

    def test_preview_blocked_reason_includes_plausibility(self) -> None:
        dialog = _mock_dialog()
        dialog.input_manager.is_section_valid.return_value = True
        dialog.input_manager.can_preview.return_value = False
        dialog.input_manager.get_crs_plausibility_error.return_value = "looks like degrees"
        manager = UIStatusManager(dialog)

        self.assertEqual(manager._preview_blocked_reason(), "looks like degrees")


class TestAssemblePreviewParams(BaseTestCase):
    """Pure assembly of PreviewParams without validation or side effects."""

    def test_fields_mapped_with_defaults(self) -> None:
        """Known keys map through; missing keys fall back to defaults."""
        params = assemble_preview_params(
            {"raster_layer": "r1", "crossline_layer": "l1"},
            {},
            800,
        )
        self.assertIsInstance(params, PreviewParams)
        self.assertEqual(params.raster_layer, "r1")
        self.assertEqual(params.line_layer, "l1")
        self.assertEqual(params.band_num, 1)
        self.assertEqual(params.buffer_dist, 100.0)
        self.assertEqual(params.max_points, 1000)
        self.assertTrue(params.auto_lod)
        self.assertEqual(params.canvas_width, 800)

    def test_explicit_values_win(self) -> None:
        """Explicit values override the defaults."""
        params = assemble_preview_params(
            {"selected_band": 3, "buffer_distance": 50.0},
            {"max_points": 500, "auto_lod": False},
            640,
        )
        self.assertEqual(params.band_num, 3)
        self.assertEqual(params.buffer_dist, 50.0)
        self.assertEqual(params.max_points, 500)
        self.assertFalse(params.auto_lod)
        self.assertEqual(params.canvas_width, 640)


class TestIsPreviewCurrent(BaseTestCase):
    """PreviewManager.is_preview_current hash comparison logic."""

    def _manager(self) -> PreviewManager:
        manager = PreviewManager.__new__(PreviewManager)
        manager.dialog = MagicMock()
        manager.hasher = PreviewParamHasher()
        manager.last_success_hash = None
        manager.last_success_ve = None
        manager.last_result = None
        manager.dialog.get_selected_values.return_value = {}
        manager.dialog.get_preview_options.return_value = {}
        manager.dialog.preview_widget.canvas.width.return_value = 800
        manager.dialog.page_dem.auto_ve_check.isChecked.return_value = False
        manager.dialog.page_dem.vertexag_spin.value.return_value = 1.0
        return manager

    def test_no_success_hash_is_not_current(self) -> None:
        """Without a recorded success the preview is never current."""
        manager = self._manager()
        manager.last_result = object()
        self.assertFalse(manager.is_preview_current())

    def test_matching_inputs_are_current(self) -> None:
        """Identical inputs reproduce the recorded success hash."""
        manager = self._manager()
        params = assemble_preview_params({}, {}, 800)
        manager.last_success_hash = manager._calculate_params_hash(params)
        manager.last_success_ve = 1.0
        manager.last_result = object()
        self.assertTrue(manager.is_preview_current())

    def test_changed_inputs_are_not_current(self) -> None:
        """Any input change invalidates the recorded preview."""
        manager = self._manager()
        params = assemble_preview_params({}, {}, 800)
        manager.last_success_hash = manager._calculate_params_hash(params)
        manager.last_success_ve = 1.0
        manager.last_result = object()
        manager.dialog.get_selected_values.return_value = {"raster_layer": "other"}
        self.assertFalse(manager.is_preview_current())

    def test_changed_ve_is_not_current(self) -> None:
        """Changing the vertical exaggeration invalidates the preview."""
        manager = self._manager()
        params = assemble_preview_params({}, {}, 800)
        manager.last_success_hash = manager._calculate_params_hash(params)
        manager.last_success_ve = 1.0
        manager.last_result = object()
        manager.dialog.page_dem.vertexag_spin.value.return_value = 2.5
        self.assertFalse(manager.is_preview_current())


class TestResetClearsPreviewCurrency(BaseTestCase):
    """Resetting the dialog invalidates the recorded preview."""

    def test_reset_clears_hashes(self) -> None:
        """reset_to_defaults clears the success hash and cached result."""
        dialog = _mock_dialog()
        dialog.preview_manager.last_success_hash = "abc"
        dialog.preview_manager.last_success_ve = 2.0
        dialog.preview_manager.last_result = object()
        StateManager(dialog).reset_to_defaults()
        self.assertIsNone(dialog.preview_manager.last_success_hash)
        self.assertIsNone(dialog.preview_manager.last_success_ve)
        self.assertIsNone(dialog.preview_manager.last_result)


if __name__ == "__main__":
    unittest.main()
