"""Performance metrics module for SecInterp plugin.

This module provides tools for tracking performance and resource usage
across the plugin's operations.
"""

from __future__ import annotations

from contextlib import contextmanager
import time
from typing import Any, Optional

from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


class MetricsCollector:
    """Collects and aggregates performance metrics."""

    def __init__(self):
        self.timings: dict[str, float] = {}
        self.counts: dict[str, int] = {}
        self.metadata: dict[str, Any] = {}
        self._start_time = time.perf_counter()

    def record_timing(self, operation: str, duration: float) -> None:
        """Record duration of an operation.

        Args:
            operation: Name of the operation
            duration: Duration in seconds
        """
        self.timings[operation] = duration

    def record_count(self, metric: str, count: int) -> None:
        """Record a count metric (e.g. number of points).

        Args:
            metric: Name of the metric
            count: Count value
        """
        self.counts[metric] = count

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the metrics collection.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

    def get_summary(self) -> dict[str, Any]:
        """Get summary of collected metrics.

        Returns:
            Dictionary with all collected metrics
        """
        return {
            "timings": self.timings,
            "counts": self.counts,
            "metadata": self.metadata,
            "total_duration": time.perf_counter() - self._start_time,
        }

    def clear(self) -> None:
        """Clear all collected metrics."""
        self.timings.clear()
        self.counts.clear()
        self.metadata.clear()
        self._start_time = time.perf_counter()


class PerformanceTimer:
    """Context manager for timing operations."""

    def __init__(
        self,
        operation_name: str,
        collector: Optional[MetricsCollector] = None,
        logger_func: Optional[Any] = None,
    ):
        """Initialize timer.

        Args:
            operation_name: Name of operation to measure
            collector: Optional metrics collector to record into
            logger_func: Optional logger function for immediate logging
        """
        self.operation_name = operation_name
        self.collector = collector
        self.logger_func = logger_func
        self.start_time: float = 0.0
        self.duration: float = 0.0

    def __enter__(self):
        """Start the timer.

        Returns:
            self: The timer instance
        """
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the timer and record/log validity.

        Args:
            exc_type: Exception type if raised
            exc_val: Exception value if raised
            exc_tb: Exception traceback if raised
        """
        self.duration = time.perf_counter() - self.start_time

        if self.collector:
            self.collector.record_timing(self.operation_name, self.duration)

        if self.logger_func:
            self.logger_func(f"{self.operation_name}: {self.duration:.3f}s")


def format_duration(seconds: float) -> str:
    """Format duration in human readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g. "1.2s", "150ms")
    """
    if seconds < 0.001:
        return f"{seconds * 1000000:.0f}µs"

    if seconds < 1.0:
        return f"{seconds * 1000:.0f}ms"

    return f"{seconds:.1f}s"


# --- New Implementation ---

from functools import wraps
import logging
import tracemalloc


class PerformanceMonitor:
    """Performance monitoring using only Python standard library."""

    def __init__(self, log_file="performance.log"):
        self.logger = self._setup_logger(log_file)
        self.metrics = {}

    def _setup_logger(self, log_file):
        """Setup performance logger."""
        logger = logging.getLogger("performance")
        logger.setLevel(logging.INFO)

        # Check if handler already exists to avoid duplicates
        if not logger.handlers:
            # Create file handler
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    @contextmanager
    def measure_operation(self, operation_name, **metadata):
        """Context manager to measure operation performance."""
        # Start measuring
        start_time = time.perf_counter()
        start_memory = self._get_memory_usage()
        tracemalloc.start()

        try:
            yield
        finally:
            # Stop measuring
            end_time = time.perf_counter()
            end_memory = self._get_memory_usage()

            try:
                current, peak = tracemalloc.get_traced_memory()
            except RuntimeError:
                # Tracemalloc might not be started if nested calls improperly handle it
                _current, peak = 0, 0

            tracemalloc.stop()

            # Calculate metrics
            duration = end_time - start_time
            memory_diff = end_memory - start_memory

            # Log metrics
            log_data = {
                "operation": operation_name,
                "duration_seconds": round(duration, 4),
                "memory_mb": round(memory_diff, 2),
                "memory_peak_mb": round(peak / 1024 / 1024, 2),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                **metadata,
            }

            self.logger.info(f"Performance: {log_data}")

            # Store for analysis
            if operation_name not in self.metrics:
                self.metrics[operation_name] = []
            self.metrics[operation_name].append(log_data)

    def _get_memory_usage(self):
        """Get current memory usage in MB."""
        try:
            import psutil

            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            # Fallback without psutil
            return 0.0

    def get_operation_stats(self, operation_name):
        """Get statistics for an operation."""
        if operation_name not in self.metrics:
            return None

        operation_metrics = self.metrics[operation_name]

        durations = [m["duration_seconds"] for m in operation_metrics]
        memory_usages = [m["memory_mb"] for m in operation_metrics]

        return {
            "count": len(operation_metrics),
            "avg_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "avg_memory": sum(memory_usages) / len(memory_usages),
            "min_memory": min(memory_usages),
            "max_memory": max(memory_usages),
        }


def performance_monitor(func):
    """Decorator to automatically monitor function performance."""
    monitor = PerformanceMonitor()

    @wraps(func)
    def wrapper(*args, **kwargs):
        operation_name = f"{func.__module__}.{func.__name__}"

        with monitor.measure_operation(
            operation_name, args_count=len(args), kwargs_keys=list(kwargs.keys())
        ):
            return func(*args, **kwargs)

    return wrapper
