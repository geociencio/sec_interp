from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from sec_interp.gui.tasks.geology_task import GeologyGenerationTask
from sec_interp.core.domain import GeologyContext


class TestGeologyGenerationTask(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Mock QCoreApplication for logger
        self.patcher = patch("qgis.PyQt.QtCore.QCoreApplication")
        self.mock_qapp_cls = self.patcher.start()
        self.mock_qapp_cls.instance.return_value.thread.return_value = "MainThread"

        self.mock_service = MagicMock()
        self.mock_input = MagicMock(spec=GeologyContext)

        self.task = GeologyGenerationTask(
            description="Test Task",
            context=self.mock_input,
            service=self.mock_service,
            params=MagicMock(),
        )

    def tearDown(self):
        self.patcher.stop()
        super().tearDown()

    def test_run_success(self):
        """Test successful task execution."""
        # Setup service to return results
        expected_results = [MagicMock()]
        self.mock_service.build_segments.return_value = expected_results

        success = self.task.run()

        self.assertTrue(success)
        self.mock_service.build_segments.assert_called_with(
            self.mock_input, feedback=self.task
        )

        # Test completion via finished method
        self.task.finished(True)
        self.assertEqual(self.task.result, expected_results)

    def test_run_failure(self):
        """Test task failure handling."""
        # Setup service to raise exception
        self.mock_service.build_segments.side_effect = Exception("Processing Error")

        # Mock QgsMessageLog to avoid potential QGIS application errors during log
        with patch("sec_interp.gui.tasks.geology_task.QgsMessageLog") as mock_log:
            success = self.task.run()

            self.assertFalse(success)
            self.assertIsNotNone(self.task.exception)

            # Test completion failure
            self.task.finished(False)
            self.assertIsNone(self.task.result)
            mock_log.logMessage.assert_called()
