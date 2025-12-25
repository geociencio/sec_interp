"""Parallel geology processing service.

This module implements parallel processing capabilities for geology services
using QThread.
"""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
import os
import threading
from typing import Any

from qgis.PyQt.QtCore import QObject, QThread, pyqtSignal

from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


class GeologyProcessingThread(QThread):
    """Thread for parallel geological data processing."""

    progress_updated = pyqtSignal(int)
    processing_finished = pyqtSignal(object)
    error_occurred = pyqtSignal(str)

    def __init__(self, data: list[Any], processing_func: Callable[[Any], Any]):
        """Initialize processing thread.

        Args:
            data: List of items to process
            processing_func: Function to process each item
        """
        super().__init__()
        self.data = data
        self.processing_func = processing_func
        self.result = None

    def run(self):
        """Execute processing in separate thread."""
        try:
            results_list = []
            total = len(self.data)
            for i, item in enumerate(self.data, 1):
                # Process each item
                res = self.processing_func(item)
                if res is not None:
                    results_list.append(res)

                if total > 0:
                    progress = int((i / total) * 100)
                    self.progress_updated.emit(progress)

            self.result = results_list
            self.processing_finished.emit(self.result)
        except Exception as e:
            logger.error(f"Error in processing thread: {e}", exc_info=True)
            self.error_occurred.emit(str(e))


class ParallelGeologyService(QObject):
    """Service with parallel processing using QThreads."""

    all_finished = pyqtSignal(list)
    batch_progress = pyqtSignal(int)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.active_threads = []
        self._results = []
        self._total_items = 0
        self._processed_items = 0
        self.max_threads = self._get_optimal_thread_count()

    def _get_optimal_thread_count(self):
        """Get optimal number of threads based on CPU cores."""
        return min(os.cpu_count() or 1, 8)  # Limit to 8 for QGIS stability

    def process_profiles_parallel(
        self,
        profiles: list[Any],
        processing_func: Optional[Callable[[Any], Any]] = None,
    ):
        """Process multiple profiles in parallel using threads asynchronously.

        Args:
            profiles: List of profiles to process
            processing_func: Optional custom processing function.
                If None, uses internal _process_profile_chunk.
        """
        if not profiles:
            self.all_finished.emit([])
            return

        self._results = []
        self.active_threads = []
        self._total_items = len(profiles)
        self._processed_items = 0

        # Use provided function or default
        worker_func = (
            processing_func if processing_func else self._process_profile_chunk
        )

        # Split work into chunks
        chunk_size = max(1, len(profiles) // self.max_threads)
        chunks = [
            profiles[i : i + chunk_size] for i in range(0, len(profiles), chunk_size)
        ]

        for chunk in chunks:
            thread = GeologyProcessingThread(chunk, worker_func)

            # Connect signals
            thread.processing_finished.connect(self._on_chunk_finished)
            thread.progress_updated.connect(self._on_chunk_progress)
            thread.error_occurred.connect(self._on_chunk_error)

            # Ensure thread cleanup
            thread.finished.connect(lambda t=thread: self._cleanup_thread(t))

            self.active_threads.append(thread)
            thread.start()

    def _on_chunk_finished(self, result):
        """Handle completion of a chunk."""
        if result:
            self._results.append(result)

        # Check if all threads are done
        # Note: This simple check might need to be more robust for production
        # relying on active_threads list management in cleanup

    def _cleanup_thread(self, thread):
        """Clean up finished thread and check for batch completion."""
        if thread in self.active_threads:
            self.active_threads.remove(thread)

        if not self.active_threads:
            self.all_finished.emit(self._results)

    def _on_chunk_progress(self, progress):
        """Aggregate progress from threads (simplified)."""
        # A proper implementation would need to weigh progress by chunk size
        # giving a rough estimate for now
        pass

    def _on_chunk_error(self, error_msg):
        """Handle error from a thread."""
        logger.error(f"Parallel processing error: {error_msg}")
        self.error_occurred.emit(error_msg)

    def _process_profile_chunk(self, profile_chunk):
        """Process a chunk of profiles (single item from chunk list).

        Args:
            profile_chunk: A single profile item (despite the name)
        """
        # Default behavior: Command Pattern
        # If the item is a tuple/list where the first element is callable, execute it
        if isinstance(profile_chunk, (list, tuple)) and len(profile_chunk) > 0:
            func = profile_chunk[0]
            args = profile_chunk[1:]
            if callable(func):
                return func(*args)

        # Fallback or other logic could go here
        return None
