"""Tests for DrillholeGenerationTask."""

import unittest
from unittest.mock import MagicMock, patch

from sec_interp.tests.base_test import BaseTestCase
from sec_interp.gui.tasks.drillhole_task import DrillholeGenerationTask


class TestDrillholeGenerationTask(BaseTestCase):
    """Test suite for DrillholeGenerationTask."""

    def setUp(self):
        super().setUp()
        self.mock_orchestrator = MagicMock()
        self.mock_input = MagicMock()
        self.params = MagicMock()
        self.task = DrillholeGenerationTask(
            "Test Task", self.mock_input, self.mock_orchestrator, self.params
        )

    def test_initialization(self):
        """Test task initialization."""
        self.assertEqual(self.task.description(), "Test Task")
        self.assertEqual(self.task.task_input, self.mock_input)
        self.assertEqual(self.task.orchestrator, self.mock_orchestrator)
        self.assertIsNone(self.task.result)
        self.assertIsNone(self.task.exception)

    def test_run_success(self):
        """Test successful task execution."""
        expected_result = (["geol"], ["hole1", "hole2"])
        self.mock_orchestrator.process_task_data.return_value = expected_result

        success = self.task.run()

        self.assertTrue(success)
        self.assertEqual(self.task.result, expected_result)
        self.mock_orchestrator.process_task_data.assert_called_once_with(
            self.mock_input, feedback=self.task
        )

    def test_run_error(self):
        """Test task execution with error."""
        error = ValueError("Something went wrong")
        self.mock_orchestrator.process_task_data.side_effect = error

        success = self.task.run()

        self.assertFalse(success)
        self.assertEqual(self.task.exception, error)

    def test_finished_success(self):
        """Test finished signal on success."""
        # Mock signal emission
        self.task.finished_with_results.emit = MagicMock()

        expected_result = (["geol"], ["hole1"])
        self.task.result = expected_result

        with patch("sec_interp.gui.tasks.drillhole_task.QTimer.singleShot") as mock_timer:
            # Execute the lambda immediately
            mock_timer.side_effect = lambda ms, func: func()
            self.task.finished(True)

        self.task.finished_with_results.emit.assert_called_once_with(expected_result)

    def test_finished_error(self):
        """Test finished signal on error."""
        # Mock signal emission
        self.task.error_occurred.emit = MagicMock()

        self.task.exception = ValueError("Critical error")

        # We need to patch QgsMessageLog to avoid real logging
        with patch("qgis.core.QgsMessageLog.logMessage") as mock_log:
            self.task.finished(False)
            mock_log.assert_called_once()

        self.task.error_occurred.emit.assert_called_once_with("Critical error")

    def test_set_progress(self):
        """Test progress changed signal."""
        # Mock signal emission
        self.task.progress_changed.emit = MagicMock()

        self.task.setProgress(50.0)

        self.task.progress_changed.emit.assert_called_once_with(50.0)


if __name__ == "__main__":
    unittest.main()
