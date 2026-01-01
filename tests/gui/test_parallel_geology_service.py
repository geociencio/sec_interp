
import unittest
from unittest.mock import MagicMock, call, patch
import threading
import  time

# BaseTestCase MUST be imported before qgis.core to setup mocks correctly
from tests.base_test import BaseTestCase

from qgis.PyQt.QtCore import QObject, pyqtSignal

# Import the service to test
from sec_interp.gui.services.parallel_geology_service import (
    ParallelGeologyService,
    GeologyProcessingThread
)

class TestGeologyProcessingThread(unittest.TestCase):

    def test_run_success(self):
        """Test successful execution of thread."""
        data = [1, 2, 3]
        processed_data = []

        def process_func(item):
            processed_data.append(item * 2)
            return item * 2

        thread = GeologyProcessingThread(data, process_func)

        # Reset signal mocks (they may be shared across instances)
        thread.processing_finished.emit.reset_mock()
        thread.progress_updated.emit.reset_mock()

        # Run synchronously for test since QThread.run is just a method in Python
        # In real QGIS, .start() calls .run() in separate thread
        thread.run()

        self.assertEqual(processed_data, [2, 4, 6])
        self.assertEqual(thread.result, [2, 4, 6])
        # Check signal emit directly
        thread.processing_finished.emit.assert_called_with([2, 4, 6])
        # Progress should be emitted for each item (33%, 66%, 100%)
        self.assertEqual(thread.progress_updated.emit.call_count, 3)

    def test_cancellation(self):
        """Test thread cancellation."""
        data = [1, 2, 3, 4, 5]
        processed_data = []

        # Function that cancels after 2 items
        def process_func(item):
            if len(processed_data) >= 2:
                thread.cancel()
            processed_data.append(item)
            return item

        thread = GeologyProcessingThread(data, process_func)

        thread.run()

        self.assertTrue(thread.is_canceled())
        thread.canceled.emit.assert_called()
        # Should stop processing after cancellation check in loop
        # Note: cancel() is called during processing of item 3, but the check
        # happens at the start of the next iteration. So items 1, 2, 3 are processed.
        self.assertEqual(len(processed_data), 3)

    def test_error_handling(self):
        """Test error during processing."""
        data = [1]

        def process_func(item):
            raise ValueError("Boom")

        thread = GeologyProcessingThread(data, process_func)

        thread.run()

        thread.error_occurred.emit.assert_called()
        args = thread.error_occurred.emit.call_args[0][0]
        self.assertIn("Boom", str(args))


class TestParallelGeologyService(unittest.TestCase):

    def setUp(self):
        self.service = ParallelGeologyService()

    def test_process_parallel_basic(self):
        """Test basic parallel processing logic."""
        # We need to mock GeologyProcessingThread to avoid actual threading but verify management
        with patch('sec_interp.gui.services.parallel_geology_service.GeologyProcessingThread') as MockThread:
            mock_thread_instance = MockThread.return_value
            mock_thread_instance.data = [1, 2] # Dummy data for chunk

            profiles = list(range(10))

            # Force max threads to 2 for predictable chunking
            self.service.max_threads = 2

            self.service.process_profiles_parallel(profiles)

            # Should create 2 threads (chunk size 5)
            # chunks: [0..4], [5..9]
            self.assertEqual(MockThread.call_count, 2)
            self.assertEqual(len(self.service.active_threads), 2)

            # Signals connected
            mock_thread_instance.processing_finished.connect.assert_called()
            mock_thread_instance.start.assert_called()

    def test_progress_aggregation(self):
        """Test progress calculation."""
        # Setup active threads state manually
        t1 = MagicMock()
        t2 = MagicMock()
        t1.data = [1] * 50
        t2.data = [1] * 50

        self.service.active_threads = [t1, t2]
        self.service._total_items = 100

        # T1 at 50% (25 items done), T2 at 0%
        # Total done = 25. Overall = 25%
        self.service._on_chunk_progress(t1, 50)
        self.service.batch_progress.emit.assert_called_with(25)

        # T1 at 100% (50 items), T2 at 50% (25 items)
        # Total done = 75. Overall = 75%
        self.service._on_chunk_progress(t1, 100)
        self.service._on_chunk_progress(t2, 50)
        self.service.batch_progress.emit.assert_called_with(75)

    def test_result_collection_and_cleanup(self):
        """Test result collection and finish signal."""
        t1 = MagicMock()
        self.service.active_threads = [t1]

        # T1 finishes
        chunk_result = ["A", "B"]
        self.service._on_chunk_finished(chunk_result)
        self.assertEqual(self.service._results, [chunk_result])

        # Cleanup T1
        self.service._cleanup_thread(t1)
        self.assertEqual(len(self.service.active_threads), 0)
        self.service.all_finished.emit.assert_called_with([chunk_result])

    def test_cancellation_service(self):
        """Test service cancellation."""
        t1 = MagicMock()
        t2 = MagicMock()
        self.service.active_threads = [t1, t2]

        self.service.cancel_processing()

        t1.cancel.assert_called()
        t2.cancel.assert_called()

        # Verify signal emission when threads confirm cancel
        # _on_chunk_canceled checks if active_threads is empty
        # We manually empty it to simulate threads confirming/cleaning up
        self.service.active_threads = []
        self.service._on_chunk_canceled()
        self.service.processing_canceled.emit.assert_called()

    def test_default_worker(self):
        """Test default worker function (Command Pattern)."""
        # (func, arg1, arg2)
        mock_func = MagicMock(return_value="Result")
        item = (mock_func, 1, 2)

        result = self.service._process_profile_chunk(item)

        mock_func.assert_called_with(1, 2)
        self.assertEqual(result, "Result")

        # Fallback
        self.assertIsNone(self.service._process_profile_chunk("NotTuple"))
        self.assertIsNone(self.service._process_profile_chunk([]))

    def test_empty_profiles(self):
        """Test processing with empty profiles list."""
        self.service.process_profiles_parallel([])
        # Should emit all_finished immediately with empty results
        self.service.all_finished.emit.assert_called_with([])

    def test_progress_with_zero_total(self):
        """Test progress calculation with zero total items."""
        self.service._total_items = 0
        t1 = MagicMock()
        t1.data = []
        self.service.active_threads = [t1]

        # Should return early without emitting
        self.service._on_chunk_progress(t1, 50)
        # Verify no emit was called (reset_mock to clear previous calls)
        self.service.batch_progress.emit.reset_mock()
        self.service._on_chunk_progress(t1, 50)
        self.service.batch_progress.emit.assert_not_called()

    def test_error_propagation(self):
        """Test error handling and cancellation."""
        t1 = MagicMock()
        t2 = MagicMock()
        self.service.active_threads = [t1, t2]

        # Trigger error
        self.service._on_chunk_error("Test error")

        # Should emit error signal
        self.service.error_occurred.emit.assert_called_with("Test error")
        # Should cancel all threads
        t1.cancel.assert_called()
        t2.cancel.assert_called()
