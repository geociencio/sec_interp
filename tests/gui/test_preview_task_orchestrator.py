"""Tests for PreviewTaskOrchestrator."""

import unittest
from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from sec_interp.gui.preview_task_orchestrator import PreviewTaskOrchestrator


class TestPreviewTaskOrchestrator(BaseTestCase):
    """Tests for the PreviewTaskOrchestrator class."""

    def setUp(self):
        super().setUp()
        self.manager = MagicMock()
        self.orchestrator = PreviewTaskOrchestrator(self.manager)

        # Mock QgsApplication.taskManager()
        self.mock_task_manager = MagicMock()
        with patch(
            "qgis.core.QgsApplication.taskManager", return_value=self.mock_task_manager
        ):
            pass

    def test_cancel_active_tasks(self):
        """Test cancellation of active geology and drillhole tasks."""
        mock_geol_task = MagicMock()
        mock_drill_task = MagicMock()
        self.orchestrator.geology_task = mock_geol_task
        self.orchestrator.drillhole_task = mock_drill_task

        self.orchestrator.cancel_active_tasks()

        mock_geol_task.cancel.assert_called_once()
        mock_drill_task.cancel.assert_called_once()
        self.assertIsNone(self.orchestrator.geology_task)
        self.assertIsNone(self.orchestrator.drillhole_task)

    @patch("sec_interp.gui.preview_task_orchestrator.GeologyGenerationTask")
    @patch("sec_interp.gui.preview_task_orchestrator.resolve_layer")
    @patch("qgis.core.QgsApplication.taskManager")
    def test_start_geology_task(self, mock_qgs_tm, mock_resolve, mock_task_class):
        """Test starting a geology generation task."""
        params = MagicMock()
        service = MagicMock()
        mock_resolve.return_value = MagicMock()  # All layers exist

        self.orchestrator.start_geology_task(params, service)

        mock_task_class.assert_called_once()
        mock_qgs_tm.return_value.addTask.assert_called_once()
        self.assertIsNotNone(self.orchestrator.geology_task)

    @patch("sec_interp.gui.preview_task_orchestrator.DrillholeGenerationTask")
    @patch("sec_interp.gui.preview_task_orchestrator.resolve_layer")
    @patch("qgis.core.QgsApplication.taskManager")
    def test_start_drillhole_task(self, mock_qgs_tm, mock_resolve, mock_task_class):
        """Test starting a drillhole generation task."""
        params = MagicMock()
        service = MagicMock()
        mock_resolve.return_value = MagicMock()

        self.orchestrator.start_drillhole_task(params, service)

        mock_task_class.assert_called_once()
        mock_qgs_tm.return_value.addTask.assert_called_once()
        self.assertIsNotNone(self.orchestrator.drillhole_task)

    def test_cancel_with_error_on_disconnect(self):
        """Test cancel_active_tasks when disconnect raises error."""
        mock_geol_task = MagicMock()
        mock_geol_task.finished_with_results.disconnect.side_effect = TypeError(
            "Mock error"
        )
        self.orchestrator.geology_task = mock_geol_task

        # Should not raise
        self.orchestrator.cancel_active_tasks()
        self.assertIsNone(self.orchestrator.geology_task)

    @patch("sec_interp.gui.preview_task_orchestrator.resolve_layer")
    def test_start_geology_task_cancels_existing(self, mock_resolve):
        """Test that starting a new geology task cancels the previous one."""
        old_task = MagicMock()
        self.orchestrator.geology_task = old_task
        params = MagicMock()
        service = MagicMock()

        with patch("sec_interp.gui.preview_task_orchestrator.GeologyGenerationTask"):
            with patch("qgis.core.QgsApplication.taskManager"):
                self.orchestrator.start_geology_task(params, service)
                old_task.cancel.assert_called_once()

    @patch("sec_interp.gui.preview_task_orchestrator.resolve_layer")
    def test_start_drillhole_task_cancels_existing(self, mock_resolve):
        """Test that starting a new drillhole task cancels the previous one."""
        old_task = MagicMock()
        self.orchestrator.drillhole_task = old_task
        params = MagicMock()
        service = MagicMock()

        with patch("sec_interp.gui.preview_task_orchestrator.DrillholeGenerationTask"):
            with patch("qgis.core.QgsApplication.taskManager"):
                self.orchestrator.start_drillhole_task(params, service)
                old_task.cancel.assert_called_once()


if __name__ == "__main__":
    unittest.main()
