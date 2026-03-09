"""Tests for DialogPreviewManager."""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from tests.base_test import BaseTestCase
from qgis.core import QgsRectangle
from qgis.PyQt.QtCore import QSize
from sec_interp.gui.dialog_preview_manager import PreviewManager
from sec_interp.core.domain import PreviewParams, PreviewResult
from sec_interp.core.performance_metrics import MetricsCollector
from sec_interp.core.exceptions import SecInterpError


class TestDialogPreviewManager(BaseTestCase):
    """Tests for the PreviewManager class."""

    def setUp(self):
        super().setUp()
        self.dialog = MagicMock()
        self.dialog.tr.side_effect = lambda x: x

        # Mock preview_widget and canvas
        self.dialog.preview_widget = MagicMock()
        self.canvas = MagicMock()
        self.dialog.preview_widget.canvas = self.canvas
        self.canvas.width.return_value = 800
        self.canvas.height.return_value = 600

        # Mock plugin_instance
        self.plugin_instance = MagicMock()
        self.dialog.plugin_instance = self.plugin_instance

        # Initialize manager
        self.manager = PreviewManager(self.dialog)

        # Mock orchestrator to avoid real tasks
        self.manager.orchestrator = MagicMock()
        # Mock preview_service
        self.manager.preview_service = MagicMock()

    def test_generate_preview_invalid_params(self):
        """Test generate_preview when params validation fails."""
        self.plugin_instance._get_and_validate_inputs.return_value = None

        success, msg = self.manager.generate_preview()

        self.assertFalse(success)
        self.assertEqual(msg, "Invalid configuration")

    def test_generate_preview_success(self):
        """Test successful preview generation."""
        params = PreviewParams(
            raster_layer="raster1", line_layer="line1", band_num=1, buffer_dist=50.0
        )
        self.plugin_instance._get_and_validate_inputs.return_value = params

        result = PreviewResult(
            topo=[(0.0, 100.0), (100.0, 100.0)], metrics=MetricsCollector()
        )
        self.manager.preview_service.generate_all.return_value = result

        # Mock resolve_layer
        with patch(
            "sec_interp.gui.dialog_preview_manager.resolve_layer"
        ) as mock_resolve:
            mock_layer = MagicMock()
            mock_layer.isValid.return_value = True
            mock_resolve.return_value = mock_layer

            success, msg = self.manager.generate_preview()

            self.assertTrue(success)
            self.assertEqual(msg, "Preview generated successfully")
            self.manager.preview_service.generate_all.assert_called_once()
            self.plugin_instance.draw_preview.assert_called_once()

    def test_update_from_checkboxes_no_data(self):
        """Test update_from_checkboxes when no data is cached."""
        self.manager.last_result = None
        self.manager.update_from_checkboxes()
        self.plugin_instance.draw_preview.assert_not_called()

    def test_update_from_checkboxes_with_data(self):
        """Test update_from_checkboxes with cached data."""
        self.manager.last_result = MagicMock()
        self.manager.cached_data = {
            "topo": "topo_data",
            "geol": "geol_data",
            "struct": "struct_data",
            "drillhole": "drill_data",
        }

        # Mock checkbox states
        self.dialog.preview_widget.chk_topo.isChecked.return_value = True
        self.dialog.preview_widget.chk_geol.isChecked.return_value = False
        self.dialog.preview_widget.chk_struct.isChecked.return_value = True
        self.dialog.preview_widget.chk_drillholes.isChecked.return_value = True

        self.dialog.get_preview_options.return_value = {
            "max_points": 1000,
            "auto_lod": False,
            "use_adaptive_sampling": True,
        }

        self.manager.update_from_checkboxes()

        # Verify draw_preview was called with correct data (geol should be None)
        self.plugin_instance.draw_preview.assert_called_with(
            "topo_data",
            None,
            "struct_data",
            drillhole_data="drill_data",
            max_points=1000,
            use_adaptive_sampling=True,
        )

    def test_on_extents_changed_auto_lod_disabled(self):
        """Test on_extents_changed behavior when Auto LOD is disabled."""
        self.dialog.preview_widget.chk_auto_lod.isChecked.return_value = False
        self.manager.debounce_timer.isActive.return_value = False
        self.manager._on_extents_changed()
        # Debounce timer should not start
        self.assertFalse(self.manager.debounce_timer.isActive())

    def test_on_extents_changed_auto_lod_enabled(self):
        """Test on_extents_changed behavior when Auto LOD is enabled."""
        self.dialog.preview_widget.chk_auto_lod.isChecked.return_value = True
        self.manager._on_extents_changed()
        self.manager.debounce_timer.start.assert_called()

    def test_on_geology_finished_success(self):
        """Test handling of async geology task completion."""
        results = [MagicMock()]
        self.manager.cached_data["topo"] = MagicMock()  # Needs topo to update display

        with patch.object(self.manager, "update_from_checkboxes") as mock_update:
            self.manager._on_geology_finished(results)
            self.assertEqual(self.manager.cached_data["geol"], results)
            mock_update.assert_called_once()

    def test_on_drillhole_finished_success(self):
        """Test handling of async drillhole task completion."""
        mock_hole = MagicMock()
        mock_hole.points_3d = [MagicMock()]
        results = (MagicMock(), [mock_hole])
        self.manager.cached_data["topo"] = MagicMock()

        with patch.object(self.manager, "update_from_checkboxes") as mock_update:
            self.manager._on_drillhole_finished(results)
            self.assertEqual(self.manager.cached_data["drillhole"], [mock_hole])
            mock_update.assert_called_once()

    def test_handle_geometric_changes(self):
        """Test that interpretations are cleared when section geometry changes."""
        params = MagicMock(spec=PreviewParams)
        params.line_layer = "lyr_id"
        params.raster_layer = "raster_id"
        params.buffer_dist = 50.0

        # Mock resolve_layer and feature geometry
        with patch(
            "sec_interp.gui.dialog_preview_manager.resolve_layer"
        ) as mock_resolve:
            mock_layer = MagicMock()
            mock_feat = MagicMock()
            mock_feat.geometry().asWkt.return_value = "LINESTRING(0 0, 10 10)"
            mock_layer.getFeatures.return_value = iter([mock_feat])
            mock_resolve.return_value = mock_layer

            # First call to set initial state
            self.manager._handle_geometric_changes(params)

            # Change geometry
            mock_feat.geometry().asWkt.return_value = "LINESTRING(1 1, 11 11)"
            mock_layer.getFeatures.return_value = iter([mock_feat])

            # Second call should trigger clear
            self.dialog.interpretation_manager = MagicMock()
            self.manager._handle_geometric_changes(params)

            self.assertEqual(self.dialog.interpretation_manager.interpretations, [])
            self.dialog.interpretation_manager.save_interpretations.assert_called_once()

    def test_cleanup(self):
        """Test cleanup of resources and background tasks."""
        self.manager.cleanup()
        self.manager.orchestrator.cancel_active_tasks.assert_called_once()
        self.assertTrue(self.manager.debounce_timer.stop.called)

    def test_generate_preview_cached(self):
        """Test using cached preview data when parameters are unchanged."""
        params = PreviewParams(raster_layer="r1", line_layer="l1", band_num=1)
        self.plugin_instance._get_and_validate_inputs.return_value = params

        # Setup initial state
        result = PreviewResult(topo=[(0, 0)], metrics=MetricsCollector())
        self.manager.preview_service.generate_all.return_value = result

        with patch("sec_interp.gui.dialog_preview_manager.resolve_layer"):
            self.manager.generate_preview()
            self.assertEqual(self.manager.preview_service.generate_all.call_count, 1)

            # Second call with same params
            self.manager.generate_preview()
            # Should not call generate_all again
            self.assertEqual(self.manager.preview_service.generate_all.call_count, 1)

    def test_generate_preview_exception(self):
        """Test generate_preview exception handling."""
        self.plugin_instance._get_and_validate_inputs.side_effect = Exception("Boom")
        success, msg = self.manager.generate_preview()
        self.assertFalse(success)
        self.assertIn("Boom", msg)
        self.dialog.handle_error.assert_called()

    def test_on_geology_error(self):
        """Test handling of geology task error."""
        self.manager._on_geology_error("Failed to process segments")
        self.dialog.handle_error.assert_called()

    def test_on_drillhole_error(self):
        """Test handling of drillhole task error."""
        self.manager._on_drillhole_error("Drillhole failed")
        self.dialog.handle_error.assert_called()

    def test_update_lod_for_zoom(self):
        """Test updating detail level based on zoom."""
        self.manager.cached_data["topo"] = MagicMock()
        self.manager.cached_data["geol"] = MagicMock()
        self.manager.cached_data["struct"] = MagicMock()
        self.manager.cached_data["drillhole"] = MagicMock()

        self.dialog.get_preview_options.return_value = {"use_adaptive_sampling": True}

        self.manager._update_lod_for_zoom()
        self.plugin_instance.draw_preview.assert_called()
        # Verify it was called with preserve_extent=True
        self.assertTrue(
            self.plugin_instance.draw_preview.call_args.kwargs.get("preserve_extent")
        )

    def test_generate_preview_sec_interp_error(self):
        """Test generate_preview with SecInterpError."""
        self.plugin_instance._get_and_validate_inputs.side_effect = SecInterpError(
            "Expected"
        )
        success, msg = self.manager.generate_preview()
        self.assertFalse(success)
        self.assertEqual(msg, "Expected")

    def test_run_render_pipeline_error(self):
        """Test render pipeline error handling."""
        self.plugin_instance.draw_preview.side_effect = ValueError("Render fail")
        with self.assertRaises(ValueError):
            self.manager._run_render_pipeline(MagicMock())

    def test_update_crs_label_error(self):
        """Test update_crs_label with invalid layer."""
        self.manager._update_crs_label(None)
        self.dialog.preview_widget.lbl_crs.setText.assert_called_with("CRS: None")

        # Test exception in label update
        mock_layer = MagicMock()
        mock_layer.isValid.side_effect = AttributeError("Crash")
        self.manager._update_crs_label(mock_layer)
        self.dialog.preview_widget.lbl_crs.setText.assert_called_with("CRS: Unknown")


if __name__ == "__main__":
    unittest.main()
