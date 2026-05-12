"""Tests for GeologyGenerationTask."""

import unittest
from unittest.mock import MagicMock, patch

from sec_interp.tests.base_test import BaseTestCase
from sec_interp.gui.tasks.geology_task import GeologyGenerationTask


class TestGeologyGenerationTask(BaseTestCase):
    """Test suite for GeologyGenerationTask."""

    def setUp(self):
        super().setUp()
        self.mock_service = MagicMock()
        self.mock_input = MagicMock()
        self.params = MagicMock()
        self.task = GeologyGenerationTask(
            "Test Geology Task", self.mock_input, self.mock_service, self.params
        )

    def test_initialization(self):
        """Test task initialization."""
        self.assertEqual(self.task.description(), "Test Geology Task")
        self.assertEqual(self.task.task_input, self.mock_input)
        self.assertEqual(self.task.service, self.mock_service)
        self.assertIsNone(self.task.result)
        self.assertIsNone(self.task.exception)

    def test_run_success(self):
        """Test successful task execution."""
        expected_result = ["segment1", "segment2"]
        self.mock_service.process_task_data.return_value = expected_result

        success = self.task.run()

        self.assertTrue(success)
        self.assertEqual(self.task.result, expected_result)
        self.mock_service.process_task_data.assert_called_once_with(
            self.mock_input, feedback=self.task
        )

    def test_run_error(self):
        """Test task execution with error."""
        error = RuntimeError("Database connection failed")
        self.mock_service.process_task_data.side_effect = error

        success = self.task.run()

        self.assertFalse(success)
        self.assertEqual(self.task.exception, error)

    def test_finished_success(self):
        """Test finished signal on success."""
        # Mock signal emission
        self.task.finished_with_results.emit = MagicMock()

        expected_result = ["segment1"]
        self.task.result = expected_result

        with patch("sec_interp.gui.tasks.geology_task.QTimer.singleShot") as mock_timer:
            # Execute the lambda immediately
            mock_timer.side_effect = lambda ms, func: func()
            self.task.finished(True)

        self.task.finished_with_results.emit.assert_called_once_with(expected_result)

    def test_finished_error(self):
        """Test finished signal on error."""
        # Mock signal emission
        self.task.error_occurred.emit = MagicMock()

        self.task.exception = RuntimeError("Fatal logic error")

        with patch("qgis.core.QgsMessageLog.logMessage") as mock_log:
            self.task.finished(False)
            mock_log.assert_called_once()

        self.task.error_occurred.emit.assert_called_once_with("Fatal logic error")

    def test_set_progress(self):
        """Test progress changed signal."""
        # Mock signal emission
        self.task.progress_changed.emit = MagicMock()

        self.task.setProgress(75.5)

        self.task.progress_changed.emit.assert_called_once_with(75.5)


if __name__ == "__main__":
    unittest.main()
