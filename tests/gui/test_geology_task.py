"""Unit tests for GeologyGenerationTask."""

import unittest
from unittest.mock import MagicMock, patch

from qgis.core import QgsTask
from sec_interp.gui.tasks.geology_task import GeologyGenerationTask
from sec_interp.core.types import GeologyTaskInput

class TestGeologyGenerationTask(unittest.TestCase):
    def setUp(self):
        # Mock QCoreApplication for logger
        self.patcher = patch('qgis.PyQt.QtCore.QCoreApplication')
        self.mock_qapp_cls = self.patcher.start()
        self.mock_qapp_cls.instance.return_value.thread.return_value = 'MainThread'

        self.mock_service = MagicMock()
        self.mock_input = MagicMock(spec=GeologyTaskInput)
        self.mock_input.crs_authid = "EPSG:4326"
        self.on_finished = MagicMock()
        self.on_error = MagicMock()

        self.task = GeologyGenerationTask(
            self.mock_service,
            self.mock_input,
            self.on_finished,
            self.on_error
        )

    def tearDown(self):
        self.patcher.stop()

    def test_run_success(self):
        """Test successful task execution."""
        # Setup service to return results
        expected_results = [MagicMock()]
        self.mock_service.process_task_data.return_value = expected_results

        # Run task logic (synchronously for testing)
        success = self.task.run()

        self.assertTrue(success)
        self.mock_service.process_task_data.assert_called_with(
            self.mock_input, feedback=self.task
        )

        # Test completion
        self.task.finished(True)
        self.on_finished.assert_called_with(expected_results)
        self.on_error.assert_not_called()

    def test_run_failure(self):
        """Test task failure handling."""
        # Setup service to raise exception
        self.mock_service.process_task_data.side_effect = Exception("Processing Error")

        # Mock QgsMessageLog to avoid potential QGIS application errors during log
        with patch('sec_interp.gui.tasks.geology_task.QgsMessageLog') as mock_log:
            success = self.task.run()

            self.assertFalse(success)
            self.assertIsNotNone(self.task.exception)

            # Test completion failure
            self.task.finished(False)
            self.on_finished.assert_not_called()
            self.on_error.assert_called()
            mock_log.logMessage.assert_called()
